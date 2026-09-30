# Research — 006 Let the project decide who can read its documentation

Every claim about a dependency is read from the code the project resolves: the worktree's
`.venv/lib/python3.13/site-packages/` (django-mvp 0.25.0, django-flex-menus 0.4.6, Django 6.1.1),
plus the django-flex-menus 0.4.5 wheel from the package index for the declared floor.

## R1 — `MountedApp.check` already is a reader rule

`mvp/mounted.py` (django-mvp 0.25.0):

- `check: bool | Callable[[HttpRequest], bool] = True` (l. 127). Documented at l. 99–106: `True`
  everyone, `False` no one, or `callable(request) -> bool`.
- `is_setting("check")` is always true (l. 157–158), so `DocumentationApp(check=...)` is accepted
  by keyword. A plain function set on a subclass is made a `staticmethod` (l. 131–137).
- `bind()` wraps **every** view the mount resolves, sync or async, and calls `refusal(request)`
  before the view (l. 177–193). `MountedAppResolver.resolve()` applies it to every match
  (l. 414–419). So pages, the front page, images and downloads, and any view a later feature adds
  under the mount are all covered (FR-004), and the refusal cannot see what the build holds
  (FR-007).
- `refusal()` (l. 326–340): admitted → `None`. No user or anonymous →
  `redirect_to_login(request.get_full_path())`. Signed in → `raise PermissionDenied`, which the
  host's 403 handler answers (FR-005, FR-006).
- `has_permission()` (l. 311–324) returns `bool(check(request))` for a callable, so an exception
  raised by the rule propagates as a server error (FR-012). It keeps nothing between requests; the
  only cache is `request._mounted_app`, on the request object (l. 251–267) (FR-009).
- `menu_item()`'s entry check is `request is None or app.has_permission(request)` (l. 230–231), so
  the host's menu entry follows the rule (FR-008). `for_request()` drops a refused app
  (l. 263–266), so a refused request, including the 403 page itself, draws no app name, title
  segment or app menu. `claiming_menu()` skips refused apps (l. 293–294), so the app's menu
  (where #5 puts the contents) never claims a host page for a refused reader.
- There is no staff or superuser bypass anywhere in the class (D7).

The django-mvp docs (`docs/mounted-apps.md`, *Limiting who can reach an app*) describe the same
contract, so this package can point at it rather than restate it.

## R2 — `flex_menu.checks` gives the no-code choices

`flex_menu/checks.py`, identical names in 0.4.5 (wheel) and 0.4.6 (installed):

- `user_is_authenticated(request, **kwargs)` (l. 26): `request.user.is_authenticated`, and false
  when there is no `request.user`.
- `user_is_staff(request, **kwargs)` (l. 12).
- `user_in_any_group(*groups)` (l. 68) and `user_has_any_permission(*perms)` (l. 97): factories
  returning a check. Both return false for an anonymous user.

Each takes `(request, **kwargs)`. `MountedApp.has_permission` calls `check(request)` alone, which
the `**kwargs` signature accepts. flex-menus' own `MenuItem.check` calls `_check(request, **kwargs)`
(`flex_menu/menu.py` l. 358–372), so the same function works as a menu check as well.

django-flex-menus is already a declared dependency, imported directly for each app's `Menu`
(`pyproject.toml`), so pointing hosts at `flex_menu.checks` adds nothing to the dependency tree.

## R3 — Probe on this branch's base (c1ae4f8)

A throwaway test module, deleted afterwards, mounted the demo's app with `check` set by
`monkeypatch`:

| Request | Rule | Answer |
|---|---|---|
| `/docs/`, `/docs/page/`, `/docs/section/nested/page`, `/docs/nope/`, `/docs/nope`, `/docs/_images/pixel.png` | `user_is_authenticated`, anonymous | 302 → `/accounts/login/?next=<address>`, empty body, every one |
| `/docs/page/`, build dir missing | same | same 302 |
| `/docs` (prefix, no slash) | same | 301 → `/docs/` (`CommonMiddleware`, before any mount; D11) |
| `/docs/page/` | `user_in_any_group("staff")`, signed in, not a member | 403, templates `403.html` → `mvp/error_base.html` → `mvp/base.html`, page text absent |
| overview page | same | no `href="/docs/"` |
| after adding the user to the group, same client | same | `/docs/page/` 200, overview shows the entry |
| `/docs/page/?x=1` then POST the login form at the redirect's address | `user_is_authenticated` | login 302 → `/docs/page/?x=1` |
| `/docs/page/` and the overview page | a rule that raises | 500 for both |

So every requirement already holds on the base. The feature's work is to pin it with tests,
document it, and show it in the demo.

## R4 — The sign-in round trip is Django's

`redirect_to_login(next, login_url=None)` (`django/contrib/auth/views.py` l. 184) builds
`LOGIN_URL?next=<address>`. `LoginView.get_success_url()` → `get_redirect_url()` (l. 40–58) honours
`next` when `url_has_allowed_host_and_scheme` passes, which a same-site path does. The demo and the
suite leave `LOGIN_URL` at its default `/accounts/login/`, served by
`django.contrib.auth.urls` in `demo/urls.py`. SC-005 is demonstrable through the demo's own
sign-in view.

## R5 — Why `/docs` is not the app's to answer

`mount("docs/", ...)` builds a `RoutePattern("docs/")` (`mvp/mounted.py` l. 439–448), which `/docs`
does not match. With nothing matching, `CommonMiddleware.process_response` sees the 404 and, since
`/docs/` resolves, redirects there (`django/middleware/common.py` l. 62, 100). That runs for every
reader, whatever is mounted and whatever the build holds, so it reveals nothing about pages. The
next request, `/docs/`, is refused as usual. Every address the documentation app itself answers
starts with the prefix and its slash.
