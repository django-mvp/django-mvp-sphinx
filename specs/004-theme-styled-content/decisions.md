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
