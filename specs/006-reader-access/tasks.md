# Tasks — 006 Let the project decide who can read its documentation

**Branch**: `006-reader-access` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. The behaviour under test already
exists in django-mvp (research R1), so a new test may pass on first run. For each one, show it
would fail by running it once against a deliberately broken rule or mount (for example, the check
left at `True`), and record that run in the task's evidence. Never commit the break. A task is
done when its tests pass, the tree is green, and the work is committed. Documentation for a public
behaviour lands in the task that introduces it. No test asserts wording, classes or layout: pages
are recognised by their fixture text, files by their bytes, menu entries by the link to the app's
front page.

## Order

**US1 → US2 → US3, one at a time, in one working tree** (plan, *Story order*).

---

## US1 — Keep the documentation for signed-in people (P1)

Issue: #39. Delivers FR-002, FR-003 (signed-in option), FR-004, FR-005, FR-007, FR-008, FR-010;
SC-001 (no-code option), SC-002, SC-003, SC-004, SC-005.

### T001 — User and group factories

**Files**: `tests/factories.py`, `tests/conftest.py`

Plan, *Tests and fixtures*. `UserFactory` and `GroupFactory` (`factory_boy`
`DjangoModelFactory`, `factory.Sequence` for `username`/`name`, password `"password"` through
`PostGenerationMethodCall`). Fixtures `user` and `group` in `conftest.py` wrap them. No test of
its own: T002 onward fail if it drifts.

### T002 — Signed-in only, and everyone by default

**Files**: `tests/test_mounted.py`, `mvp_sphinx/mounted.py` (docstring only), `README.md`,
`CHANGELOG.md`, `CONTEXT.md`, `demo/urls.py`

Plan, *Public API*, *What already holds*, *Refusal matrix*. In `tests/test_mounted.py`:

- `TestEveryoneByDefault` (US1-1, FR-002, SC-004): with `check` left alone, an anonymous
  reader gets the front page, a page, an image and a download, and the overview page shows the
  entry.
- `TestSignedInOnly` with `check=user_is_authenticated` from `flex_menu.checks`: a signed-in
  reader gets each page, image and download with the same status and body as without a rule
  (US1-2, FR-010). An anonymous reader is redirected to `resolve_url(settings.LOGIN_URL)` with
  `next=<requested address>` and an empty body (US1-3, FR-005). Posting the demo's login form at
  that address as the user lands on the requested address, query string included (US1-4,
  SC-005). On the overview page the entry is absent for anonymous (US1-5) and present, leading to
  the front page, for the signed-in user (US1-6).
- The demo's sign-in page must render, or the redirect lands on an error page (D14). In
  `demo/urls.py`, route `accounts/login/` to django-mvp's `mvp.views.account.SignInView`,
  named `account_login` because its template posts there. Add it before the
  `django.contrib.auth.urls` include, which stays for sign-out. Test: a GET of the redirect's
  address answers 200, and the round-trip POST above goes through that view.
- `TestRefusal`, the anonymous half of the matrix (FR-004, FR-007, SC-002, spec edge cases): the
  front page, a page, a nested page, an image, a download, an unknown address, a slashless page
  address, a slashless unknown address, and a page when `build_dir` points at a directory that
  does not exist each answer the identical redirect: same status, `Location` differing only by the
  `next` address, empty body. Parametrise over the addresses.

`DocumentationApp` docstring: add `check` to Args (plan, *Public API*). No code change in
`mvp_sphinx/`. README: new section *Choosing who can read it* after *Naming the documentation*:
open to everyone by default, `check=user_is_authenticated` for signed-in only, what an excluded
reader gets (sign-in then back, no entry), and that the rule covers files too. Point at the
django-mvp mounted-apps guide's *Limiting who can reach an app* with an absolute link. CHANGELOG
Unreleased *Added* entry. In the README, call signed-in only one import and one keyword, not
"no code" (ARC-001). CONTEXT.md: add **Reader rule** under *Core concepts*: the
documentation app's `check`, one per documentation app, asked on every request; _Avoid_:
permission (a Django permission is one thing a rule can test), access control.

---

## US2 — Keep the documentation for a particular group (P2)

