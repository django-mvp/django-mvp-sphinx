# Feature Specification: Show a documentation page in the page info dialog

**Feature Branch**: `010-page-extracts`

**Created**: 2026-10-23

**Status**: Draft

**Serves**: G1 · **Roadmap**: — · **Issue**: [#100](https://github.com/django-mvp/django-mvp-sphinx/issues/100)

**Input**: "A developer should be able to take one page of the documentation, or one section of it,
and show it somewhere else on the site. The main use is a view's page info dialog: the info icon
would open the documentation itself instead of a link to it."

## Overview

A django-mvp view can explain itself. When it sets `page_info`, an info icon beside the page title
opens a dialog holding that text. A project that has already written the explanation in its
documentation has two poor choices today. It can copy the words into the view, where they drift
away from the documentation, or it can put a link in the dialog and send the reader away from the
page they were using.

This feature lets a developer take a page of a documentation app, or one section of a page, and use
its content anywhere on the site. The developer names the documentation app and the page's address,
and gets back the page's content, its title and its address. The content can go straight into
`page_info`, and the address into a button at the foot of the dialog that opens the full page.

What they get back is a **page extract**: the page's body as the documentation app would serve it,
without the page's own title. Every link and image in it still leads into the documentation app, and
it is drawn with the same styles the documentation app uses. It is read from the docs build when it
is asked for, like every page, so a rebuild shows without a restart, and Sphinx is never needed to
read it.

An extract follows the documentation app's reader rule. A reader who may not read the documentation
gets no extract. Nobody gets one when the page or the docs build is missing. An empty `page_info`
draws no info icon, so the host page then renders as if no explanation had been set, and never
fails.

A developer can also place an extract from a template, with a template tag that names the
documentation app and the address, without writing a view for it.

This feature builds on the pages served by
[#4](https://github.com/django-mvp/django-mvp-sphinx/issues/4) and the reader rule from
[#9](https://github.com/django-mvp/django-mvp-sphinx/issues/9). It leaves out:

- maths and live examples inside an extract, which need scripts and form handling that only the
  documentation app's own pages load

## Clarifications

### Session 2026-10-23

- Q: How does a developer say which page they want? → A: By the documentation app they mounted and
  the page's address below that app's prefix. That is the address the page is served at, such as
  `reference/accounts/`, or the empty address for the front page. A section is named by adding its
  anchor, as in `reference/accounts/#sharing`, the address a reader would follow to reach it.
  Integrated into FR-001 and FR-006.
- Q: What does a developer get when the address names no page, or the anchor names no section? → A:
  No extract, exactly as for a missing build, so the host page still renders. A mistyped address
  would otherwise fail without a trace, so the package logs a warning naming the documentation app
  and the address. Integrated into FR-010 and User Story 3.
- Q: What does a section hold? → A: Everything from its heading to the next heading at the same
  level or above, so its subsections come with it. The section's own heading is left out, as the
  page's title is, and becomes the extract's title. Integrated into FR-006 and FR-007.
- Q: Where does a link to another part of the same page lead, once the content is shown elsewhere?
  → A: To that part of the page in the documentation app. Inside a dialog on another page there is
  nothing for the link to scroll to, so it leads to where that content lives. Integrated into FR-004.
- Q: What does an extract show for maths and live examples, which this feature leaves out? → A: The
  rest of the page is unaffected. Maths appears as the source Sphinx wrote into the page, and a live
  example is left out. Integrated into FR-012 and recorded under Assumptions.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer shows a documentation page in a view's info dialog (Priority: P1)

A developer has documented a screen of their site in its user guide. In the view for that screen,
they ask for the guide's page by its address and set the extract's content as the view's
`page_info`. A reader on the screen opens the info icon and reads the documentation in the dialog
without leaving the page. It is styled as it is in the documentation app, and its links and images
work.

**Why this priority**: This is the feature. The other stories narrow it or protect it.

**Independent Test**: Build a small Sphinx project to JSON with a page holding a paragraph, an
admonition, an image, a link to another page and a link to one of its own sections. Mount it as a
documentation app, set a view's `page_info` from the page's extract, and render the view.

**Acceptance Scenarios**:

1. **Given** a page of a mounted documentation app, **When** a developer asks for its extract by the
   page's address, **Then** they get the page's body content, its title as plain text, and the
   page's address in the documentation app.
2. **Given** a view whose `page_info` is set from a page's extract, **When** the view renders,
   **Then** its info dialog holds the page's body content as markup, not as escaped text.
3. **Given** a page extract, **When** it is read, **Then** the page's own top-level heading is not
   part of its content.
4. **Given** a page whose body links to another page of the documentation, **When** its extract is
   shown on a page outside the documentation app, **Then** the link leads to that other page's
   address in the documentation app.
5. **Given** a page whose body shows an image from the docs build, **When** its extract is shown on a
   page outside the documentation app, **Then** the image's address is the one the documentation
   app serves it at.
6. **Given** a page whose body links to one of its own sections, **When** its extract is shown on a
   page outside the documentation app, **Then** the link leads to that section of the page in the
   documentation app.
7. **Given** a host page showing an extract, **When** it renders, **Then** the styles the
   documentation app uses for page content apply to the extract.
8. **Given** a page that changes in a rebuild of the docs, **When** its extract is asked for after
   the rebuild, **Then** it has the rebuilt content, without the site being restarted.
9. **Given** the front page, **When** a developer asks for the extract at the empty address, **Then**
   they get the front page's extract.
10. **Given** an environment where Sphinx is not installed, **When** a developer asks for an extract,
    **Then** they get it.

---

### User Story 2 - A developer shows one section of a page (Priority: P2)

A developer's user guide documents several screens on one page, with a section for each. In each
view, they ask for the section that covers that screen by the page's address and the section's
anchor. Each dialog holds only its own section.

**Why this priority**: Authors write documentation for readers, not for dialogs. Without sections, a
guide would need a page per screen to use this feature, or every dialog would hold the whole page.

**Independent Test**: Build a page with three sections, the second holding a subsection, and ask for
the extract of each section by its anchor.

**Acceptance Scenarios**:

1. **Given** a page with several sections, **When** a developer asks for the extract of one by the
   page's address and the section's anchor, **Then** its content holds that section and nothing
   from the sections before or after it.
2. **Given** a section that holds a subsection, **When** a developer asks for the section's extract,
   **Then** the subsection is part of its content.
3. **Given** a section extract, **When** it is read, **Then** the section's own heading is not part
   of its content, its title is the section heading's text, and its address leads to that section
   of the page in the documentation app.
4. **Given** a page address with an anchor that names no section of the page, **When** a developer
   asks for the extract, **Then** they get no extract.
5. **Given** a section whose content links to another section of the same page, **When** its
   extract is shown outside the documentation app, **Then** the link leads to that other section in
   the documentation app.

---

### User Story 3 - A developer's page keeps working when the documentation can't be shown (Priority: P2)

A developer sets a view's `page_info` from an extract. On some requests it can't be shown: the
reader isn't allowed to read that documentation, the docs haven't been built on this machine yet,
or the page has moved. In each case the view renders without an info icon, as if it had no
explanation, and the documentation app's own restrictions hold.

**Why this priority**: The info dialog sits on the host project's own pages. A documentation
problem must never break them, and documentation restricted to some readers must never reach others
through a dialog.

**Independent Test**: Mount a documentation app whose reader rule admits signed-in people only, set
a view's `page_info` from one of its pages, and render the view for an anonymous reader and a
signed-in one. Repeat with the docs build removed, and with an address that names no page.

**Acceptance Scenarios**:

1. **Given** a documentation app whose reader rule excludes the current reader, **When** a developer
   asks for one of its extracts for that reader's request, **Then** they get no extract.
2. **Given** a documentation app whose reader rule admits the current reader, **When** a developer
   asks for one of its extracts for that reader's request, **Then** they get the extract.
3. **Given** a documentation app whose docs build does not exist, **When** a developer asks for an
   extract, **Then** they get no extract, and no error is raised.
4. **Given** an address that names no page of the documentation app, **When** a developer asks for
   its extract, **Then** they get no extract, and a warning naming the documentation app and the
   address is logged.
5. **Given** a view whose `page_info` is set from an extract that could not be had, **When** the
   view renders, **Then** it renders successfully with no info icon.

---

### User Story 4 - A developer offers the full page from the dialog (Priority: P3)

A developer shows a section in a view's info dialog and wants readers who need more to reach the
whole page. They put the extract's address into a button at the foot of the dialog. The button opens
the page in the documentation app, at that section.

**Why this priority**: The dialog is for a short explanation. A way through to the full
documentation makes it safe to show only a section, but the dialog is useful without one.

**Independent Test**: Set a view's `page_info_actions` to a button whose link is a section extract's
address, render the view, and follow the button.

**Acceptance Scenarios**:

1. **Given** a page extract, **When** a developer uses its address as a link, **Then** the link opens
   that page in the documentation app.
2. **Given** a section extract, **When** a developer uses its address as a link, **Then** the link
   opens the page in the documentation app at that section.
3. **Given** a documentation app mounted under a prefix, **When** an extract's address is read,
   **Then** it includes that prefix, so the link works wherever the host page is.

---

### User Story 5 - A developer places a page from a template (Priority: P3)

A developer wants a section of the user guide on one of their own pages, beside the form it
explains, rather than in the info dialog. In the page's template they load the package's template
tags and place the section by naming the documentation app and the section's address. They need
no view code for it. Where they want the title or a link to the full page as well, they bind the
extract to a name and read its title and address.

**Why this priority**: A view already gives a developer every extract. A template tag saves them
writing a view, or a view method, for content that only a template uses.

**Independent Test**: Render a template that places a page and a section with the tag, for readers
the documentation app's reader rule admits and excludes, and with an address that names no page.

**Acceptance Scenarios**:

1. **Given** a template that places a page with the tag, naming the documentation app by its URL
   namespace, **When** it renders, **Then** it holds the page's extract content.
2. **Given** a template that places a section by the page's address and the section's anchor,
   **When** it renders, **Then** it holds that section's extract content and nothing else of the
   page.
3. **Given** a template that binds the extract to a name, **When** it renders, **Then** the name
   holds the extract, with its title and address.
4. **Given** a reader the documentation app's reader rule excludes, a missing docs build, or an
   address that names no page or section, **When** the template renders, **Then** the tag places
   nothing, and a name it binds holds nothing.
5. **Given** a namespace under which no documentation app is mounted, or a template rendered without
   its request, **When** the template renders, **Then** an error names the mistake.

### Edge Cases

- A page whose body is empty once its title is left out, such as a page holding only a table of
  contents, gives an extract with empty content. An empty `page_info` draws no icon.
- An address without its trailing slash names no page, as it does when a reader requests it, so it
  gives no extract.
- An address that tries to leave the docs build, such as one containing `..`, gives no extract and
  never reads a file outside the build.
- A page file that exists but can't be read is a broken docs build, not a missing one. No extract is
  given, the host page still renders, and a warning is logged.
- Two documentation apps mounted in one project each give extracts of their own pages only, with
  addresses under their own prefixes.
- A page that holds maths or a live example gives an extract of everything else on the page.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The package MUST let a developer ask for the extract of a page of a mounted
  documentation app by naming the app and the page's address below the app's prefix, the address
  the page is served at. The empty address MUST name the front page. (US1)
- **FR-002**: An extract MUST carry the page's body content as markup ready to place in a template,
  the page's title as plain text, and the page's address in the documentation app, including the
  app's prefix. (US1, US4)
- **FR-003**: An extract's content MUST NOT include the page's own top-level heading. (US1)
- **FR-004**: Every link and image address in an extract's content MUST lead to the same page,
  section, image or download in the documentation app, wherever on the site the extract is shown.
  This includes links to the page's own sections. (US1, US2)
- **FR-005**: An extract's content MUST be styled by the styles the documentation app applies to a
  page's content, on any page of the host project that shows it. (US1)
- **FR-006**: A developer MUST be able to ask for one section of a page by adding the section's
  anchor to the page's address. The extract's content MUST hold that section and its subsections,
  and nothing before or after it. (US2)
- **FR-007**: A section extract's content MUST NOT include the section's own heading. Its title MUST
  be that heading's text, and its address MUST lead to the section in the documentation app. (US2,
  US4)
- **FR-008**: Asking for an extract MUST take the current request, and MUST give no extract when
  the documentation app's reader rule does not admit that request. (US3)
- **FR-009**: Each of the following MUST give no extract, and MUST NOT raise an error: a missing docs
  build, an address that names no page, an anchor that names no section, an address outside the
  docs build, and a page file that can't be read. (US2, US3)
- **FR-010**: When an address names no page, an anchor names no section, or a page file can't be
  read, the package MUST log a warning naming the documentation app and the address. (US3)
- **FR-011**: An extract MUST be read from the docs build as it is on disk when it is asked for. It
  MUST NOT import Sphinx or start a build, and MUST work where Sphinx is not installed. (US1)
- **FR-012**: An extract of a page holding maths or live examples MUST hold the rest of the page's
  content. (US1)
- **FR-013**: Using extracts MUST NOT change how the documentation app's own pages are served. (US1)
- **FR-014**: The package MUST provide a template tag that places the extract of a page or section,
  given the documentation app's URL namespace and the address, asked for the template's request.
  It MUST place nothing where FR-008 and FR-009 give no extract, and MUST be able to bind the extract
  to a name instead of placing it. A namespace under which no documentation app is mounted, and a
  template rendered without its request, MUST raise an error naming the mistake. (US5)

### Key Entities

- **Page extract**: the content of one page of a documentation app, or of one section of a page,
  taken for use outside the documentation app. It has content ready to place in a template, a title
  as plain text, and the address in the documentation app that it came from.
- **Section**: a part of a page headed by a heading, holding everything up to the next heading at
  the same level or above. It is named by its anchor, the part of its address after `#`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer sets a view's info dialog to a documentation page with one call and no
  template of their own.
- **SC-002**: For every page of a test docs build, every link and image in its extract resolves to
  an address the documentation app answers with a page or a file, when the extract is shown on a
  page outside the documentation app.
- **SC-003**: No request that the documentation app's reader rule excludes ever receives the content
  of one of its pages through an extract.
- **SC-004**: A missing docs build, a missing page, a missing section and an unreadable page file
  each leave the host page rendering successfully, with no info icon.
- **SC-005**: Extracts work with Sphinx absent from the environment, and a rebuilt page shows in its
  extract on the next request.

## Assumptions

- The docs build is the same `sphinx-build -b json` output served by
  [#4](https://github.com/django-mvp/django-mvp-sphinx/issues/4). Extracts need nothing added to the
  host project's Sphinx configuration.
- The content of the docs build is the host project's own and is trusted, as it is when the
  documentation app serves it.
- The main use is django-mvp's page info dialog, set through a view's `page_info` and
  `page_info_actions`. An extract is not tied to it and can be placed in any template.
- Maths and live examples need scripts and form handling that only the documentation app's own pages
  load, so they are not supported inside an extract. Maths appears as the source Sphinx wrote into
  the page, and a live example is left out.
- A section's anchor is the one Sphinx gives its heading, the same anchor a reader follows to reach
  that section in the documentation app.
