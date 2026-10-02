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
- The documentation app's sidebar lists the whole contents. Add `extensions = ["mvp_sphinx.navigation"]` to your Sphinx `conf.py` and `sphinx-build -b json` writes a `navigation.json` into the build. Each captioned toctree becomes a group, an uncaptioned one lists its pages at the top level, hidden toctrees are included, and a page with pages of its own opens as a group. The front page's entry comes first, under the front page's own title. Sphinx is still not needed where the site runs, and without the line the sidebar holds the front page entry alone.
- Pages carry your site's look with nothing to set up. The page template links a stylesheet shipped inside the package (`mvp_sphinx/content.css`) that takes every colour from your django-mvp theme, so pages follow the light and dark themes and any theme of your own, and only pages the documentation app renders load it. Sphinx's own stylesheets are never used. A second stylesheet, `mvp_sphinx/page.css`, places the "On this page" list. If you override `mvp_sphinx/page.html`, keep `{{ block.super }}` in its `styles` block and render `{{ body }}` in place of `{{ page_data.body }}`.
- Notes, tips, important notices, warnings and dangers are told apart by what they mean, and see-also boxes and version notes are drawn the same way, with a deprecation as a warning. An admonition kind the package does not know reads as a note. Code is highlighted in your theme's colours, with captions, line numbers and emphasised lines. Text in admonitions and highlighted code stays readable (WCAG AA) in django-mvp's light and dark themes.
- Wide tables and long code lines scroll inside their own area instead of widening the page, and images and figures scale down to fit. Each table's scrolling area takes keyboard focus and is named by its caption, so a keyboard user can reach the hidden columns.
- Every heading and glossary term carries a link to itself, shown when the pointer is over it or keyboard focus reaches it, and a followed link lands clear of the top bar. If your top bar is taller than django-mvp's, set `--mvp-sphinx-header-clearance` (5rem by default) in your own stylesheet and headings and the "On this page" list both clear it. Screen readers hear each link by name, such as "Link to this heading: Installing". `BodyRewriter` adds the names and the table areas before a page is rendered, so a `PageView` subclass gets them too.
- Documented functions, classes and other objects read as part of your site. Each signature sits in a bar in your code colours with its parameters, defaults and return type told apart, and the description, parameters and return values hang from a rule beneath it. Entries inside a class are drawn inside it. This works for any language Sphinx documents, generated by `autodoc` or written by hand, and there is nothing to set up. Signature text stays readable (WCAG AA) in django-mvp's light and dark themes.
- Glossaries read as defined terms, and keys, interface labels and menu paths are marked out from the text around them.
- Every page of a documentation app has a search box that lists the pages containing all the words typed. Case is ignored, other forms of a word match ("lanterns" finds "lantern"), and common words such as "the" don't stop a search matching. It searches only that app's docs build, works with scripts turned off, and each search has an address you can bookmark (`<prefix>search/?q=...`). Pages whose title holds the words come first, each result shows a passage of the page, and a result found by a section heading links to that section. Links in your docs to Sphinx's search page now land on it. It reads the search data Sphinx already writes into the build, so nothing needs configuring and Sphinx is still not needed where the site runs. This adds `snowballstemmer` as a dependency.
- Pages list their own headings beside them, under "On this page", on wide screens, where the page's text also widens into the room beside the list. The list stays in view below the top bar as the page scrolls. It is nested the way the page nests its sections, each entry links to its heading, and it leaves out the page's title and the headings of other pages. A page with no headings below its title shows no list. It comes from the build with nothing to set up, and it follows a rebuild on the next request.
- Every page ends with links to the previous and next page in reading order, each showing the title of the page it leads to. The front page has no previous link, the last page has no next link, and a page outside every toctree has neither. The links stay within the documentation app, so several apps each link under their own address. They come from the build with nothing to set up, and they follow a rebuild on the next request.
- `python manage.py build_docs` builds your docs, so you no longer have to remember the Sphinx invocation. Give a `DocumentationApp` its Sphinx source directory as `source_dir` and the command runs the JSON build from there into the app's `build_dir`. With no arguments it builds every mounted app that has a `source_dir`, and `build_docs <namespace>` builds the ones you name. It exits with an error when Sphinx reports a failed build. Building stays a step you run: the site still never imports Sphinx or starts a build to answer a request, and an app without a `source_dir` is served as before.
- The README now has a five-step quickstart that takes a project from install to a documentation page in its own shell, and a public surface section that lists every name a project can use. Anything not listed is internal.
