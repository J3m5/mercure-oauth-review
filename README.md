# Mercure OAuth Review

This repository stores review artifacts for the Mercure OAuth 2.0 authorization work and a local Markdown mirror of the OAuth-related specifications used during the review.

## Current Status

Final review date: 2026-06-10.

This is a technical review dossier, not a conformance certification. The final pass found:

- Blocker: 0
- Major: 3
- Minor: 2
- Question: 1

Go tests passed for the reviewed worktrees, including the main compatibility-tag runs. Playwright conformance tests were prepared locally with Playwright 1.60.0. The initial E2E run failed with `400 Bad Request` because the suite still used legacy `topic` subscribe parameters; after a local adaptation to `match` / `matchURLPattern` and modern OAuth JWT authorization details, the last recorded Playwright run passed with no failed tests. The final Caddy compatibility rerun was non-conclusive because it hung without output inside the sandbox.

## Contents

- `review/`: findings-first review artifacts, normative matrix, command log, and summary.
- `oauth2-specs/`: compiled OAuth, JWT, HTTP, TLS, and related RFC references used as review source material.

## Reviewed Pull Requests

- Spec: https://github.com/dunglas/mercure/pull/1262
- Matchers: https://github.com/dunglas/mercure/pull/1269
- OAuth authorization: https://github.com/dunglas/mercure/pull/1273

## Main Artifacts

- `review/mercure-oauth-review-findings.md`
- `review/mercure-oauth-review-matrix.md`
- `review/mercure-oauth-review-commands.md`
- `review/mercure-oauth-review-summary.md`
- `review/mercure-oauth-review-plan.md`
