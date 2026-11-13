# Feature Specification: Show the documentation's contents in the app sidebar

**Feature Branch**: `002-sidebar-contents`

**Created**: 2026-09-30

**Status**: Draft

**Serves**: G2 — readers can reach every page from the sidebar and always see where they are.
G1 — a project's Sphinx docs read as pages of its own site, with its shell, its theme and its sidebar

**Roadmap**: R2 — the contents in the app sidebar

**Depends on**: #4, which serves the pages the contents link to

**Input**: Someone reading the docs needs to reach any page and see where they are, the way they
would in any documentation site. On documentation pages, the app sidebar should hold the
contents, grouped the way the docs group them, with nested pages under their parent and the current
page marked. Rebuilding the docs should update the sidebar without restarting the site. The sidebar
draws the top of the contents and the way to the page being read, and opens any other branch when a
reader asks for it, so its size doesn't grow with the docs.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reach every page from the sidebar (Priority: P1)

A reader on any page of the documentation app finds the contents in the app sidebar. The pages
are grouped the way the docs' root document groups them: each captioned toctree becomes a contents
group named by its caption, and pages from an uncaptioned toctree sit at the top level. Every page
is an entry that leads to it, and a page that lists pages of its own has a toggle that opens them
below it. The front page is reachable too.

The entries the root document's toctrees list are drawn on every page, so the top of the sidebar
never changes shape as the reader moves around. Below them, only the entries on the way to the page
being read are drawn, open. Any other entry keeps its toggle, and the first time a reader opens it
its pages are fetched and opened in place. However many pages the docs have, a page carries only the
links it shows.

The host project gets this by adding one entry to its Sphinx configuration's extension list and
naming the package's sidebar renderer in its settings. The build then carries the contents, and
nothing else needs writing.

**Why this priority**: without it, a reader can only reach pages the current page happens to link
to. It is the core of G2 and the reason the contents belongs to the site's own sidebar under G1.

**Independent Test**: build a small set of docs with two captioned toctrees, one uncaptioned
toctree, a hidden toctree and a page with sub-pages; mount a documentation app on the build; open
any page, open every toggle and follow every sidebar entry.

**Acceptance Scenarios**:

1. **Given** a docs build whose root document has two captioned toctrees, **When** a reader opens
   any page of the documentation app, **Then** the sidebar shows two contents groups, named by the
   two captions, each holding the pages its toctree lists, in the order the toctree lists them.
2. **Given** a root document with a toctree that has no caption, **When** a reader opens any page,
   **Then** the pages that toctree lists appear at the top level of the contents, in their place
   among the groups.
3. **Given** a page whose own toctree lists further pages, **When** a reader opens any page,
   **Then** that page's entry leads to it and has a toggle that opens the pages it lists.
4. **Given** pages nested three levels deep, **When** a reader opens the deepest page, **Then**
   every entry on its way is drawn open, and each entry leads to its page.
5. **Given** a toctree marked hidden, **When** a reader opens any page, **Then** the pages it lists
   appear in the contents like any other toctree's.
6. **Given** any page of the documentation app, **When** the reader looks at the sidebar, **Then**
   an entry leading to the front page is present.
7. **Given** a toctree entry with an explicit title, **When** the contents is drawn, **Then** the
   entry carries that title rather than the page's own.
8. **Given** two different pages of the same documentation app, **When** a reader opens each in
   turn, **Then** the entries the root document's toctrees list are the same, in the same order,
   on both.
9. **Given** a host project with Sphinx not installed on the server, **When** a reader opens a
   page, **Then** the contents is drawn.
10. **Given** a reader on a top-level page, **When** the page renders, **Then** no page below the
    top entries is drawn, and each top entry with pages of its own has a closed toggle.
11. **Given** a closed entry, **When** the reader opens its toggle, **Then** its pages are fetched
    and drawn below it, each with its own pages closed, without the page reloading.
12. **Given** a page of the host project outside the documentation app that draws the contents,
    **When** it renders, **Then** only the top entries are drawn.

---

### User Story 2 - See where you are (Priority: P1)

On every page, the sidebar marks the page being read, and every group and entry containing it is
open, so a reader who arrived from a search engine or a shared link can tell at once where the page
sits in the docs. The page's entry is scrolled into the middle of the sidebar, so a deep page isn't
left below the fold.

**Why this priority**: G2 asks for both halves, reaching a page and seeing where you are. A tree
with nothing marked leaves the reader to search it by eye on every page.

**Independent Test**: with the docs build from User Story 1, open a page nested two levels deep and
check the sidebar's marked entry and open groups; then open a top-level page and check again.