Issue: #40. Delivers FR-003 (own rule), FR-006, FR-007 (signed-in half), FR-008, FR-010, FR-012;
SC-001 (own rule), SC-002, SC-003.

### T003 — A rule of the host's own

**Files**: `tests/test_mounted.py`, `README.md`, `CHANGELOG.md`

Plan, *Public API*, *Refusal matrix*. `TestOwnRule` with `check=user_in_any_group(<group
fixture's name>)`:

- A member gets each page, image and download (US2-1, FR-010).
- A signed-in non-member gets 403 answered by the `403.html` the project resolves (django-mvp's, unless the host overrides it) (assert the template is in
  `response.templates`), with none of the page's fixture text or the file's bytes, for every
  address of the matrix, including unknown, slashless and missing-build (US2-2, FR-006, FR-007).
- An anonymous reader is redirected to sign in (US2-3).
- On the overview page the entry is absent for the non-member and present for the member (US2-4).
  Use the demo's `docs_app` with the group rule, because only its entry is in `AppMenu`. The
  suite's handbook app has no menu entry anywhere.
- The 403 page for a refused handbook request carries no trace of the app. Its escaped name,
  `html.escape(str(handbook_app.name))` (fixture data from `tests/urls.py`), is absent from the
  body. In the same test, an admitted request to the same page does carry it, which shows the
  absence check can fail (FR-008).
- With `check=user_has_any_permission(<a real permission codename>)`, a user granted it is served
  and one without it gets 403 (US2-5).
- With `check=False`, nobody is served and nobody sees the entry, a superuser included (spec edge
  case, D7).
- With a rule that raises, a page request raises that error through the test client, and so
  never serves the page (FR-012, D8). With the same rule on `docs_app`, the overview page raises
  too, because its menu entry asks the rule (D13).

README: extend *Choosing who can read it* with a rule of the host's own: `user_in_any_group`,
`user_has_any_permission`, a hand-written function of the request, that staff and superusers get
no bypass, and that an error in the rule is a server error on every page that draws the menu
entry, the sign-in page included (D13). Say that `user_in_any_group` and
`user_has_any_permission` are called with their arguments, and that a value that is not a
function of the request is read as a yes or no, so `check="staff"` admits everyone. CHANGELOG:
extend the entry.

---

## US3 — Different documentation for different readers (P3)

Issue: #41. Delivers FR-001, FR-009, FR-011; SC-003.

### T004 — The demo's staff guide

**Files**: `demo/staff_guide/**`, `demo/mounted.py`, `demo/urls.py`, `demo/menus.py`,
`.gitignore`, `AGENTS.md`, `tests/test_demo.py`, `tests/conftest.py`

Plan, *Demo*. Source with a front page and one more page, `conf.py` like `demo/docs/conf.py`.
`staff_guide` instance in `demo/mounted.py`, mounted at `staff-guide/`, entry appended in
`demo/menus.py`. Gitignore `demo/staff_guide/_build/`. AGENTS.md: the build command and one
sentence on who can read it and which account to use. `tests/test_demo.py`
`TestStaffGuideEntry`: on the overview page the entry is absent for anonymous and for a regular
user, and present for a staff user. Add a `staff_guide_app` fixture in `conftest.py` pointing the
instance at `handbook_build`, and one test that a staff user gets its front page. Additive edits
only in the shared demo files.

### T005 — Two apps, two rules, and standing that changes

**Files**: `tests/test_mounted.py`, `README.md`

Plan, *What already holds*. `TestSeveralApps`, with the demo's two apps from T004: `docs` left
open and `staff_guide` at `check=user_is_staff` (their entries are the two in `AppMenu`). For the
group case, set `check` on `staff_guide_app` through `monkeypatch`:

- Anonymous, a regular user and a staff user each see on the overview page only the entries their
  rules admit (US3-1, FR-011).
- Each reader's requests to both apps are served or refused as each app's own rule says (US3-2).
- Standing that changes between two requests on one client: signing in (anonymous → user), and
  being added to the admitting group (with a group rule on the handbook), changes the next
  response and the next overview page, with nothing reset in between (US3-3, FR-009).

README: extend the section with two audiences as two apps, each with its own build, name,
namespace and rule.
