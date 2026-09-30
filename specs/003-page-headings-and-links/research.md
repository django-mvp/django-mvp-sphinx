# Research — 003 Show a page's headings beside it, and links to the previous and next page

**Spec**: [spec.md](spec.md) · **Plan**: [plan.md](plan.md)

Premises read from the packages the project resolves: Sphinx 9.1.0, sphinxcontrib-serializinghtml
2.0.0, django-mvp 0.25.0, django-cotton 2.6.1, all under `.venv/lib/python3.13/site-packages/`.

## R1 — Sphinx already writes both pieces into every page's JSON

`sphinx/builders/html/__init__.py:564-642` (`get_doc_context`) returns, for every page:

- `toc`: `render_partial(document_toc(env, docname, tags))['fragment']` (lines 623-624), the
  page's own heading tree as an HTML fragment.
- `display_toc`: `env.toc_num_entries[docname] > 1` (line 640).
- `prev` / `next`: `{'link': get_relative_uri(docname, related), 'title':
  render_partial(titles[related])['title']}` (lines 572-590), or `None` when the page has no such
  neighbour. `related` comes from `self.relations`, which Sphinx derives from the toctrees.

The JSON builder dumps that context into each `.fjson` file. Nothing needs to be added to the
navigation extension from FS-002: both pieces are per-page data already in the file the view reads.

**Consequence**: FR-011 holds by construction. The view reads two more keys of the page JSON it
already loads.

## R2 — The shape of `toc`

Probed against a scratch build (`sphinx-build -b json`, Sphinx 9.1.0):

```html
<ul>
<li><a class="reference internal" href="#">Front</a><ul>
<li><a class="reference internal" href="#part-one">Part one</a></li>
<li><a class="reference internal" href="#part-two">Part <code class="docutils literal notranslate"><span class="pre">two</span></code></a><ul>
<li><a class="reference internal" href="#deep">Deep</a></li>
</ul>
</li>
</ul>
</li>
</ul>
```

- The page title is the single outer entry, linking to `#`. Its nested `<ul>` holds the sections,
  nested as the page nests them, each `href="#<id>"` (FR-001, FR-002).
- **A toctree inside a section contributes nothing to `toc`.** In the probe, `Part one` holds a
  toctree listing two pages, and neither page's title nor headings appear (FR-003, scenario 6).
- A page with no sections: `<ul><li><a href="#">Short</a></li></ul>`, `display_toc` false.
- A page whose only non-title content is a toctree (the demo's front page): the title entry holds
  an **empty** `<ul>`, `display_toc` false. So an empty inner list is a real case, not a
  hypothetical one.
- A heading holding inline markup keeps it inside the `<a>` (`<code …><span class="pre">…`). The
  spec shows it as the build renders it (Assumptions; scenario "heading whose text holds markup").
- `:orphan:` pages have a `toc` like any other page.
- `:tocdepth:` metadata is applied by `document_toc`, so "every heading the docs build records"
  respects it with no code of ours.

A page with more than one top-level section (two `=====` headings) gives more than one outer
`<li>`. Sphinx takes the first as the page title (`env.titles`), so the first outer entry is the
title and the others are headings below it.

## R3 — The shape of `prev` / `next` links

`sphinxcontrib/serializinghtml/__init__.py:68-73`: `get_target_uri` gives `''` for `index`,
`folder/` for `folder/index`, and `name/` otherwise. `link` is that address made relative to the
current page's own address. Probed on the demo build: from `about/`, prev is `../settings/`; from
`getting-started/`, prev is `../` (the front page); from the front page, next is
`getting-started/`; from `tutorials/first-page/`, next was `../../menus/` (before FS-004 put
Content tour after it; now `../../content-tour/`).

**Consequence**: `urljoin(request.path, link)` resolves every link under the app's own prefix, the
same way the FS-001 breadcrumbs already resolve `parents[*].link` (`mvp_sphinx/views.py`,
`get_breadcrumbs`). The front page resolves to the prefix itself (FR-008, scenario 4). No `reverse`
is needed and a second app at `manuals/admin/` works unchanged (scenario 5).

`title` is rendered HTML (`render_partial(...)['title']`), so it can hold inline markup, as page
titles do in the FS-001 breadcrumbs.

Orphans and pages outside every toctree have no entry in `relations`, so `prev` and `next` are
`None` (scenario 6). Hidden toctrees feed `relations` like visible ones (the demo's toctrees are
all hidden and every page has neighbours).

## R4 — What the shell's stylesheet provides

The package ships no compiled Tailwind, and a class the packaged `mvp/static/css/django-mvp.css`
does not emit does nothing (AGENTS.md, *The demo project*). Checked in that file: `xl:flex`,
`xl:block`, `hidden`, `gap-10`, `w-56`, `shrink-0`, `self-start`, `sticky`, `top-0`, `top-3`,
`min-w-0`, `flex-1`, `max-w-prose`, `overflow-y-auto`, `max-h-[calc(100vh-8.6rem)]`, `menu`,
`menu-sm`, `sm:grid-cols-2`, `rounded-box`, `border-t`, `border-base-300`, `hover:bg-base-200`,
`focus-visible:bg-base-200`, `text-end`, `opacity-70`, `font-medium`, `text-sm`, `mt-12`, `pt-6`
are all emitted. `sm:col-start-2`, `top-20`, and arbitrary grid templates such as the prototype's
`xl:grid-cols-[minmax(0,75ch)_13rem]` are **not**. The layout is built from emitted utilities only.

## R5 — django-mvp's menu components cannot nest

`mvp/templates/cotton/menu/item.html` renders a `<li>` with one link and uses its slot only to
decide a class; it draws no nested list. `menu/index.html` puts `role="navigation"` on a `<ul>`.
Neither can draw a heading tree. "On this page" is drawn with daisyUI's `menu` classes directly on
a `<nav>` + nested `<ul>`, which daisyUI styles at every depth (`.menu li > ul`), in a component of
this package.

## R6 — The prototype

django-mvp branch `wip/sphinx-docs-in-sidebar`, `mvp/templates/mvp/sphinx_view/page.html`. It
injected `doc.toc|safe` whole (title entry included) inside `<nav aria-labelledby>` and gated it on
`display_toc`, and drew previous and next as two bordered link cards with `rel="prev"` /
`rel="next"` under a `<nav aria-label>`. The owner reviewed the sketch and liked it. The plan keeps
its placement and cards and changes two things: the title entry is dropped (FR-003), and the
links are resolved against the request path, as the breadcrumbs already are (R3), rather than
written out relative.
