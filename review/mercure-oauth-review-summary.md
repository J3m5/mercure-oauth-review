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
  - Debug UI, upstream conformance tests, and several docs still use legacy `topic` / `topicURLPattern` subscribe parameters. A local adaptation of the conformance suite to `match` / `matchURLPattern` passed.
- Minor: 2
  - `application/at+jwt` handling is not fully case-insensitive despite the comment.
  - `resource_identifier` is not validated as an RFC 9728 protected resource identifier URL before being published as metadata.
- Question: 1
  - Whether RFC 9728 metadata should advertise `authorization_details_types_supported: ["mercure"]`.

Resolved since the initial review:

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

Not run / inconclusive:

- Initial Playwright conformance run, before adapting the suite, failed on `Publish update / raw string` because the hub returned `400 Bad Request` for the legacy `topic=...` EventSource subscribe URL.
- Final #1273 Caddy compat rerun was interrupted after hanging without output for more than two minutes inside the sandbox. This does not invalidate the earlier successful Caddy compat run, but the final rerun is non-conclusive.

GitHub checks:

- #1262 after `a39e15e`: `lint` fails only on `NATURAL_LANGUAGE`, `spec/mercure.md:153`, where textlint wants `website` replaced by `site`; `Test (1.26)` was pending when checked.
- #1269 after `e781ad9`: lint-related checks pass; `Test (1.26)` was pending when checked.
- #1273 after `edfaa64`: only `license/cla` was reported by `gh pr checks` when checked.

## Recommended maintainer action

Address the three Major findings before merging #1273 into a modern-default release:

1. Make JWKS algorithm pinning mandatory or provide an explicit safe default allowlist.
2. Require or derive the real hub URL for URLPattern base resolution.
3. Land the conformance-test adaptation and update UI/docs to modern `match` / `matchURLPattern` semantics.

Also address the two Minor findings for standards polish and OAuth discovery interoperability:

1. Accept both `at+jwt` and `application/at+jwt` with fully case-insensitive matching.
2. Validate `resource_identifier` as an RFC 9728 resource URL, or explicitly document any deliberate non-URL compatibility mode.

After fixes, rerun:

```bash
env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test ./...
env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test -tags deprecated_topic,deprecated_claim ./...
(cd caddy && env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test ./...)
(cd caddy && env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test -tags deprecated_topic,deprecated_claim ./...)
```

Then rerun conformance tests against a modern hub configured without `protocol_version_compatibility 8`, and add a separate compatibility conformance run only if legacy behavior is intentionally tested.
