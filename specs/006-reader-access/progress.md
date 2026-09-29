# Progress — 006 Let the project decide who can read its documentation

## 2026-09-29T23:46:00Z · S3 plan

Did: no feature delivered since this spec landed (queue `delivered_since` empty), so no
spec-against-spec re-read. The prototype has no access rule. django-mvp 0.25.0's `MountedApp.check`
already implements every requirement, and flex-menus ships the no-code rules. Both were probed on
the base (research R3). Plan: no runtime code, tests pin each FR, docs, and a staff-only demo app.
3 stories, 5 tasks. Decisions D10–D12 appended.
Analyze: FR-001..FR-012 and SC-001..SC-005 each map to a task (plan, *What already holds*); every
spec edge case is in the refusal matrix (T002/T003) or T003's `check=False`/raising cases.
Next: design review.

## 2026-09-29T23:56:21Z · S3R design review

Did: one reviewer, three lenses; request_changes, 1 high + 3 medium + 2 low, all verified by the
orchestrator against the code (no handbook entry in AppMenu; no registration/login.html) and
applied as plan/tasks edits. D13 (raising rule on host pages) and D14 (demo sign-in) appended.
Next: plan notice, then US1.
