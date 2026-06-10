# Mercure OAuth 2.0 Review Commands

All commands were run from `/home/jeremy/workspace/development/tilleuls/dunglas` unless noted.

## Setup and PR state

```bash
git -C mercure status --short --branch
git -C mercure worktree list --porcelain
git -C mercure remote -v
git -C mercure branch --list --all 'spec/oauth-authz' 'feat/matchers' 'feat/oauth-authz' 'origin/spec/oauth-authz' 'origin/feat/matchers' 'origin/feat/oauth-authz'
git -C mercure rev-parse --verify origin/feat/matchers
git -C mercure rev-parse --verify origin/feat/oauth-authz
git -C mercure rev-parse --verify origin/spec/oauth-authz
gh auth status
git fetch origin spec/oauth-authz feat/matchers feat/oauth-authz
git worktree add --detach ../mercure-feat-matchers origin/feat/matchers
git worktree add --detach ../mercure-feat-oauth-authz origin/feat/oauth-authz
gh pr view 1262 -R dunglas/mercure --json number,title,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,reviewDecision,files,url
gh pr view 1269 -R dunglas/mercure --json number,title,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,reviewDecision,files,url
gh pr view 1273 -R dunglas/mercure --json number,title,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,reviewDecision,files,url
git -C mercure-feat-matchers diff --name-status origin/main...HEAD
git -C mercure-feat-oauth-authz diff --name-status origin/feat/matchers...HEAD
gh pr checks 1262 -R dunglas/mercure
gh pr checks 1269 -R dunglas/mercure
gh pr checks 1273 -R dunglas/mercure
gh run view 27215984684 -R dunglas/mercure --job 80357447002 --log-failed
gh run view 27215984684 -R dunglas/mercure --job 80357446822 --log-failed
gh run view 27215984008 -R dunglas/mercure --job 80357444570 --log-failed
gh run view 27215984008 -R dunglas/mercure --job 80357444744 --log-failed
```

Notes:

- Initial `git fetch` required network escalation because sandbox DNS blocked `github.com`.
- `mercure` was already the `spec/oauth-authz` worktree.
- `mercure-feat-matchers` and `mercure-feat-oauth-authz` were created as detached worktrees from remote refs; no PR branch was modified.

GitHub check diagnosis:

- #1262 `Lint` fails on `publish_test.go:503` and `publish_test.go:517` with testifylint `error-is-as` (`assert.ErrorIs` expected). This is not introduced by the spec-only file diff.
- #1262 `Test (1.26)` times out during `npx playwright install` after downloading Chrome for Testing; conformance tests do not start.
- #1269 `Lint` fails on `subscribematchers.go:116` with exhaustive missing `deprecatedMatcherTypeName`.
- #1269 `Test (1.26)` times out during `npx playwright install` after downloading Chrome for Testing; conformance tests do not start.
- #1273 currently reports only `license/cla` as passing via `gh pr checks`.

## Spec and code inspection

```bash
rg -n '\b(MUST|MUST NOT|SHOULD|SHOULD NOT|MAY|REQUIRED|OPTIONAL|RECOMMENDED)\b|invalid_request|invalid_token|insufficient_scope|WWW-Authenticate|OAuth|authorization_details|URLPattern|matchExact|matchURLPattern|mercureAccessToken|resource_metadata|well-known|C0|C1|DEL|deprecated|compat' spec/mercure.md
rg -n '^#{1,6} ' spec/mercure.md
nl -ba authorization.go
nl -ba authorizationdetails.go
nl -ba bearererror.go
nl -ba resourcemetadata.go
nl -ba hub.go
nl -ba caddy/mercure.go
nl -ba handler.go
nl -ba topicselector.go
nl -ba subscribematchers.go
nl -ba publish.go
nl -ba subscribe.go
nl -ba subscriber.go
nl -ba subscription.go
rg -n 'JWKS|jwks|algorithms|WithPublisherJWTAlgorithms|WithSubscriberJWTAlgorithms|none|RS256|HS256|ES256|EdDSA|authorization_servers|resource_identifier|metadata|public_url' caddy/caddy_test.go caddy/*.go docs/UPGRADE.md docs/hub/config.md Caddyfile dev.Caddyfile
rg -n 'topicURLPattern|topic\)|topic=|searchParams\.append\("topic|matchURLPattern|matchExact|access_token|authorization|mercureAccessToken|mercureAuthorization|resource_identifier|authorization_servers|public_url|deprecated' public demo.go docs Caddyfile dev.Caddyfile conformance-tests
```

External normative references consulted:

- RFC 9068: https://www.rfc-editor.org/rfc/rfc9068.html
- RFC 9396: https://www.rfc-editor.org/rfc/rfc9396.html
- RFC 6750: https://www.rfc-editor.org/rfc/rfc6750.html
- RFC 9728: https://www.rfc-editor.org/rfc/rfc9728.html
- WHATWG URLPattern: https://urlpattern.spec.whatwg.org/

## Test execution

First attempts without cache override failed because Go tried to write modules under `/home/jeremy/go/pkg/mod`, which is read-only in the sandbox:

```bash
go test ./...
```

Then tests were run with writable caches:

```bash
env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test ./...
```

Results:

- #1269 worktree `mercure-feat-matchers`: PASS
  - `ok github.com/dunglas/mercure 1.049s`
  - `ok github.com/dunglas/mercure/common 0.004s`
- #1273 worktree `mercure-feat-oauth-authz`: PASS
  - `ok github.com/dunglas/mercure 1.040s`
  - `ok github.com/dunglas/mercure/common 0.004s`

Compatibility tests:

```bash
env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test -tags deprecated_topic,deprecated_claim ./...
```

Result on #1273:

- PASS
  - `ok github.com/dunglas/mercure 1.046s`
  - `ok github.com/dunglas/mercure/common (cached)`

Caddy tests:

```bash
cd mercure-feat-oauth-authz/caddy
env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test ./...
env GOMODCACHE=/tmp/mercure-gomodcache GOCACHE=/tmp/mercure-gocache go test -tags deprecated_topic,deprecated_claim ./...
```

Results:

- Standard Caddy tests: PASS
  - `ok github.com/dunglas/mercure/caddy 1.097s`
  - `? github.com/dunglas/mercure/caddy/mercure [no test files]`
- Caddy compatibility tests: PASS after running outside sandbox because the sandbox blocked opening `127.0.0.1:2999`
  - `ok github.com/dunglas/mercure/caddy 1.132s`
  - `? github.com/dunglas/mercure/caddy/mercure [no test files]`

Conformance tests:

```bash
find conformance-tests -maxdepth 2 -type f -printf '%p\n'
ls -la conformance-tests
sed -n '1,220p' conformance-tests/package.json
sed -n '1,220p' conformance-tests/playwright.config.ts
sed -n '1,220p' conformance-tests/mercure.spec.ts
ls -la conformance-tests/node_modules
```

Result:

- Not executed.
- There is no `node_modules` directory and no package script.
- The suite assumes an external running hub via `BASE_URL`.
- Static inspection found it still uses legacy `topic` / `topicURLPattern`, which is captured as a Major finding.
