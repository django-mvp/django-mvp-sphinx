# Implementation Plan: Make API reference pages and maths look like the rest of the site

**Branch**: `009-api-reference-and-maths` | **Date**: 2026-10-02 | **Spec**: [spec.md](spec.md) ·
**Prototype**: [sketch.md](sketch.md) · **Research**: [research.md](research.md) ·
**Tasks**: [tasks.md](tasks.md)

## Summary

The prototype approved on 2026-10-02 already holds the look: the rules for reference entries and
maths in `content.css`, the two demo pages, and the settings file for the typesetting. The look
is kept as approved. This plan builds what sits behind it and what the prototype faked.

`BodyRewriter`, which already parses every page body, takes on three more jobs. It notes whether
the body holds maths, so only those pages load the typesetting. It wraps each equation set out on
its own line in the same named, focusable scrolling region it gives tables, so a wide equation can
be scrolled from the keyboard before and after it is typeset. It names an entry's link by the
entry's own name and not its whole signature. `PageView` passes the first of these to the
template, and the prototype's `?typeset=off` switch is removed. The typesetting settings give an
unknown command a colour from the theme. The stylesheet moves the equation's scrolling onto the
new region and takes the failed-formula colour from a role that is readable in both themes.
Tests tie the new rules to measured colour roles and to the classes Sphinx really writes.

Maths is typeset by MathJax 4, fetched by the reader's browser from the jsDelivr CDN at the
address Sphinx itself uses (D6). No new dependency, no setting, no Sphinx import.

## Technical Context

**Language/Version**: Python 3.12+, Django 5.2 / 6.0 / 6.1

**Primary Dependencies**: django-mvp ≥ 0.25.0 (the shell's `extra_js` block, the theme's
`--color-*` properties). Standard library `html.parser`. No new Python dependency. MathJax 4 is
loaded in the browser from a CDN and is not installed.

**Storage**: none.

**Testing**: pytest + pytest-django; a new Sphinx source under `tests/sphinx/reference/` built to
JSON once per session; the demo guide built under `-W`; pages requested through `client`; the
stylesheet read by the existing `Stylesheet` and `ColourMath` helpers.

**Performance Goals**: no extra parse. The body is parsed once per request, as today.

**Constraints**: serving never imports Sphinx (Article XII); no colour of the package's own
(Article XIII, FR-016); a page with neither entries nor maths is byte-for-byte what it is today
(FR-020); no stylesheet from the build (FR-022).

**Scale/Scope**: two kinds of content on pages already served. No new address, view or setting.

## Constitution Check

| Article | How the plan meets it |
|---|---|
| I Testing | Test-first for everything a computation decides: maths detection, the equation region, link names, which pages load the typesetting and in what order, contrast of every colour the new rules use. Nothing asserts spacing, type, colour choice or wording. What only a browser shows is checked in a browser and recorded (research R9). |
| II Simplicity | No setting, no new class, no new template. `BodyRewriter` gains one attribute and two insertions; the view gains one context value. |
| III Anti-abstraction | The equation region reuses the table region's class and stylesheet rule. No new colour role: the failed formula uses the existing `--mvp-sphinx-code-error`. |
| IV Integration-first | Acceptance tests request real pages of a real build and read what the reader's browser would receive. |
| V Security | The body is the host's own docs build, trusted as before. The one value the rewrite interpolates, an equation's number, goes through `format_html`. The page loads a script from a third-party CDN on pages with maths: see *Risks*. |
| VI Documentation | README, CHANGELOG and CONTEXT.md in the story that introduces each behaviour: reference entries in US1, maths in US2. |
| VII Dependencies | None added. MathJax is fetched by the reader's browser (D6), so nothing is installed and `deptry` is unaffected. |
| VIII i18n | The region's name ("Equation") is translatable; catalogue refreshed. |
| IX Data model | No models. |
| X Cohesion | All three additions are part of rewriting a body and sit on `BodyRewriter`. |
| XI Compatibility | `BodyRewriter.rewrite(markup)` keeps its signature and still returns a string. New: the `has_maths` attribute and `BodyRewriter.parse`. `PageView`'s template context gains `has_maths`. Nothing removed except the prototype's unreleased `?typeset=off`. |
| XII Scope | Styles and rewrites pages already served. The general index and module index stay out (D2). |
| XIII Host look | Every colour is a role made from the theme at the top of `content.css`, including the one handed to MathJax. |

