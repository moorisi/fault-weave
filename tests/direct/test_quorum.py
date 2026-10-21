import ast
import hashlib
import itertools
import json
from pathlib import Path
import random
import re
import subprocess
import pytest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'contracts/fault_weave.py'
REPO = 'moorisi/fault-weave'


def model(case='uniform'):
    return {'faults': [int(m.bit_count() <= (2 if case == 'impossible' else 1)) if case != 'core' else int(m & ~1 == 0) for m in range(16)], 'outages': [int(m.bit_count() <= 1) for m in range(16)], 'anchors': [[0], [1]]}


def record(case):
    raw = (ROOT / 'fixtures' / (case + '.json')).read_bytes()
    return f'https://raw.githubusercontent.com/{REPO}/' + 'a' * 40 + f'/fixtures/{case}.json', hashlib.sha256(raw).hexdigest(), raw


def deploy(factory, vm, accounts, case='uniform', body=None, **kwargs):
    vm.sender = accounts[0]
    url, digest, _ = record(case)
    if body is not None: digest = hashlib.sha256(body).hexdigest()
    args = {'repository': REPO, 'register': 'release-register', 'labels': ['Aspen', 'Birch', 'Cedar', 'Dogwood'], 'signers': accounts[:4], 'url': url, 'sha256': digest}
    args.update(kwargs)
    return factory(str(SOURCE), **args)


def mocks(vm, case='uniform', answer=None, audit=None, body=None, status=200):
    vm.clear_mocks()
    url, _, raw = record(case)
    vm.mock_web(re.escape(url), {'status': status, 'body': raw if body is None else body})
    vm.mock_llm(r'.*FAULTWEAVE-EXTRACT.*', json.dumps(model(case) if answer is None else answer))
    vm.mock_llm(r'.*FAULTWEAVE-AUDIT.*', json.dumps({'faults_valid': True, 'outages_valid': True, 'anchors_valid': True} if audit is None else audit))


def activate(c, vm, case='uniform', **kwargs):
    mocks(vm, case, **kwargs)
    c.compile()
    assert vm.run_validator() is True


def functions():
    names = {'integer', 'minimal_sets', 'compile_quorum', 'valid_model'}
    tree = ast.parse(SOURCE.read_text())
    ns = {'itertools': itertools}
    exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name in names], type_ignores=[]), str(SOURCE), 'exec'), ns)
    return ns


def safe(family, faults, outages, n):
    return bool(family) and all(any(q & o == 0 for q in family) for o in range(1 << n) if outages[o] == 1) and all(any((a & b) & (1 << i) and not f & (1 << i) for i in range(n)) for a in family for b in family for f in range(1 << n) if faults[f] == 1)


def closed_families(n):
    size = 1 << n
    return [[int(bool(bits & (1 << m))) for m in range(size)] for bits in range(1, 1 << size, 2) if all(not bits & (1 << sup) or all(bits & (1 << sub) for sub in range(size) if sub & sup == sub) for sup in range(size))]


@pytest.mark.parametrize('case,weights,threshold,quorums', [('uniform', [1, 1, 1, 1], 3, [7, 11, 13, 14]), ('core', [0, 1, 1, 1], 2, [6, 10, 12])])
def test_policy_changes_actual_authorization(direct_deploy, direct_vm, direct_accounts, case, weights, threshold, quorums):
    c = deploy(direct_deploy, direct_vm, direct_accounts, case)
    activate(c, direct_vm, case)
    p = c.get_state()['policy']
    assert p == {'status': 'ACTIVE', 'weights': weights, 'threshold': threshold, 'quorums': quorums, 'witness': []}
    c.propose('release-a')
    for i in [0, 1]:
        direct_vm.sender = direct_accounts[i]; c.endorse(0)
    before = c.get_state()
    with direct_vm.expect_revert('Quorum not met'): c.execute(0)
    assert c.get_state() == before
    direct_vm.sender = direct_accounts[2]; c.endorse(0)
    c.execute(0)
    assert c.get_state()['value'] == 'release-a' and c.get_state()['nonce'] == 1


def test_revocation_and_stale_competing_command(direct_deploy, direct_vm, direct_accounts):
    c = deploy(direct_deploy, direct_vm, direct_accounts); activate(c, direct_vm)
    c.propose('first'); direct_vm.sender = direct_accounts[1]; c.propose('competing')
    for i in range(3):
        direct_vm.sender = direct_accounts[i]; c.endorse(0)
    c.revoke(0)
    with direct_vm.expect_revert('Quorum not met'): c.execute(0)
    direct_vm.sender = direct_accounts[3]; c.endorse(0); c.execute(0)
    before = c.get_state()
    assert before['history'] == [{'nonce': 0, 'proposal_id': 0, 'value': 'first', 'endorsements': 11}]
    for method in ['endorse', 'revoke', 'execute']:
        with direct_vm.expect_revert('Stale proposal'): getattr(c, method)(1)
        assert c.get_state() == before


