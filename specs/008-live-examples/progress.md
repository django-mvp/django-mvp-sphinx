# Progress — 008 Show working examples live next to their source code

## 2026-10-02T15:58:33Z · S3 plan

Did: the queue row read in-flight on this session's own claim. The build continues on pull request
#67 and its branch, merged with origin/main (ddcbfc1, which carries FS-009; one conflict in
`mvp_sphinx/views.py`, both sides kept; 678 passed). The specification was read against FS-009,
delivered since: no contradiction (research). Gates: spec shut and passed (Sam, 2026-10-02, commit
a76abb8), sketch shut and passed (Sam, 2026-10-02, commit e244c12), plan open, merge shut.
The earlier run's research had stopped for a decision on how a page shows without the shell. Sam
decided it in the session: an example's page is written without the shell (D11). The
specification's FR-008 and FR-009 were reworded with his approval. research.md completed (R1 to
R10), plan.md and tasks.md written: 3 stories, 8 tasks. Decisions D11 to D16 appended, and every
decision carries its ADR verdict.
Analyze: FR-001 to FR-018 and SC-001 to SC-005 each map to a task or, where only a browser can
show it (US1.4 and SC-002 inside the frame, US2.4, US2.6 and FR-016 at 320 pixels, the dark
theme), to the browser check at convergence (research R10). Every item under "What the prototype
faked" has a task or is kept on purpose (plan, table). No CRITICAL findings.
Next: design review.

## 2026-10-02T16:05:07Z · S3R design review

Did: one reviewer, three lenses, on plan.md, tasks.md and research.md at 8a4caee. Verdict approve:
no critical or high finding, one medium and four low, all verified. Each was applied as an edit to
the plan or the tasks and checked against the finding's own evidence (ledger, gates.design_review).
The reviewer confirmed by running them that a raw HTML node reaches a JSON build's page body, that
`mvp/base.html` draws the messages inside the `app` block, and that `uv run deptry .` fails today
on the prototype's docutils import.
Next: build US1.

## 2026-10-02T16:12:00Z · Implementer US1 · T001

Did: wrote `tests/sphinx/examples/` (conf with the one extension line; pages `single`, `two`,
`several`, `missing`, `plain` and an index; sources beside them) and the `examples_build` and
`examples_app` fixtures; wrote `tests/test_live_example.py` (16 tests, classes `TestLiveExampleElement`
and `TestLiveExampleSources`) before the code. Rebuilt `mvp_sphinx/live_example.py` to write
`<div class="mvp-sphinx-example" data-address data-title>` around one
`<div class="mvp-sphinx-example-source" data-name>` per source, each around a `literal_block`;
wrappers are raw nodes, attribute values go through `html.escape`; language by
`find_lexer_class_for_filename` with `.html` as `html+django` and no match as `text`. The class and
attribute names are constants on `LiveExamples` in `mvp_sphinx/examples.py`, which the directive
imports. The prototype's address and missing-file warnings and its `first-last` line range were
kept as they were: T004 and T006 own them.
Verified: red first, 13 of 15 failed for the right reason (the prototype wrote comments, so no
element was found; first run, before the language case was added). Two passed on first run because
the markup they describe already existed: the plain page holds no example, and the fixture's conf
names one extension. Each was shown able to fail: a plain page given an example went red, and a
conf with an extra `example_setting` went red. Other mutations, each red then restored: no
escaping (title with quotes and an ampersand), `.html` as plain `html`, every file as python.
Green: `uv run pytest tests/test_live_example.py -q` 16 passed; with `tests/test_demo.py` and
`tests/test_navigation.py` 69 passed (the demo guide builds under `-W`); `uv run deptry .` exit 0;
`uv run pre-commit run --all-files` and `uv run mypy` passed. Committed as 133792a.
Next: T002.
Watch: the fixture's `markup.html` writes the ampersand as `&amp;` and not a bare `&`: Pygments'
Django-HTML lexer warns on a bare `&` and the fixture build must be warning-free. The test still
checks that the file's `<`, `&` and a template tag read back as written. The T001 commit does not
carry this entry; it was written afterwards and lands with T002's commit.

