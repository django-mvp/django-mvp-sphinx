# Feature Specification: Serve Sphinx documentation pages inside the application shell

**Feature Branch**: `001-serve-pages`

**Created**: 2026-09-30

**Status**: Draft

**Serves**: G1, G3 · **Roadmap**: R1 · **Issue**: [#4](https://github.com/django-mvp/django-mvp-sphinx/issues/4)

**Input**: "A project that writes its user guide in Sphinx wants to serve it as part of the site
itself, not as a separate docs site. Point the package at the project's docs build, mount it at a
URL of the project's choosing, and every page appears inside the application shell, in the site's
theme, with the page named in the browser tab and breadcrumbs back to the front page. The images
and downloads a page links to should work, a missing trailing slash should find the page, and
serving should not need Sphinx installed on the server."

## Overview

A host project builds its Sphinx documentation into a docs build, then mounts a documentation app
at an address of its choosing and points it at that build. From then on every page of the build is
a page of the site. It renders inside the application shell and in the host's theme, and the browser
tab and breadcrumbs name it the way they name the site's other pages. Images and downloads the pages
link to load, and addresses behave the way the site's own addresses do. None of this needs Sphinx
installed where the site runs.

This feature serves the pages. Other features build on them:

- the contents in the app sidebar ([#5](https://github.com/django-mvp/django-mvp-sphinx/issues/5))
- On this page, and links to the previous and next page ([#6](https://github.com/django-mvp/django-mvp-sphinx/issues/6))
- styling of the markup Sphinx writes into a page ([#7](https://github.com/django-mvp/django-mvp-sphinx/issues/7))
- the README quickstart and the demo's own user guide ([#8](https://github.com/django-mvp/django-mvp-sphinx/issues/8))
- limiting who can read the docs ([#9](https://github.com/django-mvp/django-mvp-sphinx/issues/9))
- search ([#10](https://github.com/django-mvp/django-mvp-sphinx/issues/10))

## Clarifications

### Session 2026-09-30

- Q: What does a documentation app do before its docs build exists, for example on a fresh
  checkout that hasn't built the docs yet? → A: The site starts and every other page works. Each
  address under the documentation app answers with the site's ordinary not-found response until the
  build appears, and the first request after it appears is served from it, with no restart.
  Integrated into FR-011 and User Story 3.
- Q: Which files in the docs build besides pages can a reader fetch? → A: Only the images and
  downloads Sphinx copies into the build for pages to link to. Everything else in the build, such
  as page data files, the build environment and the navigation file, is never served as a file,
  and no address can reach outside the build's image and download folders. Integrated into FR-007
  and FR-008.
- Q: Does serving pages require the one line of Sphinx configuration from G3? → A: No. A plain
  `sphinx-build -b json` build is enough to serve pages. The configuration line adds the navigation
  file, which the contents feature (#5) reads. Integrated into FR-002.
- Q: Who may read the pages? → A: This feature adds no access rule of its own. Anyone the host
  project's existing configuration lets reach the address can read the page. Choosing who may read
  is #9. Recorded under Assumptions.
- Q: What name identifies the documentation in the browser tab and the breadcrumbs? → A: The
  documentation app's name. It has a default, and the host project can give each documentation app
  its own. Integrated into FR-004, FR-005 and FR-015.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read a documentation page as a page of the site (Priority: P1)

A host project mounts a documentation app at an address it chooses and points it at its docs build.
A person using the site opens that address and gets the front page, inside the same application
shell as every other page. Links in the page lead to the other pages of the build, each also
inside the shell. The tab names the page and the documentation, and the breadcrumbs lead back
through the page's parents to the front page.

**Why this priority**: Everything else on the roadmap sits on these pages. Without it there is
nothing to navigate, style, search or protect.

**Independent Test**: Build a small Sphinx project with a front page, a page and a nested page to
JSON, mount a documentation app pointed at the build, and request each page's address.

**Acceptance Scenarios**:

1. **Given** a documentation app mounted at a prefix and pointed at a docs build, **When** a reader
   requests the prefix itself, **Then** the response is the front page, rendered inside the host
   project's application shell.
2. **Given** the same app, **When** a reader requests the address of any other page in the build,
   including a page in a sub-folder of the docs source, **Then** the response is that page, rendered
   inside the shell.
3. **Given** a page built from a folder's index document, **When** a reader requests the folder's
   address, **Then** that page is served.
4. **Given** any served page, **When** it renders, **Then** it has exactly one top-level heading,
   and that heading carries the page's title.
5. **Given** any served page, **When** it renders, **Then** the browser tab's title names the page
   and the documentation app, and page titles containing markup appear there as plain text.
6. **Given** the front page, **When** it renders, **Then** the breadcrumbs hold the documentation
   app alone, as the current location.
7. **Given** a page nested under other pages, **When** it renders, **Then** the breadcrumbs lead from
   the documentation app (linking to the front page) through each parent page (each linking to that
   page) to the current page.
8. **Given** a link in one page's body to another page of the build, **When** a reader follows it,
   **Then** they reach that page under the same documentation app.
9. **Given** a served page, **When** the host project rebuilds the docs with changed content for
   that page, **Then** the next request for it shows the changed content without the site being
   restarted.
10. **Given** an environment where Sphinx is not installed, **When** any page is requested, **Then**
    it is served exactly as it is where Sphinx is installed.

---

### User Story 2 - Images and downloads load with the page (Priority: P2)

A page shows an image or links to a file the docs ship for download. The image appears in the page
and the download link fetches the file, without the host project serving those files itself.

**Why this priority**: A user guide without its screenshots, or with broken download links, reads
as broken. It comes after the page itself, which is still useful without them.

**Independent Test**: Build a page with an image and a `:download:` link, mount the build, and
fetch the page, the image address and the download address.

**Acceptance Scenarios**:

1. **Given** a page containing an image from the docs source, **When** the page renders, **Then**
   the image's address answers with the image file and a content type matching its kind.
2. **Given** a page with a download link, **When** a reader follows it, **Then** the response is
   the file Sphinx copied into the build.
3. **Given** an address that names an image or download file the build does not contain, **When**
   it is requested, **Then** the response is the site's ordinary not-found response.
4. **Given** an address built to climb out of the image or download folder, **When** it is
   requested, **Then** the response is the site's ordinary not-found response and no file outside
   those folders is returned.
5. **Given** an address that names any other file in the docs build, such as a page's data file,
   **When** it is requested, **Then** that file's contents are not returned.

---

### User Story 3 - Addresses behave like the rest of the site (Priority: P2)

A reader who types or pastes an address without its trailing slash still reaches the page, and an
address with nothing behind it gets the same not-found page the site gives anywhere else. A host
project that hasn't built its docs yet still has a working site.

**Why this priority**: These are the edges people hit first, from shared links and typos, and a
bare error page makes the docs feel bolted on. The pages in User Story 1 work without it.

**Independent Test**: Mount a build and request a page's address without its trailing slash, an
address with no page, and any address with the build directory removed.

**Acceptance Scenarios**:

1. **Given** a page's address without its trailing slash, **When** it is requested, **Then** the
   response is a permanent redirect to the address with the slash, keeping any query string.
2. **Given** an address under the documentation app with no page behind it, **When** it is
   requested, **Then** the response is the host project's ordinary not-found response, with the
   not-found status.
3. **Given** a documentation app whose docs build does not exist yet, **When** the site starts and
   serves its other pages, **Then** they work as before, and every address under the documentation
   app answers with the ordinary not-found response.
4. **Given** that same app, **When** the docs build is then produced, **Then** the next request is
   served from it without a restart.
5. **Given** the address of an image or download file, **When** it is requested, **Then** it is
   served as the file and never redirected to a slashed address.

---

### User Story 4 - The site leads readers to its documentation (Priority: P3)

The host project adds an entry for the documentation to its own menu, and the entry leads to the
front page. A project can give its documentation app a name of its own, and one with two docs
builds, such as a user guide and an administrator's guide, mounts two documentation apps that don't
affect each other.

**Why this priority**: Readers can already reach the pages by address. The menu entry and naming
make them discoverable and recognisable, and serving two builds is a less common need.

**Independent Test**: Add the documentation app's menu entry to the host's menu and follow it,
then mount a second documentation app with its own name and build at a second prefix.

**Acceptance Scenarios**:

1. **Given** a documentation app whose menu entry the host project has added to its menu, **When**
   a reader follows the entry from any page of the site, **Then** they reach the documentation's
   front page.
2. **Given** a documentation app the host project has named, **When** any of its pages renders,
   **Then** the browser tab and the breadcrumbs carry that name instead of the default.
3. **Given** two documentation apps mounted at different prefixes and pointed at different builds,
   **When** a reader requests a page under each, **Then** each is served from its own build, and
   the tab, breadcrumbs and links of each page stay within its own documentation app.

---

### Edge Cases

- A page title containing markup, such as inline code, appears as plain text wherever the page is
  named: the tab and the breadcrumbs.
- Two page addresses that differ only by a trailing slash never both render a page. One redirects
  to the other.
- A mount prefix with several segments works the same as one with one segment.
- A page file in the build that cannot be read as page data is a broken build, not a missing
  page. It fails loudly, as a server error, rather than being shown to readers as not found.
- Pages Sphinx writes for its own index and search are served as ordinary pages when the build
  contains them. Making them work as an index or a search is not part of this feature.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The package MUST provide a documentation app the host project can mount at a URL
  prefix of its choosing, pointed at one docs build. (US1)
- **FR-002**: The documentation app MUST serve pages from a build made by `sphinx-build -b json`
  alone, with no other Sphinx configuration required of the host project. (US1)
- **FR-003**: Every page of the docs build MUST be served at its own address under the prefix,
  rendered through the host project's base template inside the application shell, with the front
  page at the prefix itself and a folder's index page at the folder's address. (US1)
- **FR-004**: Each served page MUST carry the page's title as its single top-level heading and name
  the page and the documentation app in the browser tab, as plain text. (US1)
- **FR-005**: Each served page MUST set breadcrumbs that start at the documentation app, linking to
  the front page, pass through each parent page as a link, and end at the current page. The front
  page's breadcrumbs hold the documentation app alone. (US1)
- **FR-006**: Links between pages, and to files, within a page's body MUST resolve to the right
  address under the documentation app's prefix. (US1, US2)
- **FR-007**: The documentation app MUST serve the images and downloads in the docs build at the
  addresses the pages link to, with a content type matching the file. (US2)
- **FR-008**: The documentation app MUST NOT return the contents of any file other than the build's
  images and downloads, and MUST NOT return any file outside the build's image and download folders,
  whatever the address. (US2)
- **FR-009**: A request for a page's address without its trailing slash MUST be redirected
  permanently to the slashed address, keeping the query string. Image and download addresses MUST
  NOT be redirected. (US3)
- **FR-010**: An address under the prefix with no page or file behind it MUST get the host project's
  ordinary not-found response. (US3)
- **FR-011**: A documentation app whose docs build is missing MUST NOT stop the site from starting
  or affect its other pages. Its addresses answer as not found until the build exists. (US3)
- **FR-012**: Each request MUST be answered from the docs build as it is on disk at that moment, so
  a rebuild or a first build is visible without restarting the site. (US1, US3)
- **FR-013**: Serving MUST NOT import Sphinx or start a build, and MUST work where Sphinx is not
  installed. Sphinx MUST NOT become a runtime dependency of the package. (US1)
- **FR-014**: The documentation app MUST offer a menu entry the host project can add to its own
  menu, leading to the front page. (US4)
- **FR-015**: The documentation app MUST have a default name, and the host project MUST be able to
  give each documentation app its own name. That name is the one used in the tab and breadcrumbs.
  (US1, US4)
- **FR-016**: A host project MUST be able to mount several documentation apps, each at its own
  prefix with its own docs build, without any affecting another's pages, names or links. (US4)
- **FR-017**: Adopting the documentation app MUST NOT require the host project to write a template.
  (US1)

### Key Entities

- **Documentation app**: the mounted app that serves one docs build under one URL prefix. It has a
  name, a prefix and the location of its docs build.
- **Docs build**: the directory `sphinx-build -b json` writes. It holds one data file per page,
  plus the images and downloads the pages link to. It is the documentation app's only input.
- **Page**: one document of the docs build, served at its own address, with a title, a body and
  its chain of parent pages.
- **Front page**: the page built from the docs' root document, served at the documentation app's
  prefix.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a docs build with pages at the top level and in nested folders, every page in the
  build answers successfully under the documentation app, inside the application shell, and every
  link between pages and every image in them leads to a working address.
- **SC-002**: A host project serves its docs by mounting the documentation app and pointing it at
  the build. It writes no template and changes nothing in its Sphinx configuration.
- **SC-003**: With Sphinx absent from the environment, every page, image and download is served
  exactly as it is with Sphinx present.
- **SC-004**: No address under the documentation app returns the raw contents of any file, in the
  build or outside it, other than the build's images and downloads.
- **SC-005**: A missing build, an unknown address and an address without its trailing slash each
  get the same response the site gives for that case elsewhere, and none of them stops the site
  serving its other pages.

## Assumptions

- The docs build is written by the host project's own tooling and is trusted content. A page's body
  is displayed as the HTML Sphinx wrote, the same way the host's own templates are trusted.
- The feature adds no access rule. Who may read the pages is the host project's existing
  configuration until the access feature (#9) exists.
- Pages render in the host's theme through its application shell. How Sphinx's own markup
  (admonitions, code, tables) looks is #7, and this feature doesn't style it.
- The app sidebar's contents, On this page, and previous and next links belong to #5 and #6. On
  documentation pages the sidebar shows whatever the application shell shows for a mounted app with
  no contents of its own.
- One current build per documentation app. Versions and translations are out of scope
  (CONSTITUTION.md Article XII).
