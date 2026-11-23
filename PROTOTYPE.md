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
2. Give `build_dir` one directory per language:

   ```python
   docs = DocumentationApp(
       build_dir={
           "en": BASE_DIR / "docs" / "_build" / "en" / "json",
           "de": BASE_DIR / "docs" / "_build" / "de" / "json",
       },
       source_dir=BASE_DIR / "docs",
   )
   ```

3. `python manage.py build_docs` builds each language, running
   `sphinx-build -b json -D language=<code>` into its directory.
4. Turn on Django's language handling as usual: `LANGUAGES`, `LocaleMiddleware`,
   and `set_language` with django-mvp's language switcher if readers should
   pick for themselves.

## What a reader gets

- The build for Django's active language. That language comes from the
  language cookie, a URL prefix or `Accept-Language`, whichever the project
  uses.
- Fallback order: the exact language (`de-at`), its base language (`de`), then
  the same two for `LANGUAGE_CODE`, then the first build given.
- A paragraph that isn't translated yet shows in English inside the German page.
  The German build always holds every page, so no page falls back on its own.
- Every part follows the language: pages, sidebar captions and titles, search
  (German stopwords and stemming), page extracts in info dialogs, and images
  and downloads.
- Section anchors stay the same in every language, because Sphinx keeps the
  source document's ids. Links to `#searching-the-guide` and anchored page
  extracts work in German too.

## What was built

Commit `100e9c9` and the one after it.

| File | Change |
|---|---|
| `mvp_sphinx/mounted.py` | `build_dir` may be a mapping of language code to directory. `build_dir_for` picks with `build_language`, using `get_language()`. Keys may be in Django's form (`pt-br`) or Sphinx's (`pt_BR`). |
| `mvp_sphinx/management/commands/build_docs.py` | A mapping builds every language with `-D language=`. |
| `mvp_sphinx/menus.py` | Treats a mapping like a function: the directory is set for each request. |
| `demo/settings.py` | `LANGUAGES` (English, German and Italian; Italian has no docs on purpose), `LocaleMiddleware`, the language switcher in the navbar. |
| `demo/urls.py` | `django.conf.urls.i18n`. |
| `demo/mounted.py` | The guide has an `en` and a `de` build. |
| `demo/docs/conf.py` | `locale_dirs`, `gettext_compact = False`. |
| `demo/docs/locales/de/` | Catalogues for every page. Translated: front page, Your first visit, Signing in, Finding your way. |

No new screens. The look is unchanged.

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

## Decisions

- 2026-11-23 Sam: translated docs follow Django's built-in language. No switcher
  in the package, and the developer does the translation. Constitution Article
  XII amended to allow one build per language.
