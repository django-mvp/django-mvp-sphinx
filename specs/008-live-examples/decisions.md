# Decisions: FS-008 Show working examples live next to their source code

Each entry is a point the issue left open, the reading the specification takes, and why. The
maintainer handed this specification over without a round of questions, so every reading below was
made without him. Any of them can be reversed when the specification is reviewed.

## The reading the specification starts from

A page of the documentation can hold a live example: a page the host project already serves, shown
running inside the documentation page with the code that defines it beside it. The author places
one with a single marker in the page's Sphinx source. The reader uses the example where it sits and
the documentation page stays put. The example is the host project's own code at its own address,
the source is copied into the docs build when the docs are built, and serving still never imports
Sphinx. It serves G8 and is roadmap item R8. How code and API reference pages look stays with #7
and #13.

## D1. An example is a page the host project already serves

**Ambiguous:** The issue says "a live example from the site". It doesn't say whether the example is
code written in the documentation and run by the package, or something the site already has.

**Chosen:** The author names a page of the host project by its address. The package shows that
page. It never runs code found in the documentation and ships no examples (FR-001, FR-003).

**Why:** "From the site" reads as the site's own page. Running code typed into documentation would
be a new way to execute untrusted text, which CONSTITUTION.md Article V rules out, and it would be
a far larger feature than the issue asks for.

**ADR:** none — a reading of the issue, recorded in the specification

## D2. Only examples on the same site

**Ambiguous:** Whether a marker may name any address.

**Chosen:** An address on another site is reported at build time and produces no example (FR-003).

**Why:** The issue says "from the site". Embedding other sites is a different feature with its own
security questions, and nothing in the goals asks for it.

**ADR:** none — a reading of the issue, recorded in the specification

## D3. The source is copied into the docs build

**Ambiguous:** Where the code shown beside the example comes from, and when it is read.

**Chosen:** The author names files of the project, or part of one. Their text goes into the docs
build at build time and the page shows that copy (FR-004, FR-014). The example itself is live, so
the two can drift until the next build, and that is accepted.

**Why:** CONSTITUTION.md Article XII makes the docs build the only thing serving reads. Reading
project source at request time would break that and would let a page expose files the build never
named. Sphinx authors already expect included code to be as of the build.

**ADR:** none — follows Article XII; nothing new to record

## D4. Using the example never moves the documentation page

**Ambiguous:** "Work right there on the page" doesn't say what happens after the reader submits
the form.

**Chosen:** The example changes in place and the documentation page keeps its address. The reader
can reset the example and can open it on its own (FR-006, FR-007, FR-008).

**Why:** A reader who is taken away from the page they were reading has lost the explanation the
example belongs to. Reset is needed because a form that has been submitted successfully often can't
be tried again otherwise.

**ADR:** none — a reading of the issue, recorded in the specification

## D5. The host project's own rule decides who sees an example

**Ambiguous:** Whether showing an example on a documentation page changes who may see it.

**Chosen:** The example is requested as the reader. Whatever the site would answer at that address
is what appears. The documentation's reader rule covers the page and its source, and nothing else
(FR-011).

**Why:** FS-006 gave the documentation app one reader rule and said it adds no others. An example
that became visible through the documentation to someone the site refuses would be an access hole.

**ADR:** none — follows FS-006 and its record; nothing new

## D6. A broken example never breaks the page

**Ambiguous:** What a page does when its example can't be shown.

**Chosen:** An address the site doesn't have gives a page that says the example is unavailable and
still shows the source. An example the site refuses or that fails shows the site's own answer in
its place. A missing source file is reported by the build (FR-012, FR-013).

**Why:** It follows what FS-001 and FS-007 already do: a missing build and missing search data both
leave the pages working and say what is missing.

**ADR:** none — a reading of the issue, recorded in the specification

## D7. At least one source file, and as many as the author names

**Ambiguous:** Whether an example may have no source, or several files.

**Chosen:** At least one, and any number, shown one at a time in the author's order (FR-004).

**Why:** The issue's title is "next to their source code", so an example with no source is outside
it. A form example usually involves a form, a view and a template, so one file is too few.

**ADR:** none — a reading of the issue, recorded in the specification

## D8. The example shows without the application shell around it

**Ambiguous:** A page of the site normally comes with the sidebar and navbar. Shown inside a
documentation page, that would put a second shell inside the first.

**Chosen:** The example shows its own content only (FR-009). How the host project's page is
rendered that way is left to the plan.

**Why:** A reader looking at a form example wants the form. A nested copy of the site's navigation
would take most of the space and invite the reader to navigate away inside the example.

