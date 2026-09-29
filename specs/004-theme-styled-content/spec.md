# Feature Specification: Make user-guide content look like the rest of the site

**Feature Branch**: `004-theme-styled-content`

**Created**: 2026-09-30

**Status**: Draft

**Serves**: G1 (a project's Sphinx docs read as pages of its own site: its shell, its theme, its sidebar), G4 (what a user guide is written with renders properly in the host's theme)

**Roadmap**: R3 — User-guide content looks right in the host's theme

**Issue**: #7

**Depends on**: #4, which serves the pages this feature styles

**Input**: The content of every page a documentation app serves looks like the rest of the host
project. Headings, paragraphs, lists, links and inline code read as the site's own text.
Admonitions (notes, tips, warnings, dangers and the rest) are told apart by their meaning. Code is
highlighted. Tables, images and figures fit the page, and glossaries and cross-references look like
the site's own definitions and links. Every colour comes from the host project's django-mvp theme,
so a theme change or dark mode needs nothing from the host project, and adopting the package adds
no setup step for styling. Headings carry a link a reader can copy, revealed on hover or keyboard
focus. The styling touches the page's content only, never the host project's other pages or the
shell around the page. API reference pages and maths belong to #13. Where the page sits on the
screen, the contents in the sidebar and "On this page" belong to #4, #5 and #6.

## Clarifications

### Session 2026-09-30

The coverage scan found five ambiguities. Each was answered from the issue, its siblings, the
constitution and the prototype this package grew from. Longer rationale is in `decisions.md`.

- **Q: The issue names notes, warnings, code, tables and glossaries. Does "look like the rest of
  the site" also cover the ordinary text of a page (headings, paragraphs, lists, links, inline
  code)?**
  A: Yes. A page's body arrives as plain HTML, and without styling its headings, lists and links
  lose the look the rest of the site gives them, which is the problem the issue describes. #4 puts
  the page in the shell and this feature styles what is inside it. Recorded as FR-001.

- **Q: Sphinx and its extensions can produce admonition kinds this package does not know about,
  such as a generic admonition with a custom title or one from a third-party extension. How do
  those look?**
  A: Like a note. Every admonition is shown as an admonition, and a kind with no meaning of its own
  falls back to the informational one rather than rendering as unstyled text. Recorded as FR-004.

- **Q: A docs build ships Sphinx's own stylesheets, including the one that colours highlighted
  code. Are they used?**
  A: No. A Sphinx stylesheet carries fixed colours and a Sphinx theme's look, which Article XIII
  rules out. The pages never load them, and highlighted code takes its colours from the theme like
  everything else. Recorded as FR-003 and FR-006.

- **Q: Colours taken from the theme are only as readable as the combinations this package makes
  from them, for example tinted admonition backgrounds or coloured code tokens. Who is responsible
  for their contrast?**
  A: This package, for the combinations it creates. Text inside admonitions and highlighted code
  meets WCAG 2.2 AA contrast against its own background in django-mvp's default light and dark
  themes. The contrast of the theme's own colours stays the theme's concern. Recorded as FR-015.

- **Q: A table can be scrolled sideways, but only someone with a pointer can scroll a region that
  never receives focus. Does a wide table need to be scrollable from the keyboard?**
  A: Yes. A region that scrolls and cannot be reached by keyboard fails WCAG 2.1.1, and the reader
  it excludes has no other way to see the hidden columns. Recorded as FR-008.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Pages read as the site's own pages, with admonitions told apart by meaning (Priority: P1)

A reader opens a page of the user guide. Its headings, paragraphs, lists, links and inline code
read the way text reads elsewhere on the site. The notes, tips, warnings and dangers the author
wrote stand out from the text around them, and a warning is plainly different from a tip. When the
reader switches the site to dark mode, or the host project changes its theme, the page follows with
nothing configured.

**Why this priority**: Without it the documentation looks like a different site, which is the
problem this issue exists to fix and what G1 calls essential. Admonitions carry the warnings a user
guide most needs its readers to notice.

