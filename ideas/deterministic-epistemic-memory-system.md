# Deterministic Epistemic Memory System

## Motivation

The PiyAPI experiments suggest that persistent storage plus vector retrieval is
not enough for a memory system expected to preserve current truth, uncertainty,
provenance, and evidentiary independence.

The proposed system is closer to an epistemic database than a vector store. It
stores immutable source memories, compiles them into normalized claims, tracks
where evidence originated, preserves temporal and scoped states, and determines
whether a question is answerable before producing context for an LLM.

An LLM may assist with extracting candidate structure from uncontrolled prose or
rendering a final answer. It must not silently control identity, provenance,
evidence counting, supersession, or temporal state.

## Design principles

1. Source memories are immutable.
2. Claims and evidence are different objects.
3. Repeated documents are not automatically independent evidence.
4. Claim identity includes scope and time semantics.
5. Contradiction is explicit and never silently resolved by document count.
6. Historical belief and presently reconstructed truth are separate timelines.
7. Abstention has a structured reason, not merely a similarity threshold.
8. Retrieval returns a diverse evidentiary package, not only nearest text.
9. Every inferred relationship records its origin and confidence.
10. Ground-truth or benchmark-oracle fields never enter the production compiler.

## Data model

### Memory

An immutable source record:

```text
Memory
  id
  original text
  source and author
  event time
  observation time
  ingestion time
  scope
  extracted claims
  provenance links
```

### Claim assertion

The current deterministic identity is:

```text
(
  normalized subject entity,
  normalized predicate,
  normalized object,
  canonical non-null scope
)
```

The tuple is hashed into a stable claim ID. Display text, source authority,
confidence language, and ingestion order do not affect identity.

### Claim family

A claim family groups potentially competing assertions by:

```text
(normalized subject entity, normalized predicate, canonical scope)
```

Objects remain separate assertions inside the family. This allows the system to
compare alternatives without collapsing them into one value prematurely.

### Evidence root

An evidence root represents a real observation or originating artifact, not a
document that merely repeats it.

```text
EvidenceRoot
  stable observation/artifact ID
  source
  observation time
  directness
  reliability dimensions
  accessibility
  descendant memories
```

### Relations

The graph should support at least:

```text
supports
contradicts
derived_from
quotes
supersedes
corrects
narrows
generalizes
same_evidence_root
```

## Deterministic compilation pipeline

For already-structured input:

1. Validate required fields and unique memory IDs.
2. Normalize Unicode, whitespace, entity IDs, predicates, objects, and scope.
3. Build stable claim-assertion IDs.
4. Group assertions into claim families.
5. Validate every graph reference.
6. Add typed derivation, contradiction, and supersession edges.
7. Traverse provenance to compute leaf roots.
8. Detect and report derivation cycles.
9. Construct temporal indexes using event, observation, and ingestion times.
10. Emit deterministic JSON suitable for evaluation or storage.

For uncontrolled natural language, semantic extraction cannot be guaranteed by a
pure parser. A production ingestion boundary should require either trusted
structured fields or an extractor proposal that is validated before acceptance.

## Required evidence contract

Experiment 5 demonstrated that `derived_from` alone cannot reliably determine
evidentiary independence. The input contract should explicitly include:

```json
{
  "claim_relation": "supports | contradicts | neutral",
  "evidence_kind": "independent_observation | derivative | synthesis | context",
  "evidence_root_ids": ["stable-observation-or-artifact-id"],
  "derived_from": ["memory-id"],
  "supersedes": ["memory-id"]
}
```

These fields must not be inferred from author seniority, repetition, confidence
language, or embedding similarity.

## Evidence scoring

Document count is not evidence strength. A starting model is:

```text
claim strength = sum over independent roots of:
  source reliability
  × observation directness
  × scope compatibility
  × temporal applicability
  × measurement quality
```

Derivative documents improve discoverability but do not add an independent root.
A partially independent synthesis can contribute only the roots it actually adds.

The system should preserve the components rather than reduce everything to one
opaque confidence number.

## Temporal state

At minimum, keep these clocks separate:

```text
event time       when something happened in the world
observation time when a source observed it
ingestion time   when the memory system learned it
belief time      when a particular actor held or asserted a belief
```

