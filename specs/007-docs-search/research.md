# Research — 007 Search the documentation

Premises read from Sphinx 9.1.0 and snowballstemmer 3.1.1 as installed in the development
environment, Sphinx 8.1.3 (the lowest version the dev dependencies allow) where it differs, and
django-mvp 0.25.0. Each is something the plan relies on; each was checked against a real
`sphinx-build -b json` of `tests/sphinx/guide/`.

## R1. The JSON build already carries Sphinx's search data

`sphinx-build -b json` writes `searchindex.json` at the root of the build, with no configuration.
Its keys: `docnames`, `filenames`, `titles`, `terms`, `titleterms`, `alltitles`, `indexentries`,
`objects`, `objtypes`, `objnames`, `envversion`.

- `docnames[i]` is the document name (`section/index`, `section/nested/page`); `titles[i]` its
  title as plain text.
- `terms` maps a word key to the documents whose body text holds it; `titleterms` the same for words
  in any heading of the document (the title and every section heading). A value is one document
  number or a list of them.
- `alltitles` maps each heading's plain text to `[[document, anchor], ...]`; the anchor is `null`
  for the document's own title and the section's `id` otherwise (`"Tables": [[0, "tables"]]`).
- Only documents are in it: `genindex` and `search`, which the JSON build also writes as
  `genindex.fjson` and `search.fjson`, are not in `docnames` and so can never be a result.
- It holds only text a reader sees: markup, attribute values and the document's file name are not
  indexed.

`search.fjson` is Sphinx's own search page. The JSON builder links to it at `search/` relative to
the build root, so a docs link to it (`:ref:\`search\``) resolves to `<prefix>search/`.

## R2. How Sphinx turns words into keys

At build time (`sphinx/search/__init__.py`, `IndexBuilder.feed`), each word of the text is stemmed
with the language's stemmer after lower-casing, and the stem is stored unless it is a stopword; when
the stem is filtered, the original word is tried instead. Hence keys such as `This` or `A`: the stem
(`this`, `a`) is a stopword and the capitalised original is kept.

The stemmer is `snowballstemmer`, a pure-Python package with no dependencies that Sphinx itself
depends on:

- Sphinx 9.x English: `snowballstemmer.stemmer("english")` (`tables` → `tabl`, `notice` → `notic`).
- Sphinx 8.1 English: `snowballstemmer.stemmer("porter")`. The two agree on almost every word and
  differ on a few endings.
- Other languages Sphinx supports with a stemmer (`da de es fi fr hu it nl no pt ro ru sv tr`) use
  the snowball algorithm of that language's name. `ja` and `zh` use their own splitters and are
  out of this feature's reach.

The build's language is the `language` key of `globalcontext.json` (`"en"` by default).

Consequence for the plan: a searched word is looked up under each of its possible keys: its lower
case form, and its stem under every snowball algorithm the build's language may have used (for
English both `english` and `porter`). A key that exists means a match. No version sniffing, no
Sphinx import.

## R3. How Sphinx's own search reads a query

`_static/searchtools.js` (`Search._parseQuery`, `performTermsSearch`), 9.1.0:

- The query is split on anything that is not a letter, digit or underscore.
- A word is dropped when its lower case form is a stopword, or when it is only digits.
- The rest are stemmed; a document is a result when it holds every stem in `terms` or `titleterms`.
  (Sphinx relaxes this for words of two letters or fewer; the plan keeps that rule, see plan.)
- Sphinx also matches fragments (`word.length > 2`, a substring of a key). The specification rules
  that out (FR-006, clarification 2), so this plan does not.

The stopwords are in the build, in `_static/language_data.js`:
`const stopwords = new Set(["a", "about", ...]);` in 9.x, `var stopwords = [...]` in older builds.
The bracketed list is valid JSON in both. That file is written by every HTML-family builder,
including JSON, so reading it needs nothing from the host's configuration. When it is missing or
unreadable, no word is treated as a stopword; a query of stopwords alone then finds nothing, which
is the spec's "nothing matched", not an error.

## R4. SC-002 is checkable without a browser

Sphinx's HTML search lists, for a whole-word search, exactly the documents under that word's key in
`terms` and `titleterms` (fragment matches aside, which the spec excludes). So "every page Sphinx's
own search lists is listed here" can be tested over the real search data: for every key in `terms`
and `titleterms` of the fixture build that is a plain lower-case word, searching for it lists every
document the index lists under it. No JavaScript runtime is needed.

## R5. Passages come from the page files

The search data carries no text. The passage for a result comes from that page's `.fjson` `body`,
turned into plain text with `html.parser` (the standard library, already used by
`mvp_sphinx.page_body`), skipping `a.headerlink` (the ¶ link), `script` and `style`, as Sphinx's own
summary does (`Search.htmlToText`). The passage is the text around the first word whose key matches
a searched key, cut at word boundaries, about 240 characters, as Sphinx's `makeSearchSummary`.

Reading one page file per result is proportionate: guides here are tens to a few hundred pages
(spec Assumptions) and each file is already read whole to serve the page.

## R6. Access and the missing build

- `MountedApp.bind` wraps every view of the mount's URL patterns in the app's `check`, so an address
  added to `DocumentationApp.urls` is governed like every page with nothing more to do (FR-012).
  The access feature (#9, PR #49) adds no runtime code for the same reason.
- `PageView` answers 404 for every address when the build directory does not exist
  (`DocsBuild.page()` returns `None`). The results page answers the same way (FR-013).

## R7. What the prototype offers

The reviewed prototype (django-mvp `wip/sphinx-docs-in-sidebar`) has no search. Its demo build
carries `searchindex.json`, which is what confirmed R1 in the first place. Nothing is taken from it
for this feature beyond the page it renders into, which FS-001 already brought over.

## R8. Where the form goes, in the shell

django-mvp 0.25.0 ships `c-actions.search` (an input with no form or name) and
`c-page.list.actions.search` (bound to a list view's `filterForm`). Neither submits to an address of
our choosing, so the package ships its own small component, built from the same daisyUI `join`,
`input` and `btn` classes the shell's stylesheet already emits. Placement is left to the walkthrough
(decisions D9).
