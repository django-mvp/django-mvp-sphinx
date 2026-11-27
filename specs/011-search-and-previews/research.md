# Research: Get the documentation found by search engines and previewed well when shared

## Assumptions checked

Run on `main` at 9f154b3, 2026-11-17, before the spec gate.

- **Front matter reaches the docs build with no extension configured.** A scratch Sphinx project
  with `myst_parser` and `mvp_sphinx.navigation`, built with `sphinx-build -b json`. A page whose
  front matter is `description: A page about things.` writes it into the page's `meta` as
  `{"description": "A page about things.", ...}`, and its `metatags` holds only the viewport tag.
  A page with both a front matter `description` and `myst.html_meta.description` writes the front
  matter one into `meta` and the metadata one into `metatags` as a rendered `<meta>` tag, so the
  two are told apart when a page is served. Holds.
- **The author's metadata already reaches the head.** `PageView.get_meta_tags` reads `metatags`
  through `MetaTags.from_markup` and drops the viewport tag. `uv run pytest tests -k meta` is green
  (7 passed). The demo guide's kitchen-sink page sets `myst.html_meta.description`, and its build
  carries it in `metatags`. Holds.
- **The site's name is available from django-mvp.** The installed django-mvp has
  `MVP_CONFIG["site_name"]` (default `None`) and `mvp.utils.site_name(request)`, which falls back
  from the current site's name to the request's host. Holds.
- **Django's sitemap framework takes a site, not a request.** `Sitemap.get_urls(page, site,
  protocol)` is called with the `Site` (or `RequestSite`) the sitemap is served for, and `items()`
  takes no arguments. A documentation app whose `build_dir` is a function of the request has no
  request to call it with inside the sitemap. This is a planning question, not a defect: the build
  has to be chosen from the site the sitemap is given (User Story 1, scenario 9). The demo installs
  `django.contrib.sites` and its middleware, so the demo can serve a sitemap.
- **The results page is a template of its own.** `mvp_sphinx/search.html` does not extend
  `mvp_sphinx/page.html`, so tags added to the page template do not reach it (FR-013). Holds.