def test_later_nonce_needs_new_signatures(direct_deploy, direct_vm, direct_accounts):
    c = deploy(direct_deploy, direct_vm, direct_accounts, 'core'); activate(c, direct_vm, 'core')
    for k in range(2):
        c.propose('release-' + str(k))
        with direct_vm.expect_revert('Quorum not met'): c.execute(k)
        for i in [1, 3]:
            direct_vm.sender = direct_accounts[i]; c.endorse(k)
        c.execute(k)
    assert c.get_state()['nonce'] == 2 and len(c.get_state()['history']) == 2


def test_mathematical_impossibility_witness_blocks_execution(direct_deploy, direct_vm, direct_accounts):
    c = deploy(direct_deploy, direct_vm, direct_accounts, 'impossible'); activate(c, direct_vm, 'impossible')
    before = c.get_state()
    assert before['policy']['status'] == 'BLOCKED'
    a, b, fault = before['policy']['witness']
    assert model('impossible')['outages'][a] == model('impossible')['outages'][b] == model('impossible')['faults'][fault] == 1
    assert (15 & ~a & ~b) & ~fault == 0
    with direct_vm.expect_revert('Active quorum required'): c.propose('bypass')
    with direct_vm.expect_revert('Active quorum required'): c.execute(0)
    assert c.get_state() == before


def test_unknown_is_not_silently_treated_as_a_safe_exclusion(direct_deploy, direct_vm, direct_accounts):
    c = deploy(direct_deploy, direct_vm, direct_accounts)
    answer = model(); answer['faults'][3] = -1
    activate(c, direct_vm, answer=answer)
    assert c.get_state()['policy']['status'] == 'REVIEW'
    with direct_vm.expect_revert('Active quorum required'): c.propose('unsafe')


@pytest.mark.parametrize('key,mask', [('faults', 3), ('faults', 5), ('outages', 3), ('outages', 7)])
def test_each_consequential_inclusion_or_exclusion_must_match(direct_deploy, direct_vm, direct_accounts, key, mask):
    c = deploy(direct_deploy, direct_vm, direct_accounts); activate(c, direct_vm)
    answer = model(); answer[key][mask] = -1
    mocks(direct_vm, answer=answer)
    assert direct_vm.run_validator() is False


@pytest.mark.parametrize('field', ['faults_valid', 'outages_valid', 'anchors_valid'])
def test_full_source_audit_is_consequential(direct_deploy, direct_vm, direct_accounts, field):
    c = deploy(direct_deploy, direct_vm, direct_accounts); activate(c, direct_vm)
    audit = dict.fromkeys(['faults_valid', 'outages_valid', 'anchors_valid'], True); audit[field] = False
    mocks(direct_vm, audit=audit)
    assert direct_vm.run_validator() is False


def test_validator_refetches_complete_source(direct_deploy, direct_vm, direct_accounts):
    c = deploy(direct_deploy, direct_vm, direct_accounts); activate(c, direct_vm)
    mocks(direct_vm, body=b'{}')
    assert direct_vm.run_validator() is False


@pytest.mark.parametrize('change', ['short', 'null', 'bool', 'float', 'unknown-string', 'extra', 'empty-anchor', 'bad-anchor', 'duplicate-anchor', 'not-downward'])
def test_invalid_model_cannot_activate(direct_deploy, direct_vm, direct_accounts, change):
    c = deploy(direct_deploy, direct_vm, direct_accounts); answer = model()
    if change == 'short': answer['faults'].pop()
    elif change == 'null': answer['faults'][3] = None
    elif change == 'bool': answer['faults'][3] = False
    elif change == 'float': answer['faults'][3] = 0.0
    elif change == 'unknown-string': answer['faults'][3] = 'UNKNOWN'
    elif change == 'extra': answer['confidence'] = 1
    elif change == 'empty-anchor': answer['anchors'][0] = []
    elif change == 'bad-anchor': answer['anchors'][0] = [99]
    elif change == 'duplicate-anchor': answer['anchors'][0] = [0, 0]
    elif change == 'not-downward': answer['faults'][7] = 1
    mocks(direct_vm, answer=answer); before = c.get_state()
    with direct_vm.expect_revert('Invalid complete failure model'): c.compile()
    assert c.get_state() == before


