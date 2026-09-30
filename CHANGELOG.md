# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
  Everything not yet released goes under [Unreleased], grouped by change type:
  Added, Changed, Deprecated, Removed, Fixed, Security. Prepare Release promotes
  that section to a version heading and dates it.

  Do NOT write a version heading by hand. Tag Release fires on any push to main
  that touches pyproject.toml, and the only thing stopping it cutting a release
  from that push is the absence of a `## [X.Y.Z]` section matching the version
  in pyproject.toml. Writing one here defeats that guard, and the repository
  ends up with a tag and a GitHub Release for a version nobody prepared.

  Write for someone deciding whether to upgrade. Say what changed for them and
  what they have to do about it, not which files moved.
-->

## [Unreleased]

### Added

- `DocumentationApp` serves a Sphinx JSON build (`sphinx-build -b json`) as pages of your site. Mount it in your URLs and point `build_dir` at the build, and each page renders inside your application shell with its title in the tab and breadcrumbs back to the front page. Pages are read on every request, so a rebuild shows without a restart, and serving never imports Sphinx.
- Images and downloads that a page links to are served from the build (`_images/` and `_downloads/`), and nothing else in the build can be fetched as a file.
- Addresses behave like the rest of your site: a page address without its trailing slash redirects permanently to the slashed one, keeping the query string, and an unknown address gets your ordinary 404 page. A build that doesn't exist yet leaves the rest of the site working, and its pages appear on the first request after it is built.
- A `DocumentationApp` can be named with `name`, which the tab title, first breadcrumb and menu entry use. Mount several, each with its own `namespace` and prefix, and each serves only its own build under its own name.
- The documentation app's sidebar lists the whole contents. Add `extensions = ["mvp_sphinx.navigation"]` to your Sphinx `conf.py` and `sphinx-build -b json` writes a `navigation.json` into the build. Each captioned toctree becomes a group, an uncaptioned one lists its pages at the top level, hidden toctrees are included, and a page with pages of its own opens as a group. Sphinx is still not needed where the site runs, and without the line the sidebar holds the front page entry alone.
- Pages carry your site's look with nothing to set up. The page template links a stylesheet shipped inside the package (`mvp_sphinx/content.css`) that takes every colour from your django-mvp theme, so pages follow the light and dark themes and any theme of your own, and only pages the documentation app renders load it. Sphinx's own stylesheets are never used. If you override `mvp_sphinx/page.html`, keep `{{ block.super }}` in its `styles` block and render `{{ body }}` in place of `{{ page_data.body }}`.
- Notes, tips, important notices, warnings and dangers are told apart by what they mean, and see-also boxes and version notes are drawn the same way, with a deprecation as a warning. An admonition kind the package does not know reads as a note. Code is highlighted in your theme's colours, with captions, line numbers and emphasised lines. Text in admonitions and highlighted code stays readable (WCAG AA) in django-mvp's light and dark themes.
- Wide tables and long code lines scroll inside their own area instead of widening the page, and images and figures scale down to fit. Each table's scrolling area takes keyboard focus and is named by its caption, so a keyboard user can reach the hidden columns.
- Every heading and glossary term carries a link to itself, shown when the pointer is over it or keyboard focus reaches it, and a followed link lands clear of the top bar. Screen readers hear each link by name, such as "Link to this heading: Installing". `BodyRewriter` adds the names and the table areas before a page is rendered, so a `PageView` subclass gets them too.
- Glossaries read as defined terms, and keys, interface labels and menu paths are marked out from the text around them.
