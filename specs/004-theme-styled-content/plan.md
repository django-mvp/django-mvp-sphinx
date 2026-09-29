# Implementation Plan: Make user-guide content look like the rest of the site

**Branch**: `004-theme-styled-content` | **Date**: 2026-09-30 | **Spec**: [spec.md](spec.md) ·
**Research**: [research.md](research.md) · **Tasks**: [tasks.md](tasks.md)

## Summary

The page template links one plain-CSS stylesheet shipped inside the package, and marks the
article that holds the page body with a class every rule in that stylesheet is scoped under. The
stylesheet keys off the class names Sphinx writes (admonitions, Pygments tokens, captions,
glossaries, labels) and takes every colour from the theme's `--color-*` custom properties, mixing
them with `color-mix(in oklab, …)` where a combination has to reach 4.5:1. django-mvp's `prose`
already styles headings, paragraphs, lists, links and inline code in the theme (research R2), so
the stylesheet adds only what Sphinx's markup needs beyond that. Two things CSS cannot do, an
accessible name for each heading link and a focusable scrolling area around each table, are done
by rewriting the body's HTML before it is rendered, in one small class on the standard library's
`HTMLParser`. The styling follows the reviewed prototype (research R3, R4) with its colour mixes
corrected to meet FR-015.

## Technical Context

**Language/Version**: Python 3.12+, Django 5.2 / 6.0 / 6.1