## 2026-10-02T16:25:00Z · Implementer US1 · T002

Did: wrote `tests/test_examples.py` (`TestParts`, 14 tests), `TestLiveExamples` in
`tests/test_views.py` (9 tests, on `examples_app`) and `TestExamplePage` in `tests/test_demo.py`
(4 tests) first. Rebuilt `LiveExamples.parts(body)` on an `ExampleReader(HTMLParser)` that tracks
`div` depth and slices by offset (D17, D18); `available` is Django's same-site check, then
`resolve` on the path with the script prefix taken off. `PageView` passes `body_parts` and
`has_examples`; `page.html` links `example.css` only when `has_examples`. Added
`mvp_sphinx/example.html`; deleted `mvp_sphinx/base.html`, `LiveExamples.FRAMED` and
`framed_address`; the component's frame `src` and "Start again" use `example.address` and its
`@prop` line is corrected. The demo's `base.html` extends `mvp/base.html`; its three example
templates extend `mvp_sphinx/example.html` and fill `content`; `ContactView` redirects to
`request.path` and the contact form posts to `request.path`. The demo guide's line ranges did not
move (status.html 3-9 and the four views.py ranges still hold the same code). `single.rst` in the
fixture gained two sections around the example, so the "On this page" test has headings to compare.
Verified: red first, 20 of 27 failed. Seven passed on first run because they describe behaviour
the prototype already had: no marker is one markup part; an unclosed wrapper stays markup (the
regex never matched it); the example sits between two paragraphs; the sidebar contents match the
plain page's; "On this page" matches the page's own headings; the plain page's article is the
rewritten body; a valid post redirects to its own address. Each was shown able to fail by breaking
one thing, red then restored: body stripped; an unclosed example kept; the component wrapped in a
`div`; an extra heading added on example pages; an entry dropped from the sidebar on the example
page; the redirect given a query; the article text altered; the stylesheet always linked. A lazy
`import sphinx` inside `parts` turned the Sphinx-blocked test red.
Green: `uv run pytest tests/test_examples.py tests/test_views.py::TestLiveExamples
tests/test_demo.py -q` 65 passed; `uv run pre-commit run --all-files` and `uv run mypy` passed.
Next: T003.
Watch: the Sphinx-blocked test cannot catch a top-level Sphinx import in `mvp_sphinx/examples.py`,
because the module is already imported when the test blocks Sphinx; it catches a lazy one. The same
holds for the existing tests of that pattern.

## 2026-10-02T16:45:00Z · Implementer US1 · T003

Did: README "Live examples" section under "Using it" (what one is; the marker with address,
`:title:` and one source file; writing the example's page on `mvp_sphinx/example.html` with a short
template and that a page with the shell shows with the shell; `X_FRAME_OPTIONS = "SAMEORIGIN"` with
the reason, that it covers the sign-in and error pages, and the `frame-ancestors` note; that the
source is a copy made at build time; that the host's own rule for the address decides who sees the
example). README Public surface: the directive, `LiveExamples` and `ExampleReader`, `example.html`,
the `live_example` component, `example.css`, and the `body_parts` and `has_examples` context values.
CHANGELOG Unreleased/Added: one entry. CONTEXT.md: "Live example" and "Example source" with
`_Avoid_` lines. AGENTS.md and the `navigation.py` docstring: two modules import Sphinx; AGENTS.md
also describes the demo's example views. `makemessages -l en` run, 5 new strings from the
component. `pyproject.toml`: `mvp_sphinx/live_example.py` added to `[tool.forge.docs] exempt-paths`
beside `navigation.py`, as the brief directed. The README and CHANGELOG text was read against the
humanizer skill's patterns; no change followed.
Verified: no test for this task. `uv run pre-commit run --all-files` and `uv run mypy` passed after
the edits. The `forge` command is not installed in this environment, so the docs step was not run
here; the three names the brief lists (`LiveExample`, `LiveExamples`, module `logger`) are now
covered by the README entry for `LiveExamples` and the exemption for `live_example.py`.
`ExampleReader` is a new public name from T002 and has a README line too.
Next: full verify, then the report.
Watch: no README line shows a line range or several sources; T004 and T005 own those.

