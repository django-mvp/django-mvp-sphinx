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

## Planning notes, answered

Run on 2026-11-24 against main at `e7b3da7` and the prototype branch.

- **Reading `conf.py` with `ast`. Adopted.** One reader, in `mvp_sphinx/languages.py`:
  `conf_assignments` and `conf_value`. `build_docs.theme_arguments` and the language lookups both
  call it.
- **Choosing the build for a request. Adopted.** `DocumentationApp.build_dir_for` is the one place
  that calls `languages.build_for`. Every reader of a build already goes through it: `views.py` (two
  places), `mounted.py` (`DocumentationPages` search and `page_extract`), `menus.py`.
- **Language code conversion. Adopted.** Django's `to_language`, nothing custom.
- **Per-build menu cache. Adopted**, see `plan.md`, "The menu".

## What already exists

- Reading `conf.py` settings: this repo, `build_docs.theme_arguments` (moves, not rewritten).
- Choosing and listing language builds: new code, small. Django has no concept of a build folder,
  and the prototype's `BuildLanguages` class and its lock and `st_mtime` cache are dropped for plain
  functions, because DocsBuild already reads the build from disk on every request (ADR 0001).
- Matching `pt_BR` with `pt-br`: Django, `to_language`.
- Reading the active language: Django, `get_language`.
- The German catalogue: Django's `makemessages` and `compilemessages`, from `mvp_sphinx/`
  (Constitution Article VIII). The check that it is complete uses Babel, which Sphinx already
  installs.
- Per-language Sphinx builds: Sphinx itself, `-D language=<code>`. Catalogue compiling:
  Sphinx's `gettext_auto_build`.
- The cache of the menu's contents per build folder: this repo, `DocumentationMenu.refresh` already
  holds one build's contents. It holds a dict of them.
- Clearing the layout a rebuild no longer writes: the standard library, `shutil.rmtree`.
