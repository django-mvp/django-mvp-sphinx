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

## 2026-10-02T16:10:19Z · Implementer US1 · T001

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

## 2026-10-02T16:15:01Z · Implementer US1 · T002

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

## 2026-10-02T16:16:23Z · Implementer US1 · T003

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

## 2026-10-02T16:26:29Z · Implementer US3 · T006

Did: Tests first in `tests/test_live_example.py::TestLiveExampleWarnings`, reading Sphinx's warning stream with `capsys` after `sphinx_build` (no new fixture; `build_warnings` filters the WARNING lines). Rebuilt in `mvp_sphinx/live_example.py`: the address is accepted by one pattern (`/` then no second `/`, backslash or whitespace); `final_argument_whitespace` is on, so an address holding a space reaches the check as one argument and gets the build warning in place of docutils' own directive error; a range that is reversed, zero or past the end of the file is a warning naming the file, and that source is left out. README "What the build reports", with `-W`.
Verified: red first, `uv run pytest tests/test_live_example.py::TestLiveExampleWarnings -q` 7 failed, 8 passed. The seven: an address with a backslash (the prototype accepted it), an address with a space (docutils' own error, no Sphinx warning), and five ranges (reversed, zero, zero-first, past the end, last past the end), which the prototype read as a wrong slice with no warning. Green: `uv run pytest tests/test_live_example.py tests/test_demo.py -q` 83 passed (the demo guide builds under `-W`). `uv run pre-commit run --all-files` and `uv run mypy` passed. Passed on first run, because the prototype's code already did it: a missing file keeping the other sources, an only source missing, no source lines, the scheme, network-path and no-slash addresses, and the two not-a-number ranges (read as a path that does not exist). Each shown able to fail: the missing-file warning removed (four red), the second-slash lookahead removed (network-path), the leading slash made optional (scheme and no-slash), the no-source warning removed (the no-lines test), the range pattern widened to any word (three).
Next: T007.
Watch: a last word that is not a number is part of the path, so `long.py three` is reported as a missing file `long.py three` and not as a bad range; the message still names the file. The brief's `-W` bullet stays untested, as the design review ruled.

## 2026-10-02T16:29:36Z · Implementer US3 · T007

Did: Tests in `tests/test_views.py`: `TestUnavailableExample` (the page naming an address the site lacks: 200, no frame, no link to the address, one `role="alert"` element inside the example, the source still there; and a docs build copy whose body names an address on another site, in three shapes, served with no frame and no links), `TestRefusedExample` (the demo guide's page for the staff-only example answers 200 to an anonymous reader and to a regular user, with the source and a frame holding nothing and no `srcdoc`; the example's address answers each as it does to a client that never asked for the page), `TestFailingExample` (the page naming the failing example answers 200), `TestReaderRule` (the staff guide app pointed at the examples build: an anonymous reader gets the redirect the plain page gets, a regular user the 403 the plain page gets with none of the source and no example element, a staff user the example), `TestRebuild` (a copy of the build with a changed source shows the new code on the next request). Helpers: `rewrite_body` and the `examples_copy` fixture, both in the test module. `mvp_sphinx/examples.py` is unchanged: no test showed a fault.
Notice hook: the component's alert carries `role="alert"` (`c-alert` renders it), so the notice is found by role. The approved markup is unchanged.
Verified: `uv run pytest tests/test_views.py -k "TestLiveExamples or TestUnavailableExample or TestRefusedExample or TestFailingExample or TestReaderRule or TestRebuild" -q` 32 passed. `uv run pre-commit run --all-files` and `uv run mypy` passed. All fourteen new cases passed on their first run (after a fixture fix: the first version of the staff-example lookup assumed every example has a frame, a test error and not a fault), because serving already does what they describe; that is not a red step. Each shown able to fail by breaking one thing and restoring it: `available` always true (four red); the same-site check removed (scheme and network-path red); the resolve step removed (the missing-address test); `srcdoc` added to the frame (both readers); the staff view opened to everyone (both readers); the staff guide's rule set to everyone (both reader-rule tests); a cache on `DocsBuild.page` (the rebuild test); an error raised for the broken address (the failing-example test). The backslash address stays unavailable only because it does not resolve, so no single mutation isolates it; the three addresses name the real example path so that the scheme and network-path cases do depend on the same-site check.
Next: T008.
Watch: the unclosed-source case did not come up, since the reader only records an example whose wrapper closes, and nothing was changed for it. The staff-only and failing examples are named only by the demo guide's page, so those tests use `demo_guide_app` and need the demo guide build; the slow example is never requested.

## 2026-10-02T16:32:45Z · Implementer US3 · T008

Did: Tests in `tests/test_demo.py::TestDemoGuideStates`, on the two pages of the demo guide build: for every example of each page, each source shown is the named file's text, or the named lines with their common leading indentation removed (the expected text is worked out from the `.rst` page's own lines by `written_sources`, a small reader of the page in the test module); the working-form page holds two examples, one of three sources (three radio inputs and three panes) and one of a single source that is part of a file; the cannot-run page holds frames for `/examples/slow/`, `/examples/staff/` and `/examples/broken/` in that order and one example with no frame that holds one `role="alert"`, with none in the framed three; both pages answer 200 to an anonymous reader. No change to `demo/docs/examples/*.rst`, `demo/examples/**` or the templates: the ranges and the states were already as the tasks describe. AGENTS.md "The demo project": the five example views, why the demo keeps `X_FRAME_OPTIONS = "SAMEORIGIN"`, that the slow one is never requested, and that ranges must follow edits (and that the tests cannot see a drifted range). CHANGELOG: the entry finished with what the build reports, the notice and the demo's Examples part.
Verified: `uv run pytest tests/test_demo.py -q` 48 passed; the six new cases alone `uv run pytest tests/test_demo.py::TestDemoGuideStates -q -k "shown or working_form or cannot_run or anonymous_reader"` 6 passed. `uv run pre-commit run --all-files` and `uv run mypy` passed. All six passed on their first run, because the pages and the code already did this; that is not a red step. Each shown able to fail by breaking one thing and restoring it: dedent removed in the directive (both source cases red, since `status.html` 3-9 is indented); the range's first line shifted by one (both red); the third source removed from the contact example (the three-source test); the retired address changed to a real one (the cannot-run test); the slow address changed to the retired one (the cannot-run test). The anonymous-reader cases would fail on a missing page (a KeyError in the responses), which I did not run as a mutation beyond hiding the page, where the build itself failed.
Next: full verify, then the report.
Watch: the tests compare the shown source with the range the page writes, so they cannot see a range that has drifted from the code it was meant to show; that stays by eye, as AGENTS.md now says. Screens 2, 4 and 9 (narrow layout, a used example, scripts off) are browser checks for convergence (R10).

