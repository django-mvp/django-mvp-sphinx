# Research: Serve documentation translated with Sphinx in the reader's Django language

The full research comes when the feature is planned. This file holds only the checks run before the
specification was put up for approval.

## Assumptions checked

Run on 2026-11-24 against the prototype branch `prototype-translated-docs`, which the spec
describes.

- **`build_docs` builds a translated source once per language.** `python manage.py build_docs` on
  the demo wrote `demo/docs/_build/json/en/` and `demo/docs/_build/json/de/`, each holding a full
  build with its own `_static/language_data.js`, and built the untranslated staff guide straight
  into its `build_dir`. Holds.
- **Django converts Sphinx's language codes.** `to_language("pt_BR")` returns `pt-br` and
  `to_locale("pt-br")` returns `pt_BR`. Holds, so no conversion of the package's own is needed.
- **The page follows Django's active language.** Requesting `/docs/first-visit/signing-in/` through
  the test client with `Accept-Language: de` served the German title, `de-at` also served German
  (base-language fallback), and `it` and `en` served English (the demo offers Italian with no
  translation). Holds.
- **Search uses the language's own search data.** A search for `Konten` found a page with German
  active and none with English active. Holds.
- **Page extracts follow the language.** `/info/section/` and `/info/whole-page/` render with German
  active. Holds.
- **The package's own strings are not yet translated.** With German active, the front page still
  carries the English "Link to this heading" label, and `mvp_sphinx/locale/` holds only `en`. This
  is the gap FR-013 closes, as `PROTOTYPE.md` records.
