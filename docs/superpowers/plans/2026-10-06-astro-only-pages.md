# Astro-only Pages Implementation Plan

> **For agentic workers:** Implement this plan task-by-task and keep the public route contract intact.

**Goal:** Remove MkDocs from the public documentation build and publish all approved research documentation through Astro only.

**Architecture:** Keep the reviewed Markdown allowlist and Astro document renderer as the source of public documentation. Move every required rendering, locale, route, link, and publication-boundary check into Astro tests or the Pages workflow, then remove the redundant MkDocs toolchain.

**Tech Stack:** Astro 7, TypeScript, Node test runner, Python 3.11/uv, pytest, GitHub Pages.

**Spec:** User-approved request in this conversation; design principles documented in `docs/superpowers/specs/2026-10-06-quant-deep-learning-independent-research-site-design.md` for the Deep Learning repository only. This plan applies to Quant Market Research's existing Astro docs renderer.

## Global Constraints

- Preserve every current public route, locale companion, heading anchor, and document allowlist.
- Do not publish internal runbooks or raw/private data.
- Deploy one `web/dist` artifact through GitHub Pages.
- Keep the checked-in Markdown as the documentation source.

## Review Focus

- Locale companions remain discoverable and navigable after removing MkDocs navigation checks.
- Old heading anchors and cross-document links keep resolving under the GitHub Pages base path.
- Public allowlisting still excludes internal material.
- Pages workflow validates and uploads only the Astro artifact.
- Local docs commands and project instructions no longer require MkDocs.

### Task 1: Replace MkDocs-specific tests with Astro publication-contract checks

**Files:** `tests/test_quality.py`, `tests/test_documentation_locales.py`, `web/src/public-docs.test.mjs`, `web/src/design-tokens.test.mjs`, `web/src/public-registry.test.mjs`, `web/scripts/verify-static-site.mjs`.

- [ ] Assert English and Chinese registry coverage and route uniqueness from the Astro public registry.
- [ ] Assert rendered public routes, anchors, assets, and allowlist boundary in the static verifier.
- [ ] Remove checks for MkDocs theme/bootstrap markup and replace them with Astro article layout and shared design-token checks.

### Task 2: Remove MkDocs build and dependencies

**Files:** `.github/workflows/pages.yml`, `web/scripts/build-pages.mjs`, `pyproject.toml`, `uv.lock`, `mkdocs.yml`, `locale_navigation.py`, `scripts/check_mkdocs_locale_navigation.py`, unused MkDocs-only overrides/assets.

- [ ] Build and verify Astro output without invoking MkDocs.
- [ ] Remove MkDocs-only dependencies/config/hooks/scripts after confirming no Astro imports them.
- [ ] Update lockfile and repository instructions.

### Task 3: Verify and publish

- [ ] Run Python tests/lint, Astro tests/build/static verification, and browser smoke tests.
- [ ] Confirm expected `/docs/` routes and search remain in `web/dist`; scan public output for private paths/secrets.
- [ ] Commit, push, and open a PR targeting `main`.
