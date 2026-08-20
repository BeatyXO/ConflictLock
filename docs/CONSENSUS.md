# Consensus design

## Consensus question

For one proposed commitment and one immutable snapshot of active commitments in the same principal-defined scope:

> Can the candidate and every active commitment in this snapshot be simultaneously honored under their ordinary meaning and supplied context?

Validators are explicitly told not to judge desirability, legality, ethics, profitability, truthfulness, or likelihood of performance. The boundary is coexistence only.

## Leader output

The leader returns structured JSON:

```json
{
  "verdict": "COMPATIBLE | CONFLICTING | INCONCLUSIVE",
  "reason": "bounded explanation",
  "conflicts": [
    {
      "commitment_id": "1",
      "category": "EXCLUSIVITY",
      "severity": "MATERIAL",
      "reason": "bounded explanation"
    }
  ]
}
```

## Deterministic normalization

Before the result can affect state, ConflictLock:

1. drops conflict IDs not present in the captured snapshot;
2. maps categories to an allow-list;
3. maps severity to `MATERIAL` or `POTENTIAL`;
4. deduplicates conflict edges;
5. refuses `CONFLICTING` without a material edge;
6. refuses `COMPATIBLE` if any conflict edge remains;
7. promotes an `INCONCLUSIVE` output containing a material edge to `CONFLICTING`.

This means model output is not trusted as arbitrary state.

## Equivalence principle

Validators independently run the same semantic classification.

- For `COMPATIBLE`, agreement on the normalized verdict is enough because normalization guarantees there are no conflict edges.
- For `INCONCLUSIVE`, agreement on the normalized verdict is enough because the contract performs no activation/rejection consequence beyond marking review required.
- For `CONFLICTING`, validators must agree on both the normalized verdict and the material-edge fingerprint: `commitment_id:category`.

Reasoning prose is deliberately excluded from equivalence.

## Why not strict equality?

Two validators may correctly describe the same incompatibility differently. Requiring identical prose would make consensus brittle without increasing safety. The state transition depends on the verdict and material conflict identity, so those are the fields that must agree.