## 2026-10-02T16:23:39Z · Implementer US2 · T004

Did: Tests first in `tests/test_live_example.py` (`TestLiveExampleRanges`, `TestLiveExampleNames`, with `write_source`, `example_page` and an `example_build` fixture that build a small source per test) and in `tests/test_views.py::TestLiveExamples` (radio inputs). Rebuilt the source reading in `mvp_sphinx/live_example.py`: a `Source` dataclass; the range is split off the last word only when it is `n` or `first-last`, so a path with spaces reads as a path (R3); `names` works out each source's name per file, with parent folders as needed and the lines added only for a file named twice (D19, R4). README "Several files, and parts of files"; CHANGELOG entry extended.
Verified: red first, `uv run pytest tests/test_live_example.py -q` 6 failed, 20 passed: a path with a space (twice, the prototype split at the first space and warned the file "my" does not exist) and the four naming tests (names stayed bare). Green: `uv run pytest tests/test_live_example.py tests/test_views.py::TestLiveExamples tests/test_demo.py -q` 80 passed. `uv run pre-commit run --all-files` and `uv run mypy` passed. Passed on first run, because the prototype or the approved markup already did it: the range shows its lines dedented, a single line number, a file with no range shown whole, a file named once keeps its bare name, the radio group (one input per source, first checked, labelled by `aria-label`), no radio for one source, and two examples with different group names. Each shown able to fail: dedent removed, `last or first` changed, range always read, lines added to every ranged name, sources reversed (the existing order test and the new ones went red); in the component the `checked` flag removed, the group name made constant, the one-source branch switched off, the label changed. Template and directive restored after each.
Notes: the three-sources-in-order criterion is covered by T001's `test_sources_come_in_the_order_written`; I probed it by reversing the sources and it went red. No fixture page holds two examples of several sources, and `tests/sphinx/examples` is outside this task's files, so that test builds its own small source (`write_source`, imported from `tests/test_live_example.py`). Range validation (reversed, zero, past the end) is T006's.
Next: T005.
Watch: a file named twice with the same lines gives two identical names (D19).

## 2026-10-02T16:24:30Z · Implementer US2 · T005

Did: Tests in `tests/test_views.py::TestLiveExamples`: each available example has one link whose `target` is its own frame's `name` and whose `href` is its address; one link to the address with no `target`; on the page with two examples each "Start again" names its own frame and the two differ; the component holds no `script` element and no attribute starting with `on`, on four pages (single, two, several, and the page whose example the site does not have). The component is unchanged. README: one paragraph on the two controls and that they and the tabs work with scripts off.
Verified: `uv run pytest tests/test_views.py::TestLiveExamples -q` 19 passed. `uv run pre-commit run --all-files` passed. All five new tests (eight cases) passed on their first run, because they pin what the approved markup already does; that is not a red step. Each shown able to fail by breaking the component and restoring it: the `target` removed (three tests red), the target made a constant (two), a `target` added to "Open on its own" (two), "Start again" pointed at another address (one), a `script` element inside the section (four cases), an `onload` on the frame (three). My first script probe put the element outside the section and stayed green, which is correct for a test of the component; the second probe placed it inside.
Next: T006.
Watch: the unavailable example's notice is found in T007, not here. Scroll-free layout at 320 pixels and the returned frame without a page reload are browser checks for convergence (R10).
