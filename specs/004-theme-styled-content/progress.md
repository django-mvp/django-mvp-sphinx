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
