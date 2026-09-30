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

## D11. Stem with snowballstemmer, the stemmer Sphinx uses (S3 plan)

**Ambiguous:** FR-006 asks for matching "as Sphinx's own search does", and FR-015 forbids importing
Sphinx. The search data holds stems, so the searched words must be stemmed the same way.

**Chosen:** `snowballstemmer` becomes a runtime dependency. It is pure Python with no dependencies
of its own, and Sphinx itself depends on it, so every environment that builds the docs already has
it (research R2).

**Why:** The alternative is a copy of the Porter and snowball algorithms in this package, which
would drift from the stemmer the build used. Article VII asks for the justification to be recorded;
this is it.

## D12. Stopwords come from the build (S3 plan)

**Ambiguous:** FR-005 says words Sphinx leaves out as too common must not empty a search. The list
lives in Sphinx, which serving may not import.

**Chosen:** Read the list the build already carries, in `_static/language_data.js`. When that file
is missing or unreadable no word is a stopword, and a search made only of stopwords then finds
nothing, which the results page reports as no match (research R3).

**Why:** The list matches the language the docs were built in with nothing configured, and it is
the exact list the build filtered with.

## D13. A word is looked up under every stem its language may have used (S3 plan)

**Ambiguous:** Sphinx 8.1 stems English with the Porter algorithm, Sphinx 9 with snowball English.
The package supports builds from both.

**Chosen:** Look each word up under its lower-case form and under its stem from each algorithm the
build's language may have used. A key that exists is a match (research R2).

**Why:** No sniffing of Sphinx versions, and a host can upgrade Sphinx without its search changing
behaviour. The two algorithms agree on almost every word, so the looser lookup adds nothing a reader
would call a wrong match.

## D14. The results page replaces Sphinx's own search page at `search/` (S3 plan)

**Ambiguous:** D4 says links to Sphinx's search page lead here. The results page could live
anywhere, with a redirect from Sphinx's page.

**Chosen:** The results page is served at `search/` under the documentation app, the address Sphinx's
JSON build gives its own search page. That page, which has no content in a JSON build, is no longer
served.

**Why:** Every link a docs author writes to the search page works with no rewrite and no redirect,
and the results address is the one a reader of Sphinx docs would guess.

## D15. SC-002 is checked on whole words (S3 plan)

**Ambiguous:** SC-002 says every page Sphinx's own search lists is listed here. Sphinx's search also
matches fragments of words, which the specification rules out (clarification 2, FR-006).

**Chosen:** SC-002 is read for searches of whole words, and checked over the real search data: for
each word key in the fixture build, searching it lists every page the data lists under it
(research R4).

**Why:** The clarification is the more specific ruling, and it came after the criterion was
written. Read literally, SC-002 would require fragment matching that FR-006 forbids.

## D16. Three tiers: page title, section heading, elsewhere (S3 plan)

**Ambiguous:** FR-010 puts title matches first. It says nothing about the order of the rest, or
about a match in a section heading.

**Chosen:** Pages whose title holds every word, then pages with a section heading holding every word
(linked to that section), then the rest. Within a tier, by title.

**Why:** A heading is the next best sign that a page is about the words, as in Sphinx's own
scoring, and a stable order by title makes the same search give the same list (US1.8).

## D17. No cache of the search data (S3 plan)

**Ambiguous:** The search data could be parsed once and kept until the build changes.

**Chosen:** Parse it on every search.

**Why:** FR-014 wants the build as it is on disk, the guides in scope give files of tens to hundreds
of kilobytes, and a cache is a second copy to keep correct. It can be added if a real guide shows
the cost (Article II).

## D18. The search form sits above the page's text, for now (S3 plan)

**Ambiguous:** D9 leaves placement to the browser review.

**Chosen:** One component, placed above the article in the page template. The results page shows it
too, holding the reader's search.

**Why:** It is the smallest change to a template that FS-003 is rewriting in parallel, and it can be
moved without touching anything else once the walkthrough settles where it belongs.

## D19. Design review, one round: approve, seven findings applied to the plan (S3R)

**Ambiguous:** None of the findings was critical or high, so none forced a re-plan.

**Chosen:** All seven applied as plan edits, verified against each finding's evidence by the
orchestrator. The short-word exemption from `searchtools.js` is dropped, because FR-005 asks for
every word and Sphinx 9 indexes short words (DR-001). Sphinx's own search page leaves the
`TestSphinxsOwnPages` parametrize, as a declared edit (DR-002). Keys are looked up case-folded,
which finds words Sphinx kept capitalised (DR-005). There is no `search_view_class` setting: a host
that needs another view subclasses `DocumentationApp` (DR-006). An unreadable page file gives an
empty passage (DR-007). JavaScript off gets no test of its own, and tests get no docstrings (DR-004).
For the reader rule, the reviewer suggested adding the search address to FS-006's parametrized
tests (DR-003). The plan adds a new class that reuses FS-006's setup instead, so FS-006's tests stay
unedited and the tamper check stays meaningful. `example.html`, the scaffold's starter component,
stays: retiring it is outside this feature.

**Why:** Each edit either removes work or is one line of design, and each was checkable from the
finding's own text.
