# Ready to submit

Category: **Builder → Intelligent Contracts**

Title: **FaultWeave: Consensus quorum policy compiler**

## Notes / Description

FaultWeave compiles commit-pinned failure-policy prose into a signer authorization quorum. Leader and validators independently fetch full texts and extract named fault/outage cohorts. Code expands every signer subset; validators compare both complete vectors exactly and audit every named-subset decision. Bounded synthesis checks honest intersection and outage availability; unresolved or unsupported models cannot activate, and impossibility has a constructive witness. Real signer transactions endorse or revoke nonce-bound proposals; a valid quorum updates the register and makes competing drafts stale. StudioNet proofs cover 3-of-4 and trusted-core 2-of-3 policies, revocation, fresh signatures, stale proposals and blocked execution. Includes 78 direct tests, exhaustive small-model checks and 28 verified primary receipts. Earlier rejected attempts are archived. Synthetic trust assumptions do not prove real-world signer behavior; this is not a replacement BFT replication protocol.

## Evidence links

- [Repository](https://github.com/moorisi/fault-weave)
- [GenLayer contract source](https://github.com/moorisi/fault-weave/blob/main/contracts/fault_weave.py)
- [Primary StudioNet contract](https://explorer-studio.genlayer.com/address/0x8E1410DC607D538e382063Ab3D9e1189c469d311)
- [Primary deployment transaction](https://explorer-studio.genlayer.com/tx/0x3a7fecbc474aa24bd6acecf275a14cef5df76dee7d521d728dc1f19b30c827bf)
- [Complete scenario proofs](https://github.com/moorisi/fault-weave/blob/main/proofs/README.md)
- [Passing CI](https://github.com/moorisi/fault-weave/actions/runs/39743637017)