**Acceptance Scenarios**:

1. **Given** a reader on a page listed in the contents, **When** the page renders, **Then** that
   page's entry is marked as the current page and no other entry is.
2. **Given** a reader on a page nested inside two entries, **When** the page renders, **Then** both
   entries are open.
3. **Given** a reader on a page that has pages of its own, **When** the page renders, **Then** its
   entry is marked as current and its pages are open.
4. **Given** a reader on the front page, **When** the page renders, **Then** the front page's entry
   is marked as current.
5. **Given** a page served by the documentation app that no toctree lists, **When** a reader opens
   it, **Then** the top entries are drawn and no entry is marked.
6. **Given** a reader on a page whose entry is below the sidebar's fold, **When** the page loads, or
   the sidebar opens on a phone, **Then** the page's entry is scrolled into the middle of the
   sidebar.

---

### User Story 3 - A rebuilt docs build updates the sidebar (Priority: P2)

A host project rebuilds its docs while the site is running. The next page a reader opens shows the
new contents: added pages appear, removed pages disappear, renamed captions and titles change. No
restart is needed. A docs build that carries no contents never breaks the site.

**Why this priority**: docs change far more often than the site is deployed. Without this, every
docs edit needs a restart before readers can find the new page. It depends on User Story 1 and
refines it rather than standing as the core of the feature.

**Independent Test**: with the site running, add a page to a toctree and rebuild the docs; open a
documentation page and find the new entry. Then remove the extension's output from the build and
check that pages still serve.

**Acceptance Scenarios**:

1. **Given** a running site whose docs build is replaced by a build that adds a page to a toctree,
   **When** a reader next opens any documentation page, **Then** the new page's entry appears in
   the contents without the site restarting.
2. **Given** a running site whose docs build is replaced by one that removes a page, **When** a
   reader next opens any documentation page, **Then** that page's entry is gone.
3. **Given** a docs build made without the package's Sphinx extension, **When** a reader opens a
   documentation page, **Then** the page is served, and the contents holds only the entry for the
   front page.
4. **Given** a docs build whose contents cannot be read, **When** a reader opens a documentation
   page, **Then** the page is served, and the contents holds only the entry for the front page.
5. **Given** a documentation app whose docs build is missing or unreadable, **When** a reader opens
   a page of the host project outside the documentation app, **Then** that page is served as usual.

---

### User Story 4 - Choose how a page appears in the sidebar (Priority: P2)

Someone writing the docs decides, in a page's own front matter, how that page appears in the
sidebar. A page that only groups others thematically can leave its own link out while its pages
stay, and a page with pages of its own can be drawn as a heading over them.

**Why this priority**: the contents take their shape from the toctrees, and an index page exists
in every section whether or not it has anything to say. Without this, every section carries an
entry for a page that may say nothing, and a project wanting a heading has to rebuild the menu in
its own code.

**Independent Test**: build docs with a page marked hidden, an index page marked hidden and an index
page styled as a group; open a page of the documentation app and check the sidebar's entries, then
open the hidden pages directly.

**Acceptance Scenarios**:

1. **Given** a page with `menu_hidden: true` and no pages of its own, **When** a reader opens any
   page, **Then** it has no entry in the contents, and it is still served at its address.
2. **Given** a page with `menu_hidden: true` and pages of its own, **When** a reader opens any page,
   **Then** its entry is present under its title, with its toggle and no link to the page.
3. **Given** a page with `menu_style: group` and pages of its own, **When** a reader opens any page,
   **Then** the page's entry is drawn as a heading, leading to the page, with its toggle.
4. **Given** a page with neither setting and pages of its own, **When** a reader opens any page,
   **Then** it appears as an entry with a toggle, as in User Story 1.
5. **Given** a page with both `menu_hidden: true` and `menu_style: group`, **When** a reader opens
   any page, **Then** the page's entry is drawn as a heading over its pages, with no link to the
   page.
6. **Given** a reader on a hidden page that has pages of its own, **When** the page renders, **Then**
   its pages are open and no entry is marked.
7. **Given** a page whose pages are all hidden, **When** a reader opens any page, **Then** it appears
   as a plain link with no toggle.
8. **Given** a setting with a value it doesn't take, **When** the docs are built, **Then** the build
   fails, naming the page.

---

### User Story 5 - Add something to each entry (Priority: P3)

A developer of a host project shows something of their own in every entry of the contents, such as
how many pages lie below it or a tick on a page the reader has finished. They override the entry's
template, extend the package's, and fill one block, without copying the entry's markup.

**Why this priority**: the contents are often the place a site shows a reader's progress through
its docs. Without a place for it, a host has to copy the whole entry template and keep it in step
with every release.

