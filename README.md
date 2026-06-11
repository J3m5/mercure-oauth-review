# Mercure OAuth Review

This repository stores review artifacts for the Mercure OAuth 2.0 authorization work and a local Markdown mirror of the OAuth-related specifications used during the review.

## Current Status

Final review date: 2026-06-10. Follow-up after maintainer commits: 2026-06-11.

This is a technical review dossier, not a conformance certification. The 2026-06-11 follow-up found:

- Blocker: 0
- Major: 0
- Minor: 1 remaining partial item
- Question: 0

Kevin's latest commits address the three Major findings, the mixed-case `application/at+jwt` Minor finding, and the metadata question. The remaining partial item is `resource_identifier`: it now rejects non-URL and fragment-bearing values, but still publishes non-HTTPS resource identifiers with only a warning. Go tests pass on #1273 at `0a415e4`, including compatibility-tag and Caddy runs. #1262 and #1269 GitHub checks pass; #1273 still only exposes `license/cla` through `gh pr checks`.

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
