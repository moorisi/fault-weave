# Earlier fixture attempts — excluded from primary suite

Contract bytes are unchanged: SHA-256
`a1c1c5661210dba1dec244986702d82018201bd11c9a6c12252ec1fb877807f9`.
These runs used fixture revision `9a56ecbf708ffb7e0d20e6daf18058b7259085b7`.

| Run | Case | Result |
| --- | --- | --- |
| [39670292115](https://github.com/moorisi/fault-weave/actions/runs/39670292115) | Uniform | 12 finalized MAJORITY_AGREE receipts; complete fresh verification passed |
| [39670299749](https://github.com/moorisi/fault-weave/actions/runs/39670299749) | Trusted core | 12 finalized MAJORITY_AGREE receipts; complete fresh verification passed |
| [39733140355](https://github.com/moorisi/fault-weave/actions/runs/39733140355) | Earlier impossible fixture | Deployment passed; compile finalized MAJORITY_DISAGREE; no successful activation or fresh suite verification |

Rejected compile:
[`0x548fd9d5a92acfbb92698af1f448f54d18ddbc3c9826e18e1964143d5cffde19`](https://explorer-studio.genlayer.com/tx/0x548fd9d5a92acfbb92698af1f448f54d18ddbc3c9826e18e1964143d5cffde19).
Its vote set is **1 agree / 3 disagree / 1 idle**. The leader's execution says
SUCCESS, but the network rejected its result. Finality and local execution success
are not acceptance. Its source and expected leader vectors are preserved alongside
the complete sanitized receipt; validator-specific model outputs are not exposed,
so the precise reason for disagreement is unconfirmed.

The earlier fixture separately permitted two Byzantine signers while bounding
nonresponders to one. That is awkward as an operational model because arbitrary
Byzantine behavior can include withholding. The replacement permits one Byzantine
signer and two total nonresponders, including withholding and benign outages.
It still mathematically requires BLOCKED and a constructive impossibility witness.
No contract, audit, vector comparison, threshold, or safety condition was weakened.
All primary scenarios rerun against the new pinned fixture revision. These 26
earlier transactions, including the rejected compile, are excluded from the final
28-receipt primary count; the same immutable source is used throughout.