**Primary Dependencies**: django-mvp ≥ 0.25.0 (the shell's `base.html` and its `styles` block,
the theme's colour custom properties, `prose`). No new runtime dependency: the body rewrite uses
`html.parser` from the standard library.

**Storage**: none.

**Testing**: pytest + pytest-django, real Sphinx builds from `tests/sphinx/` (FS-001). Colour
requirements are tested as computations over the stylesheet and django-mvp's installed theme
values (research R5). Appearance is judged at the walkthrough, per the testing standard.

**Target Platform**: any host project on django-mvp.

**Project Type**: reusable Django app (library).

**Performance Goals**: the rewrite is one linear pass over a page body per request.

**Constraints**: no literal colour in the package's styles (SC-001); no step for the host
(FR-017); nothing outside the page content affected (FR-016); serving still never imports Sphinx.

## Constitution Check

| Article | How the plan meets it |
|---|---|
| XII Scope | Serving still reads the build from disk and imports nothing from Sphinx. No Sphinx theme or stylesheet is shipped or loaded. |
| XIII Pages look like the host project | Every colour is a theme custom property or a `color-mix` of two; pages render in the host's `base.html`. |
| Quality bar | README and CHANGELOG change with the new public name (`BodyRewriter`) and the new behaviour; coverage from the rewrite's and the views' tests. |
| Testing standard | No test of colours as design, class names or wording. Contrast, the absence of literal colours, the scope of the rules, accessible names and focusability are specification criteria and are tested as such. |
| Sam's code standards | No leading-underscore names anywhere (methods, helpers, templates, CSS custom properties). Line length 88. No compatibility aliases. |

## Design

### The stylesheet

`mvp_sphinx/static/mvp_sphinx/content.css`, plain CSS, no build. Every selector starts with
`.mvp-sphinx-content`, the class on the page template's `<article>`. Structure, top to bottom:

1. **Colour roles.** One rule on `.mvp-sphinx-content` declaring every colour the stylesheet
   creates as a custom property named `--mvp-sphinx-…`, each either `var(--color-…)` or
   `color-mix(in oklab, <role> N%, <role>)` of two theme colours. Nothing else in the file
   introduces a colour: later rules only say `var(--mvp-sphinx-…)` or `var(--color-…)`. This is
   what makes SC-001 and SC-005 checkable from the file alone.
   - Admonitions, one edge colour and one background per meaning:
     `--mvp-sphinx-admonition-<meaning>` = the theme role (info, success, primary, warning,
     error; `decisions.md`, *Admonition meanings*), and `--mvp-sphinx-admonition-<meaning>-bg` =
     `color-mix(in oklab, <role> 12%, var(--color-base-100))`. Admonition text is
     `var(--color-base-content)`. Meanings: `info`, `helpful`, `important`, `cautionary`,
     `dangerous`.
   - Code: `--mvp-sphinx-code-bg` (`--color-base-200`), `--mvp-sphinx-code-text`
     (`--color-base-content`), `--mvp-sphinx-code-emphasis-bg` (emphasised lines, a warning tint
     of the code background), `--mvp-sphinx-code-line-number`, and one per token group:
     `comment`, `keyword`, `string`, `number`, `name` (functions, classes, builtins, decorators,
     attributes), `inserted`, `deleted`, `error`. Each token colour is a theme role mixed toward
     `--color-base-content` (research R4) at whatever percentage makes the contrast test pass in
     both default themes, with headroom.
   - Muted text (heading-link glyph, captions): a mix of base-content toward base-100.
2. **Admonitions** (US1). `.admonition` gets the informational meaning (edge 4px on the inline
   start, tinted background, `--radius-box`, padding); meaning rules override the custom property
   the box reads. `.admonition-title` weight 600, no top margin. `.seealso` is informational;
   `.versionadded, .versionchanged` informational and `.deprecated` cautionary, drawn with the same
   box (FR-005). Nested admonitions work unchanged because each reads its own class.
3. **Code** (US2). `.highlight pre` background and text from the roles; Pygments short classes
   grouped onto the token roles; `.hll` background; `.linenos` colour and `user-select: none`;
   `.code-block-caption` muted and above the block. Code in a language Pygments did not highlight
   has no token spans and reads as `code-text`.
4. **Wide content** (US3). `.mvp-sphinx-scroll` (the table wrapper) scrolls sideways within the
   reading area; `pre` keeps `overflow-x: auto`; `img` scales to the reading area keeping its ratio;
   a figure's caption stays in the figure.
5. **Heading links** (US4). `.headerlink` muted, no underline, `opacity: 0` with a short opacity
   transition; revealed on hover of the element holding it and on the link's own `:focus-visible`;
   the transition removed under `prefers-reduced-motion: reduce`. `[id]` inside the content gets
   `scroll-margin-top: 5rem` (research R6).
6. **Glossaries and interface references** (US5). `dl.glossary` terms bold with the definition
   indented beneath; `.guilabel` a bordered chip from `--color-base-300`; `.menuselection` weight
   600; `kbd` is left to daisyUI's `.kbd` (research R2).

### The page template

`mvp_sphinx/templates/mvp_sphinx/page.html` extends the `styles` block with `{{ block.super }}`
and one `<link rel="stylesheet" href="{% static 'mvp_sphinx/content.css' %}">`, and adds
`mvp-sphinx-content` to the article's classes (US1). US3 switches the article to render the
rewritten body from the context instead of `page_data.body`. Nothing else in the template changes:
width and layout belong to #4 and the sibling features.

### The body rewrite

`mvp_sphinx/page_body.py`, one public class:

```python
class BodyRewriter(HTMLParser):
    @classmethod
    def rewrite(cls, markup: str) -> str: ...
```

`rewrite` feeds the body through a fresh parser and returns it with two changes, everything else
re-emitted exactly as it arrived (start tags from `get_starttag_text()`, entity and character
references as written, comments kept; `convert_charrefs=False`):

- **Every outermost `<table>` is wrapped** (US3, FR-008) in
  `<div class="mvp-sphinx-scroll" role="region" tabindex="0" aria-label="…">`. The label is the
  table's caption text when it has one, else the translated word "Table" (`gettext`, the one new
  string). A table nested in a table is not wrapped again. The wrapper's opening tag can only be
  written once the caption has been read, so the table's output is held until its closing tag.
- **Every `a.headerlink` gets an `aria-label`** (US4, FR-010; US5 checks glossary terms): the text
  of the element that directly holds the link, up to the link, whitespace collapsed; prefixed by
  the link's `title` and a colon when it has one (`Link to this heading: Installing`). The title
  is already in the docs build's language (research R1), so the package adds no string. The label
  is built from unescaped text and escaped once for the attribute.

`PageView.get` passes `page["body"]` through `BodyRewriter.rewrite` and hands the result to the
template as `body`, marked safe: the body is the host's own build, trusted as in FS-001, and the
rewrite escapes the only text it moves into an attribute. One request, one pass.

### Tests and fixtures

