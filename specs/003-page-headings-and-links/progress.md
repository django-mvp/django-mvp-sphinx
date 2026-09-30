# Progress — 003 Show a page's headings beside it, and links to the previous and next page

## 2026-09-30T00:40:00Z · S3 plan

Did: queue row for FS-003 read `in-flight` because the orchestrating session claimed it for this
run; no pull request built it yet. Features delivered since the spec landed (FS-001, FS-002) re-read
against it: no contradiction (D1). The old local spec branch was reset to origin/main (044ef54);
worktree `wt-sphinx-003`, identity bound. Baseline `forge verify` green on 044ef54. Planned from the
reviewed prototype (django-mvp `wip/sphinx-docs-in-sidebar`) without django-sphinx-view:
research.md (premises read from Sphinx 9.1.0, serializinghtml 2.0.0, django-mvp 0.25.0 as
installed), plan.md, tasks.md: 3 stories, 5 tasks. Decisions D1–D5 appended.
Analyze: FR-001–FR-011 and SC-001–SC-004 each map to at least one task; every edge case in the spec
has a fixture page or a test in T001, T002 or T004. No CRITICAL findings.
Next: design review.

## 2026-09-30T00:40:38Z · S3R design review

Did: rebased onto origin/main after FS-004 merged (f38982b); plan revised for its `BodyRewriter`
and article markup; verify green on 6f86d91. One reviewer, three lenses: approve, 0 critical/high,
5 low (ARCH-001 slice titles by offset; ARCH-002 one emptiness guard; ARCH-003 no neighbour shape
check; SPEC-001 demo edit narrowed to settings.rst; ARCH-004 hidden/orphan cases on the contents
source). All applied and checked against their evidence (D6). Receipts green.
Next: plan notice to the orchestrating session, then US1.

## 2026-09-30T00:58:00Z · Implementer US1 · T001

Did: `mvp_sphinx/headings.py` `PageHeadings` (HTMLParser, `convert_charrefs=False`, titles sliced
by offset as `BodyRewriter` computes positions). New source `tests/sphinx/reading/` (index, long,
single, plain; builds with no warnings) and the `reading_build` session fixture.
Verified: red first (`ModuleNotFoundError: mvp_sphinx.headings`), then
`uv run pytest tests/test_headings.py -q` 16 passed; `uv run pre-commit run --all-files` and
`uv run mypy` passed.
Next: T002, the view, page and components.
Watch: `reading_app` is added in T002.
