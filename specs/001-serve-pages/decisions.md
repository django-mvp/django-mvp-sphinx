# Decisions: FS-001 Serve Sphinx documentation pages inside the application shell

Each entry is a point the issue left open, the reading the specification takes, and why. Any of
them can be reversed when the specification is reviewed.

## Starting point for the plan

A working prototype of this feature exists on the `wip/sphinx-docs-in-sidebar` branch of
[django-mvp](https://github.com/django-mvp/django-mvp), under `mvp/integrations/sphinx_view/`,
`mvp/templates/mvp/sphinx_view/` and `demo/sphinx_docs/`. It was built inside django-mvp as a
mounted app on top of django-sphinx-view, and the maintainer reviewed it favourably. This package
drops the django-sphinx-view dependency and owns its view (docs/brainstorm.md), so the plan may
start from the prototype but not from its dependency. Where the issue is silent, the prototype's
behaviour is the default reading, and the entries below follow it unless they say otherwise.

## D1. No Sphinx configuration needed to serve pages

**Ambiguous:** G3 promises "a mount and one line in the Sphinx config". It wasn't clear whether
this feature needs that line.

**Chosen:** No. A plain `sphinx-build -b json` build is enough to serve pages (FR-002). The
configuration line adds the navigation extension, which writes the navigation file. Only the
contents in the sidebar (#5) reads that file.

**Why:** Each feature then asks only for what it uses, and the pages can be tried on any existing
JSON build.

## D2. A missing build is not found, never a failed start

**Ambiguous:** What a documentation app does when its build directory doesn't exist yet.

**Chosen:** The site starts normally. Every address under the app answers with the ordinary
not-found response, and the first request after the build appears is served from it (FR-011,
FR-012).

**Why:** The build is produced outside the site and often after it, on a fresh checkout or in a
deploy step. Refusing to start would take the whole site down over optional documentation, and a
startup check would also go stale when the build is removed later.

## D3. Only images and downloads are served as files

**Ambiguous:** The issue says the images and downloads a page links to should work. It says
nothing about the rest of the build.

**Chosen:** Only the build's image and download folders are served as files. Nothing else in the
build, and nothing outside those folders, can be fetched by any address (FR-007, FR-008).

**Why:** The build also holds page data, the pickled build environment and the navigation file,
and none of those is for readers. The prototype's first version let `_images/../environment.pickle`
through before it was fixed, so the boundary is a stated requirement with its own scenarios
(User Story 2, scenarios 4 and 5).

## D4. The page's own title is the single page heading

**Ambiguous:** Sphinx's page body always opens with the document's title as a heading, and the
application shell can also draw a page title.

**Chosen:** The page has exactly one top-level heading, carrying the page's title (FR-004).

**Why:** Two top-level headings saying the same thing would fail an accessibility review. The
prototype kept the document's own heading, restyled to match the site's other page titles. How it
looks is left to the plan.

## D5. The documentation app's name heads the breadcrumbs and the tab

**Ambiguous:** What "breadcrumbs back to the front page" start with, and what names the docs in
the browser tab.

**Chosen:** The documentation app's name, which has a default and can be set per app (FR-005,
FR-015). The breadcrumbs then pass through the page's parents to the page itself. The front page's
breadcrumbs hold the app's name alone.

**Why:** django-mvp's mounted apps already name themselves in the tab and breadcrumbs, and the
prototype followed that. A host with two documentation apps needs to tell them apart.

## D6. The menu entry is part of this feature

**Ambiguous:** The issue doesn't mention how readers find the docs, and #8 and #9 both refer to "the
menu entry" without saying which feature provides it.

**Chosen:** This feature provides a menu entry the host adds to its own menu, leading to the front
page (FR-014, User Story 4).

**Why:** Without it the pages are only reachable by typing their address, and #9's rule that
excluded readers don't see "the menu entry" needs an entry to exist first. The prototype offered it
the same way.

## D7. Several documentation apps side by side

**Ambiguous:** The issue speaks of one docs build.

**Chosen:** A host can mount several documentation apps, each with its own prefix, build and name,
and none affects another (FR-016).

**Why:** CONTEXT.md and CONSTITUTION.md Article XII both say a project needing two builds mounts two
documentation apps. That only works if this feature allows more than one.

## D8. The trailing-slash redirect is permanent, keeps the query string, and skips files

**Ambiguous:** The issue says a missing trailing slash "should find the page".

**Chosen:** A permanent redirect to the slashed address, keeping any query string. Image and
download addresses are never redirected (FR-009).

**Why:** This matches Django's own trailing-slash behaviour. Pages must live at slashed addresses
for the relative links Sphinx writes into them to resolve, and a file address with a slash
appended would no longer name the file.

## D9. A page file that can't be read is a server error

**Ambiguous:** What happens when a page's data file exists but can't be read as page data.

**Chosen:** It fails loudly, as a server error (Edge Cases).

**Why:** A corrupt file is a broken build, and the host project needs to see it in its error
reporting. Answering "not found" would hide the fault behind a response that looks like a typo.

## D10. No access rule and no styling in this feature

**Chosen:** The pages are readable by whoever the host's existing configuration lets through
(access is #9). This feature adds no styling of Sphinx's markup (#7), and no contents, On this
page, or previous and next links (#5, #6).

**Why:** Each has its own feature request, and each depends on this one. Folding any of them in
would make this feature wait on decisions that belong to them.

## D11. The page body is trusted HTML

**Chosen:** A page's body is displayed as the HTML Sphinx wrote, without escaping.

**Why:** The docs build is produced by the host project's own tooling from its own sources, the
same trust level as its templates. Escaping it would break every page. Uploading builds through
the site, the case where this would be unsafe, is ruled out by CONSTITUTION.md Article XII.

## D12. Sphinx's own index and search pages get no special handling

**Chosen:** If the build contains Sphinx's general index or search page, they are served like any
other page. Nothing makes them work as an index or a search.

**Why:** Search is #10. A working general index hasn't been asked for, and it would need its own
feature request.
