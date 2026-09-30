# Progress — 007 Search the documentation

## 2026-09-30T00:38:00Z · S3 plan

Did: queue row for FS-007 read `blocked` on the sibling pull requests (FS-003, FS-006) only; the
orchestrating session claimed this feature for this run and several features are built in parallel
tonight, so the row is treated as ready. `delivered_since` is empty, so the spec-against-spec check
is skipped. Worktree `wt-sphinx-007` off origin/main f38982b, identity bound. Research read from a
real JSON build (Sphinx 9.1.0) and Sphinx 8.1.3's stemmer; plan.md, research.md, tasks.md: 3 stories,
4 tasks. Decisions D11–D18 appended.
Analyze: FR-001–FR-015 and SC-001–SC-005 each map to at least one task; every edge case in the
spec has a test in T001–T004. No CRITICAL findings.
Next: design review.

## 2026-09-30T01:20:00Z · Implementer US1 · T001

Did: `mvp_sphinx/search.py` with `DocsSearch` (search data, stopwords from the build, stemmers by
language, `words`, `keys`, `results`, `path`); new source `tests/sphinx/search/` (eleven pages);
`search_build` fixture; `tests/test_search.py`; `snowballstemmer>=2.2` in dependencies, `uv.lock`
updated. Decisions D20.
Verified: `uv run pytest tests/test_search.py -q` → 55 passed. Red step: collection failed on the
missing module before `search.py` existed. Mutation probes (each broke the code, then restored):
no stemmers → 7 failed; no case-fold → 1; no stopwords → 3; any-word instead of all-words → 6;
no `titleterms` → 10; digits kept → 2; no word cut → 1; no ordering → 1. `uv run pre-commit run
--all-files` passes.
Next: T002, the view, URL, form and results page.
Watch: `results()` returns `anchor=""` and `passage=""` until T003; `data()` keeps `alltitles` only as
a dict, and T003 has to check the shape of its entries itself.
