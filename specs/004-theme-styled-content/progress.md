# Progress — 004 Make user-guide content look like the rest of the site

## 2026-09-30 · S3 plan

Did: branch `004-theme-styled-content` from origin/main (c1ae4f8) in its own worktree
(`wt-sphinx-004`), identity bound to the bot. The queue showed this feature waiting on FS-002's
open pull request; the orchestrating session claimed it for this run as one of three parallel
builds (FS-002, FS-004, FS-006), so it was treated as ready. `delivered_since` empty, so no
spec-against-spec re-read. plan.md, research.md, tasks.md written from a probe build of every
construct (Sphinx 9.1.0) and django-mvp's installed stylesheet: 5 stories, 8 tasks. Decisions
D1–D7.
Next: design review.

## 2026-09-30T00:25+02:00 · Implementer US1 · T001

Did: `mvp_sphinx/static/mvp_sphinx/content.css` (colour-roles rule left empty for T002),
`page.html` extends `styles` with `{{ block.super }}` and the stylesheet link, `{% load static %}`,
`mvp-sphinx-content` on the article. Fixture `tests/sphinx/guide/content.rst` (orphan). README
*How pages look*, CHANGELOG line.
Verified: `uv run pytest tests/test_views.py::TestContentStyling` red first (link test failed, the two
absence tests passed as guards), then green; `uv run pytest tests/test_views.py` 58 passed;
`uv run pre-commit run --all-files` passed.
Next: T002, admonition colours and the stylesheet tests.
Watch: none.

## 2026-09-30T00:55+02:00 · Implementer US1 · T002

Did: colour roles and admonition/version-note rules in `content.css` (five meanings, muted
colour); `tests/test_static/` with `TestContentStylesheet` (no literal colour, scoped selectors,
contrast in the light and dark themes read from django-mvp's stylesheet; the OKLCH/color-mix/WCAG
helpers sit on `ColourMath`, the rule reader on `Stylesheet`); `non-mirror-paths` in
`pyproject.toml`; fixture page gains every meaning; demo `content-tour.rst` linked from the index
and its hidden toctree; CHANGELOG line.
Verified: tests red first on the empty stylesheet (literal-colour and four contrast tests), then
green: `uv run pytest tests/test_static` 10 passed. Probed by mutation: 90% warning tint and a 30%
muted mix fail the contrast tests, an appended `#fff` unscoped rule fails the literal and scope
tests. `uv run sphinx-build -b json -W demo/docs demo/docs/_build/json` exit 0.
Next: full verify.
Watch: the theme parse takes the first `[data-theme=NAME]` rule holding `--color-base-100`.

## 2026-09-30T02:20+02:00 · Implementer US2 · T003

Did: code colour roles (background, text, emphasis background, line number, comment, keyword,
string, number, name, inserted, deleted, error) added to the colour-roles rule in `content.css`;
Pygments short classes grouped onto them; `.highlight pre`, `.hll`, `.linenos` and
`.code-block-caption` rules. Token roles are a theme role at 40% over base-content; comment and
line number reuse the muted colour; the emphasis background is warning at 15% over base-200.
`TestCodeStylesheet` in `tests/test_static/test_content_css.py` measures every code text role on
both code backgrounds in both themes. Demo: Python, console, JSON, a captioned block with line
numbers and emphasis, and a `text` block on `content-tour.rst`. CHANGELOG line.
Verified: `uv run pytest tests/test_static/test_content_css.py` red first (roles test failed on the
missing roles), then 15 passed; probed by mutation (string at 95% success fails the light cases);
`uv run sphinx-build -b json -W demo/docs /tmp/demo-json` exit 0; pre-commit passed.
Next: full verify.
Watch: lowest measured pair is the number colour on the emphasised background in the light theme
(about 6.5:1). No role moved far from its hue, so no decisions.md entry.

## 2026-09-30T02:40+02:00 · Implementer US3 · T004

Did: `mvp_sphinx/page_body.py` with `BodyRewriter` (stdlib `HTMLParser`, records insertion offsets
from `getpos()`, result is the original string with insertions spliced in); wraps each outermost
table in a focusable named region, label from the caption or `gettext_lazy("Table")`, escaped with
`format_html`. `PageView.get` passes the body through it and gives the template `body`;
`page.html` renders `{{ body }}`. Fixture page gains a captioned table, a plain table and a table
in a warning. `Table` msgid added to `django.po` with `makemessages`. README *How pages look*.
Verified: `uv run pytest tests/test_page_body.py` red first (12 failed on a stub that returned the
markup unchanged, 8 guards passed), then 20 passed; `uv run pytest tests/test_views.py::TestWideContent`
red (2 failed), then `uv run pytest tests/test_page_body.py tests/test_views.py` 80 passed. Probed by
mutation: dropping the line offset from the position and an off-by-one on the end tag each fail
a test (the first only after the wrapper-placement assertion was added). `uv run pre-commit run
--all-files` passed.
Next: T005, the stylesheet rules and demo.
Watch: `mark_safe` in `PageView.get` carries a `noqa: S308`; the body is the host's own build.

