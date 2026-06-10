# Mercure OAuth 2.0 Normative Matrix

Source spec: `mercure/spec/mercure.md` from PR #1262 (`e66c4c252cd67756e23f194c34c12fcfcc4a1632`).

Follow-up comparison after maintainer pushes on 2026-06-10:

- #1262 spec: `a39e15e`
- #1269 matchers: `e781ad9`
- #1273 OAuth: `edfaa64`

Final spec-grounded review:

- Date: 2026-06-10
- Local normative corpus: `oauth2-specs/`

Status legend: OK, Partial, Gap, Not checked, N/A.

| ID | Requirement | Section | Level | Expected behavior | PR / implementation files | Status |
| --- | --- | --- | --- | --- | --- | --- |
| M01 | Topic strings are valid UTF-8 and contain no C0/C1/DEL. | Terminology, Subscription, Publication | MUST / MUST NOT | Reject invalid topic or matcher values with 400. | #1269 `matchertype.go`, `subscribematchers.go`; #1273 `authorizationdetails.go`, `publish.go` | OK |
| M02 | Subscribe uses `match`, `matchExact`, `matchURLPattern`; unknown `match*` names are rejected. | Subscription | MUST | Parse canonical matcher params; reject `topic` outside v8 compat. | #1269 `subscribematchers.go`, `subscribe_notdeprecated_topic_test.go` | OK for code; Gap in UI/docs/conformance |
| M03 | Subscribe matcher count and pattern length are bounded. | Subscription | SHOULD / MUST | Reject excessive count or long patterns with 400. | #1269 `subscribematchers.go`; #1273 `authorizationdetails.go` | OK |
| M04 | Exact matcher is byte-for-byte, no normalization, no relative URL resolution. | Exact Matching | MUST / MUST NOT | Exact comparison only. | #1269 `topicselector.go`, `topicselector_test.go` | OK |
| M05 | URLPattern matcher is supported. | URL Pattern | MUST | Compile and evaluate WHATWG URLPattern. | #1269 `topicselector.go` using `github.com/dunglas/go-urlpattern` | OK |
| M06 | Relative URLPattern patterns/topics use the hub URL as base. | URL Pattern | MUST | Use actual hub URL as base. | #1269 `topicselector.go`; #1273 `Caddyfile`, `docs/hub/config.md` | Gap: falls back to `http://mercure.invalid` when `public_url` unset |
| M07 | URLPattern matching is case-sensitive (`ignoreCase` disabled). | URL Pattern | MUST NOT | Do not enable ignoreCase. | #1269 `topicselector.go` | OK |
| M08 | URLPattern parse/eval errors are treated as non-match or rejected during request validation. | URL Pattern | MUST | Invalid submitted patterns rejected with 400; eval error aborts match. | #1269 `subscribematchers.go`, `topicselector.go`; #1273 `authorizationdetails.go` | OK |
| M09 | Wildcard `*` matches every topic and is not addressable as a literal topic. | Matcher Types / Security | Protocol rule | Recognize before matcher-type dispatch. | #1269 `topicselector.go` | OK |
| M10 | Publish request has exactly one `topic` in modern mode. | Publication | MUST | Reject multiple topics unless v8 compat path is active. | #1269/#1273 `publish.go`, `publish_notdeprecated_topic.go` | OK |
| M11 | Publish topics must not address reserved `/.well-known/mercure/` namespace. | Publication / Security | MUST NOT / MUST | Reject reserved namespace with 403. | #1269/#1273 `publish.go`, `reservedtopic.go` | OK; follow-up now resolves as URL reference and decodes unreserved percent encodings |
| M12 | Access token is JWT access token (RFC 9068), compact JWS, signed, short-lived recommended. | Authorization | MUST / SHOULD | Parse signed JWT and validate claims. | #1273 `authorization.go` | OK |
| M13 | Token presentation order is header, then `access_token` query, then cookie. | Presenting Access Token | MUST | Select exactly one token; ignore lower-priority mechanisms. | #1273 `authorization.go` | OK |
| M14 | Legacy `authorization` query and `mercureAuthorization` cookie are v8/deprecated only. | Presenting Access Token / Compatibility | Compatibility rule | Ignore outside `deprecated_claim` + compat mode. | #1273 `authorization.go`, `authorization_deprecated.go`, `authorization_notdeprecated.go` | OK |
| M15 | No token gives 401 Bearer challenge without error code, with `resource_metadata` when pertinent. | Error Responses | MUST / SHOULD | `WWW-Authenticate: Bearer resource_metadata=...` without error. | #1273 `bearererror.go`, `bearererror_test.go` | OK |
| M16 | Invalid token gives 401 `invalid_token`; insufficient scope gives 403 `insufficient_scope`; malformed auth request gives 400 `invalid_request`. | Error Responses | MUST | RFC 6750-style challenge/error mapping. | #1273 `bearererror.go`, `publish.go`, `subscription.go` | OK for auth paths; malformed `authorization_details` now maps to `401 invalid_token`; general malformed non-auth requests still plain 400 |
| M17 | `typ` must be `at+jwt` or `application/at+jwt`. | Token Validation / RFC 9068 | MUST | Reject other token types. | #1273 `authorization.go` | Partial: lowercase `application/` accepted; mixed-case prefix not |
| M18 | Accepted JWS algorithms are explicitly allowlisted; `alg=none` is rejected; algorithms are not derived from token. | Token Validation | MUST / MUST NOT | Always pass explicit accepted algorithms to JWT parser. | #1273 `authorization.go`, `hub.go`, `caddy/mercure.go` | Gap for JWKS path without configured algorithms |
| M19 | Audience is required and must contain the hub resource identifier. | Token Validation / RFC 9068 | MUST | Require `aud` and compare to `resource_identifier`. | #1273 `authorization.go`, `hub.go`, `caddy/mercure.go` | OK |
| M20 | `exp` is required; `nbf` is enforced when present. | Token Validation | MUST | Reject missing/expired/future-not-before tokens. | #1273 `authorization.go`; jwt/v5 registered claims validation | OK |
| M21 | If authorization servers are advertised, issuer must match one of them. | Token Validation / RFC 9068 | MUST in configured AS mode | Reject untrusted `iss`; self-issued deployments may omit. | #1273 `authorization.go`, `hub.go` | OK |
| M22 | `authorization_details` is an array; `mercure` details require type/actions/topics; actions only publish/subscribe. | Authorization Details / RFC 9396 | MUST | Validate all `mercure` entries; ignore non-Mercure entries. | #1273 `authorizationdetails.go`, tests | OK |
| M23 | Invalid `mercure` authorization detail rejects the whole request, no partial application. | Authorization Details | MUST | 401 invalid_token for invalid details. | #1273 `authorizationdetails.go`, `bearererror.go` | OK after follow-up |
| M24 | Authorization detail topics are object form `{match, matchType?}`; `matchType` defaults Exact and is case-sensitive. | Topic Matcher List | MUST | Reject strings/unknown types; default Exact. | #1273 `authorizationdetails.go` | OK |
| M25 | Subscribe payload is meaningful only for subscribe; first matching detail wins. | Payloads | MAY / SHOULD | Resolve payload for subscription matcher in detail order. | #1273 `authorizationdetails.go`, `subscriber.go` | OK |
| M26 | Publisher must have publish grant for update topic. | Publishers | MUST | Reject unauthorized publish with 403 insufficient_scope. | #1273 `publish.go` | OK |
| M27 | Subscriber receives private update only with subscribe grant for update topic. | Subscribers | MUST NOT | Do not dispatch private updates outside grant. | #1273 `subscriber.go`, transport matching | OK |
| M28 | Subscriber connection closes no later than token expiration. | Subscribers | MUST | Deadline bounded by `exp`. | #1273 `subscribe.go` | OK |
| M29 | Subscription events use `/.well-known/mercure/subscriptions/{matchType}/{match}/{subscriber}`, canonical `matchType`, single percent-encoding. | Subscription Events | MUST | Modern subscription IDs and JSON-LD expose match/matchType. | #1269/#1273 `subscriber.go`, `subscription.go` | OK |
| M30 | Subscription API authorizes requested subscription URL as a topic. | Subscription API | MUST | Require subscribe grant on request path. | #1273 `subscription.go` | OK |
| M31 | Protected resource metadata is served at `/.well-known/oauth-protected-resource/.well-known/mercure`. | Discovery / RFC 9728 | SHOULD | Serve JSON metadata for protected hub. | #1273 `handler.go`, `resourcemetadata.go`, `caddy/mercure.go` | OK |
| M32 | Metadata includes `resource`, `authorization_servers`, RFC 6750 bearer methods only, and cookie extension separately. | Protected Resource Metadata | SHOULD / extension | Advertise header/query, not cookie in bearer methods; use `mercure_cookie`. | #1273 `resourcemetadata.go` | OK; Question about optional `authorization_details_types_supported` |
| M33 | Access token in query is discouraged and tokens are redacted from logs. | Security / RFC 6750 | SHOULD / MUST where applicable | Redact `access_token` and legacy `authorization` query fields. | #1273 `Caddyfile`, `dev.Caddyfile` | OK |
| M34 | Cookie named `mercureAccessToken` should be Secure/HttpOnly/SameSite. | Cookie / Security | SHOULD / MUST | Default cookie name and secure attributes. | #1273 `authorization.go`, `demo.go`, docs | Partial: demo relaxes Secure/HttpOnly over HTTP for local use |
| M35 | v8 topic selectors, alternate topics, legacy claim and legacy routes are behind build tags and `protocol_version_compatibility 8`. | Compatibility | MUST for compat boundary | Modern mode rejects old behavior; compat tests cover old behavior. | #1269/#1273 `*_deprecated*.go`, tests | OK |
| M36 | Protected resource identifier is an HTTPS URL without a fragment before being published in RFC 9728 metadata. | Protected Resource Metadata / RFC 9728 | Definition / validation requirement for clients | Reject or avoid publishing invalid resource identifiers. | #1273 `hub.go`, `resourcemetadata.go`, `caddy/mercure.go` | Partial: value is required for JWT validation but not validated as an RFC 9728 URL |
