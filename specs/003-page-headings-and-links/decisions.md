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
