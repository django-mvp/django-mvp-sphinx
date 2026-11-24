# Tasks — 012 Serve documentation translated with Sphinx in the reader's Django language

**Branch**: `012-translated-docs` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. A task is done when its tests pass,
the tree is green, and the work is committed. No test asserts wording or layout. Code standards
for every task: no leading-underscore names anywhere; line length 88; no compatibility aliases;
Cotton components, never `{% include %}`; docstrings per `docs/contributing/standards/code-documentation.md`;
no docstrings on tests; test modules mirror the source tree.

## User Story 1 — A developer serves translated documentation in each reader's language (P1)

Issue: #156. Delivers FR-001 – FR-007, FR-010 – FR-012, FR-014; SC-001, SC-005, SC-006.

- [ ] T001 [US1] The language module and the translated fixture
- [ ] T002 [US1] build_docs builds each language
- [ ] T003 [US1] build_docs clears the layout it no longer writes
- [ ] T004 [US1] The documentation app serves the build for the active language
- [ ] T005 [US1] The sidebar's contents are cached per build folder
- [ ] T006 [US1] The demo and the documentation

### T001 — The language module and the translated fixture

**Files**: `tests/sphinx/translated/**`, `tests/conftest.py`, `tests/test_languages.py`, `mvp_sphinx/languages.py`, `mvp_sphinx/management/commands/build_docs.py`

Plan, *The language module*. `conf_assignments`, `conf_value`, `source_language`, `translations`,
`site_languages`. `theme_arguments` calls `conf_assignments`. Tests: `TestConf` (literal, not
literal, unreadable), `TestTranslations` (default `locales`, several `locale_dirs`, a missing
folder, no `.po`), `TestSiteLanguages` (`pt_BR` against `pt-br`).

### T002 — build_docs builds each language

**Files**: `tests/test_management/test_commands/test_build_docs.py`, `mvp_sphinx/management/commands/build_docs.py`

Plan, *build_docs*. Per-language builds with `-D language`, the source built once whether or not it
has catalogues, `pt_BR`, a skipped translation reported in one line (not when quiet), a source
`language` of German, two apps. Tests: `TestTranslatedBuilds`. Untranslated docs build straight
into `build_dir`: the existing tests pass unchanged.

### T003 — build_docs clears the layout it no longer writes

**Files**: `tests/test_management/test_commands/test_build_docs.py`, `mvp_sphinx/management/commands/build_docs.py`

Plan, *build_docs*, `clear_other_layout`. Tests: `TestClearingTheOtherLayout` (single build to
language folders, language folders to a single build, a dropped language, a rebuild keeps the
folders it rebuilds, a `build_dir` with neither is untouched).

### T004 — The documentation app serves the build for the active language

**Files**: `tests/test_languages.py`, `tests/test_mounted.py`, `mvp_sphinx/languages.py`, `mvp_sphinx/mounted.py`

Plan, *The language module*, `language_builds`, `build_for`, and `build_dir_for`. Tests:
`TestLanguageBuilds`, `TestBuildFor` (order, a build of its own wins, a function `build_dir` is
untouched, layout seen without a restart, Sphinx not importable), and a served page in each of
two languages through the test client.

### T005 — The sidebar's contents are cached per build folder

**Files**: `tests/test_menus.py`, `mvp_sphinx/menus.py`

Plan, *The menu*. Tests: `TestContentsPerBuild` (alternating languages read each build once,
a changed build is seen, a function `build_dir`, entries a project placed survive a switch).

### T006 — The demo and the documentation

**Files**: `demo/settings.py`, `demo/urls.py`, `demo/docs/conf.py`, `demo/docs/locales/de/**`, `tests/test_demo.py`, `README.md`, `CHANGELOG.md`, `CONTEXT.md`, `mvp_sphinx/mounted.py`

Plan, *The demo*. The README's translated-documentation section (workflow, layout, how a reader's
build is chosen, fallback order), CHANGELOG entry, CONTEXT.md term **Language build**, the
`DocumentationApp` docstring. Tests: `TestTranslatedGuide` (the demo's guide in German and
English reaches the right build).

## User Story 2 — A reader reads the documentation in the language they use for the site (P1)

Issue: #157. Delivers FR-009, FR-013 (FR-008's order lands in T004); SC-002 – SC-004.

- [ ] T007 [US2] The package's own strings in German
- [ ] T008 [US2] Every part of the app follows the language
- [ ] T009 [US2] The fallback for a reader with no build

### T007 — The package's own strings in German

**Files**: `mvp_sphinx/locale/de/LC_MESSAGES/django.po`, `django.mo`, `tests/test_locale.py`, `pyproject.toml`, `uv.lock`

Plan, *The package's own strings*. `babel` joins the dev group and `tests/test_locale.py` the conformance list of tests that do not mirror a module. Tests: `TestGermanCatalogue` (the message ids match the English catalogue, each is translated, the
`.mo` matches the `.po`), and a project's `LOCALE_PATHS` translation wins over the package's.

### T008 — Every part of the app follows the language

**Files**: `tests/test_mounted.py`, `tests/test_views.py`, `tests/test_search.py`, `tests/test_extracts.py`

Spec US2 scenarios 1 to 6 and 11. Tests: pages, files (image and download), search (German
stemming finds the page and the English reader does not), the extract, the contents branch address and the site search kind in German, an anchor reaching the same
section in each language, an untranslated paragraph kept in the source language, the language
changed between two requests.

### T009 — The fallback for a reader with no build

**Files**: `tests/test_mounted.py`

Spec US2 scenarios 7 to 9. Tests through the test client: `de-at` served from German, an Italian
reader served from the `LANGUAGE_CODE` build, then from the source language build when that has
none.
