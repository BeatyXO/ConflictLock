# Security notes

## Prompt injection

Commitment text and context are untrusted data. The validator prompt explicitly treats embedded instructions as data and restricts judgment to coexistence.

## Invented conflicts

A model cannot create a valid conflict edge to an arbitrary ID. Normalization drops every ID not present in the captured active snapshot.

## Weak conflict inflation

`POTENTIAL` conflicts cannot cause rejection. `CONFLICTING` is accepted only with at least one `MATERIAL` edge.

## Semantic race / stale reads

The revision check prevents a proposal from resolving against a stale active set after another commitment was activated or deactivated.

## Exact duplicates

Exact active duplicates are rejected deterministically before consensus. Semantic near-duplicates remain a validator question.

## Scope poisoning

Scope identifiers are canonicalized to lowercase and restricted to `a-z`, `0-9`, `.`, `_`, and `-`.

## Bounded work

Commitment/context lengths, conflicts, and active commitments per scope are capped. This bounds prompt size and storage growth per resolution.

## Known limitation

ConflictLock can only compare commitments registered in the same principal-defined scope. A poorly chosen scope can omit relevant commitments. Consumers should define narrow, stable scope conventions and document them as part of their integration policy.