**Independent Test**: Serve a page containing ordinary text and one admonition of every kind, view
it under the default light and dark themes, and confirm each part is styled from the theme and each
admonition kind is presented according to its meaning.

**Acceptance Scenarios**:

1. **Given** a page with headings, paragraphs, lists, links and inline code, **When** a reader
   opens it, **Then** each is presented with the site's own styling for its kind of content.
2. **Given** a page with a note, a tip, an important notice, a warning and a danger, **When** a
   reader opens it, **Then** each is presented as an admonition, admonitions of the same meaning
   are presented alike, and admonitions of different meanings are distinguishable.
3. **Given** a page with an admonition kind the package has no meaning for, **When** a reader
   opens it, **Then** it is presented as an informational admonition.
4. **Given** a reader viewing a page in the light theme, **When** they switch the site to the dark
   theme, **Then** every part of the page's content follows the new theme without a reload and
   without any configuration by the host project.
5. **Given** a host project with a documentation app and ordinary pages of its own, **When** a
   reader opens one of the ordinary pages, **Then** it is unaffected by this package's styling.
6. **Given** a page with a "see also" box and version notes for an addition, a change and a
   deprecation, **When** a reader opens it, **Then** each is presented as distinct from the
   surrounding prose, and the deprecation note carries the cautionary meaning.
7. **Given** an admonition of any meaning, **When** a reader views it in django-mvp's default light
   or dark theme, **Then** its text meets WCAG 2.2 AA contrast against the admonition's background.
8. **Given** a host project that has done only what serving its pages requires, **When** a reader
   opens a page, **Then** all of this feature's styling is present, with no stylesheet added, asset
   build run or setting changed by the host project.

---

### User Story 2 - Code is highlighted in the site's theme (Priority: P1)

A reader following a how-to copies a command or a snippet from a code block. The code is
highlighted so its parts are easy to tell apart, the highlighting follows the site's theme and dark
mode, and it stays readable against its background.

**Why this priority**: Code samples are one of the first things a user guide is written with, and
Sphinx's own highlighting brings fixed colours that clash with the theme and break in dark mode.

**Independent Test**: Serve a page with code blocks in several languages, view it under the default
light and dark themes, and confirm the highlighting takes its colours from the theme and meets the
contrast requirement.

**Acceptance Scenarios**:

1. **Given** a page with a highlighted code block, **When** a reader opens it, **Then** the code is
   highlighted with colours taken from the site's theme and no Sphinx stylesheet is loaded.
2. **Given** a highlighted code block, **When** the reader switches between light and dark themes,
   **Then** the highlighting follows the theme.
3. **Given** a code block with a caption, line numbers or emphasised lines, **When** a reader
   opens the page, **Then** the caption, numbers and emphasis are shown and remain readable in both
   themes.
4. **Given** highlighted code, **When** a reader views it in django-mvp's default light or dark
   theme, **Then** every highlighted part meets WCAG 2.2 AA contrast against the code's background.

---

### User Story 3 - Wide content stays inside the page (Priority: P2)

A reader on a phone opens a page with a wide table, a long line of code or a large image. The page
itself never scrolls sideways. The table and the code scroll within their own area, including from
the keyboard, and the image shrinks to fit.

**Why this priority**: A page that scrolls sideways is broken on small screens and fails WCAG
1.4.10 (reflow). It matters on every device, but only on pages that carry wide content.

**Independent Test**: Serve a page with a table wider than the screen, a code line longer than the
screen and an image wider than the screen, view it at 320 CSS pixels wide, and confirm the page
does not scroll horizontally while each of the three stays fully reachable.

**Acceptance Scenarios**:

1. **Given** a page with a table wider than the reading area, **When** a reader opens it on a
   narrow screen, **Then** the page does not scroll horizontally and the table can be scrolled
   within its own area to reach every column.
2. **Given** a wide table, **When** a keyboard-only reader moves focus through the page, **Then**
   they can reach the table's scrolling area and scroll it.
