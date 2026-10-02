# Implementation Plan: Show working examples live next to their source code

**Branch**: `008-live-examples` | **Date**: 2026-10-02 | **Spec**: [spec.md](spec.md) ·
**Prototype**: [sketch.md](sketch.md) · **Research**: [research.md](research.md) ·
**Tasks**: [tasks.md](tasks.md)

## Summary

The prototype approved on 2026-10-02 holds the look: the box, the title bar, the frame beside its
source, the tabs, the two quiet buttons, the soft warning and the skeleton, in
`cotton/mvp_sphinx/live_example.html` and `example.css`. That markup, those styles and the copy
are kept as approved. This plan rebuilds what sits behind them, test-first, and replaces what the
prototype faked.

Three things change shape. An example's page is written without the application shell, on a base
template this package ships, so the prototype's address flag and its replacement for the host's
`base.html` both go (D11, research R1). The build writes each example into the page as elements
and the served page reads them with `html.parser`, in place of comments and a regular expression
(R2). And the marker's syntax, the names of sources and their languages are settled (R3 to R5).

No new dependency, no setting, no model, no new address. Serving still never imports Sphinx.

## Technical Context

**Language/Version**: Python 3.12+, Django 5.2 / 6.0 / 6.1

**Primary Dependencies**: django-mvp ≥ 0.25.0 (the `app` block of `mvp/base.html`, `c-alert`,
`c-messages`, DaisyUI tabs and skeleton). Standard library `html.parser`. Sphinx and Pygments at
build time only, as today. No new dependency.

**Storage**: none. An example's source lives in the page's body in the docs build.

**Testing**: pytest + pytest-django; a new Sphinx source under `tests/sphinx/examples/` built to
JSON once per session; small sources built per test for the build's warnings; the demo guide built
under `-W`; pages requested through `client`.

**Performance Goals**: a page without an example pays one substring test. A page with one is
parsed a second time, by `LiveExamples`.

**Constraints**: serving never imports Sphinx and reads nothing outside the docs build
(Article XII, FR-014); a host's `base.html` is untouched (planning note, FR-009); a page without
an example is served as before (FR-017); every colour from the theme (Article XIII); the approved
look is not this build's to change (`sketch.md`, "What was ruled by eye").

**Scale/Scope**: one directive, one serving class, one component, one base template, one
stylesheet, two pages of the demo guide.

## Constitution Check

| Article | How the plan meets it |
|---|---|
| I Testing | Test-first for everything a computation decides: what the directive writes and refuses, how a body is split, whether an address is the site's, what a source is called. Nothing asserts wording, spacing or colour. What only a browser shows is checked in a browser and recorded (research R10). |
| II Simplicity | One selector for part of a file (a line range). No setting. No cache-busting scheme. No change to django-mvp. |
| III Anti-abstraction | `LiveExamples` is its own small parser and does not become a base for `BodyRewriter` or share one with it. |
| IV Integration-first | Acceptance tests build a real Sphinx source with the host's one line of configuration and request real pages. |
| V Security | The address is checked when the docs are built and again when the page is served. The source is escaped by Sphinx as any code block is; attribute values by `html.escape` at build time and by the template layer when served. See *Security*. |
| VI Documentation | README, CHANGELOG and CONTEXT.md in the story that introduces each name: the marker, the base template and the setup step in US1. |
| VII Dependencies | None added. Pygments is imported only in the build module, where Sphinx already requires it. `deptry` is checked for that import in T001. |
| VIII i18n | The component's strings are translatable (they already are); the catalogue is refreshed. Build warnings are for the author and follow Sphinx's own untranslated convention. |
| IX Data model | No models. |
| X Cohesion | The build side is one directive class. The serving side is one class, `LiveExamples`. |
| XI Compatibility | New public names only: the `live-example` directive, `mvp_sphinx/example.html`, `LiveExamples`, the `body_parts` context value. `PageView`'s `body` context value is kept. Nothing released is removed. |
| XII Scope | The example is the host's own page at its own address. Nothing is executed from the documentation, and serving reads only the docs build. |
| XIII Host look | The example's base template extends the host's `base.html`, so the example is in the host's theme. `example.css` sets sizes and borders and no colour. |

## The build side

`mvp_sphinx/live_example.py`, the `LiveExample` directive, registered by `mvp_sphinx.navigation`'s
`setup` as today. It imports Sphinx and is loaded only during a build (research R9).

- **Address.** Accepted when it starts with one `/` and holds no scheme, host, backslash or
  whitespace. Otherwise a warning at the directive's location, and the directive returns nothing,
  so the page carries no example and no source for it (FR-003, US3.5).
- **Sources.** Each content line is read as research R3 describes. A file that does not exist, or
  a range that is not inside the file, is a warning naming the file, at the directive's location,
  which names the page (FR-013). That source is left out. An example left with no source is a
  warning and returns nothing (FR-004).
- **Names and languages.** Research R4 and R5.
- **What it returns.** Research R2: a `raw` opening wrapper, then per source a `raw` opening
  wrapper, a `literal_block` and a `raw` close, then a `raw` close. The class names and attribute
  names are constants of `LiveExamples`, imported from `mvp_sphinx.examples`.