## 2026-10-02T16:37:28Z · S5 converge

Did: all three stories accepted after an independent verify each (lint, types, docs check, suite,
build green; tamper check clean for US1, and for US2 and US3 one flag on `tests/test_views.py`
that is an import line with no assertion touched). Every FR and SC of the specification maps to a
passing test or to the browser check below; no gap, so no converge task. No migrations. The
simplify pass over the feature's diff found nothing to remove. All 19 decisions carry an ADR
verdict, none graduates. One line of the demo guide still called an example's own address "an
ordinary page of the site" and was reworded to match the refined specification.
Browser check (research R10), Chromium against the demo on the development server, both demo pages:
- A form sent inside the frame: sent empty with the browser's own validation off, the frame
  showed the three field errors; sent filled in, it showed the thanks message. Both times the
  frame stayed at the example's address with no shell in it, and the documentation page's address
  and its script state were unchanged, so it had not reloaded (US1.4, SC-002).
- "Start again" returned the form to its empty state without reloading the page (US2.4).
- The second example on the page was untouched throughout (US1.7).
- At 320 pixels wide neither page scrolls sideways, and neither does the content of any frame; the
  example and its source stack, frame 448 pixels tall (US2.6, FR-016).
- With the dark theme chosen, each frame is in the dark theme too.
- The cannot-run page: the slow example arrived; the missing one shows the notice; the staff-only
  one shows the sign-in page to a signed-out reader; the failing one shows the site's error page.
  The documentation page was unaffected in each case (SC-004).
Next: code review.

## 2026-10-02T16:43:50Z · S6 review

Did: one reviewer with the correctness, specification and security lenses over the feature's diff at
9488273. Verdict request changes: one high finding and two low, all verified, no security finding.
Each was given a test that failed first and then remedied, and each remedy was checked against the
finding's own reproduction (ledger, gates.review). Full verify green afterwards.
Next: walkthrough and the pull request opened for review.
