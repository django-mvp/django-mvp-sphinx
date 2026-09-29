# Implementation Plan: Let the project decide who can read its documentation

**Branch**: `006-reader-access` | **Date**: 2026-09-30 | **Spec**: [spec.md](spec.md) ·
**Research**: [research.md](research.md) · **Tasks**: [tasks.md](tasks.md)

## Summary

A documentation app's reader rule is the `check` it already inherits from django-mvp's
`MountedApp`. `check` is `True` (everyone, the default), `False` (no one) or a function of the
request, and django-mvp already asks it on every request, before the view runs. When it says no,
the menu entry disappears, the app is left out of the shell, an anonymous visitor goes to the
sign-in page and comes back afterwards, and a signed-in person gets a 403 (research R1, R3).
"Signed-in people only" and the common own-rule cases are ready-made functions in
`flex_menu.checks`, which the package already depends on: `user_is_authenticated`,
`user_in_any_group(...)`, `user_has_any_permission(...)` (R2). A host writes
`DocumentationApp(build_dir=..., check=user_is_authenticated)` and nothing else.

So this feature adds **no new runtime code** (D10). It adds the tests that hold every requirement
of the spec against the mounted app as a host project uses it, documents `check` on
`DocumentationApp` and in the README, adds the glossary term, and gives the demo a second
documentation app open only to staff, so every refusal state can be seen with the standard
accounts (D12). The prototype had no access rule (decisions.md, *Starting point*), so nothing here
comes from it.

## Technical Context

**Language/Version**: Python 3.12+, Django 5.2 / 6.0 / 6.1

**Primary Dependencies**: unchanged. django-mvp ≥ 0.25.0 is the first version with
`MountedApp.check` (R1, read from the installed 0.25.0). django-flex-menus ≥ 0.4.5 already ships
`flex_menu.checks` with the four functions this plan names (R2, checked in the 0.4.5 wheel as well
as the installed 0.4.6).

**Storage**: none. The tests create users and groups through factories.

**Testing**: pytest + pytest-django through `client`, against the demo's documentation app and the
suite's second app (`tests/urls.py`), with `check` set per test through `monkeypatch`.

**Project Type**: reusable Django app (library).

**Constraints**: the rule is asked on every request and nothing is cached across requests
(FR-009); a refusal happens before `PageView` runs, so it cannot depend on what the build holds
(FR-007).

## Constitution Check

| Article | How the plan meets it |
|---|---|
| I Testing | Every task test-first against the spec's scenarios, in `tests/test_mounted.py` (the rule belongs to `DocumentationApp`) and `tests/test_demo.py` (demo wiring). Users and groups come from one factory per model in `tests/factories.py`, wrapped by fixtures in `conftest.py`. No test reads wording or layout; content is found by fixture data. |
| II Simplicity | No new code path. The rule is django-mvp's `check`, and the no-code choices are flex-menus functions already installed. |
| III Anti-abstraction | No wrapper around `check`, no second setting, no alias (D10). |
| IV Integration-first | Every acceptance test goes through `client` against a mounted app, the way a host touches it. |
| V Security | Authorisation is the subject. S3R threat-models it. The refusal matrix (every address shape, missing build, slashless, unknown) is tested so FR-007 cannot regress. No staff bypass (D7). |
| VI Documentation | `DocumentationApp` docstring gains `check`. README gains *Choosing who can read it*, extended per story. CHANGELOG Unreleased entry. CONTEXT.md gains *Reader rule*. |
| VII Dependencies | None added. `flex_menu` is already a declared, directly imported dependency. |
| VIII i18n | The demo's new app name is `gettext_lazy`. |
| IX Data model | No models. |
| X Cohesion | Nothing new to group. |
| XI Compatibility | Additive. An app mounted without `check` behaves exactly as before (SC-004). |
| XII Scope | One rule per documentation app. Two audiences are two apps, each with its own build. |
| XIII Host look | Refusals are the host's own sign-in page and `403.html`. |

No violations. Complexity tracking is empty.

## Design

### Public API (documentation only; no new names)

```python
from flex_menu.checks import (
    user_has_any_permission,
    user_in_any_group,
    user_is_authenticated,
)
from mvp_sphinx.mounted import DocumentationApp

# everyone (default, unchanged)
docs = DocumentationApp(build_dir=BASE_DIR / "docs" / "_build" / "json")

# signed-in people only: no code of the host's own
docs = DocumentationApp(build_dir=..., check=user_is_authenticated)

# a rule of the host's own: a group, a permission, or any function of the request
docs = DocumentationApp(build_dir=..., check=user_in_any_group("Support"))
docs = DocumentationApp(build_dir=..., check=user_has_any_permission("support.view_ticket"))


def staff_only(request):
    return request.user.is_staff


handbook = DocumentationApp(build_dir=..., namespace="handbook", check=staff_only)
```

