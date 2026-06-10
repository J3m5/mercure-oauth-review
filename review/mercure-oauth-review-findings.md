# Mercure OAuth 2.0 Review Findings

PRs reviewed:

- Spec: https://github.com/dunglas/mercure/pull/1262 (`spec/oauth-authz`, `e66c4c252cd67756e23f194c34c12fcfcc4a1632`)
- Matchers: https://github.com/dunglas/mercure/pull/1269 (`feat/matchers`, `6acf34e3004173a13bfe89a37996e062d4a9844f`)
- OAuth: https://github.com/dunglas/mercure/pull/1273 (`feat/oauth-authz`, `4669234f611ffb5c2a0ac2fab00efc32fc023334`)

Follow-up comparison after maintainer pushes on 2026-06-10:

- Spec: `a39e15e`
- Matchers: `e781ad9`
- OAuth: `edfaa64`

Final spec-grounded review:

- Date: 2026-06-10
- OAuth worktree: `mercure-feat-oauth-authz` at `edfaa64`
- Spec worktree: `mercure` / `spec/oauth-authz` at `a39e15e`
- Local normative corpus: `oauth2-specs/`

## Blocker

No blocker found.

## Major

### 1. JWKS validation can run without the explicit JWS algorithm allowlist required by the spec

- PR: #1273
- Files:
  - `authorization.go` lines 168-173: https://github.com/dunglas/mercure/blob/4669234f611ffb5c2a0ac2fab00efc32fc023334/authorization.go#L168-L173
  - `caddy/mercure.go` lines 288-313: https://github.com/dunglas/mercure/blob/4669234f611ffb5c2a0ac2fab00efc32fc023334/caddy/mercure.go#L288-L313
  - `caddy/mercure.go` lines 133-146: https://github.com/dunglas/mercure/blob/4669234f611ffb5c2a0ac2fab00efc32fc023334/caddy/mercure.go#L133-L146
- Requirement: `spec/mercure.md` token validation requires an explicit allowlist of accepted signature algorithms and forbids deriving accepted algorithms from the token. RFC 9068 also requires signed JWT access tokens, rejects `alg=none`, and requires validation failures to be reported as `invalid_token`.
- Evidence: `jwtParserOptions` only appends `jwt.WithValidMethods(algs)` when `len(algs) > 0`. The Caddy JWKS path accepts `publisher_jwks_url` / `subscriber_jwks_url` and only appends `WithPublisherJWTAlgorithms` / `WithSubscriberJWTAlgorithms` if optional directives are present. The code comment calls the directives "Recommended", not required.
- Impact: a JWKS-backed deployment can be configured without a protocol-level algorithm allowlist. That weakens the defense against algorithm confusion and makes acceptance depend on library/JWK metadata behavior instead of Mercure's normative policy.
- Proposed fix: make JWKS algorithm allowlists mandatory in modern mode. For Caddy, reject provisioning when `publisher_jwks_url` is set without `publisher_jwks_algorithms`, and similarly for subscribers. Alternatively provide a deliberately explicit default allowlist, document it, and pass it into `jwt.WithValidMethods`.
- Expected tests: Caddy provisioning fails for JWKS without algorithms in modern mode; succeeds with algorithms; a token signed with an algorithm outside the configured list is rejected with `401 invalid_token`; compatibility behavior, if intentionally different, is covered separately.
- Follow-up status at `edfaa64`: still open. The comment now explicitly says the JWKS path relies on per-key algorithm constraints when no allowlist is configured, and Caddy still treats `publisher_jwks_algorithms` / `subscriber_jwks_algorithms` as optional.

### 2. URLPattern matching falls back to a synthetic base instead of the hub URL when `public_url` is unset

- PR: #1269, affects #1273 deployments
- Files:
  - `topicselector.go` lines 24-32: https://github.com/dunglas/mercure/blob/6acf34e3004173a13bfe89a37996e062d4a9844f/topicselector.go#L24-L32
  - `topicselector.go` lines 93-108: https://github.com/dunglas/mercure/blob/6acf34e3004173a13bfe89a37996e062d4a9844f/topicselector.go#L93-L108
  - `topicselector.go` lines 185-186: https://github.com/dunglas/mercure/blob/6acf34e3004173a13bfe89a37996e062d4a9844f/topicselector.go#L185-L186
  - `docs/hub/config.md` lines 51-52: https://github.com/dunglas/mercure/blob/4669234f611ffb5c2a0ac2fab00efc32fc023334/docs/hub/config.md#L51-L52
  - `Caddyfile` lines 22-33: https://github.com/dunglas/mercure/blob/4669234f611ffb5c2a0ac2fab00efc32fc023334/Caddyfile#L22-L33
