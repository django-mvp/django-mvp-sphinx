# Feature Specification: Search the documentation

**Feature Branch**: `007-docs-search`

**Created**: 2026-09-30

**Status**: Draft

**Serves**: G6 · **Roadmap**: R6 · **Issue**: [#10](https://github.com/django-mvp/django-mvp-sphinx/issues/10)

**Input**: "Once a user guide grows past a handful of pages, readers expect to type a word and find
the page that covers it. The documentation should be searchable from within its own pages. It
searches the documentation only, not the rest of the site."

## Overview

Every page of a documentation app lets the reader search that documentation. The reader types one
or more words and gets a results page, inside the application shell like every other page, listing
the pages that contain those words. Each result leads to its page, and pages whose titles match
come before pages that only mention the words in passing. A search covers the pages of that one
documentation app and nothing else: never the host project's own pages or data, and never another
documentation app's pages.

Search reads what the docs build already contains. It needs nothing extra from the host project's
Sphinx configuration, it never needs Sphinx installed where the site runs, and it works with
JavaScript turned off.

This feature builds on the pages served by
[#4](https://github.com/django-mvp/django-mvp-sphinx/issues/4) and leaves other work to its own
issues:

- the contents in the app sidebar ([#5](https://github.com/django-mvp/django-mvp-sphinx/issues/5))
- who may read the documentation ([#9](https://github.com/django-mvp/django-mvp-sphinx/issues/9))
- searching the host project's own content, which is out of scope for this package

## Clarifications

### Session 2026-09-30

- Q: When a reader types several words, must a result contain all of them or any of them? → A: All
  of them, in any order and anywhere in the page. Adding a word narrows the results, which is what
  readers expect from a documentation search box and what Sphinx's own search does. Integrated into
  FR-005 and User Story 1.
- Q: How loosely does a word match? → A: Case never matters, and different forms of the same word
  (a plural, an "-ing" or "-ed" form) find the same pages, in the way Sphinx's own search does for
  the language the docs were built in. A fragment of a word is not a match. Integrated into FR-006.
- Q: Does search need JavaScript in the reader's browser? → A: No. The search is a form that leads
  to a results page at its own address, so it works with scripts off and a search can be
  bookmarked or shared as a link. Search-as-you-type is not part of this feature. Integrated into
  FR-002, FR-003 and User Story 1.
- Q: What does a search do when the docs build has no search data in it, such as a build made
  before the index was written or one that was only partly copied? → A: The documentation's pages
  keep working, and the search answers that it is unavailable, which a reader can tell apart from
  a search that found nothing. It never raises a server error. Integrated into FR-013 and User
  Story 3.
- Q: Who can see the results page, given that limiting access is a separate feature? → A: The
  results page is an address of the documentation app like any page, so whatever decides who may
  read the pages decides who may search them. This feature adds no access rule. Integrated into
  FR-012 and recorded under Assumptions.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Find the pages that mention a word (Priority: P1)

A reader on any page of the documentation types a word into the search and submits it. A results
page opens inside the application shell and lists every page of this documentation that contains
the word, each leading to its page. Several words narrow the list to pages containing all of them.
When nothing matches, the results page says so and the reader can search again from it.

**Why this priority**: This is the feature. A user guide beyond a handful of pages is hard to use
without it, and everything in the other stories refines these results.

**Independent Test**: Build a small Sphinx project to JSON with several pages, some sharing words
and some with a word unique to them, mount it as a documentation app, and submit searches from a
page of the app.

**Acceptance Scenarios**:

1. **Given** any page of a documentation app, **When** it renders, **Then** it offers a search
   that submits to that documentation app's results page.
2. **Given** a word that appears in exactly one page's text, **When** a reader searches for it,
   **Then** the results list that page, and only that page.
3. **Given** a word that appears in several pages, **When** a reader searches for it, **Then** every
   one of those pages is listed, each once, and each result links to its page's address under the
   same documentation app.
4. **Given** two words that each appear in several pages, **When** a reader searches for both,
   **Then** only the pages containing both words are listed.
5. **Given** a word written in a different case, or in a different form of the same word, from the
   way it appears in a page, **When** a reader searches for it, **Then** that page is listed.
6. **Given** words that appear in no page, **When** a reader searches for them, **Then** the results
   page renders successfully, lists no pages, tells the reader nothing matched, and still offers the
   search.
7. **Given** a search submitted with no words, or only spaces, **When** the results page renders,
   **Then** it lists no pages, reports no error, and offers the search.
8. **Given** a results page for a search, **When** its address is opened again later or by another
   reader, **Then** it shows the same search and the same results.
9. **Given** words that appear only in the host project's own pages or data, **When** a reader
   searches for them, **Then** no results are listed.
10. **Given** a search that contains characters with meaning in HTML or in a URL, **When** the
    results page renders, **Then** the reader's text is shown back as plain text and never
    interpreted as markup.
11. **Given** the browser has JavaScript turned off, **When** a reader searches, **Then** the
    results are the same as with it on.
12. **Given** a link in the docs to Sphinx's own search page, **When** a reader follows it, **Then**
    they reach this documentation app's search.

---

### User Story 2 - See which result is the right one (Priority: P2)

A reader scanning the results needs to pick the right page without opening each one. Pages whose
title contains the words come first. Each result shows a short passage of the page with the words
in it, and when a section heading of the page matches, the result leads straight to that section.

**Why this priority**: User Story 1 already finds the pages. This makes a long list usable, and
matters more as the guide grows.

**Independent Test**: Build pages where a word appears in one page's title, in a section heading of
another, and only in the body text of a third, then search for that word.

**Acceptance Scenarios**:

1. **Given** a word in one page's title and only in the body text of other pages, **When** a reader
   searches for it, **Then** the page with the word in its title is listed before the others.
2. **Given** a result, **When** the results page renders, **Then** the result names its page by the
   page's title, as plain text.
3. **Given** a word that appears in a page's body text, **When** that page is listed, **Then** its
   result shows a passage of the page's text containing the word, as plain text with none of the
   page's markup.
4. **Given** a word that appears in a section heading within a page, **When** that page is listed,
   **Then** its result leads to that section of the page rather than the top of the page.

---

### User Story 3 - Search keeps up with the docs build (Priority: P3)

The host project rebuilds its docs and new pages become searchable straight away. A project that
serves two documentation apps gets two separate searches. A build that turns out to have no search
data leaves the pages working and says search is unavailable.

**Why this priority**: These are the conditions a host project meets after the first deploy. The
first search works without them.

**Independent Test**: Mount a build, search, rebuild with an added page and search again, then
mount a second documentation app with a different build, then remove the search data from a build
and search.

**Acceptance Scenarios**:

1. **Given** a documentation app serving a docs build, **When** the host project rebuilds the docs
   with a page containing a new word, **Then** the next search for that word lists the new page
   without the site being restarted.
2. **Given** two documentation apps pointed at different docs builds, **When** a reader searches
   from a page of one, **Then** only that documentation app's pages are listed, and every result
   leads to an address under that documentation app.
3. **Given** a docs build that contains pages but no search data, **When** a reader searches,
   **Then** the results page tells the reader search is unavailable, in a way distinguishable from
   a search that matched nothing, and the documentation's pages keep being served.
4. **Given** a documentation app whose docs build does not exist yet, **When** its search address
   is requested, **Then** the response is the same one the documentation app gives for its pages
   before the build exists.
5. **Given** an environment where Sphinx is not installed, **When** a reader searches, **Then** the
   results are the same as where Sphinx is installed.

---

### Edge Cases

- A search much longer than any sensible query is still answered, without a server error. Words
  beyond a sensible limit may be ignored.
- Very common words that Sphinx leaves out of its search data, such as "the" or "and", never make
  a search come back empty on their own. A search for "the product list" finds the pages that
  contain "product" and "list".
- A page Sphinx builds for its own index or search appears in no results.
- The words in a page's address, or in the markup around its text, don't make it match. Only text a
  reader sees on the page counts.
- A page that matches in its title and its body appears once.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every page served by a documentation app MUST offer a search of that documentation
  app, and the host project's pages outside the documentation app MUST NOT gain one. (US1)
- **FR-002**: A search MUST lead to a results page at an address of the documentation app that
  carries the search's words, rendered inside the host project's application shell, so the same
  address shows the same search and results again. (US1)
- **FR-003**: Searching and reading the results MUST work in a browser with JavaScript turned off.
  (US1)
- **FR-004**: The results MUST list the pages of the documentation app's own docs build and nothing
  else, each page at most once, each linking to the page's address under that documentation app.
  (US1, US3)
- **FR-005**: When a search has several words, a page MUST be listed only if it contains all of
  them. Words Sphinx leaves out of its search data as too common MUST NOT prevent a match. (US1)
- **FR-006**: Matching MUST ignore case and MUST treat different forms of a word as the same word,
  as Sphinx's own search does for the language the docs were built in. (US1)
- **FR-007**: A search with no words, or with words no page contains, MUST render a results page
  with no results that tells the reader nothing matched and offers the search again, without error.
  (US1)
- **FR-008**: The results page MUST show the reader's search, each result's title and each passage
  as plain text, never as markup. (US1, US2)
- **FR-009**: A link in the docs to Sphinx's own search page MUST lead to this documentation app's
  search. (US1)
- **FR-010**: Pages whose title contains the searched words MUST be listed before pages that contain
  them only elsewhere. (US2)
- **FR-011**: Each result MUST name its page by title and, where the words appear in the page's body
  text, show a passage of that text containing them. Where the words appear in one of the page's
  section headings, the result MUST link to that section. (US2)
- **FR-012**: The results page MUST be governed by the same rule that governs who may read the
  documentation app's pages. This feature MUST NOT add an access rule of its own. (US1)
- **FR-013**: When the docs build has no search data, the results page MUST tell the reader search
  is unavailable, distinguishably from a search with no matches, and every page MUST keep being
  served. When the docs build does not exist, the search address MUST answer as the documentation
  app's pages do. (US3)
- **FR-014**: Each search MUST use the docs build as it is on disk at that moment, so a rebuild is
  searchable without restarting the site. (US3)
- **FR-015**: Search MUST NOT import Sphinx or start a build, MUST work where Sphinx is not
  installed, and MUST need nothing added to the host project's Sphinx configuration beyond what
  serving pages already needs. (US3)

### Key Entities

- **Search**: the words a reader submits, scoped to one documentation app.
- **Search data**: the record Sphinx writes into the docs build of which words each page contains,
  in its titles, headings and text. It is the search's only input.
- **Result**: one page of the documentation app that matches a search. It has the page's title, its
  address (or the address of the matching section), and a passage of its text.
- **Results page**: the documentation app's page that shows a search and its results, served inside
  the application shell at an address that carries the search's words.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a docs build in which each page contains at least one word no other page
  contains, searching for each page's unique word lists that page, and only that page, for every
  page in the build.
- **SC-002**: Across a set of searches run against the same docs build, every page Sphinx's own
  HTML search lists for a search is also listed here.
- **SC-003**: No search, whatever its words, lists a page outside the documentation app being
  searched or anything from the host project's own content.
- **SC-004**: A reader reaches the results page from any page of the documentation in one step,
  with JavaScript on or off, and with Sphinx absent from the environment.
- **SC-005**: A missing search data file, an empty search and a search with no matches each produce
  a working results page, and none of them stops the documentation's pages being served.

## Assumptions

- The docs build is the same `sphinx-build -b json` output served by
  [#4](https://github.com/django-mvp/django-mvp-sphinx/issues/4), and Sphinx writes its search data
  into that build by default. Search needs no configuration beyond what #4 needs.
- One docs build per documentation app, in one language. Searching across versions or translations
  is out of scope (CONSTITUTION.md Article XII).
- User guides this package serves run to tens or a few hundred pages. All results are shown on one
  results page, without paging through them.
- Who may search is who may read. Until the access feature
  ([#9](https://github.com/django-mvp/django-mvp-sphinx/issues/9)) exists, that is the host
  project's existing configuration.
- How the search and the results look comes from the host's django-mvp theme and application
  shell (CONSTITUTION.md Article XIII). Where the search sits on the page is settled when the
  feature is looked at in a browser, not in this specification.
- Suggestions while typing, highlighting the searched words on the page a result leads to, and
  searching Sphinx's general index are not part of this feature.
