# Deterministic epistemic compiler

This package compiles already-structured memories into stable claim identities,
typed graph edges, and provenance-leaf evidence roots. It does not call an LLM,
embedding model, or external service.

## Public claim identity

A claim assertion is identified by:

```text
(normalized subject_entity_id, normalized predicate, normalized object, canonical non-null scope)
```

The full tuple is hashed to a stable `claim_<sha256-prefix>` identifier. Display
text, source authority, confidence language, and ingestion order do not affect
identity.

## Evidence-root algorithm

For a memory with no `derived_from` parents, its root is its own memory ID. For a
derived memory, its roots are the sorted union of its parents' roots. This makes
copies and summaries contribute no additional independent roots when their
provenance is complete.

Cycles are detected and reported instead of being counted as evidence roots.
Missing references and duplicate memory IDs are hard errors.

## Security boundary

`compiler.py` drops `_oracle` and `truth_role`. Tests confirm those fields cannot
change its output. `verify_exp05_compiler.py` is a separate benchmark-side tool
that may read oracle data solely to score compiler output.

## Current limitation discovered by Experiment 05

Derivation edges alone do not define *evidentiary* independence. Experiment 05's
public records do not consistently expose:

- whether a memory supports, contradicts, or is neutral toward its normalized
  assertion;
- whether a rootless document contains a new observation or only an uncited
  restatement;
- a stable real-world observation/artifact identifier shared by all derivatives.

Consequently, provenance-leaf counts should not yet be presented as independent
evidence counts. The oracle verifier currently exists to quantify this gap.

A production ingestion contract should require these explicit fields:

```json
{
  "claim_relation": "supports | contradicts | neutral",
  "evidence_kind": "independent_observation | derivative | synthesis | context",
  "evidence_root_ids": ["artifact-or-observation-id"],
  "derived_from": ["memory-id"],
  "supersedes": ["memory-id"]
}
```

Those values can be supplied by a trusted structured source or proposed by an
extractor and held for validation. They must not be silently inferred from author
seniority, document repetition, or semantic similarity.

## Commands

```bash
python3 benchmark/compile_exp05.py
python3 benchmark/verify_exp05_compiler.py
python3 -m unittest discover -s benchmark/tests -v
```
