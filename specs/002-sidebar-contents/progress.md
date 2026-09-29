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

## 2026-09-29T23:58:00Z · S3R design review

Did: one reviewer, three lenses; request_changes, 2 high (ARCH-001 non-atomic children swap →
per-menu lock; SPEC-001 planned `menu-active` class assertion → removed), 2 medium (ARCH-002 temp
file mode → fixed sibling name + write_text; ARCH-003 loose functions → NavigationWriter class and
DocsBuild staticmethod), 4 low (SEC-001 url filter removed; SPEC-002 atomic-write test removed;
SPEC-003 `sections` → `groups`; ARCH-004 catch ValueError, invalid UTF-8 case). All applied as
plan/research/tasks/decisions edits and checked against each finding's evidence (D8).
Next: plan notice, then US1.
