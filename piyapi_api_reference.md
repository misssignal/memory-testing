# PiyAPI — Condensed API Reference (verified against live OpenAPI spec)

Source: `GET https://api.piyapi.cloud/docs/openapi.json` + `GET /api/v1/endpoints`, fetched 2026-09-03.
Superseding the vendor PDF (`piyapi_developer_setup_manual.pdf`) where they disagree — see **Discrepancies** below.

**Base URL:** `https://api.piyapi.cloud/api/v1`
**Auth header:** `Authorization: Bearer $PIYAPI_API_KEY` (key format `sk_live_...`)
**Health check (no auth):** `GET https://api.piyapi.cloud/health` → `{status, timestamp}`

---

## Memories

| Method | Path | Body / Params | Notes |
|---|---|---|---|
| POST | `/memories` | `content*` (string), `namespace`, `tags[]`, `metadata{}` | Creates a memory |
| GET | `/memories` | query: `namespace`, `tags`, `limit`, `offset` | List |
| GET | `/memories/{id}` | — | Full memory object (fields below) |
| PATCH | `/memories/{id}` | `content*`, `namespace`, `tags[]`, `metadata{}` | Partial update |
| PUT | `/memories/{id}` | same | Full replace |
| DELETE | `/memories/{id}` | — | → `{deleted, id}` |

**Memory object fields (returned by GET/search):**
`id, content, namespace, tags[], metadata{}, memory_type` (enum: user/system/conversation/document/note/task/event/episodic), `importance_score, confidence_score, is_pinned, version, is_deprecated, superseded_by_id, valid_at, invalid_at, event_time, access_count, token_count, is_encrypted, created_at, updated_at`

Also present but **not in the PDF at all**:
`data_classification` (enum: public/internal/confidential/restricted), `contains_phi` (bool), `phi_risk_level` (enum: none/low/medium/high), `source_type`.

This is compliance/PHI-grade metadata on every memory object — more than a "store some text" API implies. Consistent with other endpoints seen in the full index (`/api/compliance/reports/hipaa`, `/soc2`, `/retention`).

---

## Search

| Method | Path | Body | Response |
|---|---|---|---|
| POST | `/search` | `query*`, `limit`, `namespace`, `min_similarity`, `tags[]`, `tags_match` (any/all), `include_deprecated`, `as_of` | `{results: [{memory, similarity}], count}` |
| POST | `/search/hybrid` | `query*`, `limit`, `namespace`, `semantic_weight`, `keyword_weight` | `{results: [{memory, semantic_score, keyword_score, combined_score}]}` |

## Context retrieval

| Method | Path | Body/Params | Response |
|---|---|---|---|
| GET or POST | `/context/retrieve` | `query*`, `max_tokens`, `namespace`, `format` (json/text/xml/markdown), `context_session_id`, `delta` | `{memories: [...], metadata: {tokens_used, tokens_remaining, memories_returned, memories_available}}` |

## Ask (RAG)

| Method | Path | Body | Response |
|---|---|---|---|
| POST | `/ask` | `query*`, `limit`, `namespace`, `includeAttributions` | `{answer, confidence, sources[], attributions[], model, tokensUsed, latencyMs}` |

---

## Discrepancies vs. the PDF (flagging, not fixed)

1. **`context/retrieve` response shape doesn't match.** The PDF describes `result["content"]` (a pre-formatted string for prompt injection), `result["tokenCount"]`, `result["user_profile"]`, `result["header"]`, `result["scoring_reasons"]`. The live spec returns `{memories: [...], metadata: {...}}` — a list of raw memory objects, no formatted `content` string, no `user_profile`, no `header`, no `scoring_reasons`. Code copied verbatim from the PDF's "Recommended Pattern" section (`context = result["content"]`) will `KeyError`.
2. **`search/hybrid` response doesn't match.** PDF claims `result["weights"]`, `result["facets"]`, `result["metrics"]`. The spec shows only `results[]` with `semantic_score`/`keyword_score`/`combined_score` — no weights/facets/metrics fields.
3. **Cost claims ("free" vs. "costs compute") aren't in the OpenAPI spec at all** — that framing exists only in the PDF's prose, steering you toward `/search` + `/context/retrieve` and away from `/ask`. Can't verify or refute it from the schema; treat it as a vendor claim, not a documented fact.

## Scope note

`/api/v1/endpoints` returns **433 routes total**. The overwhelming majority are unrelated to memory storage — full billing/subscription lifecycle, promo codes, pricing/discount overrides, user impersonation (`POST /api/users/:userId/impersonate`), SAML/OIDC, enterprise quota admin, webhook receivers for Stripe/PayPal/Razorpay. Not documented here since it's out of scope for what you're testing, but worth knowing this key has a much larger blast radius than "memory API" suggests if it were ever compromised or over-scoped.
