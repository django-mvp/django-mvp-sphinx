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

## 2026-09-30T00:54:14Z · Implementer US1 · T001

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

## 2026-09-30T00:58:38Z · Implementer US1 · T002

Did: `SearchView` in `views.py`; `PageView.get_context_data` adds `search_url`; `search/` pattern in
`DocumentationApp.urls` ahead of the catch-all; `search_form.html` component; `search.html` results
page (results, no-match and unavailable states); one line in `page.html`; `search_app` fixture;
`TestSearchForm`, `TestSearchResults` (`test_views.py`), `TestSearchUnderTheReaderRule`
(`test_mounted.py`), `TestDocumentationSearch` (`test_demo.py`); `/docs/search/` removed from
`TestSphinxsOwnPages` (declared edit); message catalogue refreshed with `makemessages -l en`;
README Search subsection, CHANGELOG entry, CONTEXT.md "Search data" and "Results page". Decision D21.
Verified: `uv run pytest tests/test_search.py tests/test_views.py tests/test_mounted.py
tests/test_demo.py -q` → 252 passed. Red step: 26 of the new view tests failed before the view and
templates existed. Mutation probes (each restored): form removed from pages → 18 failed; `search/`
route removed → 33; query unescaped → 1; result title unescaped → 1; form method post → 11; no
`role="status"` → 4; field renamed → 21; result href wrong → 5. Not probed: the reader rule (the
mount wraps every pattern, and I found no seam to route the view around it without editing
django-mvp). `pre-commit run --all-files` passes.
Next: US2 (T003) and US3 (T004) in a later dispatch.
Watch: `results()` still returns empty `anchor` and `passage`; the template already renders a passage
when there is one. The unavailable state exists and is reachable, but has no test yet (T004).

## 2026-09-30T01:08:00Z · Implementer US2+US3 · T003

Did: `DocsSearch.results()` tiers each match (title holds every word, then a section heading of
`alltitles` with an anchor, then the rest) and sorts by tier, title, document name; new
`holds()`, `sections()`, `passage()` and `PageText` in `mvp_sphinx/search.py`; the result's
`anchor` and `passage` are filled. `search.html` and `SearchView.href` needed no change. Tests:
`TestResultOrder`, `TestSectionLink`, `TestPassage`, `TestPageText` (`test_search.py`),
`TestSearchResultDetails` (`test_views.py`). README Search section and CHANGELOG entry updated.
Decision D22.
Verified: `uv run pytest tests/test_search.py tests/test_views.py -q -k "Search or Passage or
Section or PageText"` → 138 passed, 2 failed. The two failures are T001 tests that assert the
pre-T003 behaviour (`test_a_result_has_the_page_title_and_path_and_no_section_or_passage`,
`test_results_are_ordered_by_title_then_document_name`); not edited, see D22 and the report.
Red step: collection failed on the missing `PageText`; then 12 of the new search tests failed on
missing behaviour; the four view tests that depend on the new `search.py` failed against the old
one. `uv run mypy` and `uv run pre-commit run --all-files` pass.
Next: T004.
Watch: the two stale US1 tests need a Forge decision before the tree is green.

## 2026-09-30T01:09:00Z · Implementer US2+US3 · T004

Did: tests only, in `tests/test_views.py`: `TestSearchAfterARebuild`, `TestTwoApps`,
`TestUnavailableSearch`, `TestSearchOfAMissingBuild`, `TestSearchWithoutSphinx`,
`TestSearchOfAVeryLongQuery` (30 tests). No production file changed. Decision D23.
Verified: `uv run pytest tests/test_views.py -q -k "TestSearchAfterARebuild or TestTwoApps or
TestUnavailableSearch or TestSearchOfAMissingBuild or TestSearchWithoutSphinx or
TestSearchOfAVeryLongQuery"` → 30 passed on first run (the FS-002 T005 precedent). Mutation probes,
each restored: search data cached across requests → 7 failed; view reads another app's build → 2;
unavailable drawn as no match → 6; missing-build 404 removed → 1; `import sphinx.util` inside
`results()` → 1; long query rejected → 3. A module-level `import sphinx.util` is not caught, because
the blocked-Sphinx test only affects imports after it runs (D23).
Next: full verify, report.
Watch: the two T001 tests named in T003's entry still fail.

## 2026-09-30T01:13:38Z · Forge · S4 acceptance and S5 converge

Did: US1 accepted (receipts ok; forge verify green, 406 tests; tamper-check flagged only the declared
TestSphinxsOwnPages edit). The docs gate asked for DocsSearch and SearchView on a docs page: ADR 0005
written. US2+US3: T003 came back blocked on two US1 tests that pinned placeholder results; Forge
corrected them (D24). Ledger rows for T003/T004 written from the report. Both stories accepted;
verify green, 483 tests. S5: converge found every FR and SC with a test; cleanup folded the
document-number check into DocsSearch.is_document; ADR verdicts written on all 24 decisions (12
graduated to ADR 0004 or 0005). Restamped the US1 implementer's two progress headings from their
commits' UTC author times.
Next: S6 review.

## 2026-09-30T01:23:34Z · Forge · S6 review and S7 ready

Did: two reviewers (correctness+spec+docs; security, for the new dependency and the query input),
receipts ok. Correctness: request changes, REV-001 high (passages re-stemmed every word) and REV-002
medium (passage opened with the page title), both fixed test-first by Forge with two lows (D25).
Security: approve, SEC-001 low accepted and named in ADR 0005. Review outcome recorded on #54.
forge verify green, 484 tests. PR body rewritten with the Closes block (#10, #42, #43, #44), PR
marked ready, all nine CI checks green, story-comment gate green.
Walkthrough: required (5 user-facing paths). Demo guides built in this worktree, accounts seeded,
the staff guide's searchindex.json moved out (/tmp/fs007-staff-searchindex.json) so its search
shows the unavailable state; rebuild the staff guide to restore it.
Next: walkthrough by the orchestrator, then its record, then the merge gate.