3. **Given** a page with a code line longer than the reading area, **When** a reader opens it on a
   narrow screen, **Then** the page does not scroll horizontally and the code can be scrolled within
   its own block.
4. **Given** a page with an image or figure wider than the reading area, **When** a reader opens
   it, **Then** the image is scaled down to fit, keeps its proportions, and a figure's caption stays
   with it.

---

### User Story 4 - Headings carry a link a reader can copy (Priority: P2)

A reader wants to point a colleague at one section of a page. Each heading carries a link to
itself, out of the way until the reader points at the heading or tabs to the link. Following a
copied link opens the page at that heading, fully in view.

**Why this priority**: Sharing a precise place in the guide is a common need in support
conversations, but the page is usable without it.

**Independent Test**: Serve a page with several sections, reach each heading's link by pointer and
by keyboard, open the link's address, and confirm the page opens with that heading in view.

**Acceptance Scenarios**:

1. **Given** a page with sections, **When** a reader opens it, **Then** every section heading
   carries a link whose address is the page's address with that heading's anchor.
2. **Given** a heading link, **When** the reader is not pointing at the heading and the link does
   not have keyboard focus, **Then** the link is kept out of the way, and **When** they point at
   the heading or move keyboard focus to the link, **Then** it is revealed.
3. **Given** a heading link, **When** a screen-reader user reaches it, **Then** it has an
   accessible name that identifies it as a link to that section.
4. **Given** a heading link's address, **When** a reader opens it, **Then** the page opens with the
   heading in view and not hidden behind the shell's fixed top bar.
5. **Given** a reader who has asked their browser for reduced motion, **When** a heading link is
   revealed, **Then** it appears without any transition.

---

### User Story 5 - Glossaries, cross-references and interface references look like the site (Priority: P3)

A reader meets a term they don't know, follows it to the glossary, and moves between pages through
cross-references. The glossary reads as a set of defined terms, a cross-reference reads as one of
the site's links, and the keys, buttons and menu paths the guide tells them to use are marked out
from the prose.

**Why this priority**: These make a user guide pleasant to use, but a page without them is still
readable, and they appear on fewer pages than the content in the stories above.

**Independent Test**: Serve a page with a glossary, cross-references to other pages and to glossary
terms, and interface references (keys, labels, menu paths), and confirm each is presented with the
site's styling for its kind of content.

**Acceptance Scenarios**:

1. **Given** a page with a glossary, **When** a reader opens it, **Then** each term is presented as
   a defined term with its definition beneath it, and each term carries a link a reader can copy,
   as headings do.
2. **Given** a cross-reference to another page or to a glossary term, **When** a reader opens the
   page, **Then** it is presented as one of the site's links.
3. **Given** a reader follows a link to a glossary term, **When** the page opens, **Then** the term
   is in view and not hidden behind the shell's fixed top bar.
4. **Given** a page that refers to a keyboard key, an interface label or a menu path, **When** a
   reader opens it, **Then** each is marked out from the surrounding text.

---

### Edge Cases

- A page with no admonitions, code, tables or images renders with the ordinary text styling alone.
- An admonition nested inside another admonition, or inside a list, is still presented by its own
  meaning.
- An admonition with a custom title keeps that title and is presented by its kind, or as
  informational if it has none.
- Code in a language Sphinx could not highlight is shown as plain code, readable in both themes.
- A table inside an admonition or a list scrolls within its own area like any other table.
- A heading that contains inline code or a link keeps its own link working.
- A host project using a theme other than django-mvp's defaults gets the same styling drawn from
  that theme's colours, and contrast then depends on that theme.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The ordinary text of every page a documentation app serves (headings, paragraphs,
  lists, block quotes, links and inline code) MUST be presented with the host project's styling for
  that kind of content.
- **FR-002**: Every colour this package applies to page content MUST be taken from the host
  project's django-mvp theme. The package MUST define no colour of its own.