- **Fixture page.** `tests/sphinx/guide/content.rst`, marked `:orphan:` so it joins no toctree
  (keeps FS-002's contents tests untouched and the build warning-free), built into the existing
  `guide_build`. It carries, as each story needs them: a note and a warning, a table with a
  caption, a table without one, a table inside an admonition, code, sections whose headings hold
  inline code and an ampersand, and a glossary.
- `tests/test_page_body.py` mirrors `mvp_sphinx/page_body.py`: `TestBodyRewriter` on literal
  markup strings shaped like research R1, asserting names, wrappers, escaping, and that markup the
  rewrite does not touch comes back byte-for-byte.
- `tests/test_views.py`, through `client` on the fixture page: the stylesheet is linked on a
  docs page and not on the demo overview page; no stylesheet under the build's `_static/` is
  linked; the rendered page carries named heading links and wrapped tables (proof the view uses
  the rewrite).
- `tests/test_static/test_content_css.py` (declared under
  `[tool.forge.conformance] non-mirror-paths`; its subject is a static asset):
  `TestContentStylesheet`: no literal colour in any declaration (SC-001; checked by stripping the
  allowed forms, `var(…)`, `color-mix(in oklab, …)`, percentages, lengths and the keywords
  `solid`, `none`, `currentcolor`, `inherit`, from every colour-bearing declaration and asserting
  nothing is left); every selector starts with `.mvp-sphinx-content` (FR-016); the contrast of
  every pair the package creates is at least 4.5:1 in django-mvp's `[data-theme=light]` and
  `[data-theme=dark]` values, read from the installed `mvp/static/css/django-mvp.css` (research
  R5). Pairs: base-content on each admonition background (US1); code text, each token colour and
  the line-number colour on the code background and on the emphasised-line background (US2).
- No test asserts a colour value, a layout, a width, a class chosen for looks, or wording.

### Demo

`demo/docs/content-tour.rst`, linked from the guide's front page and listed in its hidden
toctree: every construct the spec covers, in the states the walkthrough needs. Each story adds its
part: admonitions of every meaning, an unknown kind, a custom title, a nested admonition,
see-also and the three version notes (US1); code in several languages with a caption, line
numbers and emphasised lines, and code Pygments cannot lex (US2); a wide table, a table in a list,
a long code line, a wide image and a figure (US3); several sections, one heading with inline code
(US4); a glossary with cross-references to it, and keys, labels and menu paths (US5).

## Story order

**US1 → US2 → US3 → US4 → US5, one at a time, in the feature's own working tree.** US1 lays the
stylesheet, the template link and the colour tests every later story extends; US3 creates the
rewrite US4 extends. Every story touches the stylesheet, so parallel worktrees would only collide.

## Project Structure

```text
mvp_sphinx/
├── page_body.py                      # new: BodyRewriter (US3, US4)
├── views.py                          # PageView.get passes the body through the rewrite (US3)
├── static/mvp_sphinx/content.css     # new: the stylesheet (every story)
├── templates/mvp_sphinx/page.html    # styles block, article class (US1), rewritten body (US3)
└── locale/en/LC_MESSAGES/django.po   # "Table" (US3)
tests/
├── sphinx/guide/content.rst          # new fixture page (every story)
├── test_page_body.py                 # new (US3, US4, US5)
├── test_views.py                     # stylesheet link, no build stylesheet, rewrite in use
└── test_static/
    ├── __init__.py
    └── test_content_css.py           # new: literal colours, scope, contrast
demo/docs/content-tour.rst            # new demo page (every story)
demo/docs/index.rst                   # link and toctree entry (US1)
pyproject.toml                        # non-mirror-paths for tests/test_static/ (US1)
README.md, CHANGELOG.md               # every story, for what it adds
```

## Complexity Tracking

| Choice | Why the simpler option does not do |
|---|---|
| An HTML rewrite in Python | CSS cannot give a link an accessible name or make an element focusable (research R1). A script would add JavaScript to every page, which the spec rules out for the copy button on the same grounds. |
| Holding a table's output until it closes | The wrapper's label comes from the caption, which follows the `<table>` tag. |
| A contrast computation in the tests | There are no browser tests in this repository, and FR-015 is a number. |