- Requirement: `spec/mercure.md` URL Pattern section says relative patterns or relative topics MUST use the hub URL as the base URL.
- Evidence: when `public_url` is empty, `TopicSelectorStore.base()` returns `http://mercure.invalid`. The comment explicitly states that cross-mode matching between a relative pattern and an absolute topic on the hub URL requires setting `WithPublicURL` / `public_url`. However, `public_url` is optional in docs and not set by the provided `Caddyfile`; a modern JWT hub can start with `resource_identifier` only.
- Impact: default/typical modern Caddy configuration can support URLPattern only partially. Relative URLPattern authorization details or subscribe matchers will not be resolved against the actual hub URL as required, so valid subscriptions or authorizations can miss updates.
- Proposed fix: make the real hub URL available to URLPattern matching in modern mode. Practical options: require `public_url` whenever URLPattern support is active, default it from a full hub `resource_identifier` when safe, or derive/store per-request base for subscriber matchers and authorization validation. Update the default Caddyfile and docs accordingly.
- Expected tests: with no `public_url`, either startup fails with a clear error or a relative pattern is resolved against the actual hub URL. Add tests for relative pattern vs absolute topic and absolute pattern vs relative topic.
- Follow-up status at `e781ad9` / `edfaa64`: still open. The code still falls back to `http://mercure.invalid`; comments now document that cross-mode matching requires `public_url`, but startup does not require it and no real hub URL is derived automatically.

### 3. Debug UI, conformance tests, and several user docs still use legacy subscribe parameters

- PR: #1269 and #1273
- Files:
  - `public/index.html` lines 41-44: https://github.com/dunglas/mercure/blob/4669234f611ffb5c2a0ac2fab00efc32fc023334/public/index.html#L41-L44
  - `public/app.js` lines 171-177: https://github.com/dunglas/mercure/blob/4669234f611ffb5c2a0ac2fab00efc32fc023334/public/app.js#L171-L177
  - `conformance-tests/mercure.spec.ts` lines 115-123: https://github.com/dunglas/mercure/blob/4669234f611ffb5c2a0ac2fab00efc32fc023334/conformance-tests/mercure.spec.ts#L115-L123
  - `docs/getting-started.md` lines 16-22: https://github.com/dunglas/mercure/blob/4669234f611ffb5c2a0ac2fab00efc32fc023334/docs/getting-started.md#L16-L22
  - `docs/hub/troubleshooting.md` lines 21-22: https://github.com/dunglas/mercure/blob/4669234f611ffb5c2a0ac2fab00efc32fc023334/docs/hub/troubleshooting.md#L21-L22
  - `docs/spec/faq.md` lines 38 and 47-62: https://github.com/dunglas/mercure/blob/4669234f611ffb5c2a0ac2fab00efc32fc023334/docs/spec/faq.md#L38
  - `docs/ecosystem/hotwire.md` lines 13-16 and 79-83: https://github.com/dunglas/mercure/blob/4669234f611ffb5c2a0ac2fab00efc32fc023334/docs/ecosystem/hotwire.md#L13-L16
- Requirement: `spec/mercure.md` subscription section defines `match`, `matchExact`, and `matchURLPattern`; #1269 rejects `topic` outside v8 compatibility.
- Evidence: the debug UI still exposes option values `topic` and `topicURLPattern`, appends those values to the subscription URL, and the conformance suite still selects `topicURLPattern` for `:param` patterns and `topic` otherwise. Several docs still tell users to subscribe with `topic=`.
- Impact: the demo/debug UI and conformance tests exercise the legacy API, not the modern protocol. In a modern-only build/default configuration, these examples fail with 400 instead of proving conformance. Users copying the docs will hit the removed path.
- Proposed fix: replace subscribe-side `topic` with `match`, and `topicURLPattern` with `matchURLPattern`, across UI, conformance tests, getting started, FAQ/troubleshooting snippets, and ecosystem examples. Keep legacy examples only in an explicitly labelled compatibility section.
- Expected tests: conformance tests use `match`/`matchURLPattern` by default and include a negative test that `topic` is rejected without compatibility. UI smoke test or unit-level DOM check verifies emitted query parameters.
- Follow-up status at `edfaa64`: still open. `public/app.js` still appends `topicURLPattern` for subscription events, `conformance-tests/mercure.spec.ts` still selects `topic` / `topicURLPattern`, and user docs still contain modern-path examples using `topic=`.

## Minor

### 4. `application/at+jwt` handling is not fully case-insensitive despite the code comment

- PR: #1273
- File: `authorization.go` lines 200-207: https://github.com/dunglas/mercure/blob/4669234f611ffb5c2a0ac2fab00efc32fc023334/authorization.go#L200-L207
- Requirement: RFC 9068 validation accepts `typ` values `at+jwt` or `application/at+jwt`. The local code comment says the media type is matched case-insensitively and tolerates the optional `application/` prefix.
- Evidence: the implementation uses `strings.TrimPrefix(typ, "application/")` before `strings.EqualFold`. That accepts `application/at+jwt` and `at+JWT`, but does not strip a mixed-case `Application/` prefix.
- Impact: standards-compliant clients using a differently cased media type prefix may be rejected. This is small because typical issuers use lowercase, but the code/comment/test coverage do not match the stated behavior.
- Proposed fix: compare `typ` case-insensitively against both accepted values, or lowercase before trimming the prefix.
- Expected tests: accept `typ: "application/at+jwt"` and a mixed-case prefix variant; still reject `JWT` / ID-token style values.
- Follow-up status at `edfaa64`: still open. `Authorization: Bearer` scheme matching was fixed, but JWT `typ` still uses `strings.TrimPrefix(typ, "application/")` before `strings.EqualFold`, so `Application/at+jwt` remains rejected.

