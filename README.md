# ConflictLock

**Semantic double-promise protection for GenLayer.**

ConflictLock is a standalone, reusable GenLayer Intelligent Contract that prevents a principal or autonomous agent from activating a new natural-language commitment when it materially conflicts with commitments already active in the same semantic scope.

Traditional smart contracts can prevent the same token from being spent twice. They cannot reliably detect that two differently worded promises cannot both be honored. ConflictLock turns that semantic compatibility question into a bounded consensus decision with a persistent state consequence.

There is **no frontend** in this repository. The repository is intentionally contract-only for reuse by other builders.

## Why this needs GenLayer

A deterministic contract can compare hashes, IDs, dates, or exact strings. It cannot generally determine that:

- "Exclusively provide Dataset X to Company B until September 30"
- and "Provide Dataset X to Company C on September 12"

are materially incompatible despite having different bytes.

ConflictLock asks GenLayer validators a narrower question: **can this proposed commitment coexist with the exact active commitments captured in its scope snapshot?**

The leader returns structured JSON. Validators independently re-evaluate the same immutable snapshot. A `CONFLICTING` outcome is equivalent only when validators agree on the verdict **and the canonical set of material conflict edges** (`commitment_id + category`). Free-form reasoning does not need to match.

## State model

Each commitment moves through a small state machine:

`PENDING -> ACTIVE | REJECTED | REVIEW_REQUIRED -> CANCELLED`

An active commitment can later move to `DEACTIVATED`.

Every principal + scope also has:

- an ordered list of active commitment IDs;
- a monotonically increasing `scope_revision`.

A proposal captures both the active IDs and the revision at creation/refresh time. `resolve_proposal` refuses to run if the revision changed. This prevents a race where two simultaneous proposals could both be judged against an outdated pre-activation snapshot.

## Verdicts

- `COMPATIBLE` — no material incompatibility exists; proposal activates.
- `CONFLICTING` — at least one material incompatibility exists; proposal is rejected.
- `INCONCLUSIVE` — ambiguity prevents safe activation; proposal enters review-required state.

Conflict categories are intentionally bounded:

- `EXCLUSIVITY`
- `RESOURCE_COLLISION`
- `TIME_COLLISION`
- `OBLIGATION_CONTRADICTION`
- `AUTHORITY_COLLISION`
- `OTHER`

Each conflict is either `MATERIAL` or `POTENTIAL`. A model cannot force rejection with a merely potential edge, an invented commitment ID, or an unrecognized category.

## Core API

```text
propose_commitment(scope, commitment_text, context, callback) -> commitment_id
refresh_proposal(commitment_id)
resolve_proposal(commitment_id)
cancel_proposal(commitment_id)
deactivate_commitment(commitment_id, reason)
send_callback(commitment_id)

get_commitment(commitment_id) -> JSON
get_commitment_text(commitment_id) -> JSON
get_resolution(commitment_id) -> JSON
get_conflict(commitment_id, index) -> JSON
scope_state(principal, scope) -> JSON
status_of(commitment_id) -> str
verdict_of(commitment_id) -> str
is_active(commitment_id) -> bool
is_compatible(commitment_id) -> bool
stats() -> JSON
```

## Example flow

1. Agent A proposes an exclusive Dataset X commitment in scope `agent.procurement`.
2. No prior commitments exist, so the first commitment activates deterministically.
3. Agent A proposes a second Dataset X delivery in the same scope.
4. ConflictLock captures the current active IDs and scope revision.
5. Validators independently compare the candidate with the captured active commitments.
6. Consensus returns `CONFLICTING` with a material `EXCLUSIVITY` edge to commitment 1.
7. The new commitment becomes `REJECTED` and cannot be consumed as compatible.

If another commitment activates between steps 4 and 5, resolution fails as stale and the proposer must call `refresh_proposal` first.

## Consumer integration

`examples/commitment_admission_consumer.py` demonstrates a downstream contract that accepts finalized callbacks and records whether a proposal was admitted. Consumers can also poll `is_compatible`/`status_of` before performing their own state transition.

## Repository layout

```text
contracts/conflict_lock.py                 Core Intelligent Contract
examples/commitment_admission_consumer.py  Reusable callback consumer
tests/direct/                              Fast direct-mode tests
tests/integration/                         Studio/StudioNet smoke test
docs/CONSENSUS.md                          Validator and equivalence design
docs/STATE_MODEL.md                        State/revision invariants
docs/SECURITY.md                           Threat model and safety properties
DEPLOYMENT.md                              Deployment and proof checklist
```

## Local verification

Requirements: Python 3.12+, GenLayer tooling, and the current GenLayer test stack.

```bash
python -m pip install -r requirements.txt
genvm-lint check contracts/conflict_lock.py
pytest tests/direct -v
```

Studio integration:

```bash
gltest tests/integration -v
```

## Submission fit

ConflictLock is not a frontend product and not a generic "AI decides X" demo. Its reusable primitive is semantic commitment admission. The nondeterministic judgment is bounded by deterministic state, snapshot revisions, allow-listed conflict IDs/categories, normalization invariants, and a custom equivalence rule tied directly to the state transition.

## License

MIT
