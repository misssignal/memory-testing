# PiyAPI — Full Endpoint Surface (non-memory routes)

Source: `GET /api/v1/endpoints`, fetched 2026-09-03 with an authenticated `sk_live_...` key.
Companion to [piyapi_api_reference.md](piyapi_api_reference.md), which covers the memory/search/context endpoints this key is actually meant to be used for.

**Purpose of this doc:** the endpoint index reports `total_endpoints: 433`, but only **367** distinct routes are actually listed (the self-reported total doesn't match — worth mentioning to the developer). Of those, only **49** relate to memory/search/graph/context — the feature this API is marketed for. The remaining **318** span a full SaaS billing/admin/compliance platform. Documenting it here purely for awareness — not something we're using or recommend using.

**Memory-related routes (46):** already documented in `piyapi_api_reference.md`.

---

## Notable / concerning routes at a glance

These stood out enough to call out individually before the full category breakdown:

- `POST /api/users/:userId/impersonate` — user impersonation endpoint, reachable (per the index) same as any other route
- `POST /api/:userId/overrides/pricing`, `/overrides/discount`, `/overrides/trial` — per-user billing overrides
- `PATCH /api/admin/enterprise-quotas/:userId/sla`, `/data-residency` — enterprise SLA/data-residency admin controls
- `GET /api/compliance/reports/hipaa`, `/soc2`, `/retention` — compliance report generation, implying this platform handles regulated data
- `POST /api/phi-check`, `GET /api/phi-stats`, `/phi-status` — PHI (protected health information) detection built in, consistent with `contains_phi`/`phi_risk_level` fields on every memory object
- `DELETE /api/saml`, `PUT /api/saml`, `DELETE /api/oidc`, `PUT /api/oidc` — enterprise SSO config, unusual for a product being marketed with a "2-minute npx MCP install" quickstart
- `POST /api/legacy/process` — explicitly named legacy route still live
- Payment webhook receivers for **PayPal and Razorpay** (`/webhooks/paypal`, `/webhooks/razorpay`) but the docs/PDF never mention pricing or a paid tier beyond the vague "ask costs compute" framing

None of this was mentioned anywhere in the developer setup PDF, which frames PiyAPI as a lightweight memory add-on.

---

## Auth & Identity (55)

```
DELETE /api/account
DELETE /api/oidc
DELETE /api/saml
DELETE /api/users/:externalId
GET /api/admin/metrics/discounts
GET /api/admin/metrics/export
GET /api/admin/metrics/revenue
GET /api/admin/metrics/subscriptions
GET /api/audit-logs/auth
GET /api/cache/warm/metrics
GET /api/google
GET /api/google/callback
GET /api/me
GET /api/messages
GET /api/messages/count
GET /api/metrics
GET /api/metrics/business
GET /api/metrics/costs
GET /api/profile
GET /api/sso/options
GET /api/user
GET /api/user/:userId
GET /api/users
GET /api/users/:externalId
GET /api/users/:userId
GET /api/users/:userId/usage
GET /auth/callback
GET /auth/login
GET /auth/metadata
GET /metrics
PATCH /api/users/:userId/plan
POST /api/:branchId/merge
POST /api/admin/user/:userId/region
POST /api/login
POST /api/logout
POST /api/messages
POST /api/metrics/reset
POST /api/password-reset
POST /api/password-reset/confirm
POST /api/refresh
POST /api/register
POST /api/resend-verification
POST /api/user
POST /api/users
POST /api/users/:userId/impersonate
POST /api/verify-email
POST /auth/callback
POST /auth/logout
POST /auth/slo/callback
PUT /api/group-mappings
PUT /api/oidc
PUT /api/password
PUT /api/saml
PUT /api/user
PUT /api/users/:externalId/limits
```

## API Keys & Licensing (8)

```
DELETE /api/keys/:id
GET /api/keys
POST /api/activate-license
POST /api/keys
POST /api/keys/:id/disable
POST /api/keys/:id/reactivate
POST /api/keys/:id/test
POST /api/license/revoke
```

## Billing & Subscription (36)

```
GET /api/all-pricing
GET /api/billing/tier-status
GET /api/budget-status
GET /api/cost-breakdown
GET /api/cost-metrics
GET /api/costs
GET /api/invoices
GET /api/plan-comparison
GET /api/plan-options
GET /api/plan-recommendations
GET /api/plans
GET /api/plans/:planId
GET /api/pricing
GET /api/pricing/:plan
GET /api/revenue
GET /api/savings/:plan
GET /api/subscription
PATCH /api/plans/:planId
PATCH /api/subscription
POST /api/:userId/overrides/pricing
POST /api/admin/bulk-operations/:operationId/cancel
POST /api/billing/apply-promo
POST /api/cancel
POST /api/checkout
POST /api/cost-saving/activate
POST /api/cost-saving/deactivate
POST /api/downgrade
POST /api/orphan/upgrade
POST /api/plan-change-confirm
POST /api/plan-change-preview
POST /api/portal
POST /api/subscription/cancel
POST /api/switch
POST /api/switch-to-annual
POST /api/upgrade
PUT /api/payment-method
```

## Admin & Enterprise Overrides (35)

```
DELETE /api/:userId/overrides/:type
DELETE /api/admin/enterprise-quotas/:userId
DELETE /api/admin/promo-codes/:code
GET /api/:userId/overrides
GET /api/admin/bulk-operations
GET /api/admin/bulk-operations/:operationId
GET /api/admin/enterprise-quotas
GET /api/admin/enterprise-quotas/:userId
GET /api/admin/enterprise-quotas/regions
GET /api/admin/enterprise-quotas/sla-levels
GET /api/admin/feature-flags
GET /api/admin/permissions/:adminId
GET /api/admin/promo-codes
GET /api/admin/promo-codes/:code
GET /api/admin/promo-codes/:code/analytics
GET /api/admin/volume-pricing/:planId
GET /api/custom-quotas
GET /api/features
GET /api/features/:featureId/access
PATCH /api/admin/enterprise-quotas/:userId
PATCH /api/admin/enterprise-quotas/:userId/data-residency
PATCH /api/admin/enterprise-quotas/:userId/sla
PATCH /api/admin/feature-flags/:flagId
PATCH /api/custom-quotas
POST /api/:userId/overrides/discount
POST /api/:userId/overrides/limits
POST /api/:userId/overrides/trial
POST /api/admin/bulk-operations
POST /api/admin/feature-flags
POST /api/admin/feature-flags/:flagId/disable
POST /api/admin/feature-flags/:flagId/enable-users
POST /api/admin/feature-flags/:flagId/percentage
POST /api/admin/promo-codes
POST /api/admin/volume-pricing/:planId
PUT /api/admin/permissions/:adminId
```

## Compliance & Privacy (14)

```
GET /api/compliance
GET /api/compliance/:region
GET /api/compliance/reports/hipaa
GET /api/compliance/reports/retention
GET /api/compliance/reports/soc2
GET /api/consent
GET /api/phi-stats
GET /api/phi-status
GET /api/privacy-policy
GET /api/terms-of-service
POST /api/consent
POST /api/opt-in
POST /api/opt-out
POST /api/phi-check
```

## Security & Audit (4)

```
GET /api/audit-logs
GET /api/audit-logs/api-keys
GET /api/errors/:correlationId
GET /api/security-status
```

## Webhooks & Third-party Integrations (11)

```
DELETE /api/integrations/:id
GET /api/integrations
GET /api/integrations/:id
GET /api/integrations/:id/logs
POST /api/:protocol/disable
POST /api/:protocol/enable
POST /api/:protocol/test
POST /api/integrations/:id/sync
POST /api/integrations/:provider
POST /webhooks/paypal
POST /webhooks/razorpay
```

## Documents & Ingestion (20)

```
DELETE /api/:documentId
GET /api/:documentId
GET /api/:documentId/delete-preview
GET /api/:documentId/download
GET /api/:documentId/status
GET /api/quarantine
GET /api/quarantine/:documentId
GET /api/tokenize/jobs/:id
POST /api/:documentId/replace/preview
POST /api/:documentId/restore
POST /api/:documentId/retry
POST /api/backfill
POST /api/ingest
POST /api/quarantine/:documentId/approve
POST /api/quarantine/:documentId/reject
POST /api/tokenize
POST /api/tokenize/async
POST /api/upload
POST /api/web-clip
PUT /api/:documentId/replace
```

## Async Jobs, Batch & Branching (20)

```
DELETE /api/:branchId
GET /api/:branchId
GET /api/:jobId
GET /api/:jobId/report
GET /api/bulk-replace/:jobId/status
GET /api/cache/warm/status/:jobId
GET /api/orphan/:scopeId
PATCH /api/curiosity/:itemId/resolve
POST /api/:branchId/discard
POST /api/accept
POST /api/async
POST /api/batch/async
POST /api/bulk-link
POST /api/bulk-replace
POST /api/commit
POST /api/dryrun
POST /api/mine
POST /api/propose
POST /api/resolve
POST /api/run
```

## Caching & Infra (11)

```
DELETE /api/summarize/cache
GET /api/cache/stats
GET /api/compression/stats
GET /api/pool/health
GET /api/queues/status
GET /api/summarize/cache-stats
POST /api/cache/clear
POST /api/cache/clear/:type
POST /api/cache/warm
POST /api/compression/reset-stats
POST /api/flush-metrics
```

## Cognitive / AI Internals (12)

```
GET /api/active-inference/stats
GET /api/cognitive
GET /api/cognitive-config
GET /api/cognitive-health
GET /api/cognitive-health/:userId
GET /api/cognitive-metrics
GET /api/communities
GET /api/correlate
GET /api/curiosity
GET /api/recommendations
GET /api/trends
POST /api/evaluate/benchmark
```

## Team / Enterprise Pools (3)

```
GET /api/team-pool/budget
GET /api/team-pool/health
GET /api/team-pool/health/:provider
```

## Sessions & Conversations (7)

```
GET /api/:sessionId
GET /api/conversation/:id
GET /api/conversations
GET /api/conversations/:conversationId
POST /api/:sessionId/review
POST /api/conversation/:id
POST /api/sessions
```

## Metrics, Health & Docs (23)

```
GET /api/:id/status
GET /api/:id/status/stream
GET /api/batch/:batchId/status
GET /api/count
GET /api/dashboard
GET /api/health
GET /api/health/detailed
GET /api/period
GET /api/phone/status
GET /api/statistics
GET /api/stats
GET /api/status
GET /docs
GET /docs/api
GET /docs/openapi.json
GET /docs/openapi.yaml
GET /docs/postman
GET /docs/swagger.json
GET /health
GET /health/extended
GET /health/live
GET /health/ready
GET /health/security
```

## Data Export / Namespace Mgmt (6)

```
DELETE /api/data
DELETE /api/namespace/:namespace
GET /api/download/:exportId
GET /api/export
GET /api/namespaces
PUT /api/ttl-config
```

## Phone / OTP (2)

```
POST /api/phone/send-otp
POST /api/phone/verify-otp
```

## Feedback (2)

```
POST /api/negative
POST /api/positive
```

## Legacy / Misc (9)

```
GET /api/check
GET /api/check/:purpose
GET /api/mode
GET /api/preview
POST /api/check
POST /api/legacy/process
POST /api/mode
POST /api/stream
POST /api/summarize
```

## Uncategorized — likely shared/generic resource routes (webhooks, jobs; ambiguous from path alone) (40)

```
DELETE /api/:id
DELETE /api/:id/pin
DELETE /api/:id/tokens
DELETE /api/:purpose
DELETE /api/batch
GET /api
GET /api/:id
GET /api/:id/deliveries
GET /api/:id/full
GET /api/:id/related
GET /api/:id/versions
GET /api/:id/versions/:version
GET /api/all
GET /api/embedding-dlq
GET /api/endpoints
GET /api/logs
GET /api/projects
GET /api/regions
GET /api/usage
GET /ping
GET /ready
PATCH /api/:id
POST /api
POST /api/:id/deliveries/:eventId/retry
POST /api/:id/pin
POST /api/:id/release
POST /api/:id/restore
POST /api/:id/review
POST /api/:id/rollback
POST /api/:id/rollback/:version
POST /api/:id/rotate
POST /api/:id/test
POST /api/:id/tokens
POST /api/:id/verify
POST /api/:id/versions/:version/rollback
POST /api/batch
POST /api/reconcile
PUT /api/:id
PUT /api/:id/rollback/:version
PUT /api/:id/versions/:version/rollback
```