**Independent Test**: in a host project, override the entry template with one that extends the
package's and fills its block with the number of pages below the entry; open a page and a fetched
branch and check every entry carries the number.

**Acceptance Scenarios**:

1. **Given** a host project whose entry template fills the block, **When** a reader opens any page,
   **Then** every drawn entry carries what the block adds, and nothing else about the entry changes.
2. **Given** the same project, **When** a reader opens a closed entry, **Then** the fetched entries
   carry it too.
3. **Given** the block, **When** it is drawn, **Then** it can read the entry's navigation data, its
   pages below it included, and the request the sidebar is drawn for.

---

### Edge Cases

- **A page listed by two toctrees.** It appears in both places, and both entries lead to the same
  page.
- **A toctree that lists a page already above it in the tree.** The contents stops at the repeat
  rather than nesting forever.
- **A toctree entry that is an external link, or refers back to the page listing it.** It is left
  out: the contents lists only pages the documentation app serves.
- **A page title containing characters that are markup in HTML.** The title shows as text, never
  as markup.
- **Two documentation apps in one host project.** Each draws its own contents on its own pages, and
  a page of one never marks an entry in the other.
- **The documentation app mounted at a different address.** Every entry leads to the page under the
  new address, and every branch is fetched from it.
- **A page at `contents/`.** The address belongs to the documentation app's branch fetching, as
  `search/` belongs to its search, so such a page is not served there.
- **An entry the reader opens after the docs were rebuilt without it.** The fetch answers not found
  and the entry stays closed.
- **A root document with no toctree at all.** The contents holds only the front page's entry.
- **`menu_style` on a page with no pages of its own to show.** It has no effect.
- **A section with every page hidden and hidden itself.** It is left out.
- **The front page.** It takes neither setting. Its entry belongs to the menu, and a project can
  take it out with the menu's own methods.
- **A rebuild in progress when a request arrives.** The page is served. The contents may be the old
  or the new tree, never an error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: On every page of a documentation app, the app sidebar MUST draw the documentation's
  contents: every page reachable through the root document's toctrees.
- **FR-002**: Each captioned toctree on the root document MUST become a contents group named by its
  caption, holding the pages that toctree lists.
- **FR-003**: Pages listed by an uncaptioned toctree on the root document MUST appear at the top
  level of the contents.
- **FR-004**: The contents MUST keep the order the toctrees give: groups in the order of the root
  document's toctrees, and pages in the order each toctree lists them.
- **FR-005**: A page whose own toctrees list further pages MUST appear as an entry leading to the
  page, with a toggle that opens those pages below it, at any depth.
- **FR-006**: Hidden toctrees MUST contribute their pages to the contents exactly as visible ones
  do.
- **FR-007**: An entry MUST carry the title its toctree gives it, or the page's own title when the
  toctree gives none.
- **FR-008**: The contents MUST include an entry leading to the front page.
- **FR-009**: The entries the root document's toctrees list MUST be drawn, in the same order, on
  every page that draws the contents. Below them, only the entries on the way to the page being read
  MUST be drawn.
- **FR-010**: Every entry MUST lead to its page under the address the documentation app is mounted
  at.
- **FR-011**: Toctree entries that are not pages of the docs build (external links, references to
  the listing page itself) MUST be left out of the contents.
- **FR-012**: A page listed more than once MUST appear at each place it is listed, and a toctree
  that lists a page above it in the tree MUST NOT make the contents nest without end.
- **FR-013**: The page being read MUST be marked as the current entry, with every group and entry
  containing it open. A page no toctree lists MUST leave every entry unmarked.
- **FR-014**: Titles and captions from the docs build MUST be shown as text, never interpreted as
  markup.
- **FR-015**: When the docs build is replaced, the next request MUST draw the new build's contents,
  with no restart of the site.
- **FR-016**: The package MUST provide a Sphinx extension that writes the contents into the docs
  build, and a host project MUST need to add nothing but that extension to its Sphinx configuration
  and the package's sidebar renderer to its settings for the contents to appear.
- **FR-017**: Drawing the contents MUST NOT import Sphinx or start a build (Article XII).
- **FR-018**: A docs build with no contents, or contents that cannot be read, MUST NOT stop any page
  from being served: documentation pages are served with only the front page's entry in the
  contents, and pages outside the documentation app are unaffected.
- **FR-019**: Each documentation app MUST draw its own build's contents only, so two documentation
  apps in one host project never share or mix their contents.
- **FR-020**: The contents MUST be drawn through the host's django-mvp sidebar menu, not as a
  navigation column inside the page (Article XIII).
