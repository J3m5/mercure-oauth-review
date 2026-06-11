# Mercure OAuth 2.0 Review Summary

Review performed against:

- #1262 spec: `e66c4c252cd67756e23f194c34c12fcfcc4a1632`
- #1269 matchers: `6acf34e3004173a13bfe89a37996e062d4a9844f`
- #1273 OAuth: `4669234f611ffb5c2a0ac2fab00efc32fc023334`

Follow-up comparison after maintainer pushes on 2026-06-10:

- #1262 spec: `a39e15e` (`spec: note that the Bearer scheme name is case-insensitive`)
- #1269 matchers: `e781ad9` (`fix(subscriptions): emit RFC 9110-quoted ETags`)
- #1273 OAuth: `edfaa64` (`fix(authz): match the Bearer scheme case-insensitively`)

Final spec-grounded review:

- Date: 2026-06-10
- OAuth worktree: `mercure-feat-oauth-authz` at `edfaa64`
- Spec worktree: `mercure` / `spec/oauth-authz` at `a39e15e`
- Local normative corpus: `oauth2-specs/`

Follow-up after Kevin's latest commits on 2026-06-11:

- #1262 spec: `75cc92a`
- #1269 matchers: `fe3122e`
- #1273 OAuth: `0a415e4`

Artifacts:

- `mercure-oauth-review-matrix.md`
- `mercure-oauth-review-findings.md`
- `mercure-oauth-review-commands.md`
- `mercure-oauth-review-summary.md`

## Findings

- Blocker: none found.
- Major: 0 remaining.
- Minor: 1 partial item remaining.
  - `resource_identifier` now rejects invalid URLs and fragments, but non-HTTPS identifiers are still published with only a warning.
- Question: 0 remaining.

Resolved since the initial review:

- JWKS-backed validation gets a default asymmetric JWS algorithm allowlist when no explicit list is configured.
- URLPattern matching derives the real base from a full hub `resource_identifier` when `public_url` is unset.
- Debug UI, conformance tests, and user docs now use `match` / `matchURLPattern` for subscriptions.
- `application/at+jwt` matching accepts mixed-case `Application/AT+JWT`.
- Protected resource metadata advertises `authorization_details_types_supported: ["mercure"]`.
- #1269 CI lint failure on `deprecatedMatcherTypeName` is fixed.
- `Authorization: Bearer` scheme matching is now case-insensitive in #1273 and documented in #1262.
- Malformed `authorization_details` is now mapped to `401 invalid_token`.
- CORS wildcard plus credentials is no longer emitted together.
- Reserved hub namespace checks and reserved update IDs have been tightened.
- Subscription API ETags are now RFC 9110 quoted strings.

## Positive coverage

The implementation covers many high-risk parts of the new protocol:

- `Authorization: Bearer` / `access_token` / cookie priority is implemented.
- `typ`, `aud`, `exp`, `nbf`, issuer checking when `authorization_servers` is configured, and token expiry-driven disconnects are covered.
- `authorization_details` validation rejects malformed Mercure details without partial application.
- `match`, `matchExact`, `matchURLPattern`, unknown `match*` rejection, C0/C1/DEL checks, wildcard behavior, and bounded matcher caches are implemented.
- Resource metadata is served at the RFC 9728 well-known URL and keeps cookie support out of `bearer_methods_supported`.
- v8 compatibility is gated by build tags plus `protocol_version_compatibility 8`.
- Token-bearing query parameters are redacted in the provided Caddyfiles.

## Tests run

Passing:

- #1269: `env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test ./...`
- #1273: `env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test ./...`
- #1273 compat: `env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test -tags deprecated_topic,deprecated_claim ./...`
- #1273 Caddy: `env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test ./...` from `caddy/`
- #1273 Caddy compat: `env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test -tags deprecated_topic,deprecated_claim ./...` from `caddy/`
- Follow-up #1269 at `e781ad9`: `env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test ./...`
- Follow-up #1273 at `edfaa64`: `env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test ./...`
- Final #1273 at `edfaa64`: `env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test ./...`
- Final #1273 compat at `edfaa64`: `env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test -tags deprecated_topic,deprecated_claim ./...`
- Final #1273 Caddy at `edfaa64`: `env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test ./...` from `caddy/`
- Local Playwright conformance after adapting `mercure/conformance-tests` to modern `match` / `matchURLPattern`: `npm run test:e2e`, last-run status `passed`, `failedTests: []`
- Follow-up #1273 at `0a415e4`: `env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test ./...`
- Follow-up #1273 compat at `0a415e4`: `env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test -tags deprecated_topic,deprecated_claim ./...`
- Follow-up #1273 Caddy at `0a415e4`: `env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test ./...` from `caddy/`
- Follow-up #1273 Caddy compat at `0a415e4`: `env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test -tags deprecated_topic,deprecated_claim ./...` from `caddy/`

Historical failed / inconclusive runs:

- Initial Playwright conformance run, before adapting the suite, failed on `Publish update / raw string` because the hub returned `400 Bad Request` for the legacy `topic=...` EventSource subscribe URL.
- A first follow-up compat run was started in parallel with another test process and failed on transient Bolt test-file collisions; rerunning it alone passed.

GitHub checks:

- #1262 after `75cc92a`: lint, tests, schema, release, and CLA pass.
- #1269 after `fe3122e`: lint, tests, schema, release, and related checks pass. The PR remains draft.
- #1273 after `0a415e4`: `gh pr checks` still reports only `license/cla`.

## Recommended maintainer action

Before merging #1273 into a modern-default release:

1. Decide whether modern mode should reject non-HTTPS `resource_identifier` values instead of only warning, or explicitly document the compatibility choice.
2. Wait for full #1273 CI visibility beyond `license/cla`, or trigger/inspect the relevant checks manually.

After fixes, rerun:

```bash
env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test ./...
env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test -tags deprecated_topic,deprecated_claim ./...
(cd caddy && env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test ./...)
(cd caddy && env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test -tags deprecated_topic,deprecated_claim ./...)
```

Then rerun conformance tests against a modern hub configured without `protocol_version_compatibility 8`, and add a separate compatibility conformance run only if legacy behavior is intentionally tested.
