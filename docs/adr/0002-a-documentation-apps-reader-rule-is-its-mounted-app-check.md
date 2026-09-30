# ADR 0002 — A documentation app's reader rule is its mounted app `check`

**Status:** accepted

## Decision

Who may read a documentation app is decided by the `check` it inherits from django-mvp's
`MountedApp`, and by nothing else. A host sets it by keyword:
`DocumentationApp(build_dir=..., check=...)`. It takes `True` (everyone, the default), `False`
(no one), or a function of the request. The ready-made functions are the ones in
`flex_menu.checks`: `user_is_authenticated` for signed-in people only, and `user_in_any_group(...)`,
`user_has_any_permission(...)` or `user_is_staff` for the common rules of a host's own.

The package adds no setting, wrapper, alias or rule function of its own for this. Everything served
under a documentation app, its menu entry, and anything a later feature adds under the app (search
results included) is governed by that one `check`.

## Why

`check` already does everything the reader-access requirements ask. django-mvp calls it before any
view the mount resolves, so pages, images, downloads and unknown addresses are refused alike, and a
refusal cannot reveal what the build holds. It hides the host's menu entry and keeps the app out of
the shell for a refused reader. It sends an anonymous visitor to sign in and back, and gives a
signed-in person the project's 403 page. It is asked on every request. A documentation app then
behaves exactly like every other mounted app in the host project.

A setting of our own, such as `readers="signed-in"`, would give one app two answers to one question.
A function of our own would duplicate one that django-flex-menus, already a dependency, ships.

## Revisit if

A rule needs something a function of the request cannot see, such as the documentation app itself.
Overriding `has_permission` on a `DocumentationApp` subclass is the route for that. Also revisit if
django-mvp's `check` stops being asked before the view, or starts caching answers across requests.
