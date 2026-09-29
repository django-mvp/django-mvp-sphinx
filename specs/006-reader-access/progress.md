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

## 2026-09-30T00:10:00Z · Implementer US1 · T001

Did: `tests/factories.py` (`UserFactory`, `GroupFactory`) and the `user` and `group` fixtures in
`tests/conftest.py`. Committed with T002's first class, `TestEveryoneByDefault`, which uses them.
Verified: `uv run pytest tests/test_mounted.py -x -q` → 11 passed. With `check=False` set on the
demo's `docs` app (never committed), `TestEveryoneByDefault` fails 5 of 5, so it can fail.
Lint: `uv run pre-commit run --all-files` passed.
Next: T002 rest (`TestSignedInOnly`, `TestRefusal`, demo sign-in route, docs).
Watch: the download link on a page is relative, so tests join it to the page address.

## 2026-09-30T00:25:00Z · Implementer US1 · T002

Did: `TestEveryoneByDefault`, `TestSignedInOnly` and `TestRefusal` in `tests/test_mounted.py`; the
demo's `accounts/login/` route to `SignInView` (`account_login`) ahead of the
`django.contrib.auth.urls` include; `check` in the `DocumentationApp` docstring (no code change in
`mvp_sphinx/`); README section *Choosing who can read it*; CHANGELOG entry; CONTEXT.md *Reader rule*.
Verified: `uv run pytest tests/test_mounted.py -q` → 29 passed. Before the demo route existed, the
sign-in GET and the round-trip POST failed (`TemplateDoesNotExist: registration/login.html`,
`NoReverseMatch: account_login`), so they failed for the reason D14 gives. With the rule replaced by
`True` in a throwaway copy of the file (not committed), 16 of the 18 signed-in and refusal tests
failed; the two that passed are the signed-in reader's cases, which hold with or without a rule.
Lint: `uv run pre-commit run --all-files` passed.
Next: US2 (T003).
Watch: the entry assertions read the sidebar of the overview page, since the page body has no link to
`/docs/`. The `docs/` pages describe no name or behaviour this story touched; `docs/ROADMAP.md` is a
plan and was left alone.
