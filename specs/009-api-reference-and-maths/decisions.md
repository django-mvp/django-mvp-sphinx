# Decisions: FS-009 Make API reference pages and maths look like the rest of the site

Each entry is a point the issue left open, the reading the specification takes, and why. The
issue is two sentences long, so most of the specification's boundary rests on these. Any of them
can be reversed when the specification is reviewed.

## The reading the specification was written from

A documentation app already serves user-guide pages styled from the host project's theme (#7).
This feature gives the same treatment to the two kinds of content #7 left out. Reference entries
for classes, functions and other objects become entries a developer can scan: signature,
description, parameters, nested members. Mathematical notation is typeset, inside a sentence or on
its own line. Both take every colour from the host project's django-mvp theme, follow dark mode,
and add no styling step for the host project. It serves G9 and, through it, G1. It changes how
content looks, never what the docs build contains or which pages are served.

## D1. Every reference entry is covered, however it was written

**Ambiguous:** The issue says "pages generated from code, such as class and function reference".
It doesn't say whether an entry an author wrote by hand counts, or whether only Python does.

**Chosen:** Every reference entry on any page, for any language Sphinx documents, generated or
written by hand (FR-001).

**Why:** Sphinx writes all of them into the docs build in the same shape, so a reader cannot tell
a generated entry from a hand-written one, and neither can the package. Treating them differently
would need information the docs build does not hold. Python is what the tests and the demo will
exercise.

## D2. The general index and the module index are out of scope

**Ambiguous:** Sphinx can also produce a general index and a module index, which are generated
from code in a loose sense.

**Chosen:** Out of scope. Recorded under Assumptions.

**Why:** They are lists of where things are, not reference content. Sphinx's JSON builder writes
them as data with no page body, so showing them means the documentation app serving a new kind of
page, which is a larger question than how content looks and is nothing the issue asks for. If it
is wanted it deserves its own feature request.

## D3. Entries get a copyable link, as headings do

**Ambiguous:** #7 gave headings and glossary terms a link a reader can copy. The issue doesn't
mention one for reference entries.

**Chosen:** Every entry Sphinx gives an anchor carries one, with the same behaviour as a heading's
link: out of the way until pointed at or focused, named for assistive technology, and its target
brought into view below the top bar (FR-005, FR-006, FR-021).

**Why:** The issue asks for these pages to look as much a part of the site as the user guide
does, and in the user guide every anchored heading has this link. Linking to one function is also
the commonest way reference documentation is shared. Sphinx already writes the anchor and the
link, so leaving them unstyled would show a stray symbol beside every signature.

## D4. Without typesetting, the reader sees the notation as written

**Ambiguous:** What a reader sees when maths cannot be typeset, such as with scripts turned off.

**Chosen:** The notation as the author wrote it, set apart from the prose and readable in both
themes. The rest of the page is unaffected, and one bad formula does not stop the others (FR-011).

**Why:** The specification must not decide how maths is typeset, which is planning work. Whatever
is chosen, there is a state where it has not happened yet or cannot, and that state needs to be
readable. Requiring typeset maths with scripts off would force typesetting at build or request
time, which means a new dependency (Article VII) or a change to the host project's Sphinx
configuration, and the issue asks for neither.

## D5. Maths works with Sphinx's default settings, and costs other pages nothing

**Ambiguous:** Whether the host project has to configure anything for maths, and whether every
page pays for it.

**Chosen:** A docs build made with Sphinx's default settings for maths is typeset with no further
step by the host project (FR-019). A page with no maths loads nothing for it (FR-012, FR-020).

**Why:** G3 and #7 both hold that adopting the package adds no styling step. Most pages of most
documentation hold no maths, and FS-007 already set the expectation that a page does not load
script it has no use for.

## D6. Left to the plan: where the typesetting comes from

**Ambiguous:** Whether whatever typesets the maths is shipped with the package, served by the
host project, or fetched by the reader's browser from another site.

**Chosen:** Not decided here. The specification says only what the reader sees.

**Why:** It is a choice of tool and delivery, which belongs to planning. It is listed as an open
risk on the pull request because it has a consequence a maintainer may care about: a documentation
app behind a sign-in, or on a network with no outside access, should not depend on a third-party
site to show its equations. The plan should weigh that.

## D7. Contrast is this package's job for the combinations it creates

**Ambiguous:** Signatures have several parts that a design may want to tell apart by colour.

**Chosen:** Text in signatures and field lists meets WCAG 2.2 AA (4.5:1) against its own
background in django-mvp's default light and dark themes (FR-018). Typeset maths takes the colour
of the text around it (FR-016), so it inherits whatever contrast that text has.

**Why:** The same rule #7 set for admonitions and highlighted code, for the same reason: theme
colours combined by this package are only as readable as the combinations it makes.

## D8. "On this page" is left alone

**Ambiguous:** Whether reference entries should be listed under "On this page".

**Chosen:** This feature neither adds nor removes anything there (Assumptions).

**Why:** #6 owns that list and builds it from what the docs build records. Changing it here would
widen this feature into a delivered sibling's scope.

## D9. Source listings are #7's, the link to them is this feature's

**Ambiguous:** A docs build can include pages listing each module's source code, with a link to
them from each entry.

**Chosen:** The link is presented with its entry (FR-007). The listing pages are ordinary pages of
highlighted code, already styled by #7, and get nothing new here.

**Why:** The link sits inside the entry, so an unstyled one would be a visible gap in exactly the
content this feature covers. The listing is highlighted code, which is delivered.

## D10. Appearance is absent from the requirements on purpose

**Ambiguous:** How much the specification should say about how entries and maths look.

**Chosen:** Nothing. The requirements say what a reader can tell apart and reach. The section
"What a reader sees" lists the screens and states so a prototype can be built from it, and the
look is settled there.

**Why:** The maintainer asked for this feature to be prototyped and reviewed by eye before it is
built. A requirement that pinned spacing, type or colour would become a test that fails whenever
the design is adjusted.

## D11. The spec directory was created by hand

**Chosen:** `specs/009-api-reference-and-maths/` was written directly, with the number assigned in
advance.

**Why:** Several specifications were being written at the same time, each in its own working
tree, and a script that picks the next free number from one tree would have given two of them the
same one.