This supports distinct questions such as:

- What did the investigation team believe on April 5?
- What does all currently available evidence say about the April 5 event?

Later evidence may change the second answer without rewriting the first.

## Claim-state algorithm

A claim family should produce structured states rather than a forced Boolean:

```text
supported
contradicted
underdetermined
partially supported
scope-dependent
historically believed
superseded
corrected
unsupported
known but inaccessible
```

State computation should:

1. Select evidence available at the requested knowledge time.
2. Filter or partition it by compatible scope and event interval.
3. Collapse derivative memories onto independent evidence roots.
4. Apply explicit support and contradiction relations.
5. Apply corrections and supersession only within compatible scope.
6. Preserve multiple live assertions when evidence does not resolve them.
7. Record the evidence and rule responsible for the resulting state.

## Query planning and retrieval

A question becomes a structured plan:

```json
{
  "entities": ["system_t4"],
  "predicate_family": ["caused_by"],
  "time_mode": "current",
  "scope": {},
  "intent": "epistemic_summary",
  "needs": [
    "candidate assertions",
    "supporting roots",
    "contradicting roots",
    "supersession history",
    "known evidence gaps"
  ]
}
```

Retrieval then proceeds in stages:

1. Use lexical and vector search only for candidate discovery.
2. Resolve candidates to claim families.
3. Expand supporting, contradicting, correction, and provenance edges.
4. apply time and scope constraints.
5. Diversify by claim assertion and independent root.
6. Determine answerability.
7. Return a structured evidence package.

Ranking should reward relevance, scope match, temporal applicability, directness,
and new evidence-root coverage while penalizing redundancy and scope conflict.

## Answerability and abstention

Abstention is a classification problem:

```text
unknown entity
known entity but unknown predicate
false premise
insufficient scope or time
known but inaccessible evidence
unresolved independent conflict
partially answerable
answerable
```

The system should return the reason and the evidence supporting that reason. A
single vector-similarity threshold cannot distinguish these cases.

## Prototype status

The initial implementation lives in `benchmark/epistemic/` with CLIs and tests in
`benchmark/`.

Current deterministic behavior:

- Unicode and whitespace normalization
- canonical non-null scopes
- stable hashed claim IDs
- claim clustering
- typed `derived_from`, `supersedes`, and `contradicts` edges
- recursive provenance-leaf computation
- shared-root deduplication
- multiple-parent root union
- missing-reference validation
- derivation-cycle detection
- explicit exclusion of `_oracle` and `truth_role`

Experiment 5 compilation produced:

```text
202 memories
61 public claim assertions
122 graph edges
0 derivation cycles
```

All 25 oracle claims map to exactly one public claim key, with no public key mixing
multiple oracle claims. Eight unit/integration tests currently pass.

## Known gap found by the prototype

Naive provenance-leaf counts matched Experiment 5's intended independent-root
count for only 4 of 25 claims, with mean absolute error 1.44 roots.

This does not invalidate deterministic compilation. It demonstrates that the
input data lacks enough public semantics to equate graph leaves with independent
supporting evidence. Explicit stance, evidence kind, and stable root identity are
required before evidence counts can be trusted.

## Next implementation stages

1. Add claim-family nodes that group competing objects.
2. Lift memory-level contradiction and supersession edges to claim assertions.
3. Implement `as_of_event_time` and `as_of_knowledge_time` snapshots.
4. Add explicit evidence-relation and evidence-kind validation.
5. Compute traceable claim states without a single opaque score.
6. Build deterministic answerability classification.
7. Add evidence-diverse retrieval over claims and roots.
8. Run Experiment 5 state evaluation.
9. Use Experiment 6 to test root recovery, cycles, and lineage depth.
10. Use Experiment 7 to test missingness and abstention reasons.

## Practical storage architecture

A first implementation can use PostgreSQL for immutable memories, normalized
claims, temporal indexes, and graph-edge tables; full-text search plus `pgvector`
for candidate discovery; and deterministic application code for graph traversal
and state computation.

The LLM, if present, proposes structure and renders answers. The database and
deterministic algorithms remain authoritative for identity, provenance, time,
scope, and evidence accounting.
