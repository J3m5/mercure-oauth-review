# Plan de Review - OAuth 2.0 dans Mercure

## Resume

Objectif : reviewer la conformite et la securite de l'implementation OAuth 2.0 de Mercure par rapport a la spec mise a jour.

PRs concernees :

- Spec : https://github.com/dunglas/mercure/pull/1262
- Matchers : https://github.com/dunglas/mercure/pull/1269
- OAuth 2.0 : https://github.com/dunglas/mercure/pull/1273

Ordre de review retenu :

1. Valider la spec `#1262`.
2. Reviewer les matchers `#1269`, base technique de `#1273`.
3. Reviewer OAuth `#1273`.
4. Faire une passe transversale spec vs implementation vs docs vs tests.

## Strategie

La review doit etre menee comme une review de conformite normative et de securite, pas comme une simple lecture de diff.

Approche :

- Extraire de `spec/mercure.md` une matrice des exigences normatives : `MUST`, `MUST NOT`, `SHOULD`, erreurs HTTP, formats de tokens, metadata, regles de compatibilite.
- Mapper chaque exigence vers l'implementation correspondante.
- Classer les ecarts en `Blocker`, `Major`, `Minor`, `Question`.
- Separer les ecarts volontaires ou documentes, par exemple le follow-up RFC 8414 annonce dans `#1273`, des ecarts accidentels.
- Ne poster aucun commentaire GitHub sans validation explicite.

References normatives a utiliser :

- RFC 9068 - JWT Profile for OAuth 2.0 Access Tokens : https://www.rfc-editor.org/rfc/rfc9068.html
- RFC 9396 - OAuth 2.0 Rich Authorization Requests : https://www.rfc-editor.org/rfc/rfc9396.html
- RFC 6750 - Bearer Token Usage : https://www.rfc-editor.org/rfc/rfc6750.html
- RFC 9728 - OAuth 2.0 Protected Resource Metadata : https://www.rfc-editor.org/rfc/rfc9728.html
- RFC 8725 - JSON Web Token Best Current Practices : https://www.rfc-editor.org/rfc/rfc8725.html
- RFC 8414 - OAuth 2.0 Authorization Server Metadata : https://www.rfc-editor.org/rfc/rfc8414.html
- WHATWG URLPattern : https://urlpattern.spec.whatwg.org/

Copies locales utilisees pour la passe finale :

- `oauth2-specs/rfc9068-json-web-token-jwt-profile-for-oauth-2-0-access-tokens.md`
- `oauth2-specs/rfc9396-oauth-2-0-rich-authorization-requests.md`
- `oauth2-specs/rfc6750-the-oauth-2-0-authorization-framework-bearer-token-usage.md`
- `oauth2-specs/rfc9728-oauth-2-0-protected-resource-metadata.md`
- `oauth2-specs/rfc8725-json-web-token-best-current-practices.md`
- `oauth2-specs/rfc8414-oauth-2-0-authorization-server-metadata.md`

## Plan de Review

### 1. Preparation

- Creer ou utiliser des worktrees separes pour eviter les bascules destructrices :
  - `spec/oauth-authz`
  - `origin/feat/matchers`
  - `origin/feat/oauth-authz`
- Recuperer les metadonnees PR avec `gh pr view`.
- Recuperer les diffs frais avec `gh pr diff`.
- Diagnostiquer les checks echoues de `#1262` et `#1269`.
- Noter l'etat initial :
  - `#1262` : branche `spec/oauth-authz`, base `main`, 1 fichier modifie.
  - `#1269` : branche `feat/matchers`, base `main`, draft.
  - `#1273` : branche `feat/oauth-authz`, base `feat/matchers`, draft.

### 2. Review de la spec `#1262`

Controler en priorite :

- Coherence interne des nouvelles notions : topic unique, matchers, OAuth protected resource, access token, authorization details.
- Coherence des noms :
  - subscribe query params : `match`, `matchExact`, `matchURLPattern`
  - publish field : `topic`
  - authorization details : `topics`, `match`, `matchType`
- Regles d'autorisation :
  - routing separe de l'autorisation
  - publish autorise sur le topic publie
  - subscribe autorise sur le topic de l'update
  - replay autorise avec le scope actuel
  - subscription API autorisee comme topic
- Regles d'erreur :
  - `400 invalid_request`
  - `401 invalid_token` ou challenge sans erreur quand aucun token
  - `403 insufficient_scope`
- Contraintes de securite :
  - rejet C0/C1/DEL
  - wildcard `*`
  - namespace reserve `/.well-known/mercure/`
  - limites anti-DoS
  - cookies `Secure`, `HttpOnly`, `SameSite`
  - fuite de tokens dans URLs/logs
- Discovery OAuth :
  - resource metadata RFC 9728
  - `resource`
  - `authorization_servers`
  - `bearer_methods_supported`
  - extension `mercure_cookie`

Livrable : une matrice spec contenant exigence, section, niveau normatif, comportement attendu, PR/fichiers d'implementation, statut.

### 3. Review de `#1269` - Matchers

Controler :

- `Exact` :
  - comparaison exacte byte-for-byte
  - pas de normalisation implicite
  - pas de resolution relative
- `URLPattern` :
  - base URL du hub pour les patterns/topics relatifs
  - `ignoreCase` desactive
  - erreurs de parsing correctement traitees
  - cache borne
  - cout d'evaluation maitrise
