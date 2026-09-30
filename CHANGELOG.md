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
- A `DocumentationApp` is open to everyone unless you limit it. Pass `check=user_is_authenticated` (from `flex_menu.checks`) to keep it for signed-in people: one import and one keyword. An anonymous visitor is sent to sign in and back to the page they asked for, the menu entry is hidden from readers the rule excludes, and images and downloads are covered too. Other rules work the same way: `user_in_any_group("Support")`, `user_has_any_permission("support.view_ticket")` or a function of your own. A signed-in reader the rule excludes gets your 403 page, staff and superusers get no bypass, and a rule that raises is a server error on every page that draws the menu entry.
- The documentation app's sidebar lists the whole contents. Add `extensions = ["mvp_sphinx.navigation"]` to your Sphinx `conf.py` and `sphinx-build -b json` writes a `navigation.json` into the build. Each captioned toctree becomes a group, an uncaptioned one lists its pages at the top level, hidden toctrees are included, and a page with pages of its own opens as a group. Sphinx is still not needed where the site runs, and without the line the sidebar holds the front page entry alone.
