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

## D6. Maths typesetting is fetched from a CDN for now

**Ambiguous:** Whether whatever typesets the maths is shipped with the package, served by the
host project, or fetched by the reader's browser from another site.

**Chosen:** Fetched by the reader's browser from the jsDelivr CDN, the address Sphinx itself uses
by default. The maintainer decided this when reviewing the prototype on 2026-10-02: "CDN is fine
for now".

**Why:** It needs no new dependency and nothing from the host project, and it matches what a
Sphinx HTML build of the same docs would do. The cost is that a documentation app on a network
with no outside access shows the notation as written and not typeset, which the specification
already treats as a readable state (FR-011). The README should say so. Shipping the typesetting
with the package stays open as a later change.

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

## D12. A page knows it holds maths from its own markup

**Decision:** `BodyRewriter` notes an element whose class list holds `math` while it parses the
body, and the view reads that. The `has_maths_elements` key Sphinx 9.1 writes into a page's file
is not used.

**Why:** The key is template context the HTML builder happens to pass to the JSON builder, not a
documented part of the build, and the host builds with its own Sphinx version. The body is parsed
on every request already, and the same parse is needed for the equation region (D13).

**Revisit if:** Sphinx documents the key as part of the JSON build.

**ADR:** none — local to how one class reads a body; ADR 0003 already covers rewriting a body.

## D13. A wide equation scrolls in the same region a table does

**Decision:** `BodyRewriter` wraps the notation of each equation set out on its own line in the
focusable, named `mvp-sphinx-scroll` region it already gives tables. The prototype scrolled the
typeset container itself.

**Why:** MathJax 4 gives each typeset container keyboard focus for its expression explorer, where
arrow keys walk the expression and do not scroll it, and before typesetting the area took no
focus at all. FR-015 needs the area reachable and scrollable from the keyboard in both states.
The table region already does this and is already styled. The approved look does not change.

**Revisit if:** MathJax scrolls its own overflowing containers from the keyboard.

**ADR:** none — an application of ADR 0003 (rewrite only what CSS cannot) to one more element.

## D14. An entry's link is named by the entry's own name

**Decision:** The link on a signature is named with the entry's name: the `id` Sphinx gave it
when that ends with the documented name, otherwise the module path and name as written. Not the
whole signature.

**Why:** `sketch.md` asked for it. Named from all the text before it, a link read out every
parameter, the return type and "[source]". The `id` is the full dotted name for Python and
JavaScript entries and is unique on the page, so two classes' same-named methods stay distinct.

**Revisit if:** a domain's `id` turns out to end with the name and still be unreadable.

**ADR:** none — local to this feature, nothing downstream inherits it.

## D15. An equation's link keeps its number as its name

**Decision:** The link in an equation's number is named as heading links already are, which gives
"Link to this equation: (1)". No special case.

**Why:** `sketch.md` asked for a name that says which equation the link leads to. The number is
how a reader and the text refer to it, and it is unique on the page. The notation itself would be
raw markup read aloud.

**Revisit if:** equations gain captions.

**ADR:** none — no change to existing behaviour.

## D16. A wrong command is coloured from the theme, by MathJax's own setting

**Decision:** The typesetting settings give `tex.noundefined.color` the value
`var(--mvp-sphinx-code-error)`, and the stylesheet gives `mjx-merror` the same role. No new
colour role is made.

**Why:** An unknown command is not an `mjx-merror`: MathJax shows its name in a literal `red`,
which the prototype's rule never reached and which FR-016 forbids. The setting accepts a CSS
variable. The prototype's choice for a failed formula, the theme's error colour unmixed, measures
2.87:1 on the light page background; the existing code-error role measures 9.2:1 and 10.4:1.

**Revisit if:** the role is not readable on an admonition background, or maths needs a second
colour.

**ADR:** none — local to this feature, nothing downstream inherits it.

## D17. The typesetting address is written in the template, at Sphinx's own version tag

**Decision:** `mathjax@4` from jsDelivr, the exact address Sphinx's HTML build uses, written in
`page.html`. No setting, no pinned patch version, no integrity hash.

**Why:** D6 accepted the CDN and named that address. A hash needs a pinned patch version, which
then never receives a fix without a release of this package, and it would cover only the first
file: MathJax fetches its fonts and speech rules from the same CDN afterwards. A setting has no
second use yet (Article II); a host that needs another source overrides the template block. The
README states the exposure.

**Revisit if:** the typesetting is shipped with the package, which D6 leaves open.

**ADR:** none — a consequence of D6, which is itself provisional.

## D18. What the design review changed

**Decision:** Seven findings, none blocking, all applied to the plan and tasks before any code:

- The entry link's name (D14) takes the `id` only when it equals the documented name or ends
  with a dot and that name, and only when the signature has one name. A C++ entry's mangled `id`
  and an option's prefixed one pass the looser test and would have been read out. A C entry
  (`c.my_func`) and a JavaScript name with a `$` still take the `id`: accepted, watch item.
- The code sample that only looks like maths moves to the fixture's plain page, so the page that
  must not load the typesetting exists from the first task.
- The equation region opens after the number only when the number is a direct child of the
  equation, so a build that renders maths as images stays well nested.
- The README and CHANGELOG say that the typesetting script runs in the host project's pages with
  the reader's session, and that pages with maths load it after upgrading.
- The test for the removed `?typeset=off` switch is dropped: it could only fail if someone put
  the switch back.
- The browser check at convergence also covers "On this page" for a heading with maths, the
  source listing's back links, and speech and the failed formula with the region in place.

**Why:** Each costs a sentence now and a rework cycle later.

**ADR:** none — corrections to this feature's own plan.

## D19. The hooks test ties the parameter rule to its tag

**Decision:** `sig-param` is in the hand-kept hooks tuple, and a hand-written build must hold it, but the stylesheet has no `.sig-param` selector: the approved rule is `dt.sig-object em`. The test checks that selector is present and that every `em` inside a `dt.sig-object` in both builds carries `sig-param`. The stylesheet is unchanged.

**Why:** Checking the class name in a selector would have failed on the approved look, and changing the selector is not this task's to do. Tying the tag to the class catches the same drift: if Sphinx stopped writing `em.sig-param`, the rule would style the wrong thing and the test would fail.

**Revisit if:** the stylesheet's parameter rule moves to `.sig-param`; then `sig-param` leaves `NAMED_BY_TAG`.

## D20. An entry's name is its elements' text, joined as written

**Decision:** When the `id` does not name the entry, the name is the text of its `sig-prename` and `sig-name` elements in document order, joined with nothing between them, then whitespace collapsed and trimmed. Only elements inside a `dt.sig-object` count.

**Why:** Sphinx puts the pieces of one name in separate elements and the joining text inside them: `ns::` and `Foo`, `--out` and `=FILE`, and for `-v, --verbose` the comma sits in an empty-looking `sig-prename`. Joining with nothing gives `ns::Foo`, `--out=FILE` and `-v, --verbose`, as the author wrote them; joining with a space would not.

**Revisit if:** a domain writes a name's pieces so that they need a separator.

## D21. An equation numbered inside a paragraph is named without its number

**Decision:** When a build renders maths as images, the number sits inside a paragraph and not
directly in the equation. The whole paragraph is wrapped, and the region is named "Equation".

**Why:** The plan fixed where the region opens in that case and left the name open. The number
is then inside the region, where a screen reader meets it anyway, and that configuration is
outside what the feature promises (spec, Assumptions).

**Revisit if:** image-rendered maths becomes something the package supports on purpose.
