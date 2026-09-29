# Feature Specification: Show a page's headings beside it, and links to the previous and next page

**Feature Branch**: `003-page-headings-and-links`

**Created**: 2026-09-30

**Status**: Draft

**Serves**: G2 (readers can reach every page from the sidebar and always see where they are)

**Roadmap**: R2

**Issue**: django-mvp/django-mvp-sphinx#6

**Depends on**: django-mvp/django-mvp-sphinx#4, which serves the pages these sit on

**Input**: "On a long page, a reader wants to jump to a section and, at the end, carry on to the
next page without going back to the contents. Wide screens should list the current page's headings
beside it under 'On this page', and every page should end with links to the previous and next page
in reading order."

## Summary

Two pieces of navigation that live on the page itself, next to the contents in the app sidebar.

- **On this page** lists the current page's headings beside it on wide screens, nested the way the
  page nests them, each one linking to its heading. It lists only the current page, never other
  pages, and a page with no headings below its title has none.
- **Previous and next** links end every page, leading to the page before and after it in reading
  order: the order the docs build puts its pages in. The first page has no previous link, and the
  last has no next.

The contents in the app sidebar belong to #5. Styling the page body, including the links a reader
can copy from each heading, belongs to #7.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Jump to a section of a long page (Priority: P1)

A reader lands on a long page of the user guide and wants the part that answers their question.
Beside the page, "On this page" lists its headings. They select one and the page moves to that
heading. The list stays in reach as they read, so they can move to another section without
scrolling back to the top.

**Why this priority**: Long pages are where readers get lost, and the sidebar's contents stop at
the page, not inside it. This is the half of the feature a reader uses on every long page.

**Independent Test**: Serve a docs build with a page that has nested sections and a page that has
none. The first page lists its section headings, each linking to its own heading on the page. The
second page has no "On this page" at all.

**Acceptance Scenarios**:

1. **Given** a page with sections, **When** a reader opens it, **Then** the page carries an
   "On this page" list holding every section heading of that page, in the order they appear on the
   page.
2. **Given** a page whose sections have sub-sections, **When** a reader opens it, **Then** each
   sub-section's entry is nested under its parent section's entry.
3. **Given** an entry in the list, **When** a reader selects it, **Then** it leads to that heading
   on the same page.
4. **Given** a page with sections, **When** a reader opens it, **Then** the list does not repeat
   the page's own title.
5. **Given** a page with no headings below its title, **When** a reader opens it, **Then** the page
   carries no "On this page" list.
6. **Given** any page, **When** a reader opens it, **Then** the list holds no heading from any
   other page.
7. **Given** a page with sections, **When** the list is read by assistive technology, **Then** it
   is a navigation region with a name of its own, distinct from the sidebar's navigation.

---

### User Story 2 - Carry on to the next page (Priority: P2)

A reader working through the user guide reaches the end of a page. Below it are links to the
previous and the next page, each naming the page it leads to. They follow "next" and carry on
reading without going back to the contents. A reader on the first page sees only the next link,
and a reader on the last page only the previous one.

**Why this priority**: It saves a trip to the sidebar at the end of every page, but the sidebar
already reaches every page, so a reader is never stranded without it.

**Independent Test**: Serve a docs build of at least three pages. From the front page, follow the
next link repeatedly. Every page is visited once, in the order the build lists them, and the last
page has no next link. Following previous links from the last page returns the same way.

**Acceptance Scenarios**:

1. **Given** a page with a page before and after it in reading order, **When** a reader reaches its
   end, **Then** it links to both, and each link names the page it leads to.
2. **Given** the first page in reading order, **When** a reader opens it, **Then** it links to the
   next page and has no previous link.
3. **Given** the last page in reading order, **When** a reader opens it, **Then** it links to the
   previous page and has no next link.
4. **Given** a page whose previous page is the front page, **When** a reader follows the previous
   link, **Then** it leads to the documentation app's own address.
5. **Given** a documentation app mounted at any URL prefix, **When** a reader follows a previous or
   next link, **Then** it leads to that page under the same documentation app.
6. **Given** a page the docs build places in no reading order, **When** a reader opens it, **Then**
   the page is served with no previous or next link.
7. **Given** a page with previous and next links, **When** they are read by a browser or assistive
   technology, **Then** they are marked as the previous and next page, inside a navigation region
   with a name of its own.

---

### User Story 3 - A rebuilt docs build shows its new headings and order (Priority: P3)

A host project adds a section to a page and a new page between two others, then rebuilds its docs.
The next request shows the new section in "On this page" and the new page in the previous and next
links, without the site being restarted.

