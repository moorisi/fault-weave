# Model, compiler and protocol

## Source and adversary boundary

The source is an immutable JSON envelope containing the exact register name,
signer order and prose clauses. Only `raw.githubusercontent.com/<fixed-repository>/`
with a full 40-hex commit and `fixtures/<name>.json` is accepted. SHA-256 covers
the complete bytes before UTF-8/duplicate-key/schema parsing. HTTP 5xx/network
errors are transient; permanent source/schema mismatches fail without activation.
Input prose is untrusted data, never prompt instructions. Scope, corrections,
negation, exclusions, superseded drafts and correlations affect the vectors.

For each bitmask of the immutable roster, the model must decide whether that exact
simultaneous Byzantine set is permitted, forbidden or unresolved, and separately
do the same for outages. Both families must be downward closed for known permitted
sets; empty set is permitted. Unknown is integer -1, never a missing/null entry.
One bounded repair may correct malformed schema; unresolved facts cannot be guessed.
Validators re-fetch, re-interpret, compare both vectors and audit every entry.
Equivalent supporting anchors need not have identical wording/indices, but every
anchor list is scoped and independently audited. Deterministic compilation consumes
only the exactly agreed vectors. LLM schema errors are never consensus-approved
merely because two models failed similarly.

## Compiler

Let F range over permitted faulty sets, O over permitted outage sets, and Q over
accepted signing coalitions. Require `(Q1 & Q2) - F` nonempty for every Q1,Q2,F.
Require a Q disjoint from each O. Monotone weighted predicates allow checking
minimal winning coalitions for intersection, and the complete available complement
for each outage. The independent JavaScript oracle checks **all** winning pairs
and explicitly finds a disjoint quorum instead.

If `A = roster - O1` and `B = roster - O2` have `A & B` contained in some F,
availability would require quorums within A and B, whose intersection is also
contained in F. This is the recorded three-mask impossibility witness. It is
stronger than reporting search exhaustion. No witness plus no weights in 0..2
means `UNSUPPORTED`; no general theorem is inferred from bounded search.

At most 3^4 weight vectors and 8 thresholds per vector; at most 15 nonempty
coalitions. The lexicographic objective is fixed, public and uses integer
arithmetic. Weight zero deliberately excludes a signer from effective authority;
its transactions never increase quorum weight. Optimality is only within this
search space and objective, not probabilistic load, latency or real-world safety.

## Register lifecycle

`UNCOMPILED -> compile -> ACTIVE | REVIEW | BLOCKED | UNSUPPORTED` is immutable.
There is no owner/admin role, override, mutable failure policy or certificate.

For ACTIVE: `propose(value)` creates a signer-attributed draft for the current
nonce. The proposer supplies no implicit approval. `endorse(id)` and `revoke(id)`
alter only the actual caller's bit. `execute(id)` checks current nonce and compiled
weight, appends the execution coalition, sets the value, and advances nonce.
Any caller may execute; only roster members propose/endorse/revoke. Old proposal
bits are immutable after a nonce change. The history is bounded at 32 updates,
with at most one draft per member per nonce. Expected rejections leave all fields
unchanged. No lock ordering or exclusive ballot requirement exists; members can
endorse competing values. Chain ordering prevents two updates at the same nonce.

## Distinctness

This mechanism synthesizes a fault-tolerant **authorization access structure**
and applies it to signed state updates. It does not reuse graph transitions,
version proposals, certificate issuance/consumption, a deterministic-only leader
check, ranked voting, auction pricing, matching, fair payouts or service attestations.
AI decisions alter which coalitions can execute or whether execution is possible.
This application remains dependent on the truth and completeness of its fixed
trust/outage assumptions; source retrieval does not cryptographically prove them.
