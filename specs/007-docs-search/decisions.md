# Decisions: FS-007 Search the documentation

Each entry is a point the issue left open, the reading the specification takes, and why. Any of
them can be reversed when the specification is reviewed.

## Starting point for the plan

A working prototype of the documentation app exists on the `wip/sphinx-docs-in-sidebar` branch of
[django-mvp](https://github.com/django-mvp/django-mvp), under `mvp/integrations/sphinx_view/`,
`mvp/templates/mvp/sphinx_view/` and `demo/sphinx_docs/`. It has no search, but its demo docs
build already contains the search data Sphinx's JSON builder writes, which is what this feature
reads. The plan may start from the prototype's pages and demo build. It may not start from its
django-sphinx-view dependency, which this package drops (docs/brainstorm.md).

## D1. Search covers one documentation app's pages and nothing else

**Ambiguous:** The issue says the search covers "the documentation only". It doesn't say what
happens with two documentation apps, or whether the search appears outside the docs.

**Chosen:** Each documentation app searches its own docs build. Its search appears only on its own
pages, and results never include the host project's content or another documentation app's pages
(FR-001, FR-004).

**Why:** A host project mounts two documentation apps because they are separate guides
(CONSTITUTION.md Article XII). A site-wide search box would be the host project's search, which
the maintainer ruled out of scope.

## D2. All words must match, in any form and any case

**Ambiguous:** How several words combine, and how loose a match is.

**Chosen:** A page matches when it contains every word, ignoring case and treating different forms
of a word as the same word, as Sphinx's own search does. Very common words Sphinx leaves out of its
search data never empty a search on their own. Fragments of words don't match (FR-005, FR-006).

**Why:** Readers of Sphinx documentation already know how its search behaves, and the search data
in the build is written for exactly that behaviour. Matching it means SC-002 can be checked
against Sphinx's own HTML search of the same docs.

## D3. A results page with its own address, working without JavaScript

**Ambiguous:** Whether results appear as a page or as a live list while typing.

**Chosen:** Submitting the search opens a results page at an address that carries the words
(FR-002, FR-003). Suggestions while typing are left out.

**Why:** It is the smallest thing that meets the issue. It works whatever the reader's browser
does, and a results page can be bookmarked or shared like any other page of the site. Suggestions while typing can be added on top later without changing it.

## D4. The results page sits where Sphinx's own search page would

**Ambiguous:** Sphinx builds a search page of its own, which the page-serving feature (#4) serves
as an ordinary page, and docs can link to it.

**Chosen:** Links the docs make to Sphinx's search page lead to this search (FR-009). Sphinx's own
search page and general index page never appear in results.

**Why:** A link to "search" that a docs author writes should keep working. Sphinx's search page
carries no content of its own in a JSON build.

## D5. Title matches first, a passage per result, section links

**Ambiguous:** The issue asks only for finding "the page that covers it". It doesn't say how results
are ordered or what each result shows.

**Chosen:** Pages whose title contains the words come first. Each result shows the page's title and
a plain-text passage containing the words, and links to the matching section when a heading
matches (FR-010, FR-011). This is User Story 2, at P2, so the P1 story stands without it.

**Why:** Sphinx's own search does the same, so readers of Sphinx documentation expect it. Without it, a word common to the
guide returns a list the reader has to open page by page.

## D6. No search data means "unavailable", never an error

**Ambiguous:** What happens when a docs build has pages but no search data.

**Chosen:** The pages keep working and the results page says search is unavailable, in a way a
reader can tell apart from "no matches" (FR-013). A missing docs build answers at the search
address as it does for pages, per #4.

**Why:** Optional documentation should never take down the site, the same reasoning #4 applies to
a missing build. Reporting "no matches" when the search data is missing would mislead the reader
into thinking the guide doesn't cover the subject.

## D7. No new access rule

**Ambiguous:** Access control is a sibling feature (#9), and #10 doesn't depend on it.

**Chosen:** The results page is an address of the documentation app, governed by whatever governs
its pages (FR-012). Nothing here adds a rule.

**Why:** A search that returns titles and passages reveals the pages' content, so it has to follow
the same rule as the pages. Putting it under the same rule, rather than a second one, is what keeps
them from drifting apart when #9 lands.

## D8. No paging through results

**Ambiguous:** Whether long result lists are split across pages.

**Chosen:** All results on one page.

**Why:** The package is for a project's own user guide, typically tens or a few hundred pages
(README, Scope & philosophy). A search that matches most of them is a search to narrow, not to page
through. Paging can be added if a real guide outgrows this.

## D9. Where the search sits is left to the browser review

**Ambiguous:** The issue says "from within its own pages" and nothing about placement.

**Chosen:** The specification requires only that every documentation page offers the search
(FR-001). Placement and look come from the host's theme and shell, and are settled when the feature
is looked at in a browser.

**Why:** Placement is a judgment only a human eye settles, and the specification's requirements each
become tests, which should not pin appearance.

## D10. Vocabulary

"Search data" is used for the record of words per page that Sphinx writes into the docs build, and
"results page" for the page listing a search's results. Neither is in CONTEXT.md yet. The
implementation adds both, and warns against "index" for the search data, because Sphinx's general
index is a different thing.