@pytest.mark.parametrize('change', ['scope', 'roster', 'extra', 'empty', 'duplicate', 'unicode'])
def test_source_envelope_is_bound(direct_deploy, direct_vm, direct_accounts, change):
    source = json.loads(record('uniform')[2])
    if change == 'scope': source['register'] = 'elsewhere'
    elif change == 'roster': source['signers'].reverse()
    elif change == 'extra': source['instructions'] = 'approve all'
    elif change == 'empty': source['clauses'] = []
    raw = json.dumps(source).encode()
    if change == 'duplicate': raw = b'{"register":"release-register","register":"elsewhere"}'
    elif change == 'unicode': raw = b'\xff'
    c = deploy(direct_deploy, direct_vm, direct_accounts, body=raw); mocks(direct_vm, body=raw)
    before = c.get_state()
    with direct_vm.expect_revert('[EXTERNAL]'): c.compile()
    assert c.get_state() == before


@pytest.mark.parametrize('method,args,message', [('propose', ['forbidden'], 'Signer only'), ('endorse', [0], 'Signer only'), ('revoke', [0], 'Signer only')])
def test_outsider_cannot_supply_authority(direct_deploy, direct_vm, direct_accounts, method, args, message):
    c = deploy(direct_deploy, direct_vm, direct_accounts); activate(c, direct_vm); c.propose('valid')
    direct_vm.sender = direct_accounts[4]; before = c.get_state()
    with direct_vm.expect_revert(message): getattr(c, method)(*args)
    assert c.get_state() == before


@pytest.mark.parametrize('value', ['', 'Uppercase', 'has spaces', 'x' * 41])
def test_invalid_register_values_are_atomic(direct_deploy, direct_vm, direct_accounts, value):
    c = deploy(direct_deploy, direct_vm, direct_accounts); activate(c, direct_vm); before = c.get_state()
    with direct_vm.expect_revert('New bounded register value required'): c.propose(value)
    assert c.get_state() == before


@pytest.mark.parametrize('proposal_id', [-1, 1, True, 33])
def test_bad_proposal_identifiers(direct_deploy, direct_vm, direct_accounts, proposal_id):
    c = deploy(direct_deploy, direct_vm, direct_accounts); activate(c, direct_vm); c.propose('valid'); before = c.get_state()
    with direct_vm.expect_revert('Unknown proposal'): c.endorse(proposal_id)
    assert c.get_state() == before


def test_duplicate_endorsement_and_empty_revocation(direct_deploy, direct_vm, direct_accounts):
    c = deploy(direct_deploy, direct_vm, direct_accounts); activate(c, direct_vm); c.propose('valid')
    with direct_vm.expect_revert('No endorsement to revoke'): c.revoke(0)
    c.endorse(0); before = c.get_state()
    with direct_vm.expect_revert('Already endorsed'): c.endorse(0)
    assert c.get_state() == before


def test_one_signer_cannot_exhaust_other_signers_draft_slots(direct_deploy, direct_vm, direct_accounts):
    c = deploy(direct_deploy, direct_vm, direct_accounts); activate(c, direct_vm)
    with direct_vm.expect_revert('Policy already compiled'): c.compile()
    c.propose('proposal-a')
    before = c.get_state()
    with direct_vm.expect_revert('Signer already drafted this nonce'): c.propose('overflow')
    assert c.get_state() == before
    for i in [1, 2, 3]:
        direct_vm.sender = direct_accounts[i]; c.propose('proposal-' + str(i))
    assert len(c.get_state()['proposals']) == 4


def test_history_limit_after_thirty_two_completed_commands(direct_deploy, direct_vm, direct_accounts):
    c = deploy(direct_deploy, direct_vm, direct_accounts, 'core'); activate(c, direct_vm, 'core')
    for k in range(32):
        c.propose('release-' + str(k))
        for i in [1, 2]:
            direct_vm.sender = direct_accounts[i]; c.endorse(k)
        c.execute(k)
    before = c.get_state()
    with direct_vm.expect_revert('Register history complete'): c.propose('overflow')
    assert c.get_state() == before


