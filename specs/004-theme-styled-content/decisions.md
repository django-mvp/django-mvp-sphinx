# Decisions — 004 Make user-guide content look like the rest of the site

Rationale too long to sit inside `spec.md`, plus every ambiguity resolved without asking the
maintainer. The specification stands alone. This file records why it says what it says.

## How the reading of the issue was settled

The maintainer delegated this specification and asked for no questions. The reading of #7 was
written from the issue, its siblings (#4 to #13), the README, `GOALS.md`, `CONSTITUTION.md`
Articles XII and XIII, `CONTEXT.md`, the roadmap, and the prototype described below. It was
treated as agreed. Every place the issue is silent and a reading was chosen is listed here.

## A prototype the plan may start from

A working prototype was built inside django-mvp before this repository existed, on the branch
`wip/sphinx-docs-in-sidebar` of github.com/django-mvp/django-mvp. It already styles admonitions,
highlighted code, wide tables and heading links from the theme's colours, and the maintainer
reviewed it and liked it. Its decisions are the default reading wherever #7 is silent, and the plan
may start from its styling. It was built on django-sphinx-view, a dependency this package drops, so
only its styling carries over, not its view.

## Self-resolved decisions

### The ordinary text of a page is in scope

The issue lists notes, warnings, code, tables and glossaries. It does not mention headings,
paragraphs, lists and links. They are included because a page's body arrives as plain HTML, and
the shell's base styles reset headings, lists and links to unstyled text. Without them a page looks
like a different site, which is the problem the issue states. #4 puts the page in the shell and
says it appears "in the site's theme", but its deliverables are about serving, not about what the
body looks like. If #4's specification ends up claiming the ordinary text, FR-001 moves to it and
this feature keeps the rest.

### Where the page sits on the screen belongs to #4

The prototype also decided the reading area's width and restyled the page's own first heading as
the page title. Both are about the page's layout rather than its content, and #4 owns the page.
This feature leaves them alone.

### Admonition meanings

Five meanings, following the prototype's mapping onto the theme's status colours:

| Meaning | Admonition kinds | Prototype colour role |
|---|---|---|
| Informational | note, seealso, and any kind with no known meaning | info |
| Helpful | tip, hint | success |
| Important | important | primary |
| Cautionary | warning, caution, attention, deprecated | warning |
| Dangerous | danger, error | error |

Which colour role stands for which meaning is a taste call the maintainer approved in the
prototype. The specification names meanings, not colours, so the mapping can change without a
requirement changing. Deprecation notes join the cautionary group because they tell the reader to
stop relying on something. Version-added and version-changed notes are informational.

### Unknown admonition kinds fall back to informational

Sphinx's generic admonition with a custom title, and admonitions from third-party extensions, carry
kinds this package cannot know in advance. Falling back to the informational meaning keeps them
looking like admonitions rather than dropping to plain text, and never raises alarm the author did
not intend.

### Sphinx's own stylesheets are never loaded

A docs build copies Sphinx's static files, including a stylesheet for the page layout and one that
colours highlighted code with a fixed palette. Loading either would bring in fixed colours and a
Sphinx theme's look, which Article XIII rules out. Code highlighting instead maps the highlighter's
token kinds onto the theme's colours, as the prototype does.

### Contrast of what this package creates is this package's concern

The contrast of the theme's own colours is the theme's concern, as django-mvp decides for itself.
This package creates new combinations from them: tinted admonition backgrounds behind body text,
and theme colours used as text on the code background. Those combinations are measured against
WCAG 2.2 AA in django-mvp's default light and dark themes. A host project on another theme gets the
same styling drawn from its own colours, and contrast then rests with that theme.

### Wide tables are scrollable from the keyboard

The issue asks that wide tables not widen the page. The obvious way to do that makes the table
scroll inside its own area, and a scrolling area that cannot take keyboard focus locks a keyboard
reader out of the hidden columns (WCAG 2.1.1). The requirement was added so the plan cannot miss it.

### Heading links have an accessible name and land clear of the top bar

Sphinx gives each heading a link whose visible text is a pilcrow, which a screen reader reads out
as a punctuation mark. The requirement asks for a name that says which section the link goes to.
The shell's top bar is fixed, so a heading reached by its anchor would otherwise land underneath
it. The prototype fixed both, and both are kept.

### Glossary terms carry links like headings do

Sphinx gives glossary terms anchors, and cross-references to a term land on them. Treating a term
like a heading, with a link a reader can copy and landing clear of the top bar, makes linking to a
definition work the same way as linking to a section.

### Keys, labels and menu paths are included

The issue does not mention them. They are included because a user guide for an application is
largely instructions of the form "press this, click that, open this menu", and Sphinx marks each of
those up specifically. Without styling they read as plain words in the sentence. They sit in the
lowest-priority story.

### Styling needs no adoption step

G3 promises adoption with a mount and one line of Sphinx configuration. A styling feature that
needed the host to include a stylesheet or run an asset build would break that promise, so the
styling reaches the page with the documentation app itself.

### What was left out

- A copy-to-clipboard button on code blocks. The issue does not ask for it and it would add a
  script to every page. It can be raised as its own feature.
- Print styling. Pages print as the host project's shell prints.
- API reference and maths, which are #13.

## Open risks

- **Overlap with #4 on ordinary text.** Both specifications are being written at the same time.
  If #4 claims the styling of headings, paragraphs, lists and links, FR-001 moves there.
- **Contrast in the dark theme.** Theme colours used as code-token text on a dark code background
  may fall short of 4.5:1 for some roles (warning yellow on a light background is the usual
  offender in the light theme). The plan may need to mix a token colour toward the text colour to
  meet FR-015, which changes how the highlighting looks but not where its colours come from.

## Planning decisions (S3, 2026-09-30)

Numbered from here on, so later stages can cite them.

## D1. One plain-CSS stylesheet, shipped as a static file and linked by the page template

**Decision:** The styling is `mvp_sphinx/static/mvp_sphinx/content.css`, plain CSS keyed off
Sphinx's class names and the theme's `--color-*` custom properties, linked from the page
template's `styles` block after django-mvp's own stylesheet.

**Why:** The prototype put its rules in django-mvp's Tailwind source, which a separate package
cannot touch. A Tailwind build inside this package would be a build step for us and a second copy
of Tailwind's reset on the page. Every rule reads a class Sphinx wrote, so nothing needs
generating. A static file inside an installed app reaches the page through the staticfiles setup
every django-mvp host already has, which is what FR-017 asks for, and only pages the documentation
app renders link it (FR-016). (research R3)

**Revisit if:** django-mvp grows a way for an installed app to contribute rules to its own
stylesheet.

**ADR:** docs/adr/0003-style-page-content-with-a-scoped-theme-stylesheet-and-rewrite-only-what-css-cannot.md

## D2. Accessible names and focusable table areas come from rewriting the body in Python

**Decision:** `BodyRewriter`, on the standard library's `HTMLParser`, rewrites each page body
before it is rendered: every heading link gets an `aria-label`, every outermost table is wrapped
in a focusable, named scrolling region. Everything else is re-emitted as written.

**Why:** FR-008 and FR-010 need attributes CSS cannot add. A script would add JavaScript to every
page, which the spec turns down for the copy button on the same grounds, and a build-time Sphinx
extension would only help hosts who add it, while FR-017 promises the styling with no step. The
standard library's parser avoids a new dependency.

**Revisit if:** the package gains a Sphinx extension every host is required to load anyway
(#5's navigation extension is optional for pages); the rewrite could then move into the build.

**ADR:** docs/adr/0003-style-page-content-with-a-scoped-theme-stylesheet-and-rewrite-only-what-css-cannot.md

## D3. A heading link's name is Sphinx's own title plus the heading's text

**Decision:** `aria-label="<title>: <text of the element holding the link>"`, the title being the
link's `title` attribute ("Link to this heading", "Link to this term", …).

**Why:** Sphinx writes that title in the docs build's own language and already says what kind of
thing the link points at, so the package adds no translatable string and a term's link is not
called a section's. The text makes each name unique on the page (FR-010).

**Revisit if:** a Sphinx release drops the `title` attribute; the label then falls back to the
text alone, which still meets FR-010.

**ADR:** none — a naming detail inside BodyRewriter, stated in its docstring

## D4. Every table gets the scrolling region, wide or not

**Decision:** The rewrite wraps every outermost table, because the server cannot know which will
overflow on the reader's screen.

**Why:** Width depends on the reader's viewport. The cost is one extra tab stop per table, which
is the usual pattern for WCAG 2.1.1 on scrollable tables.

**Revisit if:** readers report the extra tab stops as a nuisance on table-heavy pages; a script
that removes `tabindex` from regions that do not overflow is the known refinement.

**ADR:** none — a local choice in this feature's rewrite, easy to refine without touching anything else

## D5. Every colour the stylesheet creates is a named custom property, mixed from theme colours

**Decision:** One rule at the top of the stylesheet declares each colour the package makes
(`--mvp-sphinx-…`) as a theme colour or a `color-mix(in oklab, …)` of two; every other rule only
reads them. Code token colours are theme roles mixed toward `--color-base-content`.

**Why:** It makes SC-001 and SC-005 checkable from the file: the test resolves each property
against django-mvp's default light and dark themes and measures the pairs. Mixing toward the
theme's own text colour darkens a token in the light theme and lightens it in the dark one, so one
mix serves both (research R4). The prototype's unmixed status colours fall under 3:1 on the light
code background.

**Revisit if:** django-mvp ships code-token colour roles of its own.

**ADR:** docs/adr/0003-style-page-content-with-a-scoped-theme-stylesheet-and-rewrite-only-what-css-cannot.md

## D6. The body's ordinary text is left to django-mvp's `prose`

**Decision:** No rules for headings, paragraphs, lists, block quotes, links or inline code.

**Why:** The page template already wraps the body in `prose`, and daisyUI's override of it sets
every prose colour from the theme (research R2). FR-001 holds today; restyling it would only
diverge from the rest of the site.

**Revisit if:** a walkthrough finds an ordinary element that reads differently from the site.

**ADR:** none — a statement of what django-mvp already provides, nothing later work must abide by

## D7. The test fixture page is an orphan

**Decision:** `tests/sphinx/guide/content.rst` carries `:orphan:` rather than joining a toctree.

**Why:** FS-002 is being built at the same time and asserts the contents of the same fixture
guide. An orphan page adds no entry to the contents, and it keeps the build free of the "not in
any toctree" warning the fixture forbids.

**Revisit if:** a later feature wants the page in the contents.

**ADR:** none — a test-fixture detail

## D8. Design review outcome (S3R)

**Decision:** One reviewer, three lenses: approve, no critical or high findings. All four
findings were applied as plan edits because each was cheaper to fix than to carry. ARCH-001
(medium): the rewrite splices insertions into the original string instead of re-emitting parsed
tokens, which altered bare ampersands and semicolon-less references; T004's byte-for-byte test
gains those inputs. SPEC-001 (medium): the muted text colour joins the contrast pairs, on base-100
and on every admonition background. SPEC-002 (low): the glossary-term label test moves from T008
to T006, where it can be red. ARCH-002 (medium): the contrast helpers sit on one class in the test
module. Notes applied: caption label without the glyph, `gettext_lazy`, `{% load static %}`,
`django.utils.html.escape`, no unknown lexer in the demo.

**Why:** Each remedy is a paragraph in the plan; none adds a task.

**Revisit if:** the S6 reviewer finds a defect one of these remedies introduced.

**ADR:** none — a record of this feature's design review

## D9. A table's label is its caption's markup up to the heading link

**Decision:** `BodyRewriter` reads the caption as the markup between `<caption>` and the first
`a.headerlink` (or `</caption>` when there is none), strips tags, decodes entities and collapses
whitespace. A table whose end tag never arrives is left unwrapped.

**Why:** Sphinx puts the caption text in `span.caption-text` and the pilcrow link after it, so
cutting at the link needs no span tracking and still works for inline markup inside the caption.
Wrapping a table with no end tag would need a guessed end offset; leaving it as written keeps the
"nothing is invented" rule of the splice.

**Revisit if:** a Sphinx theme or extension puts other text after the caption text that is not the
heading link.

**ADR:** none — an implementation detail of BodyRewriter

## D10. The holder of a heading link is the innermost open element

**Decision:** `BodyRewriter` keeps a stack of open elements (offset where each one's content
starts). A heading link is named from the text between the start of the innermost open element's
content and the link. Void elements are never pushed, and an end tag closes the innermost element
of its name and everything opened inside it.

**Why:** Sphinx puts the link as the last child of the heading, term or caption, so "the element
that directly holds the link" is exactly the top of the stack, and no per-tag list of headings is
needed. Closing by name keeps the stack right for the unclosed `<li>` and `<p>` a raw directive can
leave.

**Revisit if:** Sphinx wraps the link in an element of its own.

**ADR:** none — an implementation detail of BodyRewriter

## D11. Code review outcome (S6)

**Decision:** One reviewer, correctness, spec, documentation and security lenses: approve, risk
low, no critical or high findings. Every finding was fixed in one cycle by the orchestrator
directly, since each was a line or two: CSS-001 (medium), the deprecation rules now select
`div.deprecated` so the label span inside the note no longer draws a second box; STD-001, the
throwaway `_` and `_text` names in the new tests are named (the `gettext_lazy as _` import stays,
as Article VIII prescribes); STD-002, two lines over 88 wrapped; TST-001, the code-roles test
asserts the expected roles are present instead of pinning the exact set; DOC-001, ADR 0003 (numbered 0002 at review) says
precisely which colours are roles; DOC-002, the README says to keep the `mvp-sphinx-content`
class in an override and that `BodyRewriter.rewrite` returns a plain string; SEC-001
(speculative), the class docstring states the well-formed-HTML assumption.

**Why:** Each remedy was smaller than a dispatch brief.

**ADR:** none — a record of this feature's review
