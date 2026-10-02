# Feature Specification: Make API reference pages and maths look like the rest of the site

**Feature Branch**: `009-api-reference-and-maths`

**Created**: 2026-10-01

**Status**: Draft

**Serves**: G9 (developer docs look right too: API reference pages and maths render properly in the host's theme), G1 (a project's Sphinx docs read as pages of its own site)

**Roadmap**: R9, API reference and maths look right

**Issue**: [#13](https://github.com/django-mvp/django-mvp-sphinx/issues/13)

**Depends on**: [#7](https://github.com/django-mvp/django-mvp-sphinx/issues/7), which styles a page's ordinary content from the host project's theme. This feature extends that styling to two kinds of content it left out.

**Input**: "Pages generated from code, such as class and function reference, and pages with
mathematical notation, should look as much a part of the site as the user guide does, taking their
colours and type from the site's theme."

## Overview

A documentation app already serves user-guide pages that read as the host project's own. Two kinds
of content still arrive unstyled: the reference entries Sphinx writes for classes, functions and
other objects, and mathematical notation.

After this feature, a reader who opens an API reference page sees each documented object as an
entry of its own, with its signature, its description and its parameters laid out so one entry is
easy to tell from the next. A reader who opens a page with maths sees typeset notation, in the
sentence where the author put it or set out on its own line. Both take every colour from the host
project's django-mvp theme, follow a theme change and dark mode, and need no styling step from the
host project.

The feature changes how this content looks and never what it contains. It leaves other work to
its own issues:

- ordinary page content, admonitions, highlighted code, tables and glossaries
  ([#7](https://github.com/django-mvp/django-mvp-sphinx/issues/7))
- which headings "On this page" lists
  ([#6](https://github.com/django-mvp/django-mvp-sphinx/issues/6))
- live examples running beside their source
  ([#12](https://github.com/django-mvp/django-mvp-sphinx/issues/12))

## What a reader sees

The screens and states below are the whole of what this feature puts in front of a person. How
each one looks is settled by looking at it in a browser, not in this specification.

**An API reference page.** A page holding reference entries, in these states:

- an entry for a module-level function, with its signature, description, parameters, return value
  and the errors it raises
- an entry for a class, with its own description and with its methods, attributes and properties
  as entries nested inside it
- an entry that is deprecated, and an entry with no description at all
- an entry whose signature is too long for the reading area
- an entry reached by a link from elsewhere, so the page opens at that entry
- a summary table listing several objects with a one-line description each, where the page has one
- each of the above in the light and the dark theme, and on a narrow screen

**A page with mathematical notation.** A page holding maths, in these states:

- maths inside a sentence
- maths set out on its own line, including an equation wider than the reading area
- a numbered equation, and a reference to it from the text
- the same page before the maths has been typeset, or when it cannot be (scripts turned off)
- each of the above in the light and the dark theme, and on a narrow screen

**A page with neither.** It looks and loads exactly as it does today.

## Clarifications

### Session 2026-10-01

The coverage scan found five ambiguities. Each was answered from the issue, its siblings, the
constitution and the specification for #7. Longer rationale is in `decisions.md`.

- Q: The issue says "pages generated from code". Does a reference entry an author wrote by hand,
  without generating it from code, get the same treatment? → A: Yes. Sphinx writes both the same
  way into the docs build, and a reader cannot tell them apart. The feature covers every reference
  entry on any page, whichever language it documents and however it was written. Integrated into
  FR-001 and User Story 1.
- Q: Sphinx can also build a general index and a module index. Are those "pages generated from
  code" for this feature? → A: No. They are lists of where things are, not reference content, and
  serving them is a matter of which pages a documentation app serves. This feature styles what is
  on the pages already served. Recorded under Assumptions.
- Q: What does a reader see where maths cannot be typeset, for example with scripts turned off? →
  A: The notation as the author wrote it, set apart from the prose and readable in both themes.
  The rest of the page is unaffected. Integrated into FR-011 and User Story 2.
- Q: Does a page with no maths pay anything for this feature? → A: No. Whatever typesetting needs
  is loaded only by pages that hold maths. Integrated into FR-012.
- Q: #7 gave headings a link a reader can copy. Do reference entries get one? → A: Yes. Pointing a
  colleague at one function is the commonest reason to link into reference documentation, and
  Sphinx already gives each entry an anchor. Entries behave as headings do: the link stays out of
  the way until it is pointed at or focused, and following it brings the entry into view.
  Integrated into FR-005, FR-006 and User Story 3.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reference entries read as part of the site (Priority: P1)

A developer opens an API reference page to find out how to call something. Each documented object
is an entry of its own. The signature stands out from the description beneath it, and the name
being documented stands out within the signature. Parameters, return values and raised errors are
laid out as lists the developer can scan. A class's methods and attributes sit visibly inside the
class. When the site switches to dark mode, or the host project changes its theme, the page
follows with nothing configured.

**Why this priority**: This is the first half of the issue. Without it a reference page is a run
of unstyled text in which one entry cannot be told from the next, and the documentation stops
looking like the host project the moment a reader leaves the user guide.

**Independent Test**: Build a small Sphinx project to JSON with a module holding a function, a
class with methods, attributes and a property, an exception and a constant, mount it as a
documentation app, and view the page under django-mvp's default light and dark themes.

**Acceptance Scenarios**:

1. **Given** a page with several reference entries, **When** a reader opens it, **Then** each
   entry is presented as a unit of its own, with its signature distinguishable from its
   description and from the entries around it.
2. **Given** a signature with a name, parameters, default values and type annotations, **When** a
   reader opens the page, **Then** the name being documented is distinguishable from the other
   parts of the signature.
3. **Given** an entry that documents parameters, a return value and raised errors, **When** a
   reader opens the page, **Then** each group is presented as a labelled list, and every item's
   name is distinguishable from its description.
4. **Given** a class entry with methods, attributes and properties, **When** a reader opens the
   page, **Then** each member is presented as an entry inside the class's entry, and a reader can
   tell which class a member belongs to.
5. **Given** a reader viewing a reference page in the light theme, **When** they switch the site
   to the dark theme, **Then** every part of every entry follows the new theme without a reload
   and without any configuration by the host project.
6. **Given** a reference entry, **When** a reader views it in django-mvp's default light or dark
   theme, **Then** every part of its signature and field lists meets WCAG 2.2 AA contrast against
   its own background.
7. **Given** a host project that has done only what serving its pages requires, **When** a reader
   opens a reference page, **Then** all of this styling is present, with no stylesheet added, asset
   build run or setting changed by the host project.
8. **Given** a reference entry written by hand and one generated from code, **When** a reader
   opens the page, **Then** both are presented the same way.

---

### User Story 2 - Maths is typeset in the site's theme (Priority: P1)

A reader opens a page that explains a calculation. The maths in a sentence sits in the line of
text as notation, and an equation set out on its own line stands apart from the prose around it.
The notation is the colour of the text around it and follows the site's theme and dark mode. If
the reader's browser cannot typeset it, they see the notation as the author wrote it, and the rest
of the page is unaffected.

**Why this priority**: This is the second half of the issue. Today a page with maths shows the
author's raw markup, which a reader cannot be expected to read, so the page is wrong and not
merely unstyled.

**Independent Test**: Build a small Sphinx project to JSON with a page holding maths inside a
sentence and on its own line, and a page with no maths. Mount it as a documentation app and view
both pages under the default light and dark themes, with scripts on and with scripts off.

**Acceptance Scenarios**:

1. **Given** a page with maths inside a sentence, **When** a reader opens it, **Then** the maths
   is typeset as notation within the line of text.
2. **Given** a page with maths set out on its own line, **When** a reader opens it, **Then** the
   maths is typeset as notation, set apart from the prose around it.
3. **Given** typeset maths, **When** the reader switches between the light and dark themes,
   **Then** the notation follows the theme and stays the colour of the text around it.
4. **Given** a page with maths, **When** the reader's browser cannot typeset it, **Then** the
   notation is shown as the author wrote it, set apart from the prose and readable in both themes,
   and the rest of the page is presented as usual.
5. **Given** a page with no maths, **When** a reader opens it, **Then** nothing is loaded for
   typesetting maths.
6. **Given** typeset maths, **When** a screen-reader user reaches it, **Then** the maths is
   available to them as maths and not skipped or read as markup.
7. **Given** a host project that builds its docs with Sphinx's default settings for maths,
   **When** a reader opens a page with maths, **Then** the maths is typeset with no step by the
   host project beyond those needed to serve the pages.

---

### User Story 3 - Point someone at one entry (Priority: P2)

A developer wants to send a colleague to one method. Each entry carries a link to itself, out of
the way until the developer points at the signature or tabs to the link. Opening a copied link
shows the page at that entry, fully in view. Names in the text that refer to other documented
objects are links to their entries, and where the docs build links an entry to its source code,
that link is there too.

**Why this priority**: Linking to a single function is the commonest way reference documentation
is shared, but a reference page can be read without it.

**Independent Test**: Serve a page with several entries that refer to one another, reach each
entry's link by pointer and by keyboard, open the link's address, and confirm the page opens with
that entry in view.

**Acceptance Scenarios**:

1. **Given** a reference page, **When** a reader opens it, **Then** every entry Sphinx gave an
   anchor carries a link whose address is the page's address with that entry's anchor.
2. **Given** an entry's link, **When** the reader is not pointing at the signature and the link
   does not have keyboard focus, **Then** the link is kept out of the way, and **When** they point
   at the signature or move keyboard focus to the link, **Then** it is revealed.
3. **Given** an entry's link, **When** a screen-reader user reaches it, **Then** it has an
   accessible name that identifies the entry it links to.
4. **Given** an entry link's address, **When** a reader opens it, **Then** the page opens with the
   entry in view and not hidden behind the shell's fixed top bar.
5. **Given** text that refers to another documented object, **When** a reader opens the page,
   **Then** the reference is presented as one of the site's links and leads to that object's
   entry.
6. **Given** a docs build that links entries to their source code, **When** a reader opens the
   page, **Then** each such link is presented with its entry and is reachable by keyboard.
7. **Given** a reader who has asked their browser for reduced motion, **When** an entry's link is
   revealed, **Then** it appears without any transition.

---

### User Story 4 - Long signatures and wide equations stay inside the page (Priority: P2)

A reader on a phone opens a reference page with a function that takes a dozen parameters, and a
page with a long equation. The page itself never scrolls sideways. The whole signature and the
whole equation can still be read.

**Why this priority**: Reference signatures and displayed equations are the widest content a
documentation page carries. A page that scrolls sideways fails WCAG 1.4.10 (reflow), but only
pages with this content are affected.

**Independent Test**: Serve a page with a signature and an equation each wider than the screen,
view it at 320 CSS pixels wide, and confirm the page does not scroll horizontally while every part
of both stays reachable, including by keyboard.

**Acceptance Scenarios**:

1. **Given** an entry whose signature is wider than the reading area, **When** a reader opens the
   page on a narrow screen, **Then** the page does not scroll horizontally and every part of the
   signature can be read.
2. **Given** an equation wider than the reading area, **When** a reader opens the page on a narrow
   screen, **Then** the page does not scroll horizontally and every part of the equation can be
   reached.
3. **Given** a signature or an equation that scrolls within its own area, **When** a
   keyboard-only reader moves focus through the page, **Then** they can reach that area and scroll
   it.
4. **Given** entries nested inside a class entry, **When** a reader opens the page on a narrow
   screen, **Then** the nesting is still apparent and the nested entries' text is not squeezed out
   of the reading area.

---

### User Story 5 - Numbered equations, deprecations and summaries (Priority: P3)

A reader follows a derivation that refers back to an earlier equation by its number, and a
developer scans a module's summary of what it contains. The equation's number stays with it and
the reference leads to it. The summary reads as one of the site's tables, each name leading to its
entry. An entry marked as deprecated says so in a way the developer notices.

**Why this priority**: These appear on fewer pages than the content in the stories above, and a
page is readable without them.

**Independent Test**: Serve a page with two numbered equations and references to them, a summary
table of documented objects, and an entry marked as deprecated, and confirm each is presented and
each link leads where it should.

**Acceptance Scenarios**:

1. **Given** a numbered equation, **When** a reader opens the page, **Then** the number is
   presented with its equation and is distinguishable from the notation.
2. **Given** a reference to a numbered equation, **When** a reader follows it, **Then** the page
   shows that equation in view and not hidden behind the shell's fixed top bar.
3. **Given** a summary table of documented objects, **When** a reader opens the page, **Then** it
   is presented as one of the site's tables and each name leads to its entry.
4. **Given** an entry marked as deprecated, **When** a reader opens the page, **Then** the
   deprecation is presented inside the entry with the cautionary meaning #7 gives deprecation
   notes.

---

### Edge Cases

- An entry with a signature and no description is still presented as an entry, without an empty
  gap where the description would be.
- A signature with no parameters, and one with many, are both presented as signatures.
- An entry three levels deep (a method of a class nested in a class) keeps its nesting apparent.
- A code example, an admonition or a table inside an entry's description is presented as #7
  presents it anywhere else.
- A reference entry for a language other than Python is presented the same way as a Python one.
- Maths inside an admonition, a table cell, a list or a heading is typeset like maths anywhere
  else, and takes the text colour of the place it sits in.
- Maths the typesetter cannot make sense of does not break the page. The reader sees that piece as
  written, and the rest of the maths on the page is still typeset.
- A page holding both reference entries and maths gets both treatments.
- A host project using a theme other than django-mvp's defaults gets the same styling drawn from
  that theme's colours, and contrast then depends on that theme.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every reference entry on a page a documentation app serves MUST be presented as a
  unit of its own, with its signature distinguishable from its description and from neighbouring
  entries. This applies whatever kind of object the entry documents, whichever language it
  belongs to, and whether it was generated from code or written by hand.
- **FR-002**: Within a signature, the name being documented MUST be distinguishable from the
  signature's other parts.
- **FR-003**: Parameters, return values, raised errors and the other field groups of an entry MUST
  be presented as labelled lists in which each item's name is distinguishable from its
  description.
- **FR-004**: An entry nested in another entry MUST be presented inside its parent so that a
  reader can tell which parent it belongs to, at every depth the docs build contains.
- **FR-005**: Every reference entry Sphinx gives an anchor MUST carry a link to its own anchor.
  The link MUST stay out of the way until the reader points at the signature or moves keyboard
  focus to the link, and MUST have an accessible name identifying the entry it links to.
- **FR-006**: Following a link to a reference entry or to a numbered equation MUST bring it into
  view below the shell's fixed top bar.
- **FR-007**: References to other documented objects MUST be presented as the site's links. Where
  the docs build links an entry to its source code, that link MUST be presented with the entry and
  be reachable by keyboard.
- **FR-008**: A summary table of documented objects MUST be presented as the site's tables are,
  with each name leading to its entry.
- **FR-009**: A deprecation note, or any other content #7 styles, MUST be presented inside a
  reference entry as it is elsewhere on a page.
- **FR-010**: Mathematical notation MUST be typeset, both inside a line of text and set out on its
  own line. Notation set out on its own line MUST be set apart from the surrounding prose.
- **FR-011**: Where maths cannot be typeset, the notation MUST be shown as the author wrote it,
  set apart from the prose and readable in both themes, and the rest of the page MUST be presented
  as usual. One piece of maths failing MUST NOT stop the others on the page being typeset.
- **FR-012**: A page with no mathematical notation MUST NOT load anything for typesetting it.
- **FR-013**: Typeset maths MUST be available to assistive technology as maths.
- **FR-014**: A numbered equation's number MUST be presented with its equation, and a reference to
  a numbered equation MUST lead to it.
- **FR-015**: A signature or an equation wider than the reading area MUST NOT make the page scroll
  horizontally, and every part of it MUST remain reachable. Any area that scrolls on its own MUST
  be reachable and scrollable from the keyboard.
- **FR-016**: Every colour this feature applies to reference entries and to maths MUST be taken
  from the host project's django-mvp theme. The package MUST define no colour of its own, and
  typeset maths MUST take the colour of the text around it.
- **FR-017**: Reference entries and maths MUST follow a change of the site's theme, including a
  switch between light and dark, without a reload and without configuration by the host project.
- **FR-018**: Text in signatures and field lists MUST meet WCAG 2.2 AA contrast (4.5:1) against
  its own background in django-mvp's default light and dark themes.
- **FR-019**: The styling of reference entries MUST work without any step by the host project
  beyond those needed to serve the pages. Maths MUST be typeset for a docs build made with
  Sphinx's default settings for maths, without any further step by the host project.
- **FR-020**: This feature MUST change nothing outside the content of pages a documentation app
  serves, and MUST NOT change how a page with neither reference entries nor maths looks or loads.
- **FR-021**: Any transition used to reveal an entry's link MUST be suppressed when the reader has
  asked for reduced motion.
- **FR-022**: Pages MUST continue to load no stylesheet from the docs build or from a Sphinx
  theme.

### Key Entities

- **Reference entry**: one documented object as Sphinx writes it into a page: a signature, a
  description, optional field groups such as parameters and return values, and optionally other
  entries nested inside it.
- **Signature**: the line of a reference entry that names the object and shows how it is called
  or declared.
- **Maths**: mathematical notation an author wrote into a page, either inside a sentence or set
  out on its own line, optionally numbered.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On a page carrying every kind of reference entry and maths this feature covers, no
  colour is applied that does not come from the host project's theme. The package's styles contain
  no literal colour value.
- **SC-002**: Switching such a page from the light theme to the dark theme changes every styled
  part of its reference entries and its maths, with zero settings changed by the host project.
- **SC-003**: Every piece of maths on a page built with Sphinx's default settings is shown to the
  reader as typeset notation, and none as the author's raw markup, in a browser with scripts on.
- **SC-004**: At 320 CSS pixels wide, no page scrolls horizontally, whatever signatures and
  equations it contains.
- **SC-005**: Every reference entry's link can be reached with the keyboard alone, and opening its
  address shows that entry in view on the first try.
- **SC-006**: Every text and background pair this package creates inside signatures and field
  lists measures at least 4.5:1 in django-mvp's default light and dark themes.
- **SC-007**: A host project that already serves its docs gets all of the above with zero
  additional adoption steps, and its pages without reference entries or maths load nothing new.

## Assumptions

- [#7](https://github.com/django-mvp/django-mvp-sphinx/issues/7) is delivered. Code examples,
  admonitions, tables, version notes and links inside a reference entry are already styled by it,
  and this feature keeps them as they are.
- The host project uses django-mvp's theme mechanism, which exposes the theme's colours to every
  page and switches between light and dark.
- The docs build is what `sphinx-build -b json` writes, with Sphinx's default settings for maths.
  A host project that has chosen another way for Sphinx to render maths, such as images, gets
  whatever that produces, sized to fit the page like any other image.
- Which objects are documented, in what order and with what text is decided by the host project's
  Sphinx configuration and its code. This feature presents what the docs build contains.
- Sphinx's general index and module index are not part of this feature. Whether a documentation
  app serves them is a question about which pages it serves.
- Pages listing a module's source code, where the docs build has them, are ordinary pages of
  highlighted code and are styled by #7. This feature covers only the link to them from an entry.
- Which headings and entries "On this page" lists stays with
  [#6](https://github.com/django-mvp/django-mvp-sphinx/issues/6). This feature does not add
  entries to it or remove them.
- How entries and maths look (spacing, type, emphasis, how nesting is drawn) is settled by looking
  at a prototype in a browser before the feature is built, and is deliberately absent from the
  requirements above.
- A way to copy a signature or an equation to the clipboard, and a way to collapse or expand
  entries, are not part of this feature.
- Printing is not a target. Pages print however the host project's shell prints.