- **FR-003**: Pages MUST NOT load any stylesheet from the docs build or from a Sphinx theme.
- **FR-004**: Every admonition MUST be presented as an admonition and grouped by meaning:
  informational, helpful, important, cautionary and dangerous. Admonitions sharing a meaning MUST be
  presented alike and different meanings MUST be distinguishable. An admonition kind with no known
  meaning MUST be presented as informational.
- **FR-005**: "See also" boxes and version notes MUST be presented as distinct from the surrounding
  prose, with deprecation notes carrying the cautionary meaning.
- **FR-006**: Highlighted code MUST take its colours from the host project's theme.
- **FR-007**: Code block captions, line numbers and emphasised lines MUST be shown.
- **FR-008**: A table or code block wider than the reading area MUST scroll within its own area,
  without making the page scroll horizontally, and a wide table's scrolling area MUST be reachable
  and scrollable from the keyboard.
- **FR-009**: Images and figures MUST scale down to fit the reading area, keep their proportions,
  and keep a figure's caption with its image.
- **FR-010**: Every section heading, and every glossary term Sphinx gives an anchor, MUST carry a
  link to its own anchor on the page. The link MUST stay out of the way until the reader points at
  the heading or moves keyboard focus to the link, and MUST have an accessible name identifying the
  section it links to.
- **FR-011**: Following a link to a heading or a glossary term MUST bring it into view below the
  shell's fixed top bar.
- **FR-012**: Glossaries MUST be presented as defined terms with their definitions, and
  cross-references MUST be presented as the site's links.
- **FR-013**: Keyboard keys, interface labels and menu paths MUST be marked out from the
  surrounding text.
- **FR-014**: Page content MUST follow a change of the site's theme, including a switch between
  light and dark, without a reload and without configuration by the host project.
- **FR-015**: Text inside admonitions and in highlighted code MUST meet WCAG 2.2 AA contrast (4.5:1)
  against its own background in django-mvp's default light and dark themes.
- **FR-016**: The styling MUST apply only to the content of pages served by a documentation app.
  The host project's other pages, and the shell around a documentation page, MUST be unaffected.
- **FR-017**: The styling MUST work without any step by the host project beyond those needed to
  serve the pages: no stylesheet to add, no asset build to run and no setting to change.
- **FR-018**: Any transition used to reveal heading links MUST be suppressed when the reader has
  asked for reduced motion.

### Key Entities

- **Page content**: the body of one page of the docs build, as Sphinx wrote it. This feature
  changes how it looks, never what it contains.
- **Admonition meaning**: the group an admonition kind belongs to (informational, helpful,
  important, cautionary, dangerous), which decides how it is presented.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On a page carrying every kind of content this feature covers, no colour is applied
  that does not come from the host project's theme. The package's styles contain no literal colour
  value.
- **SC-002**: Switching a page from the light theme to the dark theme changes every styled part of
  its content, with zero settings changed by the host project.
- **SC-003**: At 320 CSS pixels wide, no page scrolls horizontally, whatever tables, code or images
  it contains.
- **SC-004**: Every section heading's link can be reached with the keyboard alone, and opening its
  address shows that heading in view on the first try.
- **SC-005**: Every text and background pair this package creates inside admonitions and
  highlighted code measures at least 4.5:1 in django-mvp's default light and dark themes.
- **SC-006**: A host project that serves its docs with #4 gets all of the styling above with zero
  additional adoption steps.

## Assumptions

- #4 serves the pages and places them inside the shell. This feature styles what is inside the
  page and does not decide where the page sits on the screen, how wide its reading area is, or
  whether the page's own first heading is its title.
- The host project uses django-mvp's theme mechanism, which exposes the theme's colours to every
  page and switches between light and dark.
- API reference pages generated from code, and mathematical notation, are out of scope (#13).
- Search results, the contents in the sidebar and "On this page" are styled by the features that
  build them (#10, #5, #6).
- A button that copies a code block to the clipboard is not part of this feature. The issue does
  not ask for it, and it adds script to every page.
- Printing is not a target. Pages print however the host project's shell prints.