## The rewrite

`mvp_sphinx/page_body.py`. `BodyRewriter` keeps its design: it records insertions as offsets and
never re-emits what it read.

**`parse` and `has_maths`.** A new classmethod `BodyRewriter.parse(markup)` builds the parser,
feeds it and closes it, and returns the instance. `rewrite(markup)` becomes
`cls.parse(markup).splice()`, so its behaviour and signature are unchanged. A new attribute
`has_maths` starts `False` and becomes `True` when a start tag's class list holds `math`
(`"math" in class.split()`), whatever the tag. Text inside a code sample is escaped and is never
a start tag, and a class such as `mathematics` is not a match.

**The equation region.** For each `div` whose class list holds `math`, the notation is wrapped in
`<div class="mvp-sphinx-scroll" role="region" tabindex="0" aria-label="...">` … `</div>`. The
region opens after the `span.eqno` when the equation has one, otherwise straight after the
`div`'s start tag, and closes immediately before the `div`'s end tag. The number therefore stays
outside the region. The name is the translatable word "Equation" followed by the number as
Sphinx wrote it when there is one ("Equation (1)"), built with `format_html`. A `span.math` is
never wrapped. An equation inside a table is wrapped inside the table's own region, and both
regions close in the right order because each insertion is recorded at its own offset. The
notation's bytes are untouched, which is what lets MathJax find its delimiters (research R3).

**The entry link's name.** When a heading link's holder is a `dt` whose class list holds
`sig-object`, the text part of its name is the entry's own name and not the whole signature:
the text of the holder's `sig-prename` and `sig-name` elements, in order, or the holder's `id`
when that `id` ends with the `sig-name` text (the full dotted name of a nested member, research
R7). When the holder has no `sig-name`, the name is built as it is today. The link's `title`
still leads the name, so a Python function reads "Link to this definition:
demo.links.page_address". Every other heading link, the equation number's included, is named as
today: an equation's link reads "Link to this equation: (1)", which names it by the number a
reader would use.

## The view and the template

`mvp_sphinx/views.py`, `mvp_sphinx/templates/mvp_sphinx/page.html`.

`PageView.get` calls `BodyRewriter.parse(...)` once, marks `splice()` safe as `body` exactly as
today, and passes `has_maths` from the same instance into the context. The `?typeset=off` switch
and its comment are removed: no query parameter changes what a page loads.

The template keeps the prototype's block: when `has_maths`, the shell's `extra_js` block gets
`{{ block.super }}`, then the settings file as a plain script, then the library with `defer`
from `https://cdn.jsdelivr.net/npm/mathjax@4/tex-mml-chtml.js`. The address is written in the
template. It is not a setting (Article II); a host that needs another source overrides the block
in its own `mvp_sphinx/page.html`, which the README already documents as overridable.

## The typesetting settings

`mvp_sphinx/static/mvp_sphinx/maths.js` keeps `ignoreHtmlClass` and `processHtmlClass` as the
prototype has them and adds `tex.noundefined.color` set to `var(--mvp-sphinx-code-error)`
(research R4). It holds no literal colour.

## The stylesheet

`mvp_sphinx/static/mvp_sphinx/content.css`. The reference-entry rules stay as approved.

- The equation's scrolling moves from `div.math > mjx-container` to
  `div.math > .mvp-sphinx-scroll`: that region takes `flex: 1 1 0`, `min-width: 0`, the block
  padding and `overflow-y: hidden`, and inherits sideways scrolling and the focus outline from
  the existing `.mvp-sphinx-scroll` rules. `div.math` itself no longer scrolls in either state,
  and the `:has(mjx-container)` override of its overflow and the container's own focus outline
  go. The look Sam approved is unchanged: centred notation, number at the end of the line,
  sideways scrolling only when the equation is wider than the page, never a vertical scrollbar.