- **FR-021**: A page's `menu_hidden` metadata MUST decide whether its entry links to it, and its
  `menu_style` metadata whether a page with pages of its own is drawn as a heading. A value other
  than `true` or `false`, or `collapse` or `group`, MUST fail the build. Neither setting changes
  whether the page is built or served, or which pages are drawn.
- **FR-022**: A closed entry with pages of its own MUST keep its toggle, and opening it MUST fetch
  its pages from the documentation app and draw them below it, each with its own pages closed. The
  fetch MUST follow the documentation app's reader rule.
- **FR-023**: When a page loads, and when the sidebar opens on a phone, the page's entry MUST be
  scrolled into the middle of the sidebar.
- **FR-024**: A host project MUST be able to add markup to every entry by overriding the entry's
  template and filling one block, which can read the entry's navigation data and the request.
- **FR-025**: A host project whose sidebar renderer can't draw the contents' entries MUST be refused
  at startup, with the setting that fixes it.

### Traceability

| Story | Requirements |
|---|---|
| US1 — Reach every page from the sidebar | FR-001 – FR-012, FR-014, FR-016, FR-017, FR-019, FR-020, FR-022, FR-025 |
| US2 — See where you are | FR-013, FR-023 |
| US3 — A rebuilt docs build updates the sidebar | FR-015, FR-018 |
| US4 — Choose how a page appears in the sidebar | FR-021 |
| US5 — Add something to each entry | FR-024 |

### Key Entities

- **Contents**: the tree of every page, grouped the way the root document's toctrees group them.
  Made of contents groups and page entries. Its top is the same on every page of one documentation
  app.
- **Contents group**: a named part of the contents, made from one captioned toctree on the root
  document.
- **Page entry**: one page in the contents, with its title and the address it leads to. An entry for
  a page with pages of its own holds their entries in turn.
- **Navigation file**: the file the package's Sphinx extension writes into the docs build, holding
  the whole contents. It is the only source of the contents.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a docs build with nested pages, captioned and uncaptioned toctrees and a hidden
  toctree, every page the toctrees list can be reached from the sidebar of any documentation page,
  opening toggles where needed, and none is missing.
- **SC-002**: On every page the toctrees list, exactly one sidebar entry is marked current, and
  every group and entry containing it is open.
- **SC-003**: After a rebuild of the docs on a running site, the next documentation page opened
  shows the new contents, with no restart.
- **SC-004**: A host project gets the contents by adding one entry to its Sphinx configuration and
  one renderer to its settings, and nothing else.
- **SC-005**: A docs build missing its contents, or carrying contents that cannot be read, causes no
  error on any page of the host project.
- **SC-006**: A page outside the documentation that draws the contents carries the top entries' links
  and no others, and adding pages below the top entries adds nothing to it.

## Clarifications

### Session 2026-09-30

- Q: Are pages from hidden toctrees part of the contents? → A: Yes. A hidden toctree is how a Sphinx
  project lists pages for navigation alone, so its pages appear like any other (FR-006).
- Q: A page with pages of its own is both a link and a group. How does a reader reach the page
  itself? → A: Its entry is a link to the page, with a toggle beside it that opens its pages
  (FR-005).
- Q: What does the contents hold when the docs build carries none, because the extension was never
  added or its file cannot be read? → A: Only the front page's entry, and every page is still
  served (FR-018). The reader can still reach the front page, which links onward.
- Q: Do in-page headings appear in the sidebar? → A: No. The contents lists pages only. A page's
  headings belong to "On this page", which is #6.
- Q: Are external links in a toctree shown in the contents? → A: No. The contents lists the pages
  the documentation app serves (FR-011).

## Assumptions

- #4 delivers the documentation app, its mount and its pages. This feature adds the contents to
  that app's sidebar and changes nothing about how pages are served.
- The host project's application shell already draws a mounted app's menu in the sidebar, marks the
  current entry and opens the groups around it. This feature supplies the tree for it to draw.
- A docs build is replaced as a whole by rerunning Sphinx. Partial edits to the build by hand are not
  a supported way of changing the contents.
- The contents is built from the root document's toctrees and the toctrees of the pages they list.
  Pages reachable through no toctree are still served, but are not in the contents.

## Out of Scope

- "On this page" and the previous and next page links, which are #6.
- Styling of the page body, which is #7.
- Search, which is #10.
- Limiting who can read the docs or see the menu entry, which is #9.
- The entry in the host project's own menu that leads into the documentation app. It is not part
  of the contents. The README quickstart that describes adding it is #8.
- Navigation to anything outside the documentation app's own pages.
