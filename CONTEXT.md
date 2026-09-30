# django-mvp-sphinx

Domain vocabulary for django-mvp-sphinx, which serves a project's Sphinx
documentation inside its django-mvp application shell.

The terms below are the ones to use in issues, commits and tests. Sphinx,
Django and django-mvp each already use several of these words for something
else, which is why the list exists.

## Core concepts

**Host project**:
The Django project that installs this package. It owns the theme, the base
template, the URLs, and the docs build. This package renders into it and decides
none of those.
_Avoid_: consumer, client, downstream, user (a user is a person using the host
project, not the project itself).

**Docs build**:
The directory `sphinx-build -b json` writes: one `.fjson` file per page, the
images and downloads the pages link to, and the navigation file. It is the
package's only input. The host project produces it before a request arrives,
and serving a page never runs Sphinx.
_Avoid_: output, site, HTML build (Sphinx's HTML builder is a different
builder, and its output is not what this package reads).

**Documentation app**:
The mounted app that serves one docs build under one URL prefix, with the
contents in the app sidebar. A host project serving two docs builds mounts two
of them.
_Avoid_: docs site, docs server.

**Reader rule**:
The documentation app's `check`: who may read it. There is one per documentation
app, and it is asked on every request. It covers every address under the app and
the app's menu entry.
_Avoid_: permission (a Django permission is one thing a rule can test), access
control.

**Page**:
One document of the docs build, served at its own URL under the documentation
app.
_Avoid_: doc (it also means the documentation as a whole), file, article
(the `<article>` element is only the page's body).

**Front page**:
The page Sphinx builds from the project's root document, served at the
documentation app's own address.
_Avoid_: index (the Sphinx file name, not what a reader sees), home (the host
project's home page, where the sidebar's back link goes).

**Contents**:
The tree of every page, grouped the way the root document's toctrees group
them, drawn as the app sidebar's menu on every page of the documentation app.
_Avoid_: toctree (the Sphinx directive the contents is built from), sidebar (the
shell's region the contents is drawn in), table of contents (ambiguous with On
this page).

**Contents group**:
A named part of the contents, made from one captioned toctree on the root
document, drawn as a section header in the sidebar.
_Avoid_: section (that is a part of a page, headed by a heading).

**On this page**:
The headings of the current page, listed beside it on wide screens. Only the
current page's headings appear here, never other pages.
_Avoid_: toc, table of contents, local contents.

**Navigation file**:
`navigation.json`, which this package's Sphinx extension writes into the docs
build. It holds the whole contents, because Sphinx's per-page data only opens
the branch of the page being built.
_Avoid_: manifest, index.

## Terms deliberately not used

**Theme**, for anything this package ships. The host project's django-mvp theme
styles every page, and this package ships no Sphinx theme. Calling its
stylesheet a theme invites someone to port a Sphinx theme's look into it.

**Version**, for a docs build. The package serves one current build per
documentation app and has no notion of versions. Using the word invites
version pickers and versioned URLs, which are out of scope.

**Hosting**. The package serves the host project's own documentation alongside
the application. "Hosting" suggests uploads, several projects, and a docs
platform, which is a different kind of product.
