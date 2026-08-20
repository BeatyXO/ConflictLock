# State model and invariants

## Commitment states

- `PENDING`: proposed but not resolved.
- `ACTIVE`: compatible and part of the scope's active set.
- `REJECTED`: consensus found a material conflict.
- `REVIEW_REQUIRED`: consensus was inconclusive.
- `CANCELLED`: principal withdrew an unresolved proposal.
- `DEACTIVATED`: formerly active commitment is no longer in force.

## Scope state

A scope belongs to exactly one principal address and has:

- `active_ids`
- `scope_revision`

The revision increments whenever an active commitment is added or removed.

## Snapshot invariant

Every proposal stores `snapshot_ids` and `snapshot_revision`. Resolution is allowed only when:

```text
proposal.snapshot_revision == current_scope_revision
```

Therefore a proposal can never become active based on a semantic comparison that omitted a commitment activated after its snapshot was captured.

## Concurrency example

A and B are both proposed against revision 4. A resolves first and activates, producing revision 5. B is now stale. B must refresh, capture A in its new snapshot, and only then be judged.

This is the contract's core protection against semantic double-promise races.

## Capacity invariant

A scope contains at most eight active commitments. The cap keeps consensus prompts bounded and makes validator work predictable. Builders needing broader domains should split commitments into narrower semantic scopes.
