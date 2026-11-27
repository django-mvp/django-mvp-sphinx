# Decisions: 011-search-and-previews

Choices made while specifying, where the reason is longer than the spec can carry.

## Suggestions taken from the interpretation

The interpretation Sam confirmed offered three suggestions. They were taken as follows.

- **Last modification in the sitemap**: taken. A search engine uses it to decide what to read again,
  and the docs build already records when each page was written.
- **`og:type` and a card tag**: taken. Without `og:type` some services treat the page as a bare
  website, and some services read card tags rather than Open Graph ones. The card asks for a large
  image only when there is one to show, since a large card with no image draws an empty box.
- **The results page**: no preview tags at all, rather than a canonical address with the search
  words removed. A results page is not something to index or share as a page of the documentation,
  and a canonical address pointing at the empty search would tell a search engine every search is
  that one page.

## The author's tag wins, for every tag

The issue states this only for the description. It is applied to every tag the package writes,
because a page that sets its own `og:title` or `og:image` in its metadata means it, and two tags of
the same property make the result depend on which one a service reads first.

## Which description a page uses

The issue says the front matter description fills the description "when the page sets no
`html_meta` description". Taken literally, a page with a metadata description and a different front
matter one would get its `og:description` from the front matter while its `description` came from
the metadata. The metadata's description is used for both instead, so a page's two descriptions
never disagree.

## No image per page from front matter

The scratch build showed that any front matter field, `image` included, reaches the page's `meta`.
Reading a per-page image from it was left out: it was not part of what was asked, and a page can
already set `og:image` in its metadata, which FR-009 keeps.

## The sitemap registry

django-mvp#682 adds the registry a mounted app contributes its sitemap to. This spec does not wait
on it. The sitemap is a plain Django sitemap the project adds by hand, and contributing it to the
registry is one more story here once that issue ships, delivered as a resolve run.

## Spec 001 edited in this pull request

Spec 001 User Story 5, scenario 3, said a page with no metadata carries the host project's tags
"and no others". The preview tags make that untrue, so it is restated in this pull request to allow
them, and FR-018 points here.

## Glossary

`CONTEXT.md` gains **Preview tags** (as in Key Entities) when the feature is built, alongside the
code that writes them.
