# Deployment and submission proof

## Local preflight

```bash
python -m pip install -r requirements.txt
genvm-lint check contracts/conflict_lock.py
pytest tests/direct -v
python scripts/preflight.py
```

The preflight script reports deterministic local checks and explicitly does not claim StudioNet success.

## Deploy

Using the current GenLayer CLI/tooling, deploy `contracts/conflict_lock.py` to StudioNet and record the resulting identifiers below.

## StudioNet proof

| Field | Evidence |
|---|---|
| Network | StudioNet |
| Contract | `0xF0859DAa918Ec62813fD9dd6b8B2e822A8b88e03` |
| Deployment tx | `0x1ecffe76483f1909f54fc9751153852add12a899ee27e60b002f84c83ed33f10` |
| Source commit | `8a9d0f5` (contract source unchanged through deployment) |
| Source SHA-256 | `0db8704661cbd79d286b7502a5e9d0c307039add1fabc48a0c2db3810fc1ee78` |
| Explorer | https://explorer-studio.genlayer.com/contracts/0xF0859DAa918Ec62813fD9dd6b8B2e822A8b88e03 |

## Live semantic proof

- First proposal: `0xfab32cd3d6736ea5df76a8ff95a382fd5b40df3d1c86ee1369ec2b3813a7ded9`
- First resolution: `0x02eee108367d345ad9d5bccd07103617e6fd67bd9c4ec96d031cd0aa94483bd2` — `ACTIVE / COMPATIBLE`.
- Conflict proposal: `0xc6e482c58233581b67565f6e15a7ce6f47ee01fae531d4b3ba97bd2dfdfd795a`
- Conflict resolution: `0x3f2bcd84c13de65720d2ad85567480068d78afe67b7626166f2565b49707c083` — `REJECTED / CONFLICTING`.
- Stored material edge: `1:EXCLUSIVITY`.
- Compatible proposal: `0x11d669a0c8e98da101b3a930956602bc339b10f659ce5082f79c54391454adf1`
- Compatible resolution: `0x62ed4c9cf2cd1521635c397e95e49315986617ab9cdf5790d704d5740fdaa238` — `ACTIVE / COMPATIBLE`.

## Semantic proof scenario

Use one account for all writes.

1. Propose `Exclusively provide Dataset X to Company B until September 30.` in scope `agent.procurement`.
2. Resolve it. With no active commitments, it should become `ACTIVE` deterministically.
3. Propose `Provide Dataset X to Company C on September 12.` in the same scope.
4. Resolve it with normal StudioNet validators.
5. Verify the second proposal becomes `REJECTED` when consensus finds the exclusivity conflict, or `REVIEW_REQUIRED` if validators cannot reach a conclusive outcome.
6. Record `get_resolution` and `get_conflict` outputs as submission evidence.

Do not claim live semantic consensus proof until those writes have finalized on the target network.
