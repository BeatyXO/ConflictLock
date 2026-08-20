# ConflictLock submission brief

## Category

Standalone GenLayer Intelligent Contract. No frontend, dashboard, backend product flow, or application-specific UI is included.

## Purpose

ConflictLock is a reusable semantic admission primitive that prevents a principal or autonomous agent from activating commitments that materially conflict with commitments already active inside the same declared scope.

Traditional blockchains prevent double-spending of assets. ConflictLock applies a similar admission principle to natural-language commitments: before a new scoped promise becomes active, GenLayer validators determine whether it can coexist with promises already active in that scope. It does not discover conflicts hidden in unrelated scopes.

## Why GenLayer

Hashes and string matching cannot determine whether differently worded obligations are semantically incompatible. GenLayer supplies bounded validator judgment, while deterministic contract state controls scope normalization, revisions, snapshots, output normalization, state transitions, and callback authorization.

Validators must agree on the verdict; for `CONFLICTING`, they must also agree on the material `(commitment_id, category)` fingerprint. Model output cannot invent IDs, potential edges cannot reject a proposal, and malformed output fails safely to `INCONCLUSIVE`.

## Reuse

The primitive is suitable for autonomous agents, procurement protocols, service agreements, exclusivity registries, resource reservations, DAO authorization systems, and agent-to-agent commerce.

## Evidence status

| Check | Status |
|---|---|
| Python compile | PASS |
| GenVM lint | PASS |
| Direct tests / pickling | 27 passed |
| Preflight | 14/14 PASS |
| StudioNet integration | PASS: live conflict, compatible, and first activation flow |
| StudioNet deployment | `0xF0859DAa918Ec62813fD9dd6b8B2e822A8b88e03` |
| Compatible live proof | ACTIVE / COMPATIBLE |
| Conflicting live proof | REJECTED / CONFLICTING, material `1:EXCLUSIVITY` |
| Source/deployment parity | SHA-256 `0db8704661cbd79d286b7502a5e9d0c307039add1fabc48a0c2db3810fc1ee78` |

Do not label the repository fully submission-ready until live semantic consensus and deployment evidence are recorded in `DEPLOYMENT.md`.
