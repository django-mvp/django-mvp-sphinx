# Tasks — 009 Make API reference pages and maths look like the rest of the site

**Branch**: `009-api-reference-and-maths` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Prototype**: [sketch.md](sketch.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. A task is done when its tests pass,
the tree is green, and the work is committed. Documentation for a behaviour lands in the task
that introduces it. No test asserts wording, spacing, type or which colour was chosen (testing
standard, spec Assumptions); elements are found by `id`, `href`, role, and the class hooks the
stylesheet or the typesetting depends on.

**The approved look is not this build's to change.** The prototype's markup, styles and demo
pages were approved on 2026-10-02 (`sketch.md`, "What was decided by eye" and "Review"). A task
that cannot be done without changing what a reader sees stops and reports it.

Several tests here describe what the approved prototype already does, and are expected to pass on
their first run. That is not a red-step failure (the FS-002 T005 precedent): they pin a state the
prototype had no test for. Every task that changes Python or the settings file has tests that
fail first.

Code standards for every task: no leading-underscore names anywhere; line length 88; no
compatibility aliases; docstrings per `docs/contributing/standards/code-documentation.md`; no
docstrings on tests.

## Order

**US1 → US3 → US2 → US4 → US5, sequential, in the feature worktree** (plan, *Story order*).

---

## US1 — Reference entries read as part of the site (P1)

Issue: #68. Delivers FR-001 – FR-004, FR-016 – FR-019 (entries), FR-020, FR-022; SC-001, SC-002,
SC-006, SC-007 for reference entries.

### T001 — The reference fixture, and the stylesheet tied to what Sphinx writes

**Files**: `tests/sphinx/reference/**`, `tests/conftest.py`,
`tests/test_static/test_content_css.py`

Plan, *Fixtures and tests*; research R6, R8. Write `tests/sphinx/reference/` in full now
(`conf.py`, `index.rst`, `api.rst`, `maths.rst`, `plain.rst`) so later tasks need no new pages,
and the `reference_build` / `reference_app` fixtures. The build must be warning-free (the
`sphinx_json_build` fixture asserts it). Tests:

- `TestSphinxHooks`: each class in the hand-kept tuple appears in a selector of the stylesheet
  and in a page body of a real build: the reference build for the hand-written hooks, the demo
  guide build for `viewcode-link`, `autosummary`, `property` and `sig-return-icon` (FR-001, D1).
  The `js:function` entry's `dt` carries `sig-object` and holds a `sig-name`, as the Python
  entries do (FR-001, edge case: another language). A hand-written entry and a generated one of
  the same kind carry the same `dt` classes (US1.8).
- `TestReferenceStylesheet`, per theme: every rule whose selector names `sig-object` and sets
  `color` is readable (≥ 4.5:1) on `--mvp-sphinx-code-bg`; every rule whose selector names
  `field-list` and sets `color` is readable on the page background and on every admonition
  background (FR-018, SC-006, US1.6). `inherit` is skipped. Assert the rule lists are not empty.

The existing literal-colour and scope tests already cover the new rules (SC-001, FR-016); do not
duplicate them.

### T002 — The demo guide's reference states, and the documentation

**Files**: `tests/test_demo.py`, `README.md`, `CHANGELOG.md`, `CONTEXT.md`, `AGENTS.md`

Tests added to `TestDemoGuideStates`, on the link-helpers page of the demo guide build, found by
`id` and class hooks: a function entry with a field list; a class entry whose `dd` holds entries
of its own, and a class nested in it holding an entry (three levels, FR-004); an entry whose `dd`
is empty (edge case); an entry holding a deprecation (US5.4 is asserted in T007; here only that
the state exists in the demo); the page links the package stylesheet and no stylesheet from the
build (FR-022, US1.7). README, under "How pages look and the page template": a short paragraph
saying reference entries are styled from the theme with nothing to configure, for any language
and however they were written. CHANGELOG Unreleased, Added: one entry. CONTEXT.md: "Reference
entry" and "Signature" (spec, Key Entities). AGENTS.md, "The demo project": the guide's Reference
part documents `demo/links.py` with autodoc, which is why `demo/docs/conf.py` puts the repository
on `sys.path`, and nothing in the site calls that module. Humanize README and CHANGELOG text
(public markdown).

---

## US3 — Point someone at one entry (P2)

Issue: #73. Delivers FR-005, FR-006 (entries), FR-007, FR-021; SC-005.

### T003 — An entry's link is named by the entry

**Files**: `mvp_sphinx/page_body.py`, `tests/test_page_body.py`, `tests/test_views.py`,
`tests/test_demo.py`, `README.md`, `CHANGELOG.md`

Plan, *The rewrite* ("The entry link's name"); research R7. Tests, on the reference build unless
said:

- `TestEntryLinks` in `tests/test_page_body.py`: the link of a top-level function is named with
  its dotted name and holds no parameter, bracket, return type or `[source]` text; the link of a
  method is named with its class's path, so the two classes' same-named methods get different
  names; the `js:function` link is named by its name; a `dt.sig-object` with no `sig-name`
  (markup written in the test) is named as before; a `dt` with `id="_CPPv43Foo"` and `sig-name`
  `Foo` (markup written in the test) is named by `Foo`, and one with two `sig-name` elements by
  its text as written; a heading's link and a glossary term's link
  are named exactly as before (the existing tests stay untouched and green); the link's `title`
  still leads the name. Every byte outside the inserted attribute is unchanged.
- `TestEntryLinks` in `tests/test_views.py`, through `client` on `reference_app`: every
  `dt.sig-object` with an `id` holds a heading link whose `href` is `#` plus that `id` (FR-005,
  US3.1); every such link has an `aria-label` (US3.3); no two heading links of the page share a
  name (SC-005); the `:py:func:` reference in a description is an `a.reference.internal` whose
  `href` fragment is an `id` on the page (FR-007, US3.5).
- `TestDemoGuideStates`: a `[source]` link in an entry of the demo guide resolves, against the
  page's address, to a page of the app that answers 200 (FR-007, US3.6).

Reveal on pointing and focus, reduced motion and clearing the top bar (US3.2, US3.4, US3.7) are
the existing heading-link rules in `content.css`, which already name `dt` and `[id]`; they are
appearance and get no new test. README: extend the `BodyRewriter` paragraph with the entry
link's name. CHANGELOG: extend the reference entry from T002.

---

## US2 — Maths is typeset in the site's theme (P1)

Issue: #71. Delivers FR-010 – FR-013, FR-016, FR-017, FR-019 (maths), FR-020; SC-003, SC-007.

### T004 — Only a page with maths loads the typesetting

**Files**: `mvp_sphinx/page_body.py`, `mvp_sphinx/views.py`,
`mvp_sphinx/templates/mvp_sphinx/page.html`, `tests/test_page_body.py`, `tests/test_views.py`

Plan, *The rewrite* ("`parse` and `has_maths`"), *The view and the template*; research R1 – R3.
Tests:

- `TestMathsDetection` in `tests/test_page_body.py`: a body with a `span.math` has maths; one
  with a `div.math` has; a body whose code sample shows `<span class="math">` as text has not; a
  class that merely starts with `math` is not a match; an empty body has not;
  `BodyRewriter.rewrite` still returns the same string as `parse(...).splice()`.
- `TestMaths` in `tests/test_views.py`, on `reference_app`: the maths page carries a script tag
  for `mvp_sphinx/maths.js` and one for the library, the settings tag first, the library tag with
  `defer` and the settings tag without it (US2.7, research R3); the plain page, whose only "maths" is inside a code
  sample, and the reference page carry neither (FR-012, US2.5, SC-007); each notation of the maths page reaches the response as written, inside an element with
  class `math` (FR-011, US2.4: this is what a reader without scripts gets); maths inside the
  note, the table cell, the list item and the heading is each inside a `.math` element (edge
  case); a page of the host outside the documentation app carries neither tag (FR-020); the
  maths page still answers with Sphinx blocked in `sys.modules` (the `TestServingWithoutSphinx`
  pattern).

Remove `?typeset=off` and its comment from `PageView.get`.

### T005 — A failed formula keeps the theme's colours, and the documentation

**Files**: `mvp_sphinx/static/mvp_sphinx/maths.js`, `mvp_sphinx/static/mvp_sphinx/content.css`,
`tests/test_static/test_content_css.py`, `tests/test_static/test_maths_js.py`, `README.md`,
`CHANGELOG.md`, `CONTEXT.md`

Plan, *The typesetting settings*, *The stylesheet* (second bullet); research R4, R8. Tests:

- `TestMathsStylesheet`, per theme: every rule whose selector names `math`, `eqno` or `mjx-` and
  sets `color` is readable (≥ 4.5:1) on the page background and on every admonition background
  (maths inside a note). Assert the rule list is not empty. Fails first on `mjx-merror`.
- `TestMathsSettings`, in a new `tests/test_static/test_maths_js.py`: every colour named in `maths.js` is a `var(--mvp-sphinx-…)` the stylesheet
  defines, and the file holds no literal colour (SC-001, FR-016); the file names `math` as the
  class to process and the content scope as the class to ignore (hooks the page depends on).
  Fails first on the missing `noundefined` colour.

If `--mvp-sphinx-code-error` is not readable on every admonition background, report it; do not
invent a colour. README: a "Maths" subsection under "Using it": typeset by MathJax, which the
reader's browser fetches from the jsDelivr CDN at the address Sphinx's own HTML build uses; only
pages with maths load it; it works for a build made with Sphinx's default settings; on a network
with no outside access, or behind a content security policy that does not allow that origin, the
reader sees the notation as written and the rest of the page is unaffected; the script runs in
the host project's own pages with the reader's session, signed-in readers included, so a host
project that does not accept a third-party script, or needs another source, overrides the
`extra_js` block of `mvp_sphinx/page.html`; a build that renders
maths as images shows the images. README "Static files": add `mvp_sphinx/maths.js`. CHANGELOG
Unreleased, Added: one entry, which says that pages with maths now load a script from
cdn.jsdelivr.net. CONTEXT.md: "Maths" (spec, Key Entities). Humanize.

---

## US4 — Long signatures and wide equations stay inside the page (P2)

Issue: #74. Delivers FR-015; SC-004.

### T006 — An equation scrolls inside a region the keyboard can reach

**Files**: `mvp_sphinx/page_body.py`, `mvp_sphinx/static/mvp_sphinx/content.css`,
`tests/test_page_body.py`, `tests/test_views.py`,
`mvp_sphinx/locale/en/LC_MESSAGES/django.po`, `README.md`, `CHANGELOG.md`

Plan, *The rewrite* ("The equation region"), *The stylesheet* (first bullet); research R5.
Tests:

- `TestEquationRegion` in `tests/test_page_body.py`: an unnumbered `div.math` has its notation
  inside one element with `role="region"`, `tabindex="0"` and an `aria-label`; a numbered one has
  the region after its `span.eqno`, which stays outside it, and the region's name holds the
  number; the notation between the region's tags is byte-for-byte what Sphinx wrote; a
  `span.math` is not wrapped; an equation inside a table sits in its own region inside the
  table's region, and the result is well nested; a number holding markup characters is escaped
  in the name; a `div.math` whose number sits inside a paragraph (markup written in the test, as
  an image renderer writes it) has the whole paragraph inside the region, well nested; removing the inserted tags gives back the original body.
- `TestWideContent` in `tests/test_views.py`, on `reference_app`: every `div.math` of the maths
  page holds exactly one focusable named region (FR-015, US4.3).

Stylesheet: move the scrolling from the typeset container to the region, as the plan describes,
keeping the approved look. `makemessages -l en` for "Equation". A long signature needs no code:
it wraps under the approved rule, and the 320-pixel check for signatures and equations (US4.1,
US4.2, US4.4, SC-004) is made in a browser at convergence (research R9). README: extend the
`BodyRewriter` paragraph with the equation region. CHANGELOG: extend the maths entry from T005.

---

## US5 — Numbered equations, deprecations and summaries (P3)

Issue: #75. Delivers FR-006 (equations), FR-008, FR-009, FR-014.

### T007 — Numbers, references, the summary table and deprecations lead where they should

**Files**: `tests/test_views.py`, `tests/test_demo.py`

No production code is expected: these pin what T003 and T006 and FS-004 already give, for the
states this story names. If one fails, fix the cause in `page_body.py` or `content.css` within
the plan. Tests:

- `TestNumberedEquations` in `tests/test_views.py`, on `reference_app`: each labelled equation's
  `div.math` has an `id`, and its number's link has that `id` as its `href` fragment and a name
  holding the number (FR-014, US5.1); the two equations' links have different names; each `:eq:`
  reference is a link whose `href` fragment is the `id` of an equation on the page (US5.2,
  FR-006).
- `TestDemoGuideStates`: every name in the summary table of the link-helpers page is a link
  whose `href` fragment is an `id` on that page, and the table sits in a scroll region (FR-008,
  US5.3); the deprecated entry's `dd` holds the `div.deprecated` FS-004 styles (FR-009, US5.4);
  the maths page of the demo guide carries both script tags and its numbered equations each hold
  a region (the demo's own states).
