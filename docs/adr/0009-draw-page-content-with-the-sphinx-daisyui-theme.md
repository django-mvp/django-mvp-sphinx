# ADR 0009 — Draw page content with the sphinx-daisyui theme's own stylesheet and markup

**Status:** accepted

Replaces [ADR 0008](0008-draw-page-content-from-daisyui-tokens-in-an-scope-block.md), whose
stylesheet and page-body rewrite now live in the theme.

## Decision

A documentation app's docs build is made with the `daisyui` theme from
[sphinx-daisyui](https://pypi.org/project/sphinx-daisyui/), a dependency of this package.
`build_docs` and the demo's `conf.py` select it, and a project's own `conf.py` can still name
another theme.

Every build made with that theme writes `_static/styles/sphinx-daisyui-content.css`, and its page
bodies carry the markup that stylesheet draws: scroll regions around tables and display equations,
named permalinks, and admonition and version-note icons as inline SVG. The package's page template
links that one file, and `DocsBuild.file` serves that one path from the build, the way images and
downloads are served. No other file of `_static/` is served. A build made with another theme has
no such file, so its pages link none and a project that chose that theme draws its own pages.

The package ships `mvp_sphinx/static/mvp_sphinx/page.css`, which sets two of the properties the
theme lets a host set: the surface the page sits on (`--daisy-sphinx-page-bg`, django-mvp's
`base-200`) and the sunken surface (`--daisy-sphinx-surface`). The reading width stays the theme's
`--daisy-sphinx-max-width` and a project sets it in its own stylesheet. The page's container is
sized from that property, so it carries the "On this page" column beside a text of any width. It is linked after the theme's file because the last is declared on
the same element as the theme's own. The page body sits in an element with the
`daisy-sphinx-content` class, and the package's own markup inside it, a live example's title bar
and running pane, carries `daisy-sphinx-escape` so the theme's rules stop short of it.

The package keeps only what is its own: the contents, the live examples, and `page_body.has_maths`,
which says whether a page holds notation so that MathJax loads for it.

## Why

The theme draws the same page body for every site built with it, and it is maintained with the
Sphinx and sphinx-design markup it styles. A second stylesheet and a rewrite of the body here
would draw the same elements twice and drift apart. The theme's stylesheet reads only daisyUI's
tokens, so a page still follows the host's themes (Article XIII).

Serving the build's own copy keeps one source for the file's version: the one that wrote the page
bodies is the one that styles them. Copying it into the package's static files would let the two
differ whenever the theme is upgraded between a build and a deploy.

## Revisit if

- A project needs a build made with a theme other than `daisyui` to be drawn by this package.
- The theme stops writing its page-body stylesheet to the path above.
