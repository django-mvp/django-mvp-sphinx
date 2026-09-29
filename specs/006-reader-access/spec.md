# Feature Specification: Let the project decide who can read its documentation

**Feature Branch**: `006-reader-access`

**Created**: 2026-09-30

**Status**: Draft

**Serves**: G5 · **Roadmap**: R5 · **Issue**: [#9](https://github.com/django-mvp/django-mvp-sphinx/issues/9)

**Input**: "Some projects publish their user guide, while others keep it for signed-in people or a
particular group. The project should be able to choose, and people it excludes should see neither
the pages nor the menu entry that leads to them."

## Overview

A host project decides, for each documentation app it mounts, who may read it: everyone, only
signed-in people, or people who pass a rule of its own, such as belonging to a group. A reader the
rule lets in sees the documentation exactly as before. A reader it excludes finds no trace of it in
the site: no menu entry, no contents, and no page, image or download at any address under the
documentation app. A visitor who isn't signed in is asked to sign in and brought back to the page
they wanted. A signed-in person the rule excludes gets the site's ordinary forbidden response.

A documentation app with no rule set stays readable by everyone, as it is today.

This feature limits access to what the documentation app serves. It builds on the pages served by
[#4](https://github.com/django-mvp/django-mvp-sphinx/issues/4). The contents in the sidebar
([#5](https://github.com/django-mvp/django-mvp-sphinx/issues/5)) and search
([#10](https://github.com/django-mvp/django-mvp-sphinx/issues/10)) are their own features. This one
only requires that an excluded reader never reaches them.

## Clarifications

### Session 2026-09-30

- Q: What does a reader the rule excludes get when they request a documentation address? → A: A
  visitor who isn't signed in is sent to the host project's sign-in page and, once signed in, back
  to the address they asked for. A signed-in person the rule excludes gets the host project's
  ordinary forbidden response. Neither gets a page, an image or a download. Integrated into FR-005
  and FR-006 and User Story 2.
- Q: Who can read a documentation app whose host project sets no rule? → A: Everyone, which is how
  pages are served before this feature. Integrated into FR-002 and User Story 1.
- Q: Can different pages of one documentation app have different readers? → A: No. The rule covers
  the whole documentation app. A project whose docs have different audiences mounts one
  documentation app per audience, each with its own docs build and its own rule. Integrated into
  FR-001 and FR-011.
- Q: Do the images and downloads a page links to follow the rule? → A: Yes. Every address under the
  documentation app follows it, files included, so a reader excluded from a page can't fetch its
  screenshots or downloads by address either. Integrated into FR-004.
- Q: When does a change in a person's standing, such as signing in or joining a group, change what
  they can read? → A: On their next request. The rule is asked on every request and nothing it
  answered is remembered, so no restart and no fresh session is needed. Integrated into FR-009.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Keep the documentation for signed-in people (Priority: P1)

A host project whose user guide is for its own users, not the public, sets its documentation app
to signed-in people only. A signed-in person reads the docs as before. A visitor who isn't signed in
sees no menu entry for the docs, and a documentation address they have been given sends them to
sign in, then on to the page.

**Why this priority**: This is the choice most host projects with a private user guide need, and it
is expressed without writing any code. It also establishes everything an excluded reader must not
see, which the other stories reuse.

**Independent Test**: Mount a documentation app limited to signed-in people and request its front
page, a nested page, an image and a download, first without signing in and then signed in. Render
a host page in both states and look for the documentation's menu entry.

**Acceptance Scenarios**:

1. **Given** a documentation app the host project has not limited, **When** a visitor who isn't
   signed in requests any of its pages, **Then** the page is served, and the menu entry is shown on
   the host project's pages.
2. **Given** a documentation app limited to signed-in people, **When** a signed-in person requests
   any of its pages, images or downloads, **Then** each is served exactly as it is without a rule.
3. **Given** the same app, **When** a visitor who isn't signed in requests any of its pages,
   **Then** they are sent to the host project's sign-in page, and the response carries none of the
   page's content.
4. **Given** that visitor, **When** they sign in, **Then** they arrive at the documentation address
   they first requested.
5. **Given** the same app, **When** a visitor who isn't signed in views any page of the host
   project, **Then** the documentation app's menu entry is absent.
6. **Given** the same app, **When** a signed-in person views any page of the host project, **Then**
   the menu entry is present and leads to the front page.

---

### User Story 2 - Keep the documentation for a particular group (Priority: P2)

A host project whose documentation is for some of its users only, such as staff or members of a
group, gives its documentation app a rule of its own. People who pass it read the docs. A
signed-in person who doesn't pass it sees no menu entry, and a documentation address gets them the
site's ordinary forbidden response.

**Why this priority**: The issue names a particular group as a case the project must be able to
choose, but fewer host projects need it than need signed-in only, and User Story 1 already covers
what an excluded reader must not see.

**Independent Test**: Mount a documentation app with a rule admitting members of one group. Request
its pages and files as a member, as a signed-in person outside the group, and as a visitor who
isn't signed in, and render a host page as each.

**Acceptance Scenarios**:

1. **Given** a documentation app with a rule of the host project's own, **When** a person the rule
   admits requests any of its pages, images or downloads, **Then** each is served.
2. **Given** the same app, **When** a signed-in person the rule excludes requests any of its pages,
   images or downloads, **Then** the response is the host project's ordinary forbidden response,
   with the forbidden status, and carries none of the requested content.
3. **Given** the same app, **When** a visitor who isn't signed in and whom the rule excludes
   requests any of its pages, **Then** they are sent to the sign-in page, as in User Story 1.
4. **Given** the same app, **When** a person the rule excludes views any page of the host project,
   **Then** the documentation app's menu entry is absent, and a person the rule admits sees it.
5. **Given** a rule of the host project's own that admits people by a permission rather than a
   group, **When** people with and without that permission request a page, **Then** each is
   admitted or refused as the rule says.

---

### User Story 3 - Different documentation for different readers (Priority: P3)

A host project with a user guide for everyone and an administrator's guide for staff mounts two
documentation apps, each with its own rule. Each reader sees the documentation meant for them and
no trace of the other.

**Why this priority**: Two audiences are a less common need, and they follow from giving each
documentation app its own rule. The single-app stories above work without it.

**Independent Test**: Mount two documentation apps, one open to everyone and one limited to staff,
and request pages of each and render a host page as a visitor, a signed-in person and a staff
member.

**Acceptance Scenarios**:

1. **Given** two documentation apps with different rules, **When** a reader one admits and the
   other excludes views the host project's pages, **Then** only the admitting app's menu entry is
   present.
2. **Given** the same two apps, **When** that reader requests pages of each, **Then** the admitting
   app's pages are served and the excluding app's pages are refused, each as its own rule says.
3. **Given** a person whose standing changes between two requests, such as signing in or being
   added to the admitting group, **When** they make the next request, **Then** what they can read
   and which menu entries they see follow their new standing, with no restart of the site.

---

### Edge Cases

- An address under a documentation app with no page behind it is refused to an excluded reader in
  the same way as an address with a page, so the refusal never reveals which pages exist.
- A documentation app whose docs build doesn't exist yet refuses an excluded reader in the same way
  as one whose build exists.
- An address without its trailing slash is refused to an excluded reader rather than redirected, so
  the redirect never confirms that a page exists.
- An excluded reader never sees the documentation's contents, its page titles or its name in any
  part of the application shell, including on the host project's own pages.
- A rule that admits no one hides the documentation app from every reader, without the host project
  having to unmount it.
- A rule raising an error is a fault in the host project. It fails as a server error, never as
  serving the page.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The host project MUST be able to set who may read each documentation app, separately
  for each one it mounts. (US1, US2, US3)
- **FR-002**: A documentation app with no rule set MUST be readable by everyone, signed in or not.
  (US1)
- **FR-003**: The host project MUST be able to limit a documentation app to signed-in people by
  choosing that option, without writing a rule of its own. It MUST also be able to supply a rule of
  its own that decides from the request, which covers group membership, permissions and anything
  else the request tells it. (US1, US2)
- **FR-004**: The rule MUST apply to every address under the documentation app: every page, the
  front page, every image and every download, and any address later features add to the
  documentation app. (US1, US2)
- **FR-005**: A request the rule refuses from a visitor who isn't signed in MUST be sent to the host
  project's sign-in page, which returns the visitor to the requested address once they sign in.
  (US1, US2)
- **FR-006**: A request the rule refuses from a signed-in person MUST get the host project's
  ordinary forbidden response, with the forbidden status. (US2)
- **FR-007**: A refused request MUST NOT return any content from the docs build, and MUST be
  answered the same way whether or not a page or file exists at the address, whether or not the
  docs build exists, and whether or not the address has its trailing slash. (US1, US2)
- **FR-008**: A reader the rule excludes MUST NOT be shown the documentation app's menu entry, its
  contents, or any page title or name from it, on any page of the host project. A reader the rule
  admits MUST see the menu entry wherever the host project placed it. (US1, US2, US3)
- **FR-009**: The rule MUST be asked on every request, so a change in a person's standing takes
  effect on their next request without restarting the site. (US3)
- **FR-010**: A reader the rule admits MUST be served every page, image and download exactly as the
  same documentation app serves it without a rule. (US1, US2)
- **FR-011**: Each documentation app's rule MUST affect only that documentation app's addresses and
  menu entry, never another documentation app's or the host project's other pages. (US3)
- **FR-012**: An error raised by the host project's rule MUST surface as a server error and MUST NOT
  cause the request to be served. (US2)

### Key Entities

- **Documentation app**: the mounted app that serves one docs build under one URL prefix. This
  feature gives it a rule for who may read it, which defaults to everyone.
- **Reader rule**: the host project's answer, for one request, to whether the person making it may
  read the documentation app. It is one of: everyone, signed-in people only, or a rule of the host
  project's own that decides from the request.
- **Excluded reader**: a person the documentation app's rule refuses on a given request. They are
  either not signed in (and are asked to) or signed in and refused.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A host project can make its documentation public, limit it to signed-in people, or
  limit it by a rule of its own such as group membership, and each takes one setting on the
  documentation app. Limiting to signed-in people needs no code.
- **SC-002**: For every choice, a reader the rule excludes receives no page, image or download from
  any address under the documentation app, and no response to them differs by whether the address
  has something behind it.
- **SC-003**: On every page of the host project, the documentation app's menu entry is present for
  every reader the rule admits and absent for every reader it excludes.
- **SC-004**: A documentation app mounted without a rule serves every page, image and download to
  everyone, exactly as before this feature.
- **SC-005**: A visitor who isn't signed in and follows a link to a limited page reaches that page
  after signing in, with no other navigation.

## Assumptions

- The host project has a sign-in page wherever it limits documentation to signed-in people or to a
  rule that excludes visitors who aren't signed in. Providing one is the host project's concern.
- The rule covers a whole documentation app. Different readers for different pages means mounting
  one documentation app per audience (CONSTITUTION.md Article XII, one docs build per documentation
  app).
- The rule is the only thing that decides. Staff and superusers get no bypass unless the host
  project's rule admits them.
- The host project's own pages that link into the documentation, outside the documentation app and
  its menu entry, are the host project's concern.
- Search results ([#10](https://github.com/django-mvp/django-mvp-sphinx/issues/10)) are served under
  the documentation app, so this rule already governs who can search. Search itself is #10's.
