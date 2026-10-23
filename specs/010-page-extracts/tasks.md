# Tasks — 010 Show a documentation page in the page info dialog

**Branch**: `010-page-extracts` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Prototype**: [sketch.md](sketch.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. A task is done when its tests pass,
the tree is green, and the work is committed. Documentation for a behaviour lands in the task
that introduces it. No test asserts wording; elements are found by `id`, `href`, `src` and the
`mvp-sphinx-content` hook.

**The approved screens are not this build's to change.** The demo's "Info dialogs" pages, their
URLs, menu group, intro text and the "Open the full page" button were approved on 2026-10-23
(`sketch.md`, "What was ruled by eye"). The sketch's `mvp_sphinx/extracts.py` is replaced, not
extended.

Code standards for every task: no leading-underscore names anywhere; line length 88; no
compatibility aliases; docstrings per `docs/contributing/standards/code-documentation.md`; no
docstrings on tests.

## Order

**US1 → US3 → US2 → US4, sequential, in the feature worktree** (plan, *Story order*).

---

## US1 — A developer shows a documentation page in a view's info dialog (P1)

Issue: #102. Delivers FR-001 – FR-005, FR-011 – FR-013; SC-001, SC-002, SC-005.

### T001 — The fixture source and the page extract

**Files**: `tests/sphinx/extracts/**`, `tests/conftest.py`, `tests/test_extracts.py`,
`mvp_sphinx/extracts.py`, `mvp_sphinx/mounted.py`, `mvp_sphinx/views.py`

Plan, *The extract* and *Fixtures and tests*. Write the fixture source in full now. Delete the
sketch's `extracts.py` and rebuild it test-first: `PageExtract`, `SectionFinder` (page case
only is enough for this task), `plain_text`, and `DocumentationApp.page_extract` steps 2, 3
(found case), 5–8. No module-level extract function. Move `PageView.plain_text` to
`extracts.plain_text`. Tests: `TestPageExtract`, `TestExtractContent`, `TestWithoutSphinx`, the
toc-only extract being false.

### T002 — Links and images lead into the documentation app

**Files**: `tests/test_extracts.py`, `mvp_sphinx/extracts.py`

Plan, *The extract*, `LinkRewriter`. Tests: `TestExtractLinks`, every link fetched with the test
client and answering 200.

### T003 — The demo screens call the documentation app, and the documentation

**Files**: `demo/views.py`, `tests/test_demo.py`, `README.md`, `CHANGELOG.md`, `CONTEXT.md`,
`mvp_sphinx/locale/en/LC_MESSAGES/django.po`

Plan, *The demo*. Rewrite the demo views onto `docs.page_extract`, keeping every approved screen.
README: a new subsection "Showing a page somewhere else" under "Using it", with the
`page_info`/`page_info_actions` example. CHANGELOG entry. CONTEXT.md term **Page extract**.
Tests: `TestInfoDialog` (whole page, notices, action button).

## US3 — A developer's page keeps working when the documentation can't be shown (P2)

Issue: #104. Delivers FR-008 – FR-010; SC-003, SC-004.

### T004 — Reader rule, missing and broken builds, warnings

**Files**: `tests/test_extracts.py`, `tests/test_demo.py`, `mvp_sphinx/extracts.py`, `README.md`

Plan, *The extract*, steps 1 and 3. Tests: `TestReaderRule`, `TestNothingToShow` (except the
section case, which is T005's; the toc-only case is T001's), and the staff and moved screens in `TestInfoDialog`. README
subsection gains what happens when nothing can be shown.

## US2 — A developer shows one section of a page (P2)

Issue: #103. Delivers FR-006, FR-007; SC-002 for sections.

### T005 — Section extracts

**Files**: `tests/test_extracts.py`, `tests/test_demo.py`, `mvp_sphinx/extracts.py`, `README.md`

Plan, *The extract*, `SectionFinder` with an anchor, and step 8. Tests: `TestSectionExtract`, the
section screen in `TestInfoDialog`. README subsection gains sections.

## US4 — A developer offers the full page from the dialog (P3)

Issue: #105. Delivers FR-002 (address), FR-007 (section address); SC-001.

### T006 — The extract's address under any prefix

**Files**: `tests/test_extracts.py`, `README.md`

Tests: an app mounted under the test project's own prefix gives a `url` beginning with it, for a
page and for a section; two documentation apps give addresses under their own prefixes. No
production code expected: show each test can fail. README example shows the action button.

## Review fixes

### T007 — A whole page keeps everything after its title (US1)

**Files**: `mvp_sphinx/extracts.py`, `mvp_sphinx/mounted.py`, `tests/sphinx/extracts/two-parts.rst`,
`tests/test_extracts.py`

A page with two top-level sections kept only the first. The whole-page extract is now the body
less its title's heading.

### T008 — Embedded objects' addresses lead into the documentation app (US1)

**Files**: `mvp_sphinx/extracts.py`, `tests/test_extracts.py`, `README.md`

The `data` address of an `<object>`, which Sphinx uses for SVG diagrams, is rewritten like `href`
and `src`.
