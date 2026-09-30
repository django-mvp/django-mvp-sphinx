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
- Pages of the documentation carry your site's look with nothing to set up. The page template links a stylesheet shipped inside the package (`mvp_sphinx/content.css`) that reads its colours from your django-mvp theme, so pages follow the light and dark themes and any theme of your own. Only pages the documentation app renders load it. If you override `mvp_sphinx/page.html`, keep `{{ block.super }}` in its `styles` block.
- Notes, tips, important notices, warnings and dangers in your pages are told apart by what they mean, in your theme's colours, and stay readable in the light and dark themes. See-also boxes and version notes are drawn the same way, with a deprecation note as a warning, and any admonition kind the package has no meaning for reads as a note. The demo guide gains a content tour page showing them.
- Code blocks in your pages are highlighted in your theme's colours, so the highlighting follows the light and dark themes and every part of it stays readable in both, including on emphasised lines. Captions, line numbers and emphasised lines are shown, and a block in a language that can't be highlighted reads as plain code. The content tour gains examples of each.
- Wide content stays inside the page. Each table sits in a scrolling area that takes keyboard focus and is named by the table's caption (or "Table"), so a table wider than the screen scrolls sideways instead of pushing the page, and a keyboard or screen reader user can reach it. Long code lines scroll inside their own box, and images and figures scale down to fit while keeping their proportions. `PageView` applies the change through the new `BodyRewriter`, so a `PageView` subclass gets it too; if you override `mvp_sphinx/page.html`, render `{{ body }}` in place of `{{ page_data.body }}`. The content tour gains a wide table, a table in a list, a long code line, a wide image and a figure.
