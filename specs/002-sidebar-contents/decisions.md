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

## Decisions made while planning

## D1. The navigation file's name lives beside the build lookups, not in the extension

**Decided**: `DocsBuild.NAVIGATION_FILE` holds `navigation.json`; the extension imports it from
`mvp_sphinx.docs_build`, and the menu reads the file through `DocsBuild.navigation()`.

**Why**: the prototype's menu imported the file name from the extension module, which imports
Sphinx at the top, so drawing the menu imported Sphinx (FR-017). `docs_build` imports neither
Sphinx nor Django, so both sides can share it.

**Revisit if**: the extension grows enough that it needs a package of its own.

**ADR:** docs/adr/0002-draw-the-contents-from-a-navigation-file-the-build-writes.md

## D2. Only the JSON build gets a navigation file

**Decided**: the extension writes on `build-finished` only when the builder is `json`.

**Why**: the addresses it records are the JSON builder's, and the JSON build is the only one a
documentation app reads. A host that also builds HTML with the same `conf.py` gets no stray file.

**Revisit if**: the package ever serves another builder's output.

**ADR:** none — a detail of the extension, stated in its module docstring

## D3. A bad navigation file is validated once

**Decided**: `DocsBuild.navigation()` catches `(OSError, ValueError)`, checks the file's shape, and
returns `None` for any file it cannot use. Entry addresses are not filtered.

**Why**: the menu is processed on every host page (research R4), so an exception there breaks the
whole site (FR-018). One shape check keeps broad `except` clauses out of the menu. The plan first
also dropped entries whose address was not a plain relative one; the design review (SEC-001) showed
the file sits in the same trust domain as the pages the view already renders, and the spec rules
out hand edits to the build, so that guard was removed.

**Revisit if**: the file format gains fields.

**ADR:** docs/adr/0002-draw-the-contents-from-a-navigation-file-the-build-writes.md

## D4. The menu rebuilds when the file, the build directory or the mount prefix changes

**Decided**: `DocumentationMenu.refresh()` compares a stamp of build directory, front page
address and the file's `(st_mtime_ns, st_size, st_ino)`, and rebuilds only when it differs. A
per-menu lock is held across the refresh and the processing that reads `children`.

**Why**: a read and parse on every host page is the cost the specification's decision "Rebuilds
show on the next request" steers away from. Nanosecond mtime, size and inode together catch a
replacement even inside one second, and the extension's atomic replace changes the inode.

The first plan relied on one assignment being atomic; the design review (ARCH-001) showed anytree's
`children` setter is not, and a probe produced duplicated trees. The lock replaced that claim.

**Revisit if**: a host reports a filesystem where none of the three changes on replacement, or the
lock shows up in profiles.

**ADR:** docs/adr/0002-draw-the-contents-from-a-navigation-file-the-build-writes.md

## D5. The front page and a page's own entry inside its group are both labelled "Overview"

**Decided**: kept from the prototype the owner approved.

**Why**: django-flex-menus keeps links and groups apart, and the django-mvp demo's Components group
opens on an "Overview" entry. The spec leaves the label to the plan.

**Revisit if**: the owner asks for the page's own title there.

**ADR:** none — a label choice local to the menu, revisitable at any time

## D6. A page listed twice is marked at both places

**Decided**: both entries for the page being read are marked current.

**Why**: the spec keeps both entries (edge case "A page listed by two toctrees") and FR-013 marks
"the page being read". SC-002's "exactly one" is read for pages listed once, which is every page in
its fixture; marking one of two identical links would be arbitrary.

**Revisit if**: the owner prefers only the first listing marked.

**ADR:** none — a consequence of the menu's path matching, local to this feature

## D7. Captions below the root document are ignored

**Decided**: a toctree caption on a page other than the root does not make a group; that page's
toctrees are flattened into its own group.

**Why**: FR-002 makes groups from the root document's captioned toctrees only, and a page with
pages of its own already opens as a group (FR-005). Nesting a second kind of group inside it would
need a shape the sidebar does not have.

**Revisit if**: a real docs set needs sub-captions in the sidebar.

**ADR:** none — local to how this feature shapes the tree

## D8. Design review outcome

**Decided**: every finding applied as a plan edit, one round, no re-review. ARCH-001 (high): the
menu holds a lock across refresh and processing (D4). SPEC-001 (high): no test asserts the shell's
`menu-active` class; marking is tested on the processed tree. ARCH-002: the extension writes
`navigation.json.tmp` with `write_text`, then `os.replace`. ARCH-003: the walk is a
`NavigationWriter` class, the shape check a `DocsBuild` staticmethod. SEC-001: entry addresses are
not filtered (D3). SPEC-002: no test of the atomic write. SPEC-003: the file's key and the vocabulary
are `groups`, not `sections` (CONTEXT.md). ARCH-004: reads catch `(OSError, ValueError)`.

**Why**: each remedy was the smallest edit the finding named, and each was checked against the
finding's stated evidence by the orchestrator.

**Revisit if**: n/a — a record.

**ADR:** none — a record of the design review, not a decision

## D9. Sphinx cannot build a toctree cycle, so the guard is tested on a stand-in

**Decided**: the `tests/sphinx/contents/` source has no toctree pointing back up the tree, and
`sphinx_json_build` gains no keyword to allow warnings. The extension keeps skipping an entry that is
already on the path from the root, and that skip is tested on a stand-in environment built from real
docutils nodes.

**Why**: Sphinx 9.1's `_traverse_toctree` stops the whole build with a recursion error on any cycle
of two or more pages, before `build-finished`, and a page listing itself is dropped by the directive.
No real build reaches the extension with a cycle, and the remaining fixture entries build without a
warning, so the keyword would be unused.

**Revisit if**: a Sphinx release lets a cycle through to `build-finished`; then the fixture can carry
the back-pointing toctree.

**ADR:** none — a test-fixture constraint local to this feature

## D10. The unreadable-file tests skip when the suite runs as root

**Decided**: the two T007 tests that make `navigation.json` unreadable with `chmod 000` carry
`skipif(os.geteuid() == 0)`. `forge tamper-check` flags them as added skips, and they were checked
against tasks.md T007, which planned exactly this condition.

**Why**: root reads a file whatever its mode, so the test cannot set up its own precondition
there. CI and development run as ordinary users, where the tests run and pass.

**Revisit if**: CI moves to a container that runs as root, which would silently skip them.

**ADR:** none — a test environment detail local to this feature
