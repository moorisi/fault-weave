# FaultWeave

A standalone GenLayer **failure-aware authorization compiler and signed register**.
It interprets commit-pinned prose assumptions, synthesizes a bounded weighted quorum,
and uses that policy to authorize real contract-state updates. No graph proposals,
service certificates, confidence scores, price auctions or owner overrides.

## Consensus boundary

The deployer fixes 2–4 signer wallets, labels, a register scope, and an immutable
source URL/SHA-256. Anyone calls `compile()`. The leader and validators each fetch
the full source, check its bytes and scope, and independently extract maximal
**named failure cohorts** for malicious signing and unavailability. Contract code
expands these into every roster subset: `1` permitted, `0` excluded, `-1` unresolved.
Models never generate numeric bit tables. Validators compare both complete vectors
exactly and audit a named-subset table and source anchors against all clauses.
There is no numerical confidence tolerance. A hash alone never substitutes for text.

The deterministic compiler checks:

- **Honest intersection:** every two accepted coalitions intersect outside every
  permitted Byzantine set, including the same coalition paired with itself.
- **Specified availability:** every permitted outage leaves an accepted coalition.
- **Bounded optimality:** exhaustively search integer weights 0–2 and positive
  thresholds; minimize worst minimal-quorum size, sum of minimal-quorum sizes,
  total weight, threshold, then the weight vector in signer order.

An unresolved decision produces `REVIEW`. A constructive impossibility witness
produces `BLOCKED`: two required available populations intersect only inside a
permitted Byzantine set, ruling out **any** quorum family. If neither that witness
nor a bounded weighted solution exists, the result is `UNSUPPORTED`, not a claim
of general impossibility. Only `ACTIVE` policies permit register operations.

## Actual authorization

Members propose a bounded new register value at the current nonce. Each member
gets one draft per nonce, preventing a single member from consuming the other
members' draft slots. Endorsements are actual transaction signatures mapped to
roster bits; no caller can supply another member's approval. Members may revoke
their own approvals. Anyone executes a proposal only when its current endorsement
weight reaches the compiled threshold. Execution changes the value, records the
coalition and advances the nonce, making competing proposals stale. Later nonces
need new signatures. No deployer bypass exists. At most 32 updates / 128 drafts.

## Scope and limits

This is a bounded authorization primitive, **not a replacement BFT replication
protocol**. GenLayer supplies transaction ordering. Intersection guarantees concern
the stated trust model; they do not prove an endorsed value is correct or stop
honest members from approving different values. Liveness means the mathematical
availability condition under the complete stated nonresponder sets, assuming
cooperation by responding signers. Outage assumptions must include all withholding
and correlated failures an application intends to tolerate; the two input families
are not automatically combined. The contract cannot establish that human trust
assumptions match the world, recover lost keys, force signing, or reopen an
immutable failed compilation. Synthetic fixtures illustrate the mechanism.

## Reproduce

```sh
pip install -r requirements-dev.txt
npm ci --no-audit --no-fund
genvm-lint download --version v0.2.16
genvm-lint check contracts/fault_weave.py --json
python -m pytest tests/direct -q
node --test tests/rpc-preflight.test.cjs
```

The suite includes 78 direct tests, 361 exhaustive pairs of three-signer failure
families checked against all quorum families, 96 generated four-signer models,
167 exhaustive four-signer named-cohort expansions, and 27 full comparisons with
the independent optimizer. Seven transport tests
verify bounded read retries and refusal to replay signed sends.

Manual GitHub `proofs.yml` runs create four encrypted disposable CLI wallets on
an ephemeral runner and deploy through `genlayer@0.39.2` to gasless **StudioNet,
chain 61999**. No key export, funding, native token or real asset is involved.
The committed npm lock also pins genlayer-js 1.1.8 and viem 2.56.3.
Each call must finalize with the expected execution result and pass full-state
replay. [Proof methodology](proofs/README.md) · [Design](docs/design.md).

Proof wallets are discarded with their runners. The published instances preserve
scenario results; they are not an ongoing committee service. For continued use,
deploy with your own persistent signer wallets and a reviewed policy source.

Primary deployment: [contract explorer](https://explorer-studio.genlayer.com/address/0x8E1410DC607D538e382063Ab3D9e1189c469d311).
All three scenarios have 28 verified finalized receipts, including five expected
rejections. [Ready submission text](docs/submission.md) · [Complete proofs](proofs/README.md).

## Prior art and attribution

Quorum intersection and availability are established distributed-systems ideas:
[Malkhi and Reiter, Byzantine Quorum Systems](https://malkhi.com/files/byzquorums-STOC1997.pdf).
FaultWeave contributes a bounded prose-to-policy consensus boundary and executable
authorization composition; it does not claim a new quorum theorem. Its core and
scenario oracle differ from the previous allocation/auction submissions.
Generic CLI/receipt transport and Windows test scaffolding are adapted under MIT
from [HalfWeir](https://github.com/ehsanisildur-ux/half-weir); the contract, quorum
compiler, protocol tests, fixtures and scenario oracle are new.
