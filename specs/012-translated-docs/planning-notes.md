# Planning notes: Serve documentation translated with Sphinx in the reader's Django language

Notes for the build, kept out of `spec.md` because they say how. Each one is answered by name when
the feature is researched and planned.

## The prototype

This feature comes from a prototype on the branch `prototype-translated-docs`, issue
[#152](https://github.com/django-mvp/django-mvp-sphinx/issues/152). Its hand-over notes are
`PROTOTYPE.md` at the root of that branch. All of it is this feature's part except the navbar
overflow at 390 px, which is [#154](https://github.com/django-mvp/django-mvp-sphinx/issues/154).
The prototype adds no screens, so nothing is ported for the look. The demo's language switcher is
configuration in `demo/settings.py` and `demo/urls.py`, with `demo/docs/conf.py` and the German
catalogues under `demo/docs/locales/de/`, and those carry across as they are.

## The shared pieces

- Reading `conf.py` with `ast`: `build_docs.theme_arguments` already did it for `html_theme`. The
  prototype moved it into `mvp_sphinx/languages.py` (`conf_assignments`, `conf_value`) and both
  callers use it. The rebuild keeps one reader for `conf.py` settings.
- Choosing the build for a request: `DocumentationApp.build_dir_for` is the one place every reader
  of a build goes through (`views.py`, `menus.py`, `mounted.py` page extracts, `DocumentationPages`
  search). The language choice lives there and nowhere else.
- Language code conversion: Django's `to_language` / `to_locale`. Nothing custom.

## Duplication to remove

- `menus.py` sets `build_dir` to `None` for a callable `build_dir` and refreshes per request. With
  language folders a plain path can also serve several builds, so the menu should key its cached
  contents by the build folder it was given, for every form of `build_dir`. That removes the
  special case and the rebuild-on-every-language-change.
