# Feature Specification: Show working examples live next to their source code

**Feature Branch**: `008-live-examples`

**Created**: 2026-10-01

**Status**: Approved

**Refined**: 2026-10-02. An example is a page the host project writes to be shown as an example,
without the application shell around it. Changes FR-008, FR-009, User Story 1 scenario 5 and User
Story 2 scenario 5. Approved by the maintainer in the session.

**Serves**: G8 · **Roadmap**: R8 · **Issue**: [#12](https://github.com/django-mvp/django-mvp-sphinx/issues/12)

**Input**: "Developer documentation reads better when an example actually runs. A form, for
instance, should work right there on the page, beside the code that defines it. A page should be
able to include a live example from the site with its source shown next to it."

## Overview

An author writing a page of the documentation can put a live example on it. A live example is a
page of the host project itself, shown running inside the documentation page, with the code that
defines it shown beside it. The reader uses the example where it sits: they type into a form,
submit it and see what the site answers, and the documentation page around it stays where it was.

The author adds an example with one marker in the page's Sphinx source. The marker names the
example and the files whose code to show. Nothing is added to the host project's Sphinx
configuration beyond the one line it already has, and the author writes no template.

The example is the host project's own code, served by the host project at its own address. The
host project writes that page to be shown as an example, so it carries its own content and not the
application shell. This package shows it and shows its source. It ships no examples of its own and never runs code written
in the documentation. The source is copied into the docs build when the docs are built, so serving
a page with an example still never imports Sphinx and never starts a build.

This feature builds on the pages served by
[#4](https://github.com/django-mvp/django-mvp-sphinx/issues/4) and leaves other work to its own
issues:

- how highlighted code looks on a page ([#7](https://github.com/django-mvp/django-mvp-sphinx/issues/7)),
  which the example's source reuses as it is
- who may read the documentation ([#9](https://github.com/django-mvp/django-mvp-sphinx/issues/9))
- how API reference pages and maths look ([#13](https://github.com/django-mvp/django-mvp-sphinx/issues/13))

## Clarifications

### Session 2026-10-01

- Q: What is a "live example from the site"? → A: A page the host project already serves at one of
  its own addresses, such as a form view. The author names it. The package runs none of the code
  it finds in the documentation and ships no examples. Integrated into FR-001 and FR-003.
- Q: Where does the source shown beside the example come from, given that serving never reads
  Sphinx? → A: The author names one or more files of the project, or a part of one. Their text is
  copied into the docs build when the docs are built, and that copy is what the page shows. A
  rebuild refreshes it. Integrated into FR-004, FR-005 and FR-014.
- Q: What happens to the documentation page when the reader uses the example? → A: It stays put.
  Submitting a form or following a link inside the example changes the example only. The reader can
  put the example back to how it started, and can open it on its own as an ordinary page of the
  site. Integrated into FR-006, FR-007 and FR-008.
- Q: Who may see an example? → A: The example is requested as the reader, so the host project's own
  rule for that address decides, exactly as if the reader had gone there directly. The
  documentation page neither grants access to an example nor hides its source from someone who may
  read the page. Integrated into FR-011.
- Q: What does a page show when its example cannot be shown, for instance because the address it
  names no longer exists? → A: The page renders as usual with the example's source, and tells the
  reader in the example's place that it is unavailable. It is never a server error. Integrated into
  FR-012 and User Story 3.

### Session 2026-10-02

- Q: How does a page of the site show without the application shell around it when it is an
  example? → A: The host project writes the example's page that way. Its template leaves the
  shell out, and this package ships a base template that does so while keeping the host's theme.
  The page has no shell wherever it is opened, so opening it on its own shows the same thing as
  the example does. A page of the site that has the shell can still be named as an example, and
  it then shows with the shell. Integrated into FR-008, FR-009, User Story 1 scenario 5 and User
  Story 2 scenario 5.

## What a reader sees

These are the screens and states the feature puts in front of a person. How each one looks is
settled on a working prototype, looked at in a browser, and is not specified here.

1. A page with a live example. Among the page's ordinary content sits the example, running, with
   its source beside it on a wide screen. The rest of the page reads as it did before.
2. The same page on a narrow screen. The example and its source no longer fit side by side. Both
   are still there and the reader can get to each.
3. An example with several source files. The reader sees one file's code at a time, can tell which
   file it is, and can move between them.
4. An example that has been used. After the reader submits a form, the example shows what the site
   answered, such as validation errors or a confirmation. The documentation page has not moved, and
   the reader can put the example back to its starting state.
5. An example that has not appeared yet. While the example is still being fetched, its place on
   the page is held and its source is already readable.
6. An example that is unavailable. The page says so in the example's place and still shows the
   source.
7. An example the site refuses or fails. Where the site answers the example's address with a
   sign-in page, a refusal or an error, that answer is what appears in the example's place. The
   page and the source are unaffected.
8. A page with several examples. Each one runs on its own, and using one changes none of the
   others.
9. A page read with JavaScript turned off. The source is shown and the reader can still reach the
   example.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See an example running beside its source (Priority: P1)

An author adds one marker to a page, naming a page of the site and the file that defines it. A
reader opening the documentation page sees that example running inside it, with the code beside
it. They fill in the example's form and submit it. The example shows the site's answer, and the
documentation page stays where it was.

**Why this priority**: This is the feature. Without it a page can only describe an example.

**Independent Test**: In a host project with a form view, add the marker to a page of a small
Sphinx project, build it to JSON, mount it as a documentation app, open the page, and submit the
example's form with valid and invalid input.

**Acceptance Scenarios**:

1. **Given** a page whose source names a live example and one source file, **When** the docs are
   built and the page is requested, **Then** the page renders inside the application shell with the
   example's place on it pointing at the example's address on the same site, and with the named
   file's code on the page.
2. **Given** that page, **When** it renders, **Then** the code shown is the text of the named file
   as it was when the docs were built, as plain text that is never interpreted as markup.
3. **Given** a host project that already has the package's one line of Sphinx configuration,
   **When** an author adds a live example to a page, **Then** the build succeeds with no further
   configuration and no template written by the author.
4. **Given** a live example containing a form, **When** the reader submits it, **Then** the site's
   answer appears in the example and the documentation page's address and content are unchanged.
5. **Given** a live example whose page is written on the package's base template for examples,
   **When** the page renders, **Then** the example shows its own content without a second copy of
   the application shell's navigation around it.
6. **Given** a page with the example's marker placed between two paragraphs, **When** it renders,
   **Then** the example appears between those paragraphs, and the page's other content, its
   contents in the sidebar and its headings list are the same as without the example.
7. **Given** a page with two live examples, **When** the reader uses one, **Then** the other is
   unchanged.
8. **Given** an environment where Sphinx is not installed, **When** a page with a live example is
   requested, **Then** it renders the same as where Sphinx is installed.

---

### User Story 2 - Read the code that makes the example (Priority: P2)

An example is rarely one file. The author names the form, the view and the template, or only the
part of a file that matters. The reader moves between those files without leaving the example and
reads the code highlighted like any other code on the page. After trying the example they put it
back to how it started, and they can open it on its own to see it as a full page.

**Why this priority**: User Story 1 already shows an example and its code. This makes an example of
realistic size readable, and lets a reader try it more than once.

**Independent Test**: Add an example naming three source files, one of them by a part of the file
only, build, open the page, move between the files, use the example and reset it.

**Acceptance Scenarios**:

1. **Given** an example whose marker names several source files, **When** the page renders,
   **Then** every named file's code is on the page, each identified by a name the reader can tell
   apart, in the order the author gave them.
2. **Given** a marker that names part of a file, **When** the page renders, **Then** only that part
   is shown.
3. **Given** a source file in a language Sphinx highlights, **When** the page renders, **Then** its
   code is highlighted in the same way as a code block of that language on the same page.
4. **Given** an example the reader has used, **When** they reset it, **Then** it returns to the
   state it had when the page was opened, and the documentation page does not reload.
5. **Given** a live example, **When** the reader chooses to open it on its own, **Then** they reach
   the example's address, where it shows as it does in the example.
6. **Given** a screen too narrow to show the example and its source side by side, **When** the page
   renders, **Then** both remain reachable and neither makes the page scroll sideways.

---

### User Story 3 - The page holds up when an example can't be shown (Priority: P3)

Sites change. The address an example names is removed, a reader is not allowed to see it, the view
raises an error, a file named as source is deleted, or the reader's browser has scripts off. In
each case the documentation page is still a working page and the reader can tell the example is
missing instead of seeing a blank space. The author hears about a mistake when the docs are built.

**Why this priority**: These are the conditions a host project meets after the first example works.
None of them is needed to show one.

**Independent Test**: Build pages whose examples name an address that does not exist, an address
behind a sign-in, and a view that raises, and a page whose marker names a missing source file.
Request each page as an anonymous and as a signed-in reader, with scripts on and off.

**Acceptance Scenarios**:

1. **Given** an example naming an address the site does not have, **When** the page is requested,
   **Then** the page renders successfully, tells the reader in the example's place that the example
   is unavailable, and still shows the source.
2. **Given** an example at an address the reader is not allowed to see, **When** the page is
   requested, **Then** the page renders with the source, and the example's address gives that
   reader the same answer it gives when requested directly.
3. **Given** an example whose view fails, **When** the page is requested, **Then** the
   documentation page itself responds successfully.
4. **Given** a marker that names a source file that does not exist, **When** the docs are built,
   **Then** the build reports the problem, naming the page and the file.
5. **Given** a marker that names an address on another site, **When** the docs are built, **Then**
   the build reports the problem and the built page carries no example pointing off the site.
6. **Given** a browser with JavaScript turned off, **When** a page with a live example is
   requested, **Then** the source is shown and the page gives the reader a way to reach the
   example.
7. **Given** a documentation app serving a docs build, **When** the host project changes a source
   file and rebuilds the docs, **Then** the next request for the page shows the new code without
   the site being restarted.
8. **Given** a documentation app whose reader rule excludes a reader, **When** that reader requests
   a page with a live example, **Then** they get what the reader rule gives for any page, and no
   source.
9. **Given** a docs build with no live examples in it, **When** its pages are requested, **Then**
   they are served the same as before this feature.

---

### Edge Cases

- The example's code changes after the docs were built. The example runs the new code and the page
  shows the old source until the docs are rebuilt. That is accepted, and a rebuild puts it right.
- An example taller or wider than the space the page gives it can still be read and used in full.
- A docs build made by a Sphinx project without the package's extension has no examples in it and
  is served as before.
- A page read in the host's dark theme shows the example in the dark theme too, because the
  example is a page of the same site.
- The same example may appear on several pages, and each appearance is independent.
- Source text that contains characters with meaning in HTML is shown as written.
- An example that changes data does so as the reader, as it would at its own address. Whether an
  example should change anything is the host project's decision when it writes the example.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: An author MUST be able to place a live example on a page with one marker in the
  page's Sphinx source that names the example and its source files. (US1)
- **FR-002**: Adding a live example MUST need nothing in the host project's Sphinx configuration
  beyond what serving pages already needs, and no template written by the author. (US1)
- **FR-003**: A live example MUST be a page of the host project at an address of the same site. The
  package MUST NOT execute code written in the documentation, and a marker naming an address on
  another site MUST be reported when the docs are built and MUST NOT produce an example. (US1, US3)
- **FR-004**: The page MUST show, with each live example, the code of every source file its marker
  names, or of the named part of a file, in the author's order, each identified by name. A live
  example MUST name at least one source file. (US1, US2)
- **FR-005**: Source MUST be shown as plain text that is never interpreted as markup, and MUST be
  highlighted the way a code block of the same language is on that page. (US1, US2)
- **FR-006**: The example MUST run in place on the documentation page. Anything the reader does
  inside it, including submitting a form, MUST change the example only and MUST NOT change the
  documentation page's address or reload it. (US1)
- **FR-007**: The reader MUST be able to return a live example to the state it had when the page
  was opened. (US2)
- **FR-008**: The reader MUST be able to open a live example on its own, at its address. (US2)
- **FR-009**: The package MUST give the host project a way to write an example's page so that it
  shows its own content without the application shell's navigation around it, in the host's theme,
  and with what the site says after a form is sent. A host project's own base template MUST NOT
  need to change for it. (US1)
- **FR-010**: A live example MUST appear where its marker sits in the page, and a page MAY hold
  several, each independent of the others. A page's other content, its place in the contents and
  its headings list MUST be unaffected by its examples. (US1)
- **FR-011**: A live example MUST be requested as the reader, so the host project's own rule for
  the example's address decides what that reader gets. A documentation page MUST NOT make an
  example reachable by someone the site would refuse at its address, and the documentation app's
  reader rule MUST govern the page and its source as it governs any page. (US3)
- **FR-012**: When a live example's address does not exist on the site, the page MUST render
  successfully, tell the reader in the example's place that it is unavailable, and show the source.
  A live example that the site refuses or that fails MUST NOT stop the documentation page from
  rendering. (US3)
- **FR-013**: When a marker names a source file that does not exist, the build MUST report it,
  naming the page and the file. (US3)
- **FR-014**: The source shown MUST come from the docs build as it is on disk at the moment of the
  request, so a rebuild shows without restarting the site. Serving a page with a live example MUST
  NOT import Sphinx, start a build, or read source files from outside the docs build. (US1, US3)
- **FR-015**: With JavaScript turned off, a page with a live example MUST still show the source and
  give the reader a way to reach the example. (US3)
- **FR-016**: On a screen too narrow for the example and its source side by side, both MUST remain
  reachable and neither may make the page scroll sideways. (US2)
- **FR-017**: A docs build that contains no live examples MUST be served the same as before this
  feature. (US3)
- **FR-018**: The demo project's guide MUST include live examples that between them show every
  state listed under "What a reader sees", so each can be looked at in a browser. (US1, US2, US3)

### Key Entities

- **Live example**: a page of the host project shown running inside a page of the documentation.
  It has the address it runs at and one or more pieces of example source.
- **Example source**: the code shown beside a live example. Each piece has a name the reader sees,
  a language, and the text of a file or part of a file as it was when the docs were built.
- **Marker**: what the author writes in a page's Sphinx source to place a live example there. It
  names the example and its source.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An author puts a working example on a page by adding one marker to that page and
  rebuilding the docs, with no other file changed.
- **SC-002**: A reader submits an example's form and sees the site's answer without the
  documentation page's address changing, for every live example in the demo project's guide.
- **SC-003**: For every live example in the demo project's guide, the code shown is identical to
  the named file, or named part of it, at the time of the build.
- **SC-004**: Every state listed under "What a reader sees" can be reached in the demo project,
  and in none of them does the documentation page answer with a server error.
- **SC-005**: Every page with a live example is served the same with Sphinx absent from the
  environment as with it present.

## Assumptions

- The docs build is the `sphinx-build -b json` output served by
  [#4](https://github.com/django-mvp/django-mvp-sphinx/issues/4), built with the package's Sphinx
  extension, which the host project already has from the one line of configuration.
- The author of the documentation is the host project. What a marker names is trusted in the way
  the rest of the project's documentation source is.
- The host project writes its examples as pages of its own site and decides who may see them and
  what they may change. This package adds no examples and no access rule.
- An example's page is written for the purpose. A page of the site that carries the application
  shell can be named as an example too, and shows with the shell inside the example's place.
- The host project allows its own site to show its own pages in a frame. Django refuses that by
  default, so it is a documented setup step.
- The example is live and the source is a copy made at build time. The two can drift between
  builds (see Edge Cases).
- How the example and its source are arranged and how they look are settled on a working prototype
  before the build, and come from the host's django-mvp theme (CONSTITUTION.md Article XIII). That
  covers the reset and open-on-its-own controls and the unavailable notice too. The requirements
  above say what the reader can do and leave the look to the prototype.
- Editing an example's code in the browser, running code typed into the page, and examples from
  other sites are not part of this feature.
- `CONTEXT.md` gains "live example" and "example source" when the feature is built.
