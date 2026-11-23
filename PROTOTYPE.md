# Prototype: translated documentation follows Django's language

The documentation app serves the build for the reader's language, as Django has
already chosen it. The package adds no language switcher and never runs the
translation workflow: the host project translates with Sphinx's own tools and
gives the app one build per language.

## What a developer does

1. Translate the docs with Sphinx's own workflow:
   - `conf.py`: `locale_dirs = ["locales/"]`, and `gettext_compact = False` for
     one catalogue per page.
   - `sphinx-build -b gettext docs docs/_build/gettext`, then
     `sphinx-intl update -p docs/_build/gettext -l de`.
   - Fill in the `msgstr` lines of `locales/de/LC_MESSAGES/**/*.po`.
2. Give `build_dir` one folder, as for untranslated docs:

   ```python
   docs = DocumentationApp(
       build_dir=BASE_DIR / "docs" / "_build" / "json",
       source_dir=BASE_DIR / "docs",
   )
   ```

3. Turn on Django's language handling as usual: `LANGUAGES`, `LocaleMiddleware`,
   and `set_language` with django-mvp's language switcher if readers should
   pick for themselves. `LANGUAGES` is the list of languages the docs are
   offered in. There is no setting of the package's own.
4. `python manage.py build_docs` works out the rest:
   - The translations are the `<locale_dir>/<code>/LC_MESSAGES` folders holding
     `.po` files, under `conf.py`'s `locale_dirs` (Sphinx's default is
     `["locales"]`).
   - It builds the language the docs are written in (`conf.py`'s `language`,
     `en` when unset) and every translation whose language is in `LANGUAGES`,
     each into `build_dir/<code>/` with `-D language=<code>`. Sphinx's `pt_BR`
     matches Django's `pt-br`.
   - A translation not in `LANGUAGES` is skipped, and the command says so in
     one line.
   - Docs with no translations build straight into `build_dir`, as before.

## What a reader gets

- The build for Django's active language. That language comes from the
  language cookie, a URL prefix or `Accept-Language`, whichever the project
  uses.
- Fallback order: the exact language (`de-at`), its base language (`de`), then
  the same two for `LANGUAGE_CODE`, then the build of the language the docs
  are written in.
- Serving reads the layout from disk: a `build_dir` holding a build of its own
  is served as it is, otherwise its language folders are the builds. The
  listing is cached until `build_dir` changes.
- A paragraph that isn't translated yet shows in English inside the German page.
  The German build always holds every page, so no page falls back on its own.
- Every part follows the language: pages, sidebar captions and titles, search
  (German stopwords and stemming), page extracts in info dialogs, and images
  and downloads.
- Section anchors stay the same in every language, because Sphinx keeps the
  source document's ids. Links to `#searching-the-guide` and anchored page
  extracts work in German too.

## What was built

Commit `100e9c9` and the ones after it. The language folders replaced a
`build_dir` mapping in the second round.

| File | Change |
|---|---|
| `mvp_sphinx/languages.py` | Reads `language` and `locale_dirs` from `conf.py`, finds the translations, lists the language builds in `build_dir` and picks one for the reader. |
| `mvp_sphinx/mounted.py` | `build_dir_for` serves the language build for `get_language()` when `build_dir` holds language folders. |
| `mvp_sphinx/management/commands/build_docs.py` | Builds the source language and each translation in `LANGUAGES` into its own folder, with `-D language=`. |
| `demo/settings.py` | `LANGUAGES` (English, German and Italian; Italian has no docs on purpose), `LocaleMiddleware`, the language switcher in the navbar. |
| `demo/urls.py` | `django.conf.urls.i18n`. |
| `demo/docs/conf.py` | `locale_dirs`, `gettext_compact = False`. |
| `demo/docs/locales/de/` | Catalogues for every page. Translated: front page, Your first visit, Signing in, Finding your way. |

`demo/mounted.py` is as on main: one `build_dir`. No new screens. The look is
unchanged.

## Faked or skipped

- No tests, no README section, no changelog.
- The sidebar menu caches one build's contents. With readers in two languages it
  rebuilds whenever consecutive requests change language. The rebuild should
  cache per build directory.
- The package's own strings ("On this page", "Link to this heading", search
  labels) have no German catalogue. Article VIII asks for a `locale/` the host can
  extend. Only English ships.
- `<html lang="en">` is hard-coded in django-mvp's base template, so a German page
  is announced as English. It needs fixing in django-mvp.
- At 390 px in German the navbar overflows by 26 px. "On this page" and
  django-mvp's "Anmelden" sign-in button don't fit beside each other.
- The staff guide stays single-language.
- Switching a source between translated and untranslated leaves the old layout
  in `build_dir`: an old build of its own wins over new language folders.
  Delete `build_dir` before rebuilding. The rebuild should clear it.
- The source language's catalogues, if any, are not treated as a translation:
  it is always built once, as the source.

## Decisions

- 2026-11-23 Sam: translated docs follow Django's built-in language. No switcher
  in the package, and the developer does the translation. Constitution Article
  XII amended to allow one build per language.
- 2026-11-23 Sam: a `build_dir` per language is too much configuration. One
  `build_dir`, the languages are Django's `LANGUAGES`, and `build_docs` builds
  whichever of them the docs have translations for.
