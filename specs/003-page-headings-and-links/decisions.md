# Decisions: Show a page's headings beside it, and links to the previous and next page

The maintainer delegated this specification without a review conversation, so the reading of the
issue below was written and taken as agreed. Every place the issue was silent is recorded here with
the choice made and why it holds.

## The agreed reading

On a long page, a reader can jump to any section from "On this page", a list of the current page's
headings shown beside it on wide screens, nested as the page nests them and without the page's own
title. A page with no headings below its title has no list. Every page ends with links to the
previous and next page in the order the docs build records, each naming its page, with no previous
link on the first page and no next link on the last. Both read from the docs build on every request,
so a rebuild shows without a restart, and neither imports Sphinx. The contents in the sidebar (#5)
and the styling of the page body, heading links included (#7), stay with their own issues. It
serves G2.

## Self-resolved decisions

| # | The gap | Chosen | Why it holds |
|---|---|---|---|
| 1 | How deep "On this page" goes | Every section heading the build records, nested, without the page title | Sphinx already decides what a section is. Cutting at a depth would be a second rule to explain. The prototype listed the build's own heading tree the same way |
| 2 | What "reading order" is | The previous and next page the docs build records for each page | Sphinx derives them from the toctrees, so they match the order of the contents in the sidebar. Inventing an order would let the two disagree |
| 3 | A page with no sections | No list at all, not an empty one | An empty list is noise. Sphinx themes and the prototype both hide it |
| 4 | A page with one section | Still gets the list | The rule is whether headings exist below the title. A count threshold would be arbitrary |
| 5 | Narrow screens | No list and no substitute | The issue scopes it to wide screens, and the prototype did the same. Where it appears is judged by eye, so it is an assumption, not a requirement |
| 6 | Marking the section being read while scrolling | Out of scope | Not asked for, and it needs script following the scroll position. It can be requested on its own |
| 7 | Pages outside every toctree (orphans) | Served without previous or next links | Sphinx gives them no neighbours, and linking them in would put them in an order the docs never gave them |
| 8 | Pages listed only in a hidden toctree | In reading order like any other | Sphinx treats them so, and the sidebar contents in #5 include them too |
| 9 | Accessibility | Both are navigation regions with names of their own, and the links are marked as previous and next | The sidebar is already a navigation region. Distinct names let a screen-reader user tell three navigation regions apart, and the previous/next relation is what browsers and assistive technology read |
| 10 | Rebuilds | Read from the build on every request, no restart | Matches the ruling that serving reads the build and never runs Sphinx, and what #5 asks of the sidebar |
| 11 | Titles holding markup | Shown as the build renders them | The docs build is the host project's own output, trusted like the page body it sits beside |

## Prototype the plan may start from

A working prototype of this page was built inside django-mvp before this repository existed:
branch `wip/sphinx-docs-in-sidebar` on github.com/django-mvp/django-mvp, under
`mvp/integrations/sphinx_view/` and `mvp/templates/mvp/sphinx_view/`. Its page template already
draws "On this page" beside the article at wide widths and the previous and next links below it.
It depended on django-sphinx-view, which this package does not. The plan may start from it.

## Implementation decisions (S3 onward)

## D1. Re-read against the features delivered since the spec landed

**Decided**: FS-001 (#4) and FS-002 (#5) were delivered after this spec merged. Neither contradicts
it. FS-002's FR-014 shows sidebar titles as text; this spec shows heading and page titles "as the
build renders them". The two rules govern different surfaces (the sidebar menu and the page's own
navigation), and the page body beside the list is rendered as the build wrote it too, so both stand.

**Why**: the lane's spec-against-spec check; no contradiction to put to the owner.

**Revisit if**: a later feature puts titles from this list into the sidebar.

**ADR:** none — a check, not a design choice

## D2. Parse Sphinx's `toc` into a heading tree rather than inject it

**Decided**: `PageHeadings`, a standard-library `HTMLParser`, reads the page's `toc` fragment into
`{title, anchor, children}` entries without the title entry; the list is drawn by this package's
components with daisyUI `menu` classes. Whether a page has a list is whether that tree is empty, not
Sphinx's `display_toc`.

**Why**: FR-003 excludes the title, which is the fragment's outer entry; the shell's menu classes
must sit on the lists; and a page whose title holds an empty list (the demo's front page) makes
`display_toc` and the drawn tree two readings of one fact (research R2).

**Revisit if**: Sphinx changes the shape of `toc`, or a Sphinx release adds the title-less tree to
the page context.

**ADR:** pending S5

## D3. Previous and next links resolved against the request path

**Decided**: `urljoin(request.path, link)` on Sphinx's relative `prev`/`next` link, as the FS-001
breadcrumbs do with `parents`.

**Why**: Sphinx's link is relative to the page's own address, which is the address the request was
routed to, so the result stays under whatever prefix the app is mounted at with no `reverse`
(research R3).

**Revisit if**: pages are ever served at an address other than the JSON builder's own.

**ADR:** pending S5

## D4. Layout from the shell's emitted utilities only

**Decided**: the two-column layout uses only classes present in django-mvp's packaged stylesheet
(research R4). The prototype's arbitrary grid template is not emitted there and is dropped.

**Why**: the package compiles no Tailwind, and an unemitted class does nothing silently.

**Revisit if**: layout needs something the shell does not emit. FS-004's `content.css` is scoped
to the page body (`.mvp-sphinx-content`) and is the place a page-level rule would go.

**ADR:** pending S5

## D5. The new components are parts of the page, not a published API

**Decided**: `on_this_page`, `heading_list` and `page_links` exist to draw the page. The README does
not offer them to host templates, and their classes are not tested.

**Why**: the spec makes placement and look a matter for the eye and the host's theme; publishing
the markup would turn every visual adjustment into a contract.

**Revisit if**: a host project asks to place the list itself.

**ADR:** pending S5

## D6. Design review: approved, five low findings applied as plan edits

**Decided**: the one-round design review approved with no critical or high finding. All five low
findings removed work and were applied: ARCH-001, the title is sliced from the fragment by offset
(as `BodyRewriter` does) instead of re-emitted tag by tag; ARCH-002, one emptiness guard for "On
this page", in `page.html`; ARCH-003, `get_neighbour` treats only a missing or `null` key as absent,
with no shape validation; SPEC-001, only `settings.rst` changes in the demo guide, since FS-004's
content tour already has nested sections and an inline-code heading; ARCH-004, the hidden-toctree
and orphan cases run on the existing `contents` source. Notes swept: the stale FS-004 wording in
T002, the demo reading order now including Content tour, and a README sentence about incremental
Sphinx builds.

**Why**: each remedy was checked against its stated evidence (`mvp_sphinx/page_body.py`
`position()`/`splice()` with `convert_charrefs=False`; `demo/docs/content-tour.rst`;
`tests/sphinx/contents/hidden-page.rst`, `orphan.rst`; `sphinx/builders/html/__init__.py:572-590`).

**Revisit if**: n/a — a record.

**ADR:** none — a record of the review, not a decision

## D7. The hidden-page test asserts one link, not two

**Decision**: `TestPreviousAndNextPage` tests the hidden-toctree case as "`hidden-page/` has a
previous link to `reference/api/`, and that page's next link leads back to `hidden-page/`". It
does not assert a next link on `hidden-page/`.

**Why**: tasks.md T004 says `hidden-page/` has both links. In `tests/sphinx/contents/` its hidden
toctree is the last one in `index.rst`, so `hidden-page` is the last page in reading order and
Sphinx writes `next: null` for it (read from the built `hidden-page.fjson`). The source is not in
this story's files, so it was not edited. The assertion still shows that a hidden toctree feeds
the links, which is what the edge case is about.

**Revisit if**: a later story adds a page after `hidden-page` in the contents source; the test can
then assert both links.

**ADR:** none — a test-scope choice