`DocumentationApp`'s class docstring lists `check` in its Args: the three choices, that the rule
covers every address under the app and its menu entry, that it is asked on every request, and that
an error it raises is a server error. No code in `mvp_sphinx/` changes otherwise.

### What already holds, and the test that pins it

Each line is a behaviour of `MountedApp` (R1) that this package now promises, so each gets a test
through a documentation app:

| Requirement | Mechanism (R1) | Pinned by |
|---|---|---|
| FR-001, FR-011 | `check` is per instance | US3: two apps, two rules |
| FR-002, SC-004 | `check = True` default | US1: anonymous reader served, entry shown |
| FR-003, SC-001 | `check=user_is_authenticated` / own callable | US1, US2 |
| FR-004 | `bind()` wraps every view the mount resolves, files included | refusal matrix |
| FR-005, SC-005 | `refusal()` → `redirect_to_login(get_full_path())` | US1: redirect, then sign-in round trip |
| FR-006 | `refusal()` → `PermissionDenied` → host `403.html` | US2 |
| FR-007, SC-002 | refusal runs before `PageView` | refusal matrix |
| FR-008, SC-003 | `menu_item()` entry check, `for_request()`, `claiming_menu()` | US1, US2, US3 |
| FR-009 | `has_permission()` per request; the cache lives on the request object only | US3 |
| FR-010 | an admitted request reaches the unchanged view | US1, US2 |
| FR-012 | `bool(check(request))` lets the exception propagate | US2 |

**Refusal matrix** (FR-004, FR-007, spec edge cases): for an excluded anonymous reader, each of
the front page, a page, a nested page, an image, a download, an unknown address, a slashless page
address, a slashless unknown address, and a page of an app whose build does not exist answers the
same way: a redirect to `LOGIN_URL` whose `next` is the requested address, with an empty body. For
an excluded signed-in reader, the same addresses answer 403 from the host's `403.html` and carry
none of the page's fixture text or the file's bytes.

**What stays outside the app's addresses** (D11): `/docs` without its slash never reaches the
mount. Django's `CommonMiddleware` redirects it to `/docs/` for every reader, before any
documentation app runs, and the slashed address is then refused. That redirect says nothing about
which pages exist. Tests do not pin it, because it is the host's middleware.

### Demo (US3)

A second documentation app, **Staff guide**, open only to staff (D12). It shows every refusal
state with the standard accounts: anonymous → sign in, `regular.user@example.com` → 403 and no
entry, `staff.user@example.com` and `super.user@example.com` → served.

- Source `demo/staff_guide/` (`conf.py`, `index.rst`, one more page), built to
  `demo/staff_guide/_build/json` (gitignored).
- `demo/mounted.py`: `staff_guide = DocumentationApp(build_dir=..., name=_("Staff guide"),
  namespace="staff_guide", check=user_is_staff)` (from `flex_menu.checks`).
- `demo/urls.py`: `mount("staff-guide/", staff_guide)`. `demo/menus.py`: `staff_guide.menu_item()`.
- AGENTS.md: the second build command beside the first.

The demo's `/docs/` stays open to everyone, so every existing test and the README quickstart keep
their meaning. Every edit to shared demo files adds lines and moves none, because FS-002 and FS-004
are editing the same files in parallel.

### Tests and fixtures

- `tests/factories.py` (new): `UserFactory` (`username` by `factory.Sequence`, password set with
  `factory.PostGenerationMethodCall("set_password", "password")`) and `GroupFactory` (`name` by
  sequence). Variants (`is_staff=True`) at the call site.
- `tests/conftest.py`: `user` fixture → `UserFactory()`; `group` fixture → `GroupFactory()`.
- `tests/test_mounted.py`: new classes `TestEveryoneByDefault`, `TestSignedInOnly`,
  `TestRefusal` (the matrix), `TestOwnRule`, `TestSeveralApps`. `check` is set with
  `monkeypatch.setattr(app, "check", ...)` on the fixture's app instance, so it is undone after
  each test.
- Host pages are the demo's overview page (`reverse("overview")`). Menu entry presence is the
  link to the app's front page in the rendered page. Content absence is the fixture page's own
  text and the file's bytes.
- `tests/test_demo.py`: `TestStaffGuideEntry`: absent for anonymous and for a regular user,
  present for staff, on the overview page.

### Story order

US1 → US2 → US3, one at a time, in this working tree. All three add classes to
`tests/test_mounted.py` and paragraphs to the README section, so they cannot run in parallel
without colliding.

## Complexity Tracking

Empty.
