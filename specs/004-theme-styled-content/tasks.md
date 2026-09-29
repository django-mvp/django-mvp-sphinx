# Tasks — 004 Make user-guide content look like the rest of the site

**Branch**: `004-theme-styled-content` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task with behaviour follows the red-green-refactor cycle. A task is done when its tests pass,
the tree is green and the work is committed. Styling itself gets no test (testing standard §1):
colours as design, widths, spacing, class names chosen for looks and wording are judged at the
walkthrough. Documentation for a public name lands in the task that introduces it.

## Order

**US1 → US2 → US3 → US4 → US5, one at a time, in one working tree** (plan, *Story order*).

---

## US1 — Pages read as the site's own pages, with admonitions told apart by meaning (P1)

Issue: #30. Delivers FR-001 to FR-005, FR-014, FR-015 (admonitions), FR-016, FR-017; SC-001,
SC-002, SC-005 (admonitions), SC-006.

### T001 — The stylesheet reaches documentation pages, and only them

**Files**: `mvp_sphinx/static/mvp_sphinx/content.css`, `mvp_sphinx/templates/mvp_sphinx/page.html`,
`tests/sphinx/guide/content.rst`, `tests/test_views.py`, `README.md`, `CHANGELOG.md`

Plan, *The stylesheet* (item 1, the colour-roles rule, may start empty) and *The page template*.
Fixture page `content.rst` with `:orphan:`, a title, a note and a warning. Tests, class
`TestContentStyling` in `tests/test_views.py`, through `client` with `db`: a docs page links the
package stylesheet at its static URL (`static("mvp_sphinx/content.css")`); the demo overview page
does not (FR-016); no stylesheet on a docs page points into the build's `_static/` (FR-003).
README: a short *How pages look* section: pages take the host's theme with nothing to configure,
the stylesheet the page template links, and that a host overriding `mvp_sphinx/page.html` keeps
`{{ block.super }}` in `styles`. CHANGELOG: one *Added* line.

### T002 — Admonitions and version notes by meaning, in the theme's colours

**Files**: `mvp_sphinx/static/mvp_sphinx/content.css`, `tests/test_static/__init__.py`,
`tests/test_static/test_content_css.py`, `pyproject.toml`, `tests/sphinx/guide/content.rst`,
`demo/docs/content-tour.rst`, `demo/docs/index.rst`, `CHANGELOG.md`

Plan, *The stylesheet* items 1–2 and *Tests and fixtures* (the stylesheet tests). `pyproject.toml`:
`[tool.forge.conformance] non-mirror-paths = ["tests/test_static/"]`. Tests, class
`TestContentStylesheet`: no literal colour in any colour-bearing declaration (SC-001); every
selector is scoped under `.mvp-sphinx-content` (FR-016); base-content on every
`--mvp-sphinx-admonition-*-bg` is ≥ 4.5:1 in django-mvp's light and dark themes, read from the
installed `mvp/static/css/django-mvp.css` (FR-015, SC-005; research R5). The contrast helpers
(OKLCH parse, `color-mix` in OKLab, OKLab → sRGB, WCAG contrast) live in the test module, each a
small named function. Demo: `content-tour.rst` with every admonition meaning, an unknown kind, a
generic admonition with a custom title, a nested admonition, a see-also box and the three version
notes; linked from `demo/docs/index.rst` and listed in its hidden toctree. CHANGELOG line.

## US2 — Code is highlighted in the site's theme (P1)

Issue: #31. Delivers FR-006, FR-007, FR-015 (code); SC-005 (code).

### T003 — Pygments tokens on theme colours, with captions, numbers and emphasis

**Files**: `mvp_sphinx/static/mvp_sphinx/content.css`, `tests/test_static/test_content_css.py`,
`demo/docs/content-tour.rst`, `CHANGELOG.md`

Plan, *The stylesheet* items 1 and 3. Tests: every code pair is ≥ 4.5:1 in both themes: code
text, each token colour and the line-number colour, each on `--mvp-sphinx-code-bg` and on
`--mvp-sphinx-code-emphasis-bg` (FR-015). Tune each mix toward base-content until both themes pass
with headroom; record the chosen mixes in `decisions.md` only if a role had to move far from its
hue. Demo: Python, a shell session and JSON; one block with a caption, `:linenos:` and
`:emphasize-lines:`; one block in a language Pygments cannot lex (`.. code-block:: text` or an
unknown lexer that builds without a warning). CHANGELOG line.

