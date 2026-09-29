# Decisions for FS-005

Assumptions made while specifying this feature, where issue #8 left a gap. Each was decided from
the repository's own documents (README, GOALS.md, CONSTITUTION.md, CONTEXT.md, docs/ROADMAP.md) and
the sibling issues #4 to #13.

## The feature's reading

A developer with a django-mvp project and a Sphinx source directory follows the README alone, from
install to a served front page with the contents in the app sidebar: install, one line of Sphinx
configuration, build, mount a documentation app, add its menu entry. The README lists every name a
host project can use. The demo project serves a user guide written for the demo site, covering every
state that #4 to #7 draw. Nothing new is added to serving, navigation or styling.

## Decided

| # | Where #8 was silent | Decision | Why it holds |
|---|---|---|---|
| 1 | How the quickstart builds the docs | Sphinx's JSON builder, run directly | A build command is #11 (R7, aspirational) and has not shipped. Documenting it early would break Article VI |
| 2 | Whether the quickstart teaches Sphinx | No. It starts from an existing Sphinx source directory and names Sphinx's own way to create one | The README is for someone deciding whether to install this (Article VI). Sphinx has its own documentation |
| 3 | What the demo's user guide is | A user guide for the demo site, not documentation of this package | User guides for a site's users are the package's first audience (README, *Scope & philosophy*). The package's documentation stays the README |
| 4 | Where the demo's docs build comes from | Built by the README's demo instructions with the step the quickstart teaches, not committed to the repository | The demo then exercises the documented path. A committed build goes stale the moment its sources change |
| 5 | What the public surface list covers | What exists when this feature merges. #9, #10 and #11 each add their own entries | The constitution requires every public change to update the README in the same pull request |
| 6 | Which states the demo must show | Contents groups, a page with pages of its own, a long page with many headings, previous and next links, each admonition kind, code, a wide table, an image, a download, a glossary, cross-references, and a missing page | These are the states #4 to #7 name. The demo is where each one is looked at |
| 7 | Whether the demo covers access control or search | No | Both are later features (#9, #10), and their own specs decide what the demo shows |
| 8 | Order of this feature | Built after #4, #5, #6 and #7 | It describes what they deliver. The issue's footer already records the dependency |

## Starting point for planning

A working prototype exists on the `wip/sphinx-docs-in-sidebar` branch of
[django-mvp/django-mvp](https://github.com/django-mvp/django-mvp/tree/wip/sphinx-docs-in-sidebar).
Its `demo/sphinx_docs/` directory is a small user guide for an invented inventory site, with
contents groups, a nested page and a long page title, and is a reasonable base for the demo's user
guide. It was built inside django-mvp on top of django-sphinx-view. This package owns its own view
instead, so its configuration line and mount will differ from the prototype's.
