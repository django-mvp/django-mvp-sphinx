# ADR 0005 — Search reads the search data the build already holds

**Status:** accepted

## Decision

A documentation app's search answers from the files `sphinx-build -b json` already writes:
`searchindex.json` for which words each page holds, `_static/language_data.js` for the stopwords,
and `globalcontext.json` for the language. `DocsSearch` reads them on every search, with no cache
and no Sphinx import. It turns the reader's words into the keys Sphinx stored them under: lower
case, then stemmed with `snowballstemmer`, the stemmer Sphinx itself uses. Every algorithm the
build's language may have used is tried (for English, both `english` and `porter`). A page is a
result when it holds every word.

`SearchView` serves the results at `search/` under the documentation app. Sphinx gives its own
search page that address, so a docs link to it lands on this search, and Sphinx's page, which has no
content in a JSON build, is no longer served. The search form submits with `GET`, so every search
has an address and works with JavaScript off.

`snowballstemmer` is a runtime dependency of the package.

## Why

Serving never imports Sphinx or starts a build (ADR 0001, the constitution's Article XII), and a
search that needs anything added to the host's Sphinx configuration is a search most hosts would
never turn on. The build already carries everything a search needs, written for exactly this job.

Stemming has to match the build's to find the same pages. Porting the snowball algorithms into the
package would drift from the stemmer the build used. `snowballstemmer` is pure Python with no
dependencies, and it is already installed wherever the docs are built. Trying every algorithm of the
language means a host can move between Sphinx 8, which stems English with Porter, and Sphinx 9,
which uses snowball English, without the search changing under its readers.

Reading on every search keeps a rebuild searchable with no restart, as pages already are
(ADR 0001). Guides of tens to a few hundred pages give search data of tens to hundreds of
kilobytes, which is cheap to parse per request.

## Revisit if

A guide's search data grows large enough that parsing it per request shows up in response times.
The fix then is a cache keyed on the file's modification time and size. Also revisit if a Sphinx
release changes the shape of `searchindex.json`, or stems a language with an algorithm not listed in
`DocsSearch.ALGORITHMS`.
