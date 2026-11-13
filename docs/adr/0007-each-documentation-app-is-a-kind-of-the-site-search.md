# ADR 0007 — Each documentation app is a kind of result in the site's search

**Status:** accepted

## Decision

Every `DocumentationApp` registers its pages as a function kind of django-mvp's site search when it
is created, named `mvp_sphinx-<namespace>`, with the app's `name` and `icon`. The first app created
under a namespace registers it, and a later one under the same namespace registers nothing. The
function is `DocumentationPages`, which holds only the namespace: on each search it finds the app
mounted under that namespace in the request's URLconf, asks the app's `check`, and runs `DocsSearch`
on the request's build. Each result's where line is the caption and the titles above its page in
the contents, two at most and the outermost first, or the app's name when nothing is above it.

An app's own search button gives way when `mvp.actions.search` is in
`MVP_CONFIG["layout"]["navbar"]["end"]` and the site's active kinds include the app's kind.
`mvp_sphinx/base.html` then leaves out the whole `mvp_sphinx.search_toggle` block, and every page
and results page of the app has `site_search` in its context. The app's `search/` address stays.

## Why

django-mvp's guide has a package register its kind from `AppConfig.ready`, but this package has no
kind to register until a host creates an app, and the apps exist only in the host's code. Walking
the URLconf from `ready()` would import the host's URLs while other apps may not be ready, and an
admin site whose URLs are built then misses models registered later. A host creates its apps where
its menu entry is built, which flex-menus loads during start-up, so registering on creation puts the
kinds in place before Django runs its checks, without the package touching the URLconf. Tests and
hosts create more than one app under a namespace, which is why a taken name is skipped rather than
raised, and why the function looks the app up per request rather than holding the instance it was
made with.

The hand-over follows the top bar rather than whether the site's search is mounted. The site's
widget can only be in the top bar when its addresses are mounted (django-mvp's `mvp.E009`), so the
condition says the reader has a search on the page that finds the documentation. A mounted search
that no top bar shows would otherwise leave the documentation with no search at all. Leaving out
the whole block, rather than only the package's default button inside it, keeps a project's swapped
button from sitting beside the site's.

## Revisit if

django-mvp gives a package a way to register a kind after the URLconf is loaded, or places its
search somewhere other than the top bar's `end` list.
