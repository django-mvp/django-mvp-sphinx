# Tasks — 008 Show working examples live next to their source code

**Branch**: `008-live-examples` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Prototype**: [sketch.md](sketch.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. A task is done when its tests pass,
the tree is green, and the work is committed. Documentation for a behaviour lands in the task
that introduces it. No test asserts wording, spacing, type or colour (testing standard, spec
Assumptions); elements are found by tag, `id`, `name`, `href`, `src`, role and the class hooks
the stylesheet depends on.

**The approved look is not this build's to change.** The component's markup, `example.css`, the
copy and the two demo pages were approved on 2026-10-02 (`sketch.md`, "What was ruled by eye"). A
task that cannot be done without changing what a reader sees stops and reports it.

**The prototype's Python is not kept on trust.** `mvp_sphinx/live_example.py` and
`mvp_sphinx/examples.py` arrived before any test. Each task writes the tests first and rebuilds
the code it covers to pass them; the prototype is a reference, not a base. Where a test describes
something the approved markup already does and passes on its first run, that is not a red-step
failure (the FS-002 T005 precedent), and the task shows the test can fail by breaking one thing
and restoring it.

**The demo guide builds under `-W` in the existing suite.** A task that changes what the
directive accepts or writes updates `demo/docs/examples/*.rst` in the same commit, so the tree is
green at every commit.

Code standards for every task: no leading-underscore names anywhere; line length 88; no
compatibility aliases; docstrings per `docs/contributing/standards/code-documentation.md`; no
docstrings on tests.

## Order

**US1 → US2 → US3, sequential, in the feature worktree** (plan, *Story order*).

---

## US1 — See an example running beside its source (P1)

Issue: #69. Delivers FR-001 – FR-003 (same-site address accepted), FR-004 (one source), FR-005,
FR-006, FR-009, FR-010, FR-014; SC-001, SC-005.

### T001 — The marker writes an example into the docs build

**Files**: `mvp_sphinx/live_example.py`, `mvp_sphinx/examples.py` (the shared names only),
`tests/sphinx/examples/**`, `tests/conftest.py`, `tests/test_live_example.py`

Plan, *The build side*, *Fixtures and tests*; research R2, R3, R5, R9. Write
`tests/sphinx/examples/` in full now, with every page the plan lists, so later tasks add no page:
pages that later tasks need may hold markers this task does not yet test, but the build must be
warning-free (the `sphinx_json_build` fixture asserts it), so the page naming a line range is
written here and line ranges keep working as the prototype has them. Add the `examples_build` and
`examples_app` fixtures. Tests in `tests/test_live_example.py`, reading the built `.fjson` bodies:

- the page's body holds one element with the example class, whose `data-address` is the address
  written and whose `data-title` is the title written (FR-001, US1.1);
- the example holds one source element whose `data-name` is the file's name, and the text inside
  its `pre` (tags removed, entities decoded) is the file's text (US1.2, SC-003);
- the source's highlight wrapper carries the same classes as a `code-block:: python` on the same
  page (FR-005, US2.3);
- a source whose text holds `<`, `&` and `{% tag %}` reaches the body escaped and decodes to the
  file's text (US1.2, edge case);
- a `.html` source is highlighted as a Django template and a file with no known language as text
  (research R5);
- an example with no `:title:` writes an empty title;
- the fixture's `conf.py` names one extension and nothing else about examples (FR-002, US1.3);
- the example sits between the two paragraphs it was written between (FR-010, US1.6).

`LiveExamples` gains the constants for the class names and attribute names, and the directive
imports them. Run `uv run deptry .` and confirm the Pygments import raises nothing; if it does,
record why and use the mapping the prototype had.

### T002 — The served page shows the example, and an example's page has no shell

**Files**: `mvp_sphinx/examples.py`, `mvp_sphinx/views.py`,
`mvp_sphinx/templates/mvp_sphinx/page.html`, `mvp_sphinx/templates/mvp_sphinx/example.html`
(new), `mvp_sphinx/templates/mvp_sphinx/base.html` (deleted),
`mvp_sphinx/templates/cotton/mvp_sphinx/live_example.html`, `demo/templates/base.html`,
`demo/templates/demo/examples/*.html`, `demo/examples/views.py`, `tests/test_examples.py`,
`tests/test_views.py`

Plan, *The serving side*, *The component, the stylesheet and the base template*, *The demo*;
research R1, R2, R6. Tests:

- `TestParts` in `tests/test_examples.py`, on markup written in the test: a body without the
  marker class is one markup part holding the body byte for byte; a body with one example is
  markup, example, markup, and joining the markup parts with the example's original text gives
  back the body; the example carries its address, title and sources in order, each source's
  markup byte for byte; a nested `div` inside a source does not end it early; two examples get
  different ids; an example whose wrapper never closes is left in the page as markup; an address
  the urlconf has is available and one it does not have is not; an address on another site
  (`//host/`, `https://host/`) is not available.
- `TestLiveExamples` in `tests/test_views.py`, through `client` on `examples_app`: the page
  answers 200 and holds one `iframe` whose `src` is the example's address, a path on the same
  site (US1.1); the frame has a `title`; the source's text is in the response (US1.2); the
  example sits between the two paragraphs (US1.6); the page's sidebar contents and its
  "On this page" list are the same as the plain page's contents and as its own headings without
  the example (FR-010, US1.6); the page with two examples holds two frames with different `name`
  attributes (US1.7, FR-010); the page links `example.css` and the plain page does not (FR-017);
  the plain page's article is exactly the rewritten body; the page still answers with Sphinx
  blocked in `sys.modules` (the `TestServingWithoutSphinx` pattern; US1.8, SC-005).
- `TestExamplePage` in `tests/test_views.py`: the demo's contact example, requested at its own
  address, answers 200 with the form and without the shell's sidebar menu, while the overview
  page, through the same `base.html`, has it (FR-009, US1.5); sent invalid, it answers with the
  form's errors and still no sidebar menu; sent valid, it redirects to its own address, and the
  page it redirects to carries the message (US1.4, the part a server can show).

Delete `LiveExamples.FRAMED`, `framed_address` and `mvp_sphinx/base.html`. The demo's
`base.html` extends `mvp/base.html` and loses the prototype's comment. The demo's example
templates extend `mvp_sphinx/example.html` and fill `content`; keep what each example shows.
`ContactView` redirects to `request.path`.

### T003 — The documentation for a live example

**Files**: `README.md`, `CHANGELOG.md`, `CONTEXT.md`, `AGENTS.md`, `mvp_sphinx/navigation.py`
(docstring), `mvp_sphinx/locale/en/LC_MESSAGES/django.po`

No test. README, a "Live examples" section under "Using it": what one is; the marker with its
address, optional title and one source file; writing the example's page on
`mvp_sphinx/example.html`, with a short template, and that a page with the shell shows with the
shell; the setup step, `X_FRAME_OPTIONS = "SAMEORIGIN"`, with the reason, that it covers the
sign-in and error pages, and the `frame-ancestors` note (research R7); that the source is a copy
made at build time and a rebuild refreshes it; that the host's own rule for the address decides
who sees the example. README "Static files": add `mvp_sphinx/example.css`. CHANGELOG Unreleased,
Added: one entry. CONTEXT.md: "Live example" and "Example source" (spec, Key Entities), with
their `_Avoid_` lines. AGENTS.md and the `navigation.py` docstring: two modules import Sphinx,
the extension and the directive it registers (research R9); the demo's example views.
`makemessages -l en`. Humanize README and CHANGELOG text (public markdown).

---

## US2 — Read the code that makes the example (P2)

Issue: #70. Delivers FR-004 (several sources, parts), FR-007, FR-008, FR-016.

### T004 — Several sources, a part of a file, and names a reader can tell apart

**Files**: `mvp_sphinx/live_example.py`, `tests/test_live_example.py`, `tests/test_views.py`,
`README.md`, `CHANGELOG.md`

Plan, *The build side* ("Sources", "Names and languages"); research R3, R4. Tests:

- in `tests/test_live_example.py`, on the built fixture: the example with three sources holds
  three source elements in the author's order (US2.1); the source named with a range holds
  exactly those lines of the file, dedented, and a single line number holds that line (US2.2,
  SC-003); a path with a space in it and no range is read as a path;
- naming, on small sources built in the test: two files of the same name in different folders
  get names that differ and each ends with the file's name; the same file named twice with
  different ranges gets names that differ; a file named once keeps its bare name (US2.1);
- `TestLiveExamples` in `tests/test_views.py`: the page shows one radio input per source, in one
  group per example, the first checked, each labelled with its source's name; a single source
  shows no radio input; two examples on a page use different group names (US2.1, US1.7).

README: extend the marker's description with several files and line ranges, and how sources are
named. CHANGELOG: extend the entry from T003.

### T005 — Start again, and open on its own

**Files**: `tests/test_views.py`, `mvp_sphinx/templates/cotton/mvp_sphinx/live_example.html`
(only if a test shows a fault), `README.md`

Plan, *The component*. Tests in `TestLiveExamples`: each available example has one link whose
`target` is its own frame's `name` and whose `href` is its address (FR-007, US2.4); it has one
link to its address with no `target` (FR-008, US2.5); on the page with two examples each
"Start again" names its own frame; the component holds no `script` element and no inline event
handler, so both controls and the tabs work with scripts off (FR-015 is asserted in T007; this
is the markup it rests on).

That "Start again" returns the frame without reloading the page (US2.4), and that nothing
scrolls sideways at 320 pixels (US2.6, FR-016), are checked in a browser at convergence
(research R10). README: one sentence on the two controls.

---

## US3 — The page holds up when an example can't be shown (P3)

Issue: #72. Delivers FR-003 (refusal), FR-011 – FR-013, FR-015, FR-017, FR-018; SC-004.

### T006 — The build reports a marker it cannot use

**Files**: `mvp_sphinx/live_example.py`, `tests/test_live_example.py`, `README.md`

Plan, *The build side* ("Address", "Sources"). Tests, each building a small source written in
the test with `sphinx_build` and reading the warnings:

- a source file that does not exist: the build warns, the warning names the page and the file,
  and the example is written with its other sources (FR-013, US3.4);
- an example whose only source does not exist: the build warns and the page holds no example;
- an example with no source lines at all: the same (FR-004);
- an address on another site, in each of these shapes: `https://host/x`, `//host/x`, `/\host/x`,
  `host/x`, and one holding a space: the build warns, and the built page holds no example
  element and no address of that site (FR-003, US3.5);
- a range that is reversed, not a number, or past the end of the file: the build warns, naming
  the file, and that source is left out;
- under `-W` any of these fails the build.

README: what the build reports and that `-W` turns each into a failure.

### T007 — The served page holds up

**Files**: `mvp_sphinx/examples.py` (only if a test shows a fault), `tests/test_views.py`

Plan, *The serving side*, *Security*. Tests through `client`, on `examples_app` unless said:

- `TestUnavailableExample`: the page naming an address the site does not have answers 200, holds
  no `iframe` for that example and no link to its address, holds an element with `role="alert"`
  in the example's place, and still holds the source (FR-012, US3.1, SC-004);
- a docs build whose body names an address on another site (a `.fjson` written in the test)
  serves the page with no `iframe` (FR-003, research R6);
- `TestRefusedExample`: the page naming the staff-only example answers 200 to an anonymous
  reader and to a regular user, with the source and with nothing of the example's own content;
  the example's address answers each of them exactly as it does with no documentation page
  involved (FR-011, US3.2);
- the page naming the failing example answers 200 (FR-012, US3.3);
- `TestReaderRule`, on a documentation app whose reader rule excludes the reader: a page with an
  example gives what the rule gives for any page, and the response holds none of the source
  (FR-011, US3.8);
- `TestRebuild`: rewrite the page's `.fjson` in a copy of the build with a changed source, and
  the next request shows the new code, with no restart (FR-014, US3.7);
- `TestWithoutScripts`: a page with an example holds the source, a frame and a plain link to the
  example's address, and nothing in the page's article depends on a script (FR-015, US3.6);
- a build made without the extension's directive in use (the existing `guide_build`) serves each
  page with no example stylesheet and its article exactly the rewritten body (FR-017, US3.9).

### T008 — The demo guide shows every state

**Files**: `demo/docs/examples/*.rst`, `demo/examples/**`, `demo/templates/demo/examples/*`,
`tests/test_demo.py`, `AGENTS.md`, `CHANGELOG.md`

Tests added to `TestDemoGuideStates`, on the two pages of the demo guide build: for every example
in the guide, each source shown is the named file's text, or the named lines of it (SC-003); the
working-form page holds two examples, one with three sources and one with a single source that is
part of a file (screens 1, 3, 8); the cannot-run page holds a frame for the slow example, the
staff-only example and the failing example, and the notice for the one whose address is gone
(screens 5, 6, 7); every example's page in the demo, requested on its own, has no sidebar menu
(FR-009); the contact example answers a valid and an invalid post (SC-002, the part a server can
show); both pages answer 200 to an anonymous reader (SC-004). Screens 2, 4 and 9 are the narrow
layout, the used example and scripts off: they are reached on these same pages and are checked
in a browser at convergence (research R10).

The slow example's view is not requested by any test. AGENTS.md, "The demo project": the example
views, why the demo sets `X_FRAME_OPTIONS`, and that line ranges in the two pages must follow
edits to the files they name. CHANGELOG: finish the entry.