**Why this priority**: Rebuilding is how docs change, and a restart to see it would surprise a
project. It ranks last because the pages themselves already follow the build (#4); this story makes
sure the navigation on them does too.

**Independent Test**: Serve a page, rebuild the docs build with a section added to it and a page
inserted after it, and request the page again in the same process. The new section is listed and
the next link leads to the inserted page.

**Acceptance Scenarios**:

1. **Given** a served page, **When** the docs build is rebuilt with a section added to it, **Then**
   the next request for that page lists the new section, with no restart.
2. **Given** a served page, **When** the docs build is rebuilt with a page inserted after it,
   **Then** the next request for that page links to the inserted page as its next page, with no
   restart.

---

### Edge Cases

- **A page with only one section**: it still has "On this page", holding that one entry. The rule
  is whether a page has headings below its title, not how many.
- **A page not listed by any toctree** (a Sphinx orphan): Sphinx gives it no place in reading order,
  so it is served with no previous or next link and nothing points to it from its neighbours.
- **A page that is the only page**: no previous or next link.
- **Pages listed only in a hidden toctree**: Sphinx puts them in reading order like any other, so
  they get previous and next links and appear in their neighbours' links. This matches the
  contents in the sidebar (#5), which includes them too.
- **A heading whose text holds markup**, such as inline code: the entry reads as the heading reads
  on the page.
- **Two documentation apps mounted in one host project**: each page's headings and links come from
  its own docs build and stay under its own documentation app.

## Clarifications

### Session 2026-09-30

- Q: Which headings does "On this page" list: only the page's top-level sections, or every level?
  → A: Every section heading the docs build records for the page, nested as the page nests them,
  without the page's own title. Sphinx already decides which headings make a section, so the list
  follows the build rather than cutting it at a depth of its own.
- Q: What does "reading order" mean when the issue does not define it? → A: The previous and next
  page the docs build records for each page. Sphinx derives them from the toctrees, so reading
  order is the order the contents list the pages in, front page first.
- Q: What happens to "On this page" on narrow screens? → A: It is not shown there, and nothing
  replaces it. The issue asks for it on wide screens, the prototype this package grew from did the
  same, and on a narrow screen the page itself has the width. Where the list sits and at what width
  it appears is judged by eye, not by a test.
- Q: Does the list mark the section being read as the reader scrolls? → A: No. The issue does not
  ask for it and it needs script to follow scrolling. It can be asked for separately.
- Q: Do the previous and next links sit on pages outside reading order, or lead outside the
  documentation app? → A: Neither. A page with no previous or next page in the build has no link
  for it, and every link leads to a page of the same documentation app.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A page with headings below its title MUST carry an "On this page" list of every
  section heading the docs build records for it, in page order, nested as the page nests them.
  (US1)
- **FR-002**: Each entry in "On this page" MUST link to its heading on the same page. (US1)
- **FR-003**: "On this page" MUST NOT include the page's own title or any heading from another
  page. (US1)
- **FR-004**: A page with no headings below its title MUST carry no "On this page" list. (US1)
- **FR-005**: "On this page" MUST be a navigation region with an accessible name of its own,
  distinct from the sidebar's navigation. (US1)
- **FR-006**: Every page that has a previous or next page in the docs build MUST end with a link to
  each one it has, naming the page the link leads to. (US2)
- **FR-007**: A page with no previous page in the docs build MUST have no previous link, and a page
  with no next page MUST have no next link. (US2)
- **FR-008**: Previous and next links MUST lead to pages of the same documentation app, under the
  URL prefix it is mounted at, with the front page reached at the documentation app's own address.
  (US2)
- **FR-009**: Previous and next links MUST be marked as the previous and next page, inside a
  navigation region with an accessible name of its own. (US2)
- **FR-010**: "On this page" and the previous and next links MUST reflect the docs build on disk at
  the time of the request, so a rebuild shows on the next request without a restart. (US3)
- **FR-011**: Serving "On this page" and the previous and next links MUST NOT import Sphinx or start
  a build. They are read from the docs build like the page itself. (US1, US2, US3)

### Key Entities

- **On this page**: the headings of the current page, as the docs build records them for that page.
  Each has a title and the anchor of its heading, and may hold headings nested under it.
- **Previous and next page**: the neighbours of a page in reading order, as the docs build records
  them. Each has a title and the page it leads to. A page may have either, both or neither.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader reaches any section of the current page with one selection from "On this
  page", on every page that has sections.
- **SC-002**: Starting at the front page and following only next links, a reader visits every page
  in reading order exactly once and ends on the last page.
- **SC-003**: No page lists a heading from another page in "On this page", and no page with no
  sections shows the list.
- **SC-004**: After a rebuild, the next request shows the new headings and reading order, with no
  restart of the site.

## Assumptions

- Serving the page, its URL and its breadcrumbs come from #4. This feature adds to the page it
  serves and changes none of that.
- The contents in the app sidebar come from #5. "On this page" holds headings inside the current
  page, and the sidebar holds pages, so neither repeats the other.
- The links a reader can copy from each heading, and all styling of the page body, come from #7.
- The docs build is the host project's own output and is trusted the way the page body is. Heading
  and page titles are shown as the build renders them.
- "On this page" is the name CONTEXT.md gives this list, not a required label. What the list and
  the previous and next links say is wording, and no test pins it.
- Where the list sits beside the page, the width at which it appears, and how the previous and next
  links look are design decisions judged by eye, and they follow the host's django-mvp theme
  (CONSTITUTION.md, Article XIII).