### 5. `resource_identifier` is published without RFC 9728 URL validation

- PR: #1273
- Files:
  - `hub.go` lines 307-313: https://github.com/dunglas/mercure/blob/edfaa64/hub.go#L307-L313
  - `hub.go` lines 431-440: https://github.com/dunglas/mercure/blob/edfaa64/hub.go#L431-L440
  - `resourcemetadata.go` lines 17-25: https://github.com/dunglas/mercure/blob/edfaa64/resourcemetadata.go#L17-L25
  - `resourcemetadata.go` lines 40-47: https://github.com/dunglas/mercure/blob/edfaa64/resourcemetadata.go#L40-L47
- Requirement: RFC 9728 defines a protected resource identifier as a URL using the `https` scheme and no fragment component. The metadata response `resource` value is the protected resource identifier clients validate against the metadata URL or `WWW-Authenticate` `resource_metadata` flow.
- Evidence: `WithResourceIdentifier` accepts any string and `NewHub` only verifies that some value exists when JWT validation is enabled. That value is then copied verbatim to the protected resource metadata `resource` member.
- Impact: a Caddy or Go deployment can publish metadata that strict RFC 9728 clients must ignore because `resource` is not an `https` URL, contains a fragment, or otherwise cannot be the identifier used to derive the metadata URL. The token `aud` check can still work internally, but OAuth discovery interoperability is weakened.
- Proposed fix: validate `resource_identifier` in modern mode as an RFC 9728 resource identifier: absolute URL, `https` scheme, no fragment; preferably no query unless deliberately supported. If Mercure intentionally allows non-URL audiences for self-issued deployments, do not publish RFC 9728 metadata for that value or document a clearly labelled non-conformant compatibility mode.
- Expected tests: `NewHub` / Caddy provisioning rejects `resource_identifier foo`, `http://...`, and `https://...#fragment` in modern token-validating mode; valid `https://hub.example.com/.well-known/mercure` succeeds and is emitted unchanged in metadata.

## Resolved Follow-Up Items

These were review-adjacent gaps or CI issues observed during the initial pass and are no longer open after the 2026-06-10 maintainer pushes.

### #1269 CI lint fails on the `deprecated_topic` build path

- PR: #1269
- File: `subscribematchers.go` line 116: https://github.com/dunglas/mercure/blob/6acf34e3004173a13bfe89a37996e062d4a9844f/subscribematchers.go#L116
- Requirement: the v8 compatibility path must remain gated but buildable/lint-clean when official CI runs with deprecated tags.
- Evidence: GitHub check `Lint` for #1269 fails with `subscribematchers.go:116:2: missing cases in switch of type mercure.MatcherType: mercure.deprecatedMatcherTypeName (exhaustive)`.
- Impact: merge is blocked and the deprecated-topic build path is not clean under the repository lint profile, even though local `go test -tags deprecated_topic,deprecated_claim ./...` passes.
- Proposed fix: explicitly handle `deprecatedMatcherTypeName` in `matcherTypeFromParam` or add a narrowly scoped exhaustive directive if the omission is intentional because query params must never select the internal matcher type.
- Expected tests: CI lint passes with the repository's deprecated tag GOFLAGS.
- Follow-up status at `e781ad9`: resolved. `matcherTypeFromParam` now explicitly handles `deprecatedMatcherTypeName` as not addressable from the wire, and #1269 lint-related GitHub checks pass.

- `Authorization` scheme matching is case-insensitive in #1273 and documented in #1262.
- Malformed `authorization_details` is mapped to `401 invalid_token`, not `400 invalid_request`.
- Credentialed CORS no longer combines `Access-Control-Allow-Origin: *` with `Access-Control-Allow-Credentials: true`.
- Reserved hub namespace checks now resolve with the WHATWG URL algorithm and decode unreserved percent encodings before comparison.
- Publisher-supplied update IDs starting with `#` or equal to `earliest` are rejected.
- Subscription API ETags are emitted as RFC 9110 quoted strings.

## Question

### 6. Should protected resource metadata advertise supported authorization detail types?

- PR: #1273
- File: `resourcemetadata.go` lines 17-26: https://github.com/dunglas/mercure/blob/4669234f611ffb5c2a0ac2fab00efc32fc023334/resourcemetadata.go#L17-L26
- Requirement: RFC 9728 defines optional `authorization_details_types_supported`; Mercure now defines the `mercure` authorization details type.
- Observation: the metadata currently advertises `resource`, `bearer_methods_supported`, `authorization_servers`, and `mercure_cookie`, but not `authorization_details_types_supported: ["mercure"]`.
- Impact: not a spec violation because this field is optional, but clients using RFC 9728 discovery cannot learn from metadata that the resource supports the `mercure` authorization details type.
- Proposed decision: either add `authorization_details_types_supported: ["mercure"]`, or explicitly document why Mercure leaves this to AS metadata / future RFC 8414 follow-up.
