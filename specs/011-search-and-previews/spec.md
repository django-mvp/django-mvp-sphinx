# Feature Specification: Get the documentation found by search engines and previewed well when shared

**Feature Branch**: `011-search-and-previews`

**Created**: 2026-11-17

**Status**: Draft

**Serves**: G1 · **Roadmap**: — · **Issue**: [#137](https://github.com/django-mvp/django-mvp-sphinx/issues/137)

**Input**: "Documentation served by a `DocumentationApp` is often public, and a project wants it
found through search and shown well when a link is shared."

## Overview

Documentation that anyone may read is often the part of a site people find first: a search engine
sends them to a page, or someone pastes a page's link into a chat or a post. Today a documentation
app does little to help either. A search engine has to discover its pages by following links, and
a shared link shows only what the page's author wrote into its metadata by hand, which for most
pages is nothing.

This feature does three things.

A developer adds the documentation app's **sitemap** to the site's sitemaps. It lists the front
page and every page in the contents, at the addresses the documentation app serves them at, so a
search engine finds them all. Documentation that anonymous readers may not read lists nothing,
because a search engine reads as an anonymous reader.

Every page gets **preview tags** in its head: its canonical address, and the Open Graph and card
tags that decide how a shared link looks, with the page's address, title and the site's name. A
developer can give the documentation app an image for previews to show.

An author who writes a page's **description** in its front matter has it used as the page's
description for search results and for previews, without writing it again as metadata.

What an author has already written into a page's metadata, with MyST's `html_meta` front matter or
the reStructuredText `meta` directive, keeps reaching the page's head exactly as written
([#4](https://github.com/django-mvp/django-mvp-sphinx/issues/4), spec 001 User Story 5). Where the
author has written a tag, the package writes no tag of the same name beside it.

This feature builds on the pages served by spec 001 and the reader rule from spec 006. It leaves out:

- serving `/sitemap.xml` and `robots.txt`, and the registry a mounted app adds its sitemap to,
  which django-mvp owns
  ([django-mvp#682](https://github.com/django-mvp/django-mvp/issues/682)). The sitemap here is one
  a project adds to its own sitemaps, and it is shaped so that registry can take it unchanged.
- an image chosen per page by the package. A page that needs its own preview image names it in its
  metadata, which already reaches the head.
- the results page, which carries no preview tags: it shows a search, not a page of the
  documentation.

## Clarifications

### Session 2026-11-17

- Q: When an author has written a tag into a page's metadata and the package would write one of the
  same name, which wins? → A: The author's, for every tag the package writes, not only the
  description. The package's tag is left out, so the head never carries two. Integrated into FR-009.
- Q: Are the addresses in the preview tags relative or absolute? → A: Absolute, built from the
  scheme and host of the request being served, because a link preview is read away from the site.
  The canonical address is the page's own address without its query string. Integrated into FR-005.
- Q: What is the site's name in `og:site_name`? → A: The one django-mvp uses for the site
  elsewhere: its configured site name, otherwise the name of the current site, otherwise the
  request's host. Integrated into FR-006.
- Q: Which description does a page use when its front matter has one and its metadata has one too?
  → A: The metadata's. The page's description is the one in its metadata when there is one,
  otherwise the one in its front matter. It fills both the description and the Open Graph
  description, each only where the author has not written that tag. Integrated into FR-010.
- Q: Who is the sitemap asked about, when the documentation app's reader rule depends on the
  request? → A: An anonymous reader, the way a search engine reads. A reader rule that turns an
  anonymous reader away gives an empty sitemap. Integrated into FR-003.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer lists the documentation in the site's sitemap (Priority: P1)

A developer whose documentation is public wants search engines to find every page of it. They add
the documentation app's sitemap to the sitemaps their site already serves. The site's sitemap then
lists the documentation's front page and each of its pages, at the addresses the documentation app
serves them at, with when each page was last built.

**Why this priority**: A search engine that never finds a page never sends anyone to it. The tags
in User Story 2 only matter once a page has been found.

**Independent Test**: Build a small Sphinx project with a front page, pages in two contents groups
and a page left out of the contents. Mount it as a documentation app, add its sitemap to a project's
sitemaps, request the sitemap, and compare its addresses with the pages the documentation app
serves.

**Acceptance Scenarios**:

1. **Given** a documentation app whose sitemap a project serves, **When** the sitemap is requested,
   **Then** it lists the front page and every page in the contents, each once, at the address the
   documentation app serves it at.
2. **Given** a documentation app mounted under a prefix, **When** its sitemap is requested, **Then**
   every address in it includes that prefix and is answered by the documentation app with a page.
3. **Given** a docs build with a page that is not in the contents, the search results page and
   Sphinx's general index, **When** the sitemap is requested, **Then** none of them is listed.
4. **Given** a page in the sitemap, **When** it is read, **Then** its last modification is when that
   page was last written into the docs build.
5. **Given** a documentation app whose reader rule turns anonymous readers away, **When** its
   sitemap is requested, **Then** it lists nothing.
6. **Given** a documentation app whose docs build does not exist yet, **When** its sitemap is
   requested, **Then** it lists nothing, and the site's sitemap still renders.
7. **Given** a page added to the docs build in a rebuild, **When** the sitemap is requested after
   the rebuild, **Then** it lists the new page, without the site being restarted.
8. **Given** two documentation apps whose sitemaps a project serves, **When** the site's sitemap is
   requested, **Then** each lists only its own pages, under its own prefix.
9. **Given** a documentation app that chooses a build per site, **When** its sitemap is requested
   for one site, **Then** it lists the pages of the build chosen for that site.
10. **Given** an environment where Sphinx is not installed, **When** the sitemap is requested,
    **Then** it lists the pages.

---

### User Story 2 - A reader shares a link to a page and the preview shows that page (Priority: P1)

A reader of the documentation copies a page's address into a chat, a post or an email. The preview
that appears names the page, the documentation's site and the address it leads to, rather than
showing a bare link. A search engine that reaches the page by an address with a query string
attached treats it as the page's one address.

**Why this priority**: It reaches every page with nothing for the developer or the author to do,
and it is the part a person sees whenever the documentation is shared.

**Independent Test**: Build a page with a title and no metadata, a page whose metadata sets its own
Open Graph title, and Sphinx's general index. Serve each, once with a query string, and read the
tags in each page's head.

**Acceptance Scenarios**:

1. **Given** any served page, **When** it renders, **Then** its head carries one canonical link,
   to the page's absolute address without its query string.
2. **Given** a page requested with a query string, **When** it renders, **Then** its canonical
   address and its Open Graph address are the same, and neither carries the query string.
3. **Given** any served page, **When** it renders, **Then** its head carries the page's absolute
   address as its Open Graph address, the site's name as its Open Graph site name, and marks the
   page as an article.
4. **Given** a page with a title, **When** it renders, **Then** its Open Graph title is the page's
   title as plain text.
5. **Given** a page with no title, such as Sphinx's general index, **When** it renders, **Then** its
   head carries no Open Graph title.
6. **Given** a page whose metadata sets a tag the package would also write, such as its own Open
   Graph title, **When** it renders, **Then** its head carries the author's tag exactly as written
   and no other tag of that name or property.
7. **Given** any served page, **When** it renders, **Then** its head carries one card tag, so the
   preview is drawn as a card where the sharing service reads card tags rather than Open Graph ones.
8. **Given** a page whose title holds markup characters, **When** it renders, **Then** its Open
   Graph title holds them as text, escaped once.
9. **Given** the search results page, **When** it renders, **Then** its head carries no preview
   tags.

---

### User Story 3 - A developer gives the documentation's previews an image and its pages a description (Priority: P2)

A developer wants previews of the documentation to show the project's image, and the pages they
have described to show that description in search results and previews. They give the documentation
app an image address once. On each page that needs it, the author writes a `description` in the
page's front matter, the way they would for any other static site tool. Every page's preview then
carries the image, and each described page carries its description, without the author writing
either again as metadata.

**Why this priority**: A preview with a title and an address is already useful. An image and a
description make it a good one, but each needs the developer to supply something.

**Independent Test**: Mount a documentation app with a preview image, build pages with a front
matter description, with a description in their metadata only, with both, and with neither, and
read the tags in each page's head. Mount a second app with no image and read one of its pages.

**Acceptance Scenarios**:

1. **Given** a documentation app given an image address, **When** any of its pages renders,
   **Then** its head carries that image, as an absolute address, as its Open Graph image, and its
   card tag asks for a large image.
2. **Given** a documentation app given an image address relative to the site, **When** a page
   renders, **Then** the Open Graph image is that address made absolute against the request's scheme
   and host.
3. **Given** a documentation app given no image, **When** any of its pages renders, **Then** its
   head carries no Open Graph image, and its card tag asks for a summary card.
4. **Given** a page whose front matter has a description and whose metadata has none, **When** it
   renders, **Then** its head carries that description as its description and as its Open Graph
   description.
5. **Given** a page whose metadata has a description, **When** it renders, **Then** its head
   carries the author's description tag exactly as written, and its Open Graph description is that
   same description, whatever its front matter says.
6. **Given** a page whose metadata sets its own Open Graph description or image, **When** it
   renders, **Then** its head carries the author's tag and no other of that property.
7. **Given** a page with no description in its front matter or its metadata, **When** it renders,
   **Then** its head carries no description and no Open Graph description.
8. **Given** two documentation apps, one given an image and one not, **When** a page of each
   renders, **Then** only the pages of the first carry the image.

### Edge Cases

- A front matter description with markup characters or quotes reaches the head as text, escaped
  once, as the author's metadata does.
- A front matter description that is not text, such as a list, is ignored, and the page renders as
  if it had none.
- A page served at a folder's address has that address, with its trailing slash, as its canonical
  address, the one the documentation app serves it at after the slash redirect.
- A page reached through a request whose host the site does not know is answered by Django's own
  host check before any tag is written, so no tag carries an address the site does not accept.
- A documentation app mounted twice under different namespaces gives each page the canonical address
  under the prefix it was served from.
- The viewport tag Sphinx writes into every page stays out of the head, as it is today.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A documentation app MUST provide a sitemap that a project can add to its own sitemaps
  with no further configuration. It MUST list the front page and every page in the contents, each
  once, at the absolute address the documentation app serves it at, including the app's prefix.
  (US1)
- **FR-002**: The sitemap MUST NOT list pages that are not in the contents, the search results page,
  Sphinx's general index, or any image or download. (US1)
- **FR-003**: The sitemap MUST list nothing when the documentation app's reader rule turns an
  anonymous reader away. (US1)
- **FR-004**: The sitemap MUST be read from the docs build as it is on disk when it is requested,
  MUST list nothing when the build does not exist, MUST give each page's last modification as when
  the page was last written into the build, MUST list the build chosen for the site it is requested
  for when the documentation app chooses a build per site, and MUST NOT import Sphinx. (US1)
- **FR-005**: Every page a documentation app serves MUST carry in its head one canonical link and
  one Open Graph address, both the page's absolute address, built from the request's scheme and
  host, without its query string. (US2)
- **FR-006**: Every page MUST carry an Open Graph site name, the site's name as django-mvp names the
  site elsewhere, and MUST mark itself as an article in Open Graph. (US2)
- **FR-007**: A page with a title MUST carry its title as plain text as its Open Graph title. A page
  with no title MUST carry none. (US2)
- **FR-008**: Every page MUST carry one card tag, asking for a large image when the page's preview
  has an image and for a summary card otherwise. (US2, US3)
- **FR-009**: Where a page's metadata sets a tag of the same name or property as one the package
  writes, the page MUST carry the author's tag exactly as written and MUST NOT carry the package's.
  The tags of a page's metadata MUST otherwise reach its head unchanged, as spec 001 FR-018 requires.
  (US2, US3)
- **FR-010**: A page's description MUST be the description in its metadata when there is one, and
  otherwise the text `description` of its front matter. A page with a description MUST carry it as
  its description and as its Open Graph description, each subject to FR-009. A page with none MUST
  carry neither. (US3)
- **FR-011**: A developer MUST be able to give a documentation app a preview image address, absolute
  or relative to the site. Every page of that app MUST then carry it, made absolute, as its Open
  Graph image, subject to FR-009. A documentation app given none MUST carry no Open Graph image of
  its own. (US3)
- **FR-012**: Every value the package writes into a tag MUST be escaped once, so markup characters
  in a title or description reach the head as text. (US2, US3)
- **FR-013**: The search results page MUST NOT carry the preview tags. (US2)
- **FR-014**: Serving the preview tags MUST NOT import Sphinx or start a build, and MUST need
  nothing added to the host project's Sphinx configuration. (US2, US3)

### Key Entities

- **Sitemap**: the list of a documentation app's pages that search engines read, in Django's
  sitemap form, one address and last modification per page.
- **Preview tags**: the canonical link and the Open Graph and card tags the package writes into a
  page's head itself, to describe the page to search engines and to services that preview a shared
  link. Distinct from the page's **metadata**, which its author writes.
- **Description**: a short summary of a page, from its metadata or its front matter, shown in search
  results and previews.
- **Preview image**: the image a documentation app's previews show, one per documentation app.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer lists every page of the documentation in the site's sitemap by adding one
  entry to the sitemaps they already serve.
- **SC-002**: For every page of a test docs build in the contents, the sitemap holds exactly one
  address, and every address in the sitemap is answered with a page.
- **SC-003**: No sitemap of documentation that anonymous readers may not read names any of its
  pages.
- **SC-004**: Every page of a test docs build carries exactly one tag of each name or property the
  package writes, whether or not its author wrote that tag too.
- **SC-005**: An author's metadata reaches the head unchanged on every page of the demo's guides,
  compared before and after the feature.
- **SC-006**: A described page needs its description written once, in its front matter, to appear
  in both its description and its Open Graph description.

## Assumptions

- The docs build is the same `sphinx-build -b json` output served by spec 001. A page's front matter
  fields reach it as the page's `meta`, and its metadata as rendered tags in `metatags`, with no
  extension configured (checked in `research.md`).
- The project serves its sitemaps with Django's sitemap framework. Absolute addresses in the
  sitemap come from it: from the Sites framework where it is installed, otherwise from the request,
  so the docs say a `Site` row must hold the real domain.
- A search engine reads as an anonymous reader, so the reader rule is asked about an anonymous
  request.
- The preview image is the same for every page of a documentation app. A project that needs one per
  page sets it in that page's metadata.
- When django-mvp's sitemap registry ships
  ([django-mvp#682](https://github.com/django-mvp/django-mvp/issues/682)), a documentation app adding
  its sitemap to it is one further story in this spec, delivered as its own change.