## US3 — Wide content stays inside the page (P2)

Issue: #33. Delivers FR-008, FR-009; SC-003.

### T004 — Tables wrapped in a focusable scrolling area

**Files**: `mvp_sphinx/page_body.py`, `mvp_sphinx/views.py`,
`mvp_sphinx/templates/mvp_sphinx/page.html`, `mvp_sphinx/locale/en/LC_MESSAGES/django.po`,
`tests/test_page_body.py`, `tests/test_views.py`, `tests/sphinx/guide/content.rst`, `README.md`

Plan, *The body rewrite* (the table half) and *The page template*. Tests, class
`TestBodyRewriter` on literal markup: a table is wrapped in an element with `tabindex="0"`,
`role="region"` and an `aria-label`; a captioned table's label is its caption text; an
uncaptioned table's label is not empty; a table nested in a table is wrapped once; a table inside
an admonition or a list item is wrapped; caption text holding `&amp;` or `"` is escaped once in
the attribute; markup with no table comes back byte-for-byte, entity references (`&amp;`,
`&#8217;`) and comments included. `tests/test_views.py`: the fixture page's tables render
wrapped (the view uses the rewrite). README: `BodyRewriter` in *How pages look*, what it adds and
that a `PageView` subclass gets it. Docstrings per `docs/contributing/standards/code-documentation.md`.

### T005 — Tables, code and images fit the reading area

**Files**: `mvp_sphinx/static/mvp_sphinx/content.css`, `demo/docs/content-tour.rst`,
`demo/docs/_static/` or an existing demo image, `CHANGELOG.md`

Plan, *The stylesheet* item 4. No test (layout). Demo: a table wider than a phone, a table inside
a list, a code line longer than the reading area, an image wider than the reading area and a
figure with a caption. CHANGELOG line.

## US4 — Headings carry a link a reader can copy (P2)

Issue: #35. Delivers FR-010 (headings), FR-011, FR-018; SC-004.

### T006 — Heading links carry an accessible name

**Files**: `mvp_sphinx/page_body.py`, `tests/test_page_body.py`, `tests/test_views.py`,
`tests/sphinx/guide/content.rst`, `README.md`

Plan, *The body rewrite* (the heading-link half). Tests: a heading's link is labelled with its
`title` and the heading's text; a heading holding inline code is labelled with the code's text
too; a link with no `title` is labelled with the text alone; heading text with `&amp;` is
unescaped then escaped once; the link's `href` is untouched. `tests/test_views.py`: every heading
link on the fixture page has an `aria-label` holding its heading's text, and its `href` is the
heading's anchor on the page. README line.

### T007 — Heading links revealed on hover and focus, anchors clear of the top bar

**Files**: `mvp_sphinx/static/mvp_sphinx/content.css`, `demo/docs/content-tour.rst`, `CHANGELOG.md`

Plan, *The stylesheet* item 5. No test (appearance and motion). Demo: enough sections that
following a heading link scrolls. CHANGELOG line.

## US5 — Glossaries, cross-references and interface references look like the site (P3)

Issue: #38. Delivers FR-010 (glossary terms), FR-012, FR-013.

### T008 — Glossary terms, cross-references, keys, labels and menu paths

**Files**: `mvp_sphinx/static/mvp_sphinx/content.css`, `tests/test_page_body.py`,
`tests/sphinx/guide/content.rst`, `demo/docs/content-tour.rst`, `CHANGELOG.md`

Plan, *The stylesheet* item 6. Test: a glossary term's link (`<dt id="term-…">`) is labelled with
its `title` and the term's text. Demo: a glossary, cross-references to its terms and to another
page, `:kbd:`, `:guilabel:` and `:menuselection:`. CHANGELOG line.

---

## Coverage

| Requirement | Tasks |
|---|---|
| FR-001 | T001 (prose already styles it; research R2) |
| FR-002, SC-001 | T001, T002 |
| FR-003 | T001 |
| FR-004, FR-005 | T002 |
| FR-006, FR-007 | T003 |
| FR-008, FR-009, SC-003 | T004, T005 |
| FR-010, SC-004 | T006, T008 |
| FR-011, FR-018 | T007 |
| FR-012, FR-013 | T008 |
| FR-014, SC-002 | T001–T003 (every colour is a theme custom property) |
| FR-015, SC-005 | T002, T003 |
| FR-016 | T001, T002 |
| FR-017, SC-006 | T001 |
