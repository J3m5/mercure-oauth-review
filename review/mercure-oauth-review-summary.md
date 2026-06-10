# Mercure OAuth 2.0 Review Summary

Review performed against:

- #1262 spec: `e66c4c252cd67756e23f194c34c12fcfcc4a1632`
- #1269 matchers: `6acf34e3004173a13bfe89a37996e062d4a9844f`
- #1273 OAuth: `4669234f611ffb5c2a0ac2fab00efc32fc023334`

Artifacts:

- `mercure-oauth-review-matrix.md`
- `mercure-oauth-review-findings.md`
- `mercure-oauth-review-commands.md`
- `mercure-oauth-review-summary.md`

## Findings

- Blocker: none found.
- Major: 3
  - JWKS validation can run without an explicit JWS algorithm allowlist.
  - URLPattern falls back to a synthetic base instead of the hub URL when `public_url` is unset.
  - Debug UI, conformance tests, and several docs still use legacy `topic` / `topicURLPattern` subscribe parameters.
- Minor: 2
  - `application/at+jwt` handling is not fully case-insensitive despite the comment.
  - #1269 CI lint fails on the `deprecated_topic` build path (`exhaustive` on `subscribematchers.go`).
- Question: 1
  - Whether RFC 9728 metadata should advertise `authorization_details_types_supported: ["mercure"]`.

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

Not run:

- Playwright conformance tests. They have no installed `node_modules`, no package script, assume an external running hub, and currently exercise legacy subscribe parameters.

GitHub checks:

- #1262: `Lint` and `Test (1.26)` are failing. Lint reports `publish_test.go` testifylint issues (`assert.ErrorIs` expected). Test times out during `npx playwright install`, before conformance execution.
- #1269: `Lint` and `Test (1.26)` are failing. Lint reports `subscribematchers.go:116` exhaustive missing `deprecatedMatcherTypeName`. Test times out during `npx playwright install`, before conformance execution.
- #1273: only `license/cla` is currently reported by `gh pr checks`.

## Recommended maintainer action

Address the three Major findings before merging #1273 into a modern-default release:

1. Make JWKS algorithm pinning mandatory or provide an explicit safe default allowlist.
2. Require or derive the real hub URL for URLPattern base resolution.
3. Update UI, conformance, and docs to modern `match` / `matchURLPattern` semantics.

After fixes, rerun:

```bash
env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test ./...
env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test -tags deprecated_topic,deprecated_claim ./...
(cd caddy && env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test ./...)
(cd caddy && env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test -tags deprecated_topic,deprecated_claim ./...)
```

Then run conformance tests against a modern hub configured without `protocol_version_compatibility 8`, and add a separate compatibility conformance run only if legacy behavior is intentionally tested.