Warnings are Sphinx warnings, so a build under `-W` fails on them, and one without it finishes
and reports them.

## The serving side

`mvp_sphinx/examples.py`, `LiveExamples`.

- `LiveExamples.parts(body, request)` returns the body in order as parts: markup, or an example.
  A body without the marker class returns one markup part holding the body unchanged.
- An example is a small frozen dataclass or dict with: `id` (`mvp-sphinx-example-<n>`, numbered
  in page order, which is what makes two appearances of one example independent), `title`,
  `address`, `available`, and `sources`, each with `name` and the highlighted `html`.
- `available` is research R6: the address passes Django's same-site check and resolves in the
  request's urlconf. Anything else is unavailable, and the component then draws the notice and no
  frame.
- The parser tracks `div` depth from each wrapper's start tag to its matching end and slices the
  body by offset, so the source's markup is passed through byte for byte. An example whose
  wrapper never closes (a damaged build) is left in the page as markup; the page still renders.

`PageView.get` passes `body_parts=LiveExamples.parts(body, request)` and
`has_examples`, alongside `body` and `has_maths`. `page.html` draws the parts in order inside the
article, and links `example.css` only when `has_examples` is true.

## The component, the stylesheet and the base template

- `cotton/mvp_sphinx/live_example.html` keeps its approved markup. `framed_address` becomes
  `address` in the frame's `src` and in "Start again".
- `example.css` is unchanged.
- `mvp_sphinx/templates/mvp_sphinx/example.html` is new (research R1). The prototype's
  `mvp_sphinx/templates/mvp_sphinx/base.html` is deleted, and the demo's `base.html` extends
  `mvp/base.html` again.

## The demo

The two guide pages stay as approved. Their example views move onto templates that extend
`mvp_sphinx/example.html`. The contact form posts to its own address and redirects to it, with no
flag to carry. The demo keeps `X_FRAME_OPTIONS = "SAMEORIGIN"`.

Because the whole guide is built under `-W` by the existing demo tests, the guide's two pages
must build cleanly at every task. A task that changes what the directive accepts updates those
pages in the same commit.

## Security

- **Trust boundary: the docs build.** It is the host project's own, written by its own build, and
  is trusted as every page body already is. The address is nonetheless checked twice, at build
  and at serve, because the cost of a mistake is another site inside a page of this one.
- **Trust boundary: the reader.** The frame is requested by the reader's browser with the
  reader's session, so the host's own rule for the address decides what they get (FR-011). The
  documentation page itself holds nothing of the example but its address and its source.
- **The source.** A docs author can show any file the build can read, as with `literalinclude`.
  The author is the host project (spec, Assumptions). Once in the build, the source is governed
  by the reader rule like the rest of the page (US3.8).
- **Framing.** `SAMEORIGIN` lets the site frame itself and nobody else. The README says what the
  setting does and that the sign-in and error pages are covered by it.
- **No new input from a request.** The page view reads nothing new from the request.

## Fixtures and tests

- `tests/sphinx/examples/`: `conf.py` with the one extension line; a page with an example between
  two paragraphs and one source; a page with two examples; a page with an example of three
  sources, one by line range, one whose text holds `<`, `&` and a template tag; a page naming an
  address the test urlconf does not have; a plain page. Source files beside the pages.
  `examples_build` and `examples_app` fixtures in `tests/conftest.py`, as `reference_build` and
  `reference_app` are.
- Example views for the suite live in the demo (`demo/examples/`), which `tests/urls.py` already
  includes.
- `tests/test_live_example.py` for the directive, `tests/test_examples.py` for `LiveExamples`,
  `TestLiveExamples` and friends in `tests/test_views.py`, and the demo's states in
  `tests/test_demo.py`. Each mirrors the module it tests.
- Build warnings are tested by building a small source written in the test with the existing
  `sphinx_build` fixture and reading Sphinx's warning stream.

## Story order

**US1 → US2 → US3, sequential, in the feature worktree.** All three edit the directive and
`LiveExamples`, so they cannot run side by side.

## What the prototype faked, and where each goes

| Faked | Task |
|---|---|
| `?example=1` and the full-address post | T002 |
| The demo's `base.html` extending `mvp_sphinx/base.html` | T002 |
| `X_FRAME_OPTIONS` set with no documentation | T003 |
| Examples carried as HTML comments, found by regular expression | T001, T002 |
| The marker's placeholder syntax | T001 (address, title, files), T004 (ranges) |
| Bare file names for sources | T004 |
| The slow example's sleep; the debug page on the failing one | kept, research "What stays" |
| A second module importing Sphinx against the repository's notes | T003 |
| No translations, CONTEXT.md, README, changelog | T003, extended in T005 and T008 |
| The demo's tests not run against the new pages | T008 |

## Risks

- **A host that has not set `X_FRAME_OPTIONS`** sees an empty frame, or the browser's own
  refusal, in the example's place. The package cannot detect it (research R7). The README's setup
  section leads with it.
- **A page with the shell named as an example** shows the shell inside the frame. Documented.
- **Line ranges drift** when the file is edited. The author sees it at the next build only by
  looking. Accepted for this build (research R3).
