# StudioNet proofs

All three final-source suites passed: **28 FINALIZED / MAJORITY_AGREE receipts**,
comprising **23 successful executions and five expected rejections**. Offline and
fresh RPC verification checked source bytes, actual signers, decoded calldata,
complete vote sets, exact error bytes and every intermediate/final state.

Independent deployments: uniform one-fault/one-outage policy; named
trusted-core policy; and an impossible one-fault/two-outage policy. Tests cover
revocation, stale competing proposals, zero-weight approvals, new-nonce signatures
and explicit refusal to activate an impossible model. Failed calls must have exact
expected error bytes and unchanged complete state.

## Network and reproducibility

Gasless **StudioNet**, chain **61999**. These are contract-native register updates,
not mainnet transactions, external release execution, token payments or real assets.

- Source revision: `5a350ca2183e5b2c443b26866b5867dd54a834d8`.
- Workflow revision: `45df88e73f3c3b54937d19a387f670b42230f257`; identical contract bytes.
- Contract SHA-256: `cca508f1d818d6dc3d0a4af73aba1424919ceba5892e397a4919f546d6f0566f`.
- Fixture revision: `b64e2aee58c4c1f0ba45317f7b55100bdc915d82`.
- [CI](https://github.com/moorisi/fault-weave/actions/runs/39743637017): lint,
  78 direct tests and seven transaction-transport tests passed.
- Final fresh verification: `2026-10-22T08:06:49.757Z` (UTC),
  [machine-readable report](verification.json).

The direct suite includes all 361 pairs of three-signer downward-closed failure
families, checked against every quorum family; 96 generated four-signer models;
all 167 nonempty downward-closed four-signer named-cohort expansions;
27 comparisons with an independent optimizer; real validator callbacks; source
commitment failures; exact positive/negative/unknown decisions; signature checks;
revocation; nonce isolation; and per-member draft bounds. Mocked LLM tests verify
contract behavior, not real model accuracy. The live compilations exercise actual
GenLayer web/LLM consensus. Source assumptions and fixtures remain synthetic.

## Uniform one-fault / one-outage policy

[Contract](https://explorer-studio.genlayer.com/address/0x8E1410DC607D538e382063Ab3D9e1189c469d311) ·
[Deployment](https://explorer-studio.genlayer.com/tx/0x3a7fecbc474aa24bd6acecf275a14cef5df76dee7d521d728dc1f19b30c827bf) ·
[Workflow](https://github.com/moorisi/fault-weave/actions/runs/39743639059).

The agreed source permits any singleton Byzantine set and any singleton outage.
The compiler finds weights `[1,1,1,1]`, threshold `3`, minimal winning masks
`[7,11,13,14]`. The independent oracle checks every winning coalition pair and
every outage, plus the complete lexicographic optimum.

| Consequential call | Transaction | Verified effect |
| --- | --- | --- |
| Compile | [Receipt](https://explorer-studio.genlayer.com/tx/0x5f7df15903a2d55e1de92a42e6eb4764dfe4d03ac072d09ec92a84fa692ae90f) | Full 32-decision model; ACTIVE three-of-four policy |
| Execute with two approvals | [Receipt](https://explorer-studio.genlayer.com/tx/0x4e985314a603b4eae0d3b2bbd10d0cb14d9d637cfb2ccdde7e2ed792c33580ef) | Expected `Quorum not met`; complete state unchanged |
| Birch revokes | [Receipt](https://explorer-studio.genlayer.com/tx/0x01dac49bde40d78b5565cd68f91f6b69acce2cf699a367b37aaeb67426ddb127) | Only Birch's actual signer bit is removed |
| Execute without Birch | [Receipt](https://explorer-studio.genlayer.com/tx/0x914a5bb30a52bc0aabe40ab013edfcd914a7d3d1fedd711f2665e1fecdd76346) | Aspen+Cedar+Dogwood, mask 13, updates value to `release-a`, nonce 1 |
| Execute competing draft | [Receipt](https://explorer-studio.genlayer.com/tx/0x2f653884ccde112d078088ad1f659669bda2f03ee890e64595eadb989f4e8b72) | Expected `Stale proposal`; complete state unchanged |

All twelve receipts finalized with `MAJORITY_AGREE`: ten successful executions
and two expected rejections. Compilation had **3 agree / 0 disagree / 2 idle**.
All raw votes are preserved; earlier-source dissent and rejected attempts remain
in their separate archives.

## Named trusted-core policy

[Contract](https://explorer-studio.genlayer.com/address/0x55810Fb6e71582bB5b5a4F04145231c508FA15eC) ·
[Deployment](https://explorer-studio.genlayer.com/tx/0x14c2f46f5612bee89fe37381e6472ed190ee4ea76f1cb9d1ce7db4910ca2dd2e) ·
[Workflow](https://github.com/moorisi/fault-weave/actions/runs/39743644896).

The source permits only Aspen to be Byzantine but permits any individual outage,
including trusted members. Compiled weights `[0,1,1,1]`, threshold `2`, minimal
winning masks `[6,10,12]` give authority to two of Birch/Cedar/Dogwood.
Aspen's valid signature contributes zero weight.

| Consequential call | Transaction | Verified effect |
| --- | --- | --- |
| Compile | [Receipt](https://explorer-studio.genlayer.com/tx/0x04df4c0b9d91d7b78908e48b31f2cda9fa2f000ec8e03990bd0e07debc8f11aa) | Exactly agreed different fault family changes effective signer authority |
| Execute with Aspen+Birch | [Receipt](https://explorer-studio.genlayer.com/tx/0x650f85caf8176c0e6d56e981d832ef3812f084340e6acc618c91cb1b56193694) | Expected rejection: two signatures supply only weight one |
| First execution | [Receipt](https://explorer-studio.genlayer.com/tx/0x556fd5f0d5a957e6d41a2a5a86677c57a2d4fcb37f965d248a290bdc4ba8c9e2) | Mask 7 supplies weight two, value `core-release-a`, nonce 1 |
| Next execution | [Receipt](https://explorer-studio.genlayer.com/tx/0x6def8e00741783e0679ee1ac480eaed3326ef2aee343ae6af258efce58785c9a) | Fresh Birch+Dogwood approvals, mask 10, value `core-release-b`, nonce 2 |

All twelve receipts finalized with `MAJORITY_AGREE`: eleven successful executions
and one expected rejection. All three hosted JUnit files report 78 tests with zero
failures, errors or skips. Detailed traces bind every intermediate state to its
actual signed call; later-nonce approvals are not inherited from earlier drafts.

## Proven impossible policy

[Contract](https://explorer-studio.genlayer.com/address/0x777C793083Ef9d14499DE09DC298DaB46dEeecc9) ·
[Deployment](https://explorer-studio.genlayer.com/tx/0xca91bfb06bda67a406ac6b0a141b43c930c731cfb952497cc9509b31a020b7ca) ·
[Workflow](https://github.com/moorisi/fault-weave/actions/runs/39743657988).

The source permits any singleton Byzantine set and any pair of total nonresponders.
Named pairs expand deterministically; every triple remains excluded. The compiler
records `BLOCKED` with witness `[1,6,8]`: an Aspen outage and a Birch+Cedar outage
leave populations whose intersection is only Dogwood, which is itself a permitted
Byzantine set. Any quorums available in those two populations could therefore
intersect only in a Byzantine signer. This rules out every quorum family, not just
the bounded weighted candidates.

| Call | Transaction | Verified result |
| --- | --- | --- |
| Compile | [Receipt](https://explorer-studio.genlayer.com/tx/0x6ee1de0500f44cac11710ce2966e9dc3910b9aa8ecd9734d88310ef8a782a3aa) | SUCCESS; BLOCKED, witness `[1,6,8]` |
| Propose | [Receipt](https://explorer-studio.genlayer.com/tx/0xe73080e6eda4d4a8ae57074a817a7900c0b13c835d9064450d435d5b400f217d) | Expected `Active quorum required`; full state unchanged |
| Execute | [Receipt](https://explorer-studio.genlayer.com/tx/0x4972a8e047f811f992241e186874ab82c154007eee6be3ca37537fd9ddc96f04) | Expected `Active quorum required`; full state unchanged |

All four receipts finalized with MAJORITY_AGREE. Final nonce is zero, value is
empty and execution history is empty. Neither the deployer nor a signer can bypass
the blocked policy.

## Verification and earlier attempts

`suite.json` binds deployments, source hash, fixture revision and public signer
addresses. `transactions.json` binds every planned label to its actual hash.
Each `*-trace.json` records the complete state before and after every call.
The verifier decodes real calldata using the pinned SDK, checks every signer and
target, requires a strict majority over the full recorded voter set including
idle votes, and compares final states and source bytes with fresh StudioNet reads.
Expected failures require exact VM error bytes plus unchanged state.

```sh
# Set GENLAYER_CLI_PATH to an absolute installed CLI entry point.
node scripts/verify-proofs.cjs --offline
node scripts/verify-proofs.cjs
```

The final report, all 28 raw sanitized receipts and three hosted JUnit files are
committed beside this page. Proof wallets were disposable; the published instances
preserve these results. Use persistent signer wallets for an ongoing deployment.

Earlier source versions are retained in [previous-fixture](previous-fixture/README.md)
and [previous-source](previous-source/README.md): **78 earlier transactions**, including
three rejected compilations, are excluded from the 28 primary receipts. The
instrumented rejection demonstrates validators refusing a leader that incorrectly
allowed triple outages. Named-cohort expansion fixes the observed bit-table failure;
it does not guarantee that future model interpretations will always reach consensus.
[Installation-only retries](tooling-retries.md) submitted no transactions.
