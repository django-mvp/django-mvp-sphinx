# Implementation Plan: Serve documentation translated with Sphinx in the reader's Django language

**Branch**: `012-translated-docs` · **Spec**: [spec.md](spec.md) · **Research**: [research.md](research.md)

## Summary

`build_docs` builds a translated documentation source once per language into folders of the app's
one `build_dir`, and the documentation app serves each request from the folder for Django's active
language. The choice lives in one function, called by `DocumentationApp.build_dir_for`, which every
reader of a build already goes through. The sidebar's contents are cached per build folder. The
package's own strings gain a German catalogue. There is no new setting.

The prototype (`prototype-translated-docs`) is the agreed behaviour. Its code is rebuilt test-first.
Three things differ from it: the layout listing is plain functions with no cache and no lock, the
menu caches per build folder, and `build_docs` clears the layout it no longer writes.

## Technical Context

- Python 3.13, Django 6.x, django-mvp as locked. No new runtime dependency.
- Serving never imports Sphinx (Article XII): `languages.py` imports Django and the standard
  library only. Tests build their docs with Sphinx, as every test module does.
- Files: `mvp_sphinx/languages.py` (new), `mvp_sphinx/mounted.py`, `mvp_sphinx/menus.py`,
  `mvp_sphinx/management/commands/build_docs.py`, `mvp_sphinx/locale/de/LC_MESSAGES/django.po` and
  `.mo` (new), `tests/test_languages.py` (new), `tests/test_menus.py`, `tests/test_mounted.py`,
  `tests/test_management/test_commands/test_build_docs.py`, `tests/sphinx/translated/` (new
  fixture), `tests/conftest.py`, `tests/test_demo.py`, `demo/settings.py`, `demo/urls.py`,
  `demo/docs/conf.py`, `demo/docs/locales/de/**.po`, `README.md`, `CHANGELOG.md`, `CONTEXT.md`.

## Constitution Check

- **XII Scope.** Reads builds from disk on every call, never imports Sphinx, builds only in the
  command and as a separate process. One build per language, as amended on 2026-11-23. Pass.
- **VIII Translation.** The package's strings get a German catalogue under `locale/`. The demo
  carries no translation markup: its settings gain `LANGUAGES`, `LocaleMiddleware` and the
  language switcher only. Pass.
- **Testing standard.** Tests assert which build serves a request, files on disk, ids and anchors
  and returned objects. No wording, no layout. A German word is used only as search input, which
  is data. Pass.

## The language module

`mvp_sphinx/languages.py`, functions only:

- `conf_assignments(source_dir)` and `conf_value(source_dir, name, default)`: `ast` over `conf.py`.
  `build_docs.theme_arguments` calls `conf_assignments`.
- `source_language(source_dir)`: `conf_value(..., "language", None)` or `"en"`; `"en"` when
  `source_dir` is `None`. Read on every call (it runs only on the last fallback step).
- `translations(source_dir)`: the language codes under `locale_dirs` (default `["locales"]`) with
  a `<code>/LC_MESSAGES` holding a `.po`, as Sphinx names them, sorted.
- `site_languages()`: `{to_language(code) for code, _ in settings.LANGUAGES}`.
- `language_builds(build_dir)`: `{}` when `build_dir` is missing or holds `globalcontext.json`,
  otherwise `{to_language(folder.name): folder}` for each folder holding `globalcontext.json`.
  Read from disk on every call.
- `build_for(build_dir, language, source_dir)`: the first of language, its base, `LANGUAGE_CODE`,
  its base, `source_language`, then the first build. `build_dir` itself when there are no language
  builds.

`DocumentationApp.build_dir_for` returns `build_dir(request)` for a function, otherwise
`build_for(self.build_dir, get_language(), self.source_dir)`.

## `build_docs`

- `language_builds(app, quiet)` (as the prototype): `[(None, build_dir)]` without translations,
  otherwise the source language and every translation in `LANGUAGES`, each `(code, build_dir /
  code)`, with `-D language=<code>`. Skipped translations are reported in one line unless quiet.
- `clear_other_layout(build_dir, folders)`, called before each app builds: when writing language
  folders, remove each child of `build_dir` that belongs to a single build (all children when
  `globalcontext.json` is in `build_dir`) and each language build folder that is not in the new
  set; when writing a single build, remove every child folder holding `globalcontext.json`. A
  `build_dir` holding neither is not touched.

## The menu

`DocumentationMenu` keeps `built: dict[build_dir, (stamp, contents, front_page_label)]`. `refresh`
looks the request's build folder up: a matching stamp reuses the cached contents, otherwise it
rebuilds and stores them. It then installs the contents (children and front-page label) when they
are not the ones already installed. The `callable(app.build_dir)` special case in `__init__` goes.
`refresh()` keeps its signature (a test pins subclasses that override it without arguments).

## The package's own strings

`makemessages -l de` from `mvp_sphinx/`, German filled in, `.mo` compiled and committed beside it
so a host gets it with no step. A test reads both with Babel: every message the English catalogue
holds has a German translation, and the `.mo` holds the same translations as the `.po`.

## The demo

`demo/settings.py`: `LocaleMiddleware`, `LANGUAGES` (English, German, Italian), the language
switcher in the navbar. `demo/urls.py`: `django.conf.urls.i18n`. `demo/docs/conf.py`:
`locale_dirs`, `gettext_compact = False`. `demo/docs/locales/de/**.po`: the prototype's German
catalogues, as they are. Sphinx compiles `.mo` files at build time, so no `.mo` is committed there.

## Fixtures and tests

`tests/sphinx/translated/`: a three-page source with `locales/de` and `locales/pt_BR` catalogues
(one page untranslated in German), an image, a download and a heading anchor, plus a catalogue for
`fr` and a source-language catalogue. `tests/conftest.py` builds it per language into one build
folder, session scoped (the layout `build_docs` writes), and a fixture to switch the active
language.

- `tests/test_languages.py`: `TestConf`, `TestTranslations`, `TestLanguageBuilds`, `TestBuildFor`
  (fallback order, `pt-br`, `de-at`, `LANGUAGE_CODE`, source language, no language builds,
  Sphinx not importable).
- `tests/test_management/test_commands/test_build_docs.py`: `TestTranslatedBuilds` (real Sphinx
  runs through `call_command`), `TestClearingTheOtherLayout`.
- `tests/test_mounted.py` and `tests/test_menus.py`: pages, files, search, extracts and sidebar from
  the right build, cache per build, language changed between requests.

## Story order

US1 (developer, issue 156) first, tasks T001 to T006: the module, the command, serving, the menu, the
demo and the documentation. Then US2 (reader, issue 157), T007 to T009: German strings and the
reader-side acceptance across every part. Sequential, in the feature worktree.
