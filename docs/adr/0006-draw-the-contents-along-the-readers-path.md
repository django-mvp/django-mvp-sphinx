# ADR 0006 — Draw the contents along the reader's path, through the package's sidebar renderer

**Status:** accepted

## Decision

The sidebar draws the entries the root document's toctrees list on every page. Below them it draws
only the entries on the way to the page being read, open. Every other entry with pages of its own
is drawn closed, with a toggle, and its pages are fetched from the documentation app's `contents/`
address the first time a reader opens it. `navigation.json` still holds the whole tree (ADR 0002),
and the menu still holds every page: `DocumentationMenu` makes each page a `ContentsEntry`, which
leaves its pages out of the processed menu when the request is not on their way.

Each page is one entry: a link to the page, and a toggle beside it when it has pages of its own. The
page is no longer repeated as the first item of a collapsible group. `menu_style: group` draws the
entry as a heading over its pages and no longer changes which pages are drawn.

The entries are drawn by `mvp_sphinx.renderers.SidebarRenderer`, a subclass of django-mvp's sidebar
renderer that a host names as its `sidebar` renderer in `FLEX_MENUS`. It draws every other item
exactly as django-mvp's does, and it carries the contents' script and styles as its media, so they
arrive wherever the sidebar is drawn. A system check refuses any other sidebar renderer. A host adds
something to each entry by overriding `mvp_sphinx/contents/entry.html`, extending the package's, and
filling its `mvp_sphinx.entry_end` block.

## Why

Drawing the whole tree on every page puts every page's link into every page of the site, including
pages outside the documentation when the docs are a project's main app. A 230-page set put 219
links, about 62 KB, into each page, and the cost grew with every page added. Documentation themes
solve the same problem the same way: Read the Docs' theme warns that a whole tree on every page makes
the pages significantly larger, and the PyData theme opens a set number of levels and the rest only
along the current page. The sidebar keeps G2: every page is still reachable, through the toggles,
and the way to the page being read is always open.

The renderer is how django-flex-menus separates a menu from its markup. Its templates are chosen by
the renderer, by depth and by whether an item has children, never by the item, and the shell asks
for the renderer by its name in `FLEX_MENUS`. An entry with a link and a toggle side by side is
markup django-mvp's templates don't draw, so the package needs a renderer of its own, and the only
place a host's shell can be pointed at it is that setting. Overriding the shell's sidebar body from
the documentation's base template was the alternative: it needs no setting, but it reaches only the
documentation's own pages and replaces any sidebar body the host's base template draws. A main app's
contents, drawn on the host's other pages, would have kept django-mvp's markup.

An overridable template with a block is how Django lets a project change one part of an app's markup.
A project's entry template extends the package's, so it changes only what it adds.

## Revisit if

django-flex-menus lets an item choose its own template, which would let the contents draw their
entries without a renderer in the host's settings.
