# Decisions — 002, the documentation's contents in the app sidebar

Rationale behind the specification that is too long to carry inside it, plus every ambiguity
resolved without asking the repository owner. The specification stands alone. This file records why
it reads the way it does.

## Starting point for the plan

A working prototype of this feature exists on the `wip/sphinx-docs-in-sidebar` branch of
django-mvp/django-mvp, under `mvp/integrations/sphinx_view/` (the Sphinx extension that writes the
navigation file, and the menu that reads it). It was built inside django-mvp on top of
django-sphinx-view. This package drops that dependency, so the plan may start from the prototype's
extension and menu but not from its view. The owner reviewed the prototype and approved its shape.
Where issue #5 is silent, the specification follows it.

## The whole tree comes from the build, not from each page

**Decided**: the contents is the same tree on every page (FR-009), written once per build by the
package's Sphinx extension into the navigation file.

**Why**: the table of contents Sphinx puts in each page's data only opens the branch of the page
being built. A sidebar made from it changes shape from page to page, which defeats "reach any page".
The build is the only place the whole tree is known. The cost is one line in the host's Sphinx
configuration, which G3 already allows for.

## Hidden toctrees are included

**Decided**: pages listed by a hidden toctree appear in the contents (FR-006).

**Why**: a hidden toctree is the usual way a Sphinx project lists pages for navigation without
printing a list on the page. Furo and the Read the Docs theme both put those pages in their
navigation, and leaving them out would hide exactly the pages an author meant for the sidebar.

## A page with pages of its own opens as a group

**Decided**: such a page becomes a group holding its pages, with the page itself reachable from
inside the group (FR-005).

**Why**: django-mvp's menus keep links and groups apart, so one entry cannot be both. The prototype
put the page first inside its own group, following the pattern the django-mvp demo already uses for
its Components group. The specification fixes only that the page is reachable. How that entry is
labelled or drawn is left to the plan.

## No contents means the front page only, never an error

**Decided**: a docs build with no navigation file, or one that cannot be read, serves every page
with a contents holding only the front page's entry (FR-018). Pages outside the documentation app
are unaffected.

**Why**: a missing extension line is the likeliest adoption mistake, and a rebuild can leave the
file half-written for a moment. Neither should take the site down. The front page still links
onward, so the reader is never stranded. Keeping the last readable contents across a bad read was
considered and rejected: it adds state to guard a moment that the next request resolves anyway.

## External links and self-references are left out

**Decided**: toctree entries that are not pages of the docs build are not in the contents (FR-011).

**Why**: the contents answers "where am I in these docs". An external link has no place in that
tree, and the prototype left them out. If a project asks for them later, they can be added without
changing anything else here.

## A page listed twice appears twice, and cycles stop

**Decided**: each listing produces an entry, and a toctree pointing back up the tree stops at the
repeat (FR-012).

**Why**: Sphinx builds happily with either. Showing a page wherever its author listed it matches
what the author wrote, and a tree that loops has to stop somewhere.

## Rebuilds show on the next request

**Decided**: replacing the docs build changes the contents on the next request, with no restart
(FR-015).

**Why**: stated in #5. The prototype re-reads the navigation file only when it changes, because the
application shell processes every mounted app's menu on every host page, and reading the build on
each of those requests would cost every page of the site. That is a plan concern and stays out of
the specification.

## Boundary with the sibling issues

**Decided**: "On this page" and the previous and next links stay with #6, even though the roadmap
lists them under the same item. The menu entry that leads into the documentation app from the host
project's own menu is not part of the contents.

**Why**: #6 was filed separately for them, and its dependency is on #4, not on this feature. The
host menu entry is how a reader enters the docs, not how they move within them.
