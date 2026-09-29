# Brainstorm

Working notes from before the first release. Nothing here is a ratified
decision.

## Prior art (September 2026)

Every package that renders Sphinx docs through a Django project's own templates
does it the same way: build with Sphinx's JSON builder, then load each page's
`.fjson` file in a view.

| Package | What it does | State |
| --- | --- | --- |
| [django-sphinx-view](https://github.com/carltongibson/django-sphinx-view) | A view that loads `<path>.fjson` and renders it through `base.html`, plus a builder that adds the site's table of contents to each page as an HTML fragment. About 74 lines, LGPL-2.1 | Maintained (26.1, February 2026) |
| [django-sphinx-hosting](https://github.com/caltechads/django-sphinx-hosting) | A multi-project documentation platform. It imports uploaded JSON builds into models and renders them with its own Bootstrap theme | Maintained, but a whole platform with its own stack |
| [django-docs](https://github.com/littlepea/django-docs) / [django-sphinx-docs](https://github.com/adamghill/django-sphinx-docs) | Serve Sphinx's finished HTML through a Django view, with access control | Stale / barely used. Pages don't render through the project's templates |
| [django-sphinxdoc](https://gitlab.com/sscherfke/django-sphinxdoc) | Integrates Sphinx builds into a site | Abandoned (2019) |
| [djangoproject.com `docs` app](https://github.com/django/djangoproject.com/tree/main/docs) | The same `.fjson` approach, with versions, languages and search | Active, but specific to that site and not a package |

None of them puts the documentation's navigation into the host site's own
navigation. django-sphinx-view comes closest, and it ships the table of
contents as ready-made HTML rather than as data a Python-declared menu can use.

## Why not depend on django-sphinx-view

What this package needs from it is a view that finds a page's `.fjson` file.
That's a few lines, and owning them lets the view do what the application shell
needs: serve the images and downloads a page links to, redirect a missing
trailing slash instead of returning 404, and fit mounted-app routing. The site
navigation comes from a small Sphinx extension that writes the whole tree as
JSON, so the builder django-sphinx-view adds isn't needed either. The page data
itself comes from Sphinx's own JSON builder.

## Starting point

A working prototype was built inside django-mvp before this repository existed.
It serves the docs as a mounted app, draws the contents in the app sidebar, and
styles admonitions, code and tables from the theme's colours. It is the
starting point for the first features here.
