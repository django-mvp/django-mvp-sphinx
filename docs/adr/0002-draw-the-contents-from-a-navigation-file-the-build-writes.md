# ADR 0002 — Draw the contents from a navigation file the build writes

**Status:** accepted

## Decision

The contents in a documentation app's sidebar comes from one file, `navigation.json`. The package's
Sphinx extension, `mvp_sphinx.navigation`, writes it into the JSON build when the build finishes. It
holds the whole tree: one group per toctree on the root document, hidden toctrees included, and each
page with the pages its own toctrees list. The extension writes a sibling file first and renames it
into place, so the file is replaced in one step.

The serving side reads that file through `DocsBuild` and never imports Sphinx. `DocumentationMenu`
turns it into the app's django-mvp menu. It rebuilds its items only when the file's modification
time, size or inode changes, or the build directory or the app's address does. It holds a lock
across the rebuild and the processing, because the shell processes every documentation app's menu
on every page of the host and a menu's children are shared between requests. A missing, unreadable
or malformed file leaves the contents holding the front page entry alone, and never raises.

## Why

The table of contents Sphinx writes into each page opens only the branch of the page being built.
A sidebar drawn from it would change shape from page to page and could not reach every page. The
build is the only place the whole tree is known, so the build has to write it down. That costs a
host one line in `conf.py`.

A file read at request time keeps the package's rule that serving never needs Sphinx
(CONSTITUTION Article XII), and it means a rebuilt docs build shows on the next request with no
restart. The menu is processed on every host page, not only on the docs, so reading and parsing
the file there each time would put that cost on the whole site; a `stat` per request is the price
instead. Replacing a menu's children is not atomic, and without the lock two requests arriving
together after a rebuild can leave the sidebar with duplicated entries until the next rebuild.
Falling back to the front page entry, instead of an error, keeps a forgotten extension line or a
half-finished rebuild from taking the host's own pages down.

## Revisit if

Sphinx starts writing the whole tree into its own output. Revisit the change detection if a host
reports a filesystem where none of modification time, size or inode changes when the file is
replaced.
