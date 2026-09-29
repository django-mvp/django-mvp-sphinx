# Progress — 002 Show the documentation's contents in the app sidebar

## 2026-09-29T23:44:00Z · S3 plan

Did: queue row for FS-002 read `in-flight` because the orchestrating session claimed it for this
run; `delivered_since` is empty, so no spec-against-spec re-read. Planned from the reviewed prototype
(django-mvp `wip/sphinx-docs-in-sidebar`, 6da698a) without django-sphinx-view: research.md (premises
read from Sphinx 9.1.0, serializinghtml 2.0.0, django-mvp 0.25.0, flex-menus 0.4.6 as installed),
plan.md, tasks.md: 3 stories, 7 tasks. Decisions D1–D7 appended.
Analyze: FR-001–FR-020 and SC-001–SC-005 each map to at least one task; every edge case in the spec
has a fixture entry in `tests/sphinx/contents/` or a test in T006/T007. No CRITICAL findings.
Next: design review.
