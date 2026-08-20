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
| Python compile | Run in CI |
| GenVM lint | PASS locally |
| Direct tests | Existing suite; pinned gltest harness is blocked by Windows temp-file cleanup on this host |
| Pickling | Enabled by direct fixture; not independently green on this Windows host |
| Preflight | Added; deterministic and local-only |
| StudioNet integration | Credential/network execution not available in this workspace |
| Deployment | Not claimed; no address/transaction fabricated |
| Source/deployment parity | Not applicable until a deployment exists |

Do not label the repository fully submission-ready until live semantic consensus and deployment evidence are recorded in `DEPLOYMENT.md`.
