# ADR 0001 — Read the docs build on every request, and serve only its images and downloads as files

**Status:** accepted

## Decision

A documentation app reads its docs build from disk on every request, with no cache and no check at
start-up. A missing build answers "not found" until it exists.

Only two folders of the build are ever returned as files: `_images/` and `_downloads/`. A page is
read from its `.fjson` file and rendered, never returned as bytes. Everything else Sphinx writes into
the build is never served under any address. That covers the search index, the sources, `_static/`,
the pickled build environment and the navigation file.

Every lookup resolves its target and refuses it unless it lies inside the build. A file must also lie
inside its own folder. The build directory is resolved first, so a build reached through a symlink
still works. Links pointing out of the build or out of a file folder are refused.

`DocsBuild` (`mvp_sphinx/docs_build.py`) is the one place these lookups happen.

## Why

The build is produced outside the site and often after it starts: on a fresh checkout, or in a deploy
step. Reading per request means a first build or a rebuild shows up without a restart, and a site
never fails to start over optional documentation. A page file is small, and a cache would need
invalidating on exactly the event this design exists to support.

The build holds far more than readers need. Serving the directory as static files would publish the
pickled environment and the sources. The prototype this package grew from let
`_images/../environment.pickle` through before that was caught. The upstream view it replaced joined
the address onto the build directory unchecked, so any `.fjson` on the disk was reachable. Naming the
two folders a page can link to, and confining each lookup to them, makes the boundary a rule instead
of a hope.

## Revisit if

A page needs a build file from outside `_images/` and `_downloads/`, such as a search feature reading
the search index or `_static/` assets. Add that folder explicitly, with the same containment check.
Revisit the no-cache rule if reading a page from disk becomes a measured cost.