**ADR:** none — its means is D11

## D9. The demo guide carries an example of every state

**Ambiguous:** Nothing in the issue mentions the demo project.

**Chosen:** The demo project's guide includes examples covering every state listed in the
specification (FR-018).

**Why:** The arrangement and look are judged on a working prototype in a browser, and the earlier
features each added their states to the demo for the same reason.

**ADR:** none — about the demo project only

## D10. How it looks is not in the specification

**Ambiguous:** Side by side or stacked, tabs or a list for several files, what the unavailable
notice says.

**Chosen:** The specification lists the screens and states and what the reader can do in each. The
arrangement, the controls and the wording are settled on the prototype.

**Why:** Requirements become tests, and a test that pins wording or layout fails whenever the
design is adjusted. The maintainer asked for this feature to be prototyped before it is built.

**ADR:** none — about how the specification was written

## D11. An example's page is written without the shell

**Ambiguous:** D8 left the means of showing an example without the application shell to the plan.
The prototype did it by having the host's `base.html` extend a template of this package, and the
maintainer ruled that out: a host's `base.html` extends `mvp/base.html`. Research then proposed a
change to django-mvp and stopped for his decision.

**Chosen:** The host project writes an example's page without the shell. Its template replaces
django-mvp's public `app` block, as django-mvp's own sign-in pages do. This package ships
`mvp_sphinx/example.html`, which extends the host's `base.html` and does that, so an example's
template extends it and fills `content`. The page has no shell wherever it is opened. The
specification's FR-008 and FR-009 were reworded to say so (2026-10-02).

**Why:** The maintainer's own answer on 2026-10-02: "if somebody is trying to show a demo page in
a sphinx view, can't they override content using template blocks in their demo page? Why does a
demo page have to show the whole thing?" It needs nothing from django-mvp and nothing private to
it, the host's `base.html` is untouched, and the page stays shell-less after a posted form, a
redirect and a followed link, which the prototype's address flag did not. What it gives up is
that an existing page of the site, shell and all, cannot be shown bare. The README says so.

**ADR:** none — a template convention local to this feature; nothing else in the package inherits it

## D12. The build writes an example as elements, and the page reads them with a parser

**Decision:** The directive wraps an example and each of its sources in `div` elements carrying
`data-` attributes, with ordinary highlighted code blocks between them. `LiveExamples` reads the
served body with `html.parser` and splits it into markup and examples.

**Why:** The prototype's HTML comments needed a regular expression over markup and showed nothing
to a reader whose host replaces the page template. Elements degrade to plain code blocks, use the
standard attribute escaping, and are read with the parser the package already relies on.
`LiveExamples` stays apart from `BodyRewriter`: one records insertions, the other cuts the body
into parts, and a page without an example never reaches it.

The build's wrappers carry the same class names as the component's own hooks. A host whose page
template still draws the body whole gets the example's stylesheet rules on them, which is
harmless.

**Revisit if:** a third thing needs to read page bodies, which would be the time to share a parse.

**ADR:** none — how one feature carries its data through the build; ADR 0003 covers reading a body

## D13. Part of a file is a range of lines, and nothing more for now

**Decision:** A source line may end with `first-last` or one line number. `literalinclude`'s other
selectors are not offered.

The lines are shown with their common leading indentation removed, and SC-003's
"identical" is read as identical after that.

**Why:** The specification asks for "part of a file" and one selector meets it (Article II). Line
numbers drift when the file is edited, which the author sees at the next build. A selector by
name can be added when a host asks.

**ADR:** none — a small syntax choice, reversible by adding selectors

## D14. A source is called by its file name, with only as much path as tells two apart

**Decision:** Research R4.

**Why:** The approved tabs show bare file names, and a path in every tab would crowd them. Two
tabs that read the same are the only case that needs more.

**ADR:** none — local to the directive

## D15. The address is checked when the docs are built and again when the page is served

**Decision:** The directive refuses an address that is not a path of this site. `LiveExamples`
checks it again with Django's own same-site test before it draws a frame.

**Why:** The docs build is trusted, but the cost of one mistake is another site framed inside a
page of this one, and the second check is one call. It also covers a build made by an older
version of the extension.

**ADR:** none — a guard inside one class

## D16. No general scheme for stale stylesheets

**Decision:** `example.css` is its own file, linked only by pages that hold an example. Nothing is
added to bust a browser's cache of the package's stylesheets.

**Why:** The fault seen in review came from adding rules to a file the browser already had. A new
file answered it. Cache busting for static files is the host's static files storage, for this
package's files as for every other.

**ADR:** none — a decision not to build something
