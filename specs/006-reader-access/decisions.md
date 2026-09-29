# Decisions: FS-006 Let the project decide who can read its documentation

Each entry is a point the issue left open, the reading the specification takes, and why. Any of
them can be reversed when the specification is reviewed.

## Starting point for the plan

A working prototype of the documentation app exists on the `wip/sphinx-docs-in-sidebar` branch of
[django-mvp](https://github.com/django-mvp/django-mvp), under `mvp/integrations/sphinx_view/`,
`mvp/templates/mvp/sphinx_view/` and `demo/sphinx_docs/`. It was built inside django-mvp as a
mounted app on top of django-sphinx-view, and the maintainer reviewed it favourably. This package
drops the django-sphinx-view dependency and owns its view (docs/brainstorm.md), so the plan may
start from the prototype but not from its dependency. The prototype has no access rule of its own.

django-mvp's mounted apps, from 0.25.0, already carry a per-app rule for who may see the app, with
the refusal behaviour D2 describes. The entries below follow that behaviour so a documentation app
is refused the same way as any other mounted app in the host project. The plan may build on it. The
package currently allows django-mvp 0.24.0, so the plan has to settle the minimum version.

## D1. Three choices, and the default is everyone

**Ambiguous:** The issue says some projects publish their guide and others keep it "for signed-in
people or a particular group". It doesn't say what the choices are called, or what happens when the
project chooses nothing.

**Chosen:** Everyone (the default), signed-in people only, or a rule of the host project's own
that decides from the request (FR-002, FR-003). Signed-in only is a plain option. A group, a
permission or anything else is expressed as the host's own rule.

**Why:** These are the three cases R5 names. A group-specific option would cover one kind of rule
and still leave the others needing code, so the general rule covers groups. The default keeps a
documentation app mounted before this feature readable exactly as it was.

## D2. Sign-in for visitors, forbidden for signed-in people

**Ambiguous:** The issue says excluded people see neither the pages nor the menu entry. It doesn't
say what answers when they request a page by address.

**Chosen:** A visitor who isn't signed in is sent to the sign-in page and returned to the page
afterwards. A signed-in person the rule refuses gets the host's ordinary forbidden response (FR-005,
FR-006).

**Why:** This is Django's own access behaviour and django-mvp's mounted apps already refuse this
way. A shared link to the docs then works for anyone who can sign in, rather than dead-ending on
"not found". A not-found response was considered, to hide that the docs exist at all, but the menu
entry already hides them from people browsing, and "not found" would break every shared link for
readers who only need to sign in.

## D3. One rule per documentation app, not per page

**Ambiguous:** Whether individual pages can have their own readers.

**Chosen:** No. The rule covers the whole documentation app (FR-001, FR-011). Different audiences
mount different documentation apps.

**Why:** CONTEXT.md and CONSTITUTION.md Article XII already make the documentation app the unit
that serves one docs build, and a project with two audiences usually writes two guides. Per-page
rules would need a way to mark pages in the Sphinx source and would leave the contents showing
pages a reader can't open.

## D4. Files follow the rule too

**Ambiguous:** The issue speaks of pages and the menu entry.

**Chosen:** Images and downloads under the documentation app follow the same rule as its pages
(FR-004).

**Why:** Screenshots and downloads are part of the documentation. A limited guide whose files can
still be fetched by address isn't limited.

## D5. A refusal never reveals what exists

**Ambiguous:** Whether an excluded reader can tell a real page from a missing one, for example by
getting "not found" for one and a sign-in redirect for the other.

**Chosen:** A refused request is answered the same way whatever is behind the address, whether the
build exists and whether the address has its trailing slash (FR-007). The trailing-slash redirect
from #4 applies only to readers the rule admits.

**Why:** Different answers would let anyone list the pages of a limited guide by guessing
addresses.

## D6. Asked on every request

**Ambiguous:** When a change in who someone is takes effect.

**Chosen:** On their next request (FR-009).

**Why:** A person who signs in, or is added to a group, expects the docs straight away. Remembering
an earlier answer would also keep showing the docs to someone just removed from the group.

## D7. No bypass for staff or superusers

**Chosen:** The rule alone decides. A host that wants staff to read limited docs writes that into
its rule (Assumptions).

**Why:** A hidden exception makes the rule say one thing and do another. It is one line in the
host's own rule when wanted.

## D8. A failing rule is a server error

**Chosen:** An error raised by the host's rule surfaces as a server error and never serves the page
(FR-012).

**Why:** Failing open would publish limited docs whenever the rule broke. Failing as "forbidden"
would hide a bug in the host project from its error reporting.

## D9. Search and contents stay with their own features

**Chosen:** This feature requires only that an excluded reader never reaches the contents (#5) or
anything served under the documentation app, which includes search (#10). How either works is
theirs.

**Why:** Each has its own feature request. Stating the boundary here keeps the rule complete
without taking on their scope.