- Subscribe query params :
  - `match`
  - `matchExact`
  - `matchURLPattern`
  - rejet des noms invalides dans le namespace `match*`
  - rejet de l'ancien `topic` hors compat v8
- Wildcard :
  - `*` reconnu avant resolution de `matchType`
  - un topic exactement egal a `*` n'est pas adressable isolement
- Publication :
  - un seul `topic`
  - plus de alternate topics en mode moderne
  - rejet du namespace reserve
- Compatibilite v8 :
  - comportements legacy derriere `deprecated_topic`
  - actives uniquement avec `protocol_version_compatibility 8`
  - stubs surs sans le build tag
- Subscription API :
  - routes modernes avec `{matchType}/{match}/{subscriber}`
  - encodage correct
  - `matchType` canonique
  - rejet des types inconnus

Tests a verifier ou demander :

- match exact positif/negatif
- URLPattern positif/negatif
- wildcard
- controles C0/C1/DEL
- trop de matchers
- pattern trop long
- ancien `topic` hors compat
- compat v8 avec et sans build tag

### 4. Review de `#1273` - OAuth 2.0

Controler :

- Validation JWT RFC 9068 :
  - token signe
  - rejet `alg: none`
  - allowlist d'algorithmes explicite
  - `typ` accepte pour `at+jwt` et `application/at+jwt`
  - `aud` obligatoire et compare au resource identifier
  - `iss` valide si `authorization_servers` est configure
  - `exp` obligatoire
  - `nbf` respecte
  - separation des cles publisher/subscriber si applicable
- `authorization_details` RFC 9396 :
  - claim tableau
  - type `mercure`
  - `actions` limite a `publish` / `subscribe`
  - `topics` non vide
  - `matchType` optionnel avec defaut `Exact`
  - rejet total si un detail `mercure` est invalide
  - limites cumulatives sur details/topics/patterns
  - payload uniquement pour subscribe
  - premier payload correspondant gagne
- Presentation du token :
  - `Authorization: Bearer`
  - query `access_token`
  - cookie `mercureAccessToken`
  - priorite header > query > cookie
  - ancien query param `authorization` uniquement en compat
- Erreurs RFC 6750 :
  - aucun token : challenge `WWW-Authenticate: Bearer`, sans code d'erreur
  - token invalide : `401 invalid_token`
  - scope insuffisant : `403 insufficient_scope`
  - requete malformee : `400 invalid_request`
  - presence de `resource_metadata` dans le challenge quand pertinent
- Metadata RFC 9728 :
  - endpoint `/.well-known/oauth-protected-resource/.well-known/mercure`
  - `resource_identifier` valide comme URL HTTPS sans fragment
  - `resource`
  - `authorization_servers`
  - `bearer_methods_supported` limite aux methodes RFC 6750
  - `mercure_cookie` comme extension dediee
  - decision explicite sur `authorization_details_types_supported`
- Compatibilite v8 :
  - legacy `mercure` claim derriere `deprecated_claim`
  - ancien cookie derriere compat si prevu
  - interaction correcte avec `deprecated_topic`
  - rejet sur quand les build tags ne sont pas presents
- Integration Caddy/Go :
  - `resource_identifier`
  - `authorization_servers`
  - algorithmes JWKS configurables
  - redaction des tokens dans les logs
  - defaults documentes et surs

Tests a verifier ou demander :

- tokens sans `typ`, mauvais `typ`, mauvais `aud`, mauvais `iss`, expires, `nbf` futur
- algorithmes non autorises
- JWKS avec algorithme inattendu
- authorization details invalides
- absence de droits publish/subscribe
- token via header/query/cookie et priorite
- metadata OAuth
- compat v8 avec/sans build tags
- non-regression des tests existants

### 5. Passe Transversale

Controler que les artefacts suivants racontent le meme protocole :

- spec
- code hub
- module Caddy
- `docs/UPGRADE.md`
- `docs/hub/config.md`
- `Caddyfile`
- `dev.Caddyfile`
- demo UI
- conformance tests

Points de coherence a verifier :

- `topic` n'est plus un subscribe matcher moderne.
- `match` est le subscribe matcher moderne par defaut.
- `access_token` remplace l'ancien parametre `authorization`.
- `mercureAccessToken` est le cookie recommande.
- `resource_identifier` est necessaire pour `aud`.
- les anciens comportements sont clairement limites a la compat v8.
- les breaking changes sont documentes avec migration claire.

## Validation

Execution recommandee, apres installation ou telechargement des dependances si necessaire :

- `go test ./...`
- `go test -tags deprecated_topic,deprecated_claim ./...`
- tests Caddy du sous-module `caddy`
- conformance tests si l'environnement Node est disponible
- checks cibles sur les tests modifies dans `authorization`, `authorizationdetails`, `bearererror`, `resourcemetadata`, `matcherclaim`, `subscribematchers`, `topicselector`, `subscription`

Si le sandbox bloque le telechargement des dependances, demander l'autorisation d'executer les commandes necessaires avec acces reseau.

## Format du Rapport Final

Le rapport de review devra etre findings-first :

- `Blocker` : faille de securite, divergence normative forte, comportement dangereux.
- `Major` : incompatibilite spec, regression fonctionnelle, breaking change mal encadre.
- `Minor` : documentation, test manquant, incoherence faible.
- `Question` : decision de design a confirmer.

Chaque finding doit contenir :

- PR concernee
- fichier et ligne si possible
- exigence spec ou RFC concernee
- impact
- correction proposee
- test attendu

Aucun commentaire ne sera publie sur GitHub sans validation explicite.
