# Feature Specification: Get a project from install to a working docs page by following the README

**Feature Branch**: `005-readme-quickstart`

**Created**: 2026-09-30

**Status**: Draft

**Serves**: G3 (adopting it takes a mount and one line in the Sphinx config, with no templates to write)

**Roadmap**: R4

**Input**: Issue #8: "Someone trying the package should get from install to a working
documentation page by reading the README alone: installing it, adding the one line of Sphinx
configuration, building the docs, mounting them and adding the menu entry. The README should also
list everything a project can use. The demo project should serve a user guide of its own, so all of
it can be seen in a browser."

## Summary

A developer with a django-mvp project and a Sphinx source directory reads the README and nothing
else, and ends with their user guide served as pages of their own site: the front page at an
address they chose, the contents in the app sidebar, and an entry in the site's menu leading there.
The README also lists, in full, everything a host project can use from the package. The demo
project serves a user guide written for the demo site, so every state the package draws can be
looked at in a browser.

This feature describes what #4, #5, #6 and #7 deliver. It adds no new behaviour to serving,
navigation or styling. Limiting who can read the docs (#9), search (#10) and a build command (#11)
are out of scope, and the README does not describe them until each one ships.

## Clarifications

### Session 2026-09-30

- Q: How does the quickstart build the docs, with Sphinx directly or with a management command?
  → A: With Sphinx's own JSON builder, run however the project already runs commands. A build
  command is #11, not yet delivered, and the README does not mention it until it ships.
- Q: Does the quickstart teach how to start a Sphinx project from nothing? → A: No. It starts from
  a project that has a Sphinx source directory, and for a project without one it names Sphinx's own
  way of creating it, without repeating Sphinx's documentation.
- Q: Is the demo's user guide the package's own documentation? → A: No. It is a user guide for the
  demo site, written the way a host project would write one for its users, which is the package's
  first audience. The package's own documentation stays the README.
- Q: Where does the demo's docs build come from? → A: The README's demo instructions build it with
  the same step the quickstart teaches, so the demo exercises the path the README documents. Serving
  in the demo still never builds.
- Q: Does the public surface list cover what later features will add? → A: No. It lists what exists
  when this feature merges. Each later feature that adds to the public surface adds its own entries,
  as the constitution requires of every public change.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Follow the quickstart to a working documentation page (Priority: P1)

A developer who has a django-mvp project and a Sphinx source directory for its user guide opens the
README. They install the package, add the one line of Sphinx configuration, build the docs, mount a
documentation app pointed at the docs build, and add its entry to the site's menu. They open the
site and their front page is there, inside the application shell, with the contents in the app
sidebar. They wrote no templates and consulted nothing but the README.

**Why this priority**: This is the whole of G3. A package that works but cannot be adopted from its
README fails the goal it exists for, and the other two stories only support this one.

**Independent Test**: Take a new django-mvp project with a small Sphinx source directory, follow
the README's quickstart literally, and open the site: the front page and the contents are served.

**Acceptance Scenarios**:

1. **Given** a django-mvp project and a Sphinx source directory, **When** a developer carries out
   every step of the quickstart as written, **Then** the front page is served at the address they
   chose, inside the application shell, with the contents in the app sidebar.
2. **Given** a project that has followed the quickstart, **When** a person opens the site's menu,
   **Then** the documentation app's entry is there and leads to the front page.
3. **Given** the quickstart, **When** a developer reads its code, **Then** every step is complete
   code that runs as written, with nothing left to fill in except the project's own names and paths.
4. **Given** a project that has followed the quickstart, **When** it serves its docs from a machine
   that does not have Sphinx installed, **Then** the pages are still served, and the README says
   that Sphinx is needed only where the docs are built.
5. **Given** a project that has followed the quickstart, **When** it changes its Sphinx sources and
   builds the docs again as the README describes, **Then** the site serves the new pages and
   contents without a restart.

---

### User Story 2 - See everything a project can use, in one list (Priority: P2)

A developer deciding whether to adopt the package, or looking for how to change something after
adopting it, reads the README's public surface section. It lists every name a host project can
touch, with what each one does, so they can tell what is supported without reading the source.

**Why this priority**: The quickstart covers the common path. The list is what a developer needs
the first time they step off it, and it is what makes an addition to the public surface a
deliberate decision.

**Independent Test**: Compare the README's public surface section against the package: every name a
host project can use appears in it, and every name in it exists.

**Acceptance Scenarios**:

1. **Given** the package, **When** a developer reads the public surface section, **Then** every
   name a host project can use (what it mounts, the options it can pass, the Sphinx extension, any
   setting, and any template it can override) appears there with what it does.
2. **Given** the public surface section, **When** each listed name is checked against the package,
   **Then** it exists and behaves as described.
3. **Given** features that have not shipped yet, such as limiting who can read the docs, search, or
   a build command, **When** a developer reads the README, **Then** it does not describe them as
   available.

---

### User Story 3 - See every state in the demo (Priority: P3)

A contributor, or a developer evaluating the package, follows the README's demo instructions and
opens the demo site. Its menu has an entry for the demo's user guide, and that guide is written so
that every state the package draws can be reached from the sidebar: contents groups, a page with
pages of its own, a long page with many headings, links to the previous and next page, and each
kind of content a user guide is written with.

**Why this priority**: It is how the work of #4 to #7 gets looked at, and how a change to it gets
judged in a browser, but a project can adopt the package without it.

**Independent Test**: Follow the README's demo instructions, open the demo, and reach each state
listed below from the sidebar without editing anything.

**Acceptance Scenarios**:

1. **Given** the README's demo instructions, **When** a contributor follows them, **Then** the demo
   site's menu has an entry for its user guide, and the guide's front page is served inside the
   application shell.
2. **Given** the demo's user guide, **When** a contributor browses it from the sidebar, **Then**
   they reach at least two contents groups, a page with pages of its own, and a page long enough to
   list several headings under "On this page".
3. **Given** the demo's user guide, **When** a contributor browses its pages, **Then** between them
   they show each kind of admonition, highlighted code, a table wider than the page, an image, a
   download, a glossary, and cross-references between pages.
4. **Given** the demo, **When** a contributor opens an address under the user guide with no page
   behind it, **Then** they get the site's ordinary not-found page.

---

### Edge Cases

- A developer skips the line of Sphinx configuration. The README says what that line is for, so a
  developer whose sidebar shows no contents can find the step they missed.
- A developer mounts the documentation app before building the docs. The README puts the build
  before the mount and says that the docs build must exist before a request arrives.
- A project whose docs build lives outside the project directory, or is produced by a separate CI
  step. The quickstart shows the location as a path the project chooses, not a fixed one.
- A project that wants two documentation apps. The public surface section says that each docs build
  gets its own documentation app, and the quickstart does not need to show it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The README MUST contain a quickstart that takes a django-mvp project with a Sphinx
  source directory to a served front page, covering, in order: installing the package, the one line
  of Sphinx configuration, building the docs, mounting a documentation app, and adding its menu
  entry. (US1)
- **FR-002**: Every step of the quickstart MUST be complete code that runs as written, needing only
  the project's own names and paths. (US1)
- **FR-003**: The quickstart MUST NOT require the host project to write or override a template.
  (US1)
- **FR-004**: The README MUST say that Sphinx is needed only where the docs are built, and that
  serving never builds them. (US1)
- **FR-005**: The README MUST say that rebuilding the docs updates the served pages and contents
  without restarting the site. (US1)
- **FR-006**: The README MUST say what the line of Sphinx configuration is for. (US1)
- **FR-007**: The README MUST point a developer without a Sphinx source directory to Sphinx's own
  way of creating one. (US1)
- **FR-008**: The README MUST contain a public surface section listing every name a host project
  can use, with what each does. (US2)
- **FR-009**: Every name in the public surface section MUST exist in the package and behave as
  described. (US2)
- **FR-010**: The README MUST NOT describe a feature that has not shipped as available. (US2)
- **FR-011**: The demo project MUST serve a user guide of its own through a documentation app, with
  an entry in the demo's menu. (US3)
- **FR-012**: The demo's user guide MUST let a contributor reach, from the sidebar, every state
  listed in User Story 3's acceptance scenarios. (US3)
- **FR-013**: The README's demo instructions MUST produce the demo's docs build with the same step
  the quickstart teaches, before the demo is served. (US3)
- **FR-014**: The README's links MUST be absolute, so they resolve on the package index as well as
  on the repository page. (US1, US2)

### Key Entities

- **Quickstart**: The README section a new host project follows from install to a served front
  page.
- **Public surface section**: The README section listing every name a host project can use.
- **Demo user guide**: The Sphinx source directory the demo project builds and serves, written as a
  user guide for the demo site.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer with a django-mvp project and a Sphinx source directory reaches a served
  front page, with the contents in the sidebar, by following the README alone.
- **SC-002**: Adopting the package takes the five steps G3 names and nothing more: install, one
  line of Sphinx configuration, build, mount, menu entry. No template is written.
- **SC-003**: The public surface section and the package agree exactly: no public name missing from
  the list, and no listed name missing from the package.
- **SC-004**: Every state in User Story 3 can be reached in the demo from the sidebar, with no data
  to edit and no step beyond the README's demo instructions.

## Assumptions

- #4, #5, #6 and #7 are delivered before this feature is built. It documents and demonstrates what
  they deliver and adds nothing to them.
- The reader of the quickstart already has a django-mvp project with its application shell working.
  Setting up django-mvp itself is django-mvp's documentation.
- The package's documentation is its README. It does not gain a documentation site of its own.
- Later features that change the public surface (#9, #10, #11) update the README themselves.
