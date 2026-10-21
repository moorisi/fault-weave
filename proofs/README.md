# StudioNet proofs

Live receipts will be added only after finalized execution, actual signer/calldata
checks, exact deployed source matching and complete independent state replay.

Planned independent deployments: uniform one-fault/one-outage policy; named
trusted-core policy; and an impossible two-fault/one-outage policy. Tests cover
revocation, stale competing proposals, zero-weight approvals, new-nonce signatures
and explicit refusal to activate an impossible model. Failed calls must have exact
expected error bytes and unchanged complete state.
