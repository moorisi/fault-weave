# Instrumented bit-table source — excluded from primary suite

Source SHA-256: `88018838edbc30044f6ed04a7002654f5411e45fd5d265d4b756a817ada9748f`.
Revision: `33c61f39e48b3a1e43219962b639a4ccbec86076`.
Fixture pin: `b64e2aee58c4c1f0ba45317f7b55100bdc915d82`.

The negative compilation in [run 39738698592](https://github.com/moorisi/fault-weave/actions/runs/39738698592)
was rejected with MAJORITY_DISAGREE. The leader incorrectly admitted three-member
outage sets even though the source permits at most two. The instrumented validators
independently produced the correct exclusions and rejected the leader's vectors.
The public diagnostic output establishes this specific cause; earlier uninstrumented
rejections do not expose enough information for the same diagnosis.

Rejected transaction:
[`0x91dab51983127f0d3148ba61d51dac661d10a6abd6f95a56bdb121d74898b7c3`](https://explorer-studio.genlayer.com/tx/0x91dab51983127f0d3148ba61d51dac661d10a6abd6f95a56bdb121d74898b7c3).
It is evidence of fail-closed disagreement, not a passing BLOCKED-policy proof.
The corresponding uniform and trusted-core runs are preserved here too, but none
of these older-source receipts is included in the primary proof count.

The replacement asks models for named maximal cohorts and computes subset tables
deterministically. A regression asserts that all six named pairs never admit
triples; another exhaustively checks all 167 nonempty downward-closed four-signer
families. Full-source audits, complete exact vector comparisons, honest intersection
and outage availability checks remain required. No tolerance or approval shortcut
was introduced. See [earlier fixture attempts](../previous-fixture/README.md) for
the preceding two batches. The primary suite uses only one final source hash.