## 2026-09-30T02:55+02:00 · Implementer US3 · T005

Did: wide-content rules at the end of `content.css` (table region scrolls sideways with a focus
outline from `--color-primary`, `pre` scrolls, images scale, figures stay in the reading area);
`content-tour.rst` gains a wide table, a table in a list item, a long code line, an image and a
figure, both images the existing `shell.png` set to 2400px wide (no new binary). CHANGELOG line.
Verified: `uv run sphinx-build -b json -q -W demo/docs /tmp/demo-json-us3b` exit 0;
`uv run pytest tests/test_static tests/test_demo.py` 19 passed (stylesheet still has no literal
colour and stays scoped); `uv run pre-commit run --all-files` passed. No test for layout.
Next: full verify.
Watch: the layout itself was not looked at in a browser; the demo page is the place to check it.

## 2026-09-30T02:15+02:00 · Implementer US4 · T006

Did: `BodyRewriter` names every `a.headerlink` (`aria-label` inserted just after `<a`): the link's
`title`, a colon, and the text of the element holding it up to the link; the text alone when there
is no title. The parser keeps a stack of open elements (void tags never pushed, an end tag closes
the innermost match) to know the holder. Fixture page gains sections (one heading with inline code
and an ampersand) and a glossary. README paragraph in *How pages look*.
Verified: `uv run pytest tests/test_page_body.py` red first (16 failed on a missing `aria-label`,
22 guards passed), then 38 passed; `uv run pytest tests/test_views.py::TestHeadingLinks` 5 passed
(4 fail with the naming call removed; the fifth is an untouched-`href` guard);
`uv run pytest tests/test_page_body.py tests/test_views.py` 103 passed. Probed by mutation: not
popping closed elements and inserting one character late each fail a test (the second only after
a separator assertion was added). `uv run pre-commit run --all-files` passed.
Next: T007, the stylesheet and demo.
Watch: a link with neither title nor text gets no label; the fixture build has to stay warning-free.

## 2026-09-30T02:15+02:00 · Implementer US4 · T007

Did: heading-link rules at the end of `content.css` (muted, no underline, opacity 0 with a 150ms
transition, revealed on hover of h1-h6, dt, caption, figcaption and `.code-block-caption` and on
the link's own `:focus-visible`, no transition under reduced motion, `[id]` gets
`scroll-margin-top: 5rem`); `content-tour.rst` gains a *Headings* section of four long subsections,
one with inline code. CHANGELOG line.
Verified: `uv run sphinx-build -b json -q -W demo/docs /tmp/demo-us4` exit 0; `uv run pytest
tests/test_static tests/test_demo.py` 19 passed (no literal colour, all rules scoped, contrast);
`uv run pre-commit run --all-files` passed. No test for appearance or motion.
Next: full verify.
Watch: the reveal, the transition and the scroll offset were not looked at in a browser; the demo
content tour is the place to check them.

## 2026-09-30T02:30+02:00 · Implementer US5 · T008

Did: `content.css` gains bold glossary terms (`dl.glossary dt`), a bordered chip for `.guilabel`
(`--color-base-300` border, `--radius-field`) and weight 600 for `.menuselection`. No rule for the
definition indent (the host's prose style already gives `dd` 1.625em), for `kbd` (daisyUI `.kbd`
styles it) or for cross-references (ordinary links through prose). `content-tour.rst` gains a
*Glossaries and interface references* section: a three-term glossary, `:term:` references, a
`:doc:` reference, `:kbd:`, `:guilabel:` and `:menuselection:`. CHANGELOG line.
Verified: `uv run sphinx-build -b json -q -W demo/docs /tmp/demo-us5b` exit 0 (fresh directory);
`uv run pytest tests/test_static tests/test_demo.py` 19 passed (no literal colour, rules scoped);
`uv run pre-commit run --all-files` passed. No test for appearance.
Next: full verify.
Watch: the bold terms, the label chip and the key caps in running text were not looked at in a
browser; the content tour is the place to check them, including in the dark theme.

## 2026-09-30 · S5 converge

Did: all five stories done and accepted on independent verify and tamper-check. Main had not
moved. Cleanup: one condition in BodyRewriter computed once; changelog tightened to what changes
for an adopter; README override example loads `static`. ADR 0002 graduated from D1, D2 and D5;
every decision verdicted. No migrations. R3 marked delivered and rewritten to its delivered form.
Next: review.