- `mjx-merror` takes `--mvp-sphinx-code-error` in place of the unmixed error colour.
- No other rule changes. If an edit here would change what was approved on screen, stop and
  report it; it is named in the plan comment and shown at the walkthrough, never quietly changed.

## Fixtures and tests

**New Sphinx source `tests/sphinx/reference/`** (hand-written directives only, no autodoc, so it
needs nothing importable): `conf.py` (`extensions = ["mvp_sphinx.navigation"]`), `index.rst`
with a toctree, and:

- `api.rst`: a `py:function` with parameters, defaults, annotations, a return value and a raised
  error and a description that refers to another entry with `:py:func:`; a `py:class` with a
  `py:method`, a `py:attribute`, a `py:property` and a nested `py:class` holding its own
  `py:method` (three levels); a second `py:class` with a method of the same name as the first's;
  a `py:exception`; a `py:data`; an entry with no description; an entry holding
  `.. deprecated::`; a `js:function` with parameters.
- `maths.rst`: maths in a sentence; an unnumbered equation; two equations with `:label:` and an
  `:eq:` reference to each; maths inside a note, a table cell, a list item and a heading; a code
  block whose text shows `<span class="math">` and a dollar sign.
- `plain.rst`: prose only.

`reference_build` (session) and `reference_app` fixtures in `tests/conftest.py`, on the pattern
of `reading_build` / `reading_app`.

**Where tests go** (mirrors the source tree): `tests/test_page_body.py` for the rewrite,
`tests/test_views.py` for what a served page carries, `tests/test_static/test_content_css.py`
for the stylesheet and the settings file, `tests/test_demo.py::TestDemoGuideStates` for the
demo guide's states (generated entries, the summary table, the source link).

**The hooks test.** A hand-kept tuple of the classes the new rules select on (`sig-object`,
`sig-name`, `sig-prename`, `sig-param`, `default_value`, `field-list`, `colon`, `math`, `eqno`,
and from the demo build `viewcode-link`, `autosummary`, `property`, `sig-return-icon`). Each must
appear in a selector of the stylesheet and in a page body of a real build. It fails when the
stylesheet drifts from what Sphinx writes, in either direction, on every Sphinx version CI runs.

**The contrast tests.** For every rule whose selector names `sig-object` and sets `color`, that
colour against `--mvp-sphinx-code-bg`; for every rule whose selector names `field-list`, `math`,
`eqno` or `mjx-` and sets `color`, that colour against the page background and every admonition
background; each at least 4.5:1 in both themes (FR-018, SC-006). A value of `inherit` is skipped.

Elements are found by `id`, `href`, role and class hooks a script or the stylesheet depends on,
never by wording. No test asserts spacing, type or which colour was chosen.

## Story order

**US1 → US3 → US2 → US4 → US5, sequential, in the feature worktree.** Two dispatches: the
reference stories (US1, US3), then the maths stories (US2, US4) with US5, which draws on both.
Every story edits `page_body.py`, `content.css` or the shared fixture source, so they cannot run
side by side.

## Risks

- **A third-party script.** A page with maths runs a script from jsDelivr in the host's origin.
  The maintainer accepted the CDN (D6). The address carries the major version only, as Sphinx's
  does, so it cannot carry an integrity hash, and MathJax fetches further files (fonts, speech)
  from the same CDN that a hash on the first file would not cover. The exposure is limited to
  pages with maths. The README says where the script comes from, that a host behind a content
  security policy has to allow that origin, and that without it the reader sees the notation as
  written.
- **What the suite cannot see.** Typeset output, the 320-pixel reflow and the theme switch are
  checked in a browser and recorded, not asserted (research R9).
- **Sphinx's markup.** The stylesheet depends on class names Sphinx writes. The hooks test runs
  on every Sphinx version in CI.