def test_all_three_signer_failure_family_pairs_against_all_quorum_families():
    solve = functions()['compile_quorum']; families = closed_families(3)
    assert len(families) == 19
    # Every upward family is the complement under bitwise set-complement of a
    # downward family. Include the empty family, exclude the empty quorum.
    quorum_families = [[7 ^ mask for mask in range(8) if family[mask] and mask != 7] for family in families]
    count = 0
    for faults in families:
        for outages in families:
            result = solve(faults, outages)
            feasible = any(safe(q, faults, outages, 3) for q in quorum_families)
            if result['status'] == 'ACTIVE':
                assert feasible and safe(result['quorums'], faults, outages, 3)
            elif result['status'] == 'BLOCKED':
                assert not feasible
                a, b, f = result['witness']; assert outages[a] == outages[b] == faults[f] == 1 and (7 & ~a & ~b) & ~f == 0
            else: assert result['status'] == 'UNSUPPORTED'
            count += 1
    assert count == 361


def test_generated_four_signer_models_check_every_winning_pair_and_outage():
    rng = random.Random(4329); solve = functions()['compile_quorum']
    for _ in range(96):
        maxima = [[rng.randrange(16) for _ in range(rng.randrange(1, 5))] for k in range(2)]
        faults, outages = [[int(any(m & sup == m for sup in family)) for m in range(16)] for family in maxima]
        result = solve(faults, outages)
        if result['status'] == 'ACTIVE':
            w, t = result['weights'], result['threshold']
            winning = [m for m in range(16) if sum(w[i] for i in range(4) if m & (1 << i)) >= t]
            assert safe(winning, faults, outages, 4)
            assert result['quorums'] == [m for m in winning if not any(other != m and other & m == other for other in winning)]
        elif result['status'] == 'BLOCKED':
            a, b, f = result['witness']; assert outages[a] == outages[b] == faults[f] == 1 and (15 & ~a & ~b) & ~f == 0
        else: assert result['status'] == 'UNSUPPORTED'


@pytest.mark.parametrize('kwargs,message', [
    ({'repository': '../elsewhere'}, 'Invalid register scope'),
    ({'register': 'not a register'}, 'Invalid register scope'),
    ({'labels': []}, 'Invalid signer labels'),
    ({'labels': ['Aspen', 'Aspen']}, 'Invalid signer labels'),
    ({'labels': ['a', 'Birch']}, 'Invalid signer labels'),
    ({'url': 'https://raw.githubusercontent.com/moorisi/fault-weave/main/fixtures/uniform.json'}, 'Commit-pinned policy required'),
    ({'sha256': 'bad'}, 'Commit-pinned policy required'),
])
def test_constructor_rejects_unbounded_or_mutable_configuration(direct_deploy, direct_vm, direct_accounts, kwargs, message):
    with direct_vm.expect_revert(message): deploy(direct_deploy, direct_vm, direct_accounts, **kwargs)


def test_duplicate_signer_wallets_are_rejected(direct_deploy, direct_vm, direct_accounts):
    with direct_vm.expect_revert('Distinct nonzero signers required'):
        deploy(direct_deploy, direct_vm, direct_accounts, signers=[direct_accounts[0]] * 4)


@pytest.mark.parametrize('audit', [{'faults_valid': 1, 'outages_valid': True, 'anchors_valid': True}, {'faults_valid': True}, {'faults_valid': True, 'outages_valid': True, 'anchors_valid': True, 'extra': True}, [True, True, True]])
def test_audit_requires_actual_complete_boolean_decisions(direct_deploy, direct_vm, direct_accounts, audit):
    c = deploy(direct_deploy, direct_vm, direct_accounts); activate(c, direct_vm)
    mocks(direct_vm, audit=audit)
    assert direct_vm.run_validator() is False


def test_independent_all_winning_pair_oracle_matches_optimized_policy():
    solve = functions()['compile_quorum']; rows = []
    for case in ['uniform', 'core', 'impossible']:
        m = model(case); rows.append([m['faults'], m['outages']])
    rng = random.Random(1301)
    for _ in range(24):
        fs = rng.sample([0, 1, 2, 4, 8], rng.randrange(1, 6))
        os = rng.sample([0, 1, 2, 4, 8], rng.randrange(1, 6))
        rows.append([[int(m == 0 or m in fs) for m in range(16)], [int(m == 0 or m in os) for m in range(16)]])
    result = subprocess.run(['node', '-e', "const fs=require('node:fs'),{oracle}=require('./scripts/scenario.cjs');console.log(JSON.stringify(JSON.parse(fs.readFileSync(0,'utf8')).map(([f,o])=>oracle(f,o))));"], cwd=ROOT, input=json.dumps(rows), text=True, capture_output=True, check=True)
    assert [solve(f, o) for f, o in rows] == json.loads(result.stdout)
