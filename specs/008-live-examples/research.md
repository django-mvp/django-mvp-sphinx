# Research: FS-008 Show working examples live next to their source code

Research for the build, against main as of 2026-10-02 (ddcbfc1, which carries FS-009), django-mvp
0.25.1 and Sphinx 9.1.0 as installed in the worktree. It answers each of the maintainer's planning
notes under his own words, then each line of `sketch.md` under "What the screens need from the
code" and "What the prototype faked".

## Planning notes

### Host base template

> "I don't really understand what you mean by 'the host's base.html extend a new package template'.
> Why? MVP project's are supposed to extend mvp/base.html."

**Adopted.** A host's `base.html` keeps extending `mvp/base.html`, and the prototype's
`mvp_sphinx/base.html` is dropped.

**What that leaves, and why it stops here.** The application shell is drawn by one block,
`{% block app %}`, in `mvp/base.html`. Every page of a host project reaches that block through its
own `base.html`. django-mvp has no setting, context value, view attribute or request check that
makes that block render the page's content alone:

- `MVP_CONFIG["layout"]` configures the sidebar, navbar and dock. None of them can be turned off,
  and the footer and dock have no switch at all.
- `mvp/entrance.html` and `mvp/error_base.html` do drop the shell, but by being different templates
  that replace `{% block app %}`. A page has to extend them, so it has no shell when opened on its
  own either. The specification wants the opposite: an ordinary page of the site that loses its
  shell only when it is shown as an example (FR-008, FR-009).
- "Full page" apps (django-mvp #247) fill the shell. They do not remove it.
- Nothing in the roadmap or the tracker of django-mvp asks for a page without its shell.

So the only template that can decide "this request gets the content alone" is `mvp/base.html`
itself, or a template placed between it and the host's pages. The second is what the prototype did
and what is ruled out.

**What this package could do on its own, and why each is a workaround:**

| Means | Why it is not the answer |
|---|---|
| The documentation page reaches into the frame and hides the shell with a stylesheet it injects | Needs scripts, so with scripts off the frame shows the whole shell. The shell is drawn first and then hidden, on every load inside the frame. It depends on django-mvp's private markup (`#mvp-app`, the drawer, the dock) and breaks silently when that changes |
| A middleware of this package rewrites the response of a framed request | A second setup step for every host, and the same dependence on django-mvp's markup, now by parsing HTML |
| This package ships its own `mvp/base.html` ahead of django-mvp's in the template order | Replaces django-mvp's base behind the host's back. Any change to the real one is lost |
| The host writes each example's template to replace `{% block app %}` | The example is then never an ordinary page of the site, and the packaged views (`MVPFormView` and the rest) cannot be examples without a template of their own |

Each of them leaves this package owning knowledge of how django-mvp draws its shell.

**The right home is django-mvp.** The change there is small: `mvp/base.html` renders
`{% block content %}` and the messages alone, in place of the shell, when the page is being shown
inside a frame. Two things recommend doing it there:

- It is the template that owns the shell, so the shell-less page stays correct when the shell
  changes.
- It can key on the request itself. A browser sends `Sec-Fetch-Dest: iframe` on every navigation
  inside a frame: the first load, a posted form, the redirect after it, and any link followed
  inside the example. That removes the prototype's `?example=1`, and with it the faked item
  "a link inside an example would lose it and bring the shell back". Example views need no code
  for it and "Open on its own" is the plain address. The header is sent by every current browser
  (Chrome 80, Firefox 90, Safari 16.4); a browser without it shows the example with its shell,
  which still works.

  A request header also means a page cannot be asked for without its shell by address alone, so
  the shell-less form adds no new address to the site.

  **A limit found on re-reading, 2026-10-02.** Browsers send `Sec-Fetch-Dest` only to an address
  they treat as secure: `https`, or `localhost` and `127.0.0.1` over plain `http`. A site reached
  over plain `http` by any other name gets no such header. That covers an intranet deployment
  without TLS and the development server reached by its machine name, which is how a walkthrough
  of this feature is opened. There the example would show with the whole shell inside the frame.
  The prototype's notes already recorded this and used `?example=1` for that reason. So the header
  alone is not enough. If django-mvp takes this on, it needs a second signal that works over plain
  `http`, and the natural one is in the page: `mvp/base.html` marks the document when it finds
  itself inside a frame, and django-mvp's own stylesheet hides the shell for a marked document.
  That needs scripts, and the header covers the reader who has them off on a secure site. Both
  stay inside django-mvp, so the reasoning above for where this belongs is unchanged.

With that in django-mvp, this package needs nothing for FR-009 beyond a higher minimum version of
django-mvp, and the demo's `base.html` goes back to extending `mvp/base.html`.

**Decided, 2026-10-02.** Put to the maintainer, he answered with a simpler means than any above:
the example's page is written without the shell. "If somebody is trying to show a demo page in a
sphinx view, can't they override content using template blocks in their demo page? Why does a demo
page have to show the whole thing?" The table above held that against the idea because the page is
then never an ordinary page of the site. He does not need it to be one. The specification was
reworded to match (FR-008, FR-009) and the decision is D11. Nothing is asked of django-mvp, and
the work described above for it is not being done.

What that means for the build is under R1.

### Frame setting

> "X_FRAME settings is fine as long as we document it."

**Adopted.** `X_FRAME_OPTIONS = "SAMEORIGIN"` is a setup step for a host that uses live examples.
The README documents it, with the reason: Django's default refuses every frame, and the sign-in
and error pages have to be frameable too because they are what a refused or failing example shows.
The demo keeps the setting. A per-view decorator was looked at and not adopted: it cannot cover the
sign-in redirect or the error pages.

### Frame height

> "We can talk about frame height later if we need to."

**Adopted.** The frame keeps one fixed minimum height, fills its pane beside a taller source, and
a taller example scrolls inside it. Nothing in the build measures the example or resizes the frame.

## Read against FS-009, delivered since this specification was approved

FS-009 styles API reference entries and typesets maths. Its specification leaves live examples to
this feature by name, and nothing in it changes a behaviour this specification describes:

- It changes how reference entries and maths look and nothing about ordinary highlighted code, so
  an example's source is still highlighted as a code block of the same language is (FR-005).
- Its links on reference entries are not headings, so a page's headings list is still what this
  specification says an example leaves alone (FR-010).
- Its rule that a page with neither reference entries nor maths looks and loads as before is about
  what FS-009 itself adds. It does not stop a page with an example loading what the example needs.

No contradiction, and nothing here that FS-009 already delivered.

## What the build settles

### R1. A page without the shell

`mvp/base.html` draws the shell inside `{% block app %}` (site-packages `mvp/templates/mvp/base.html`,
lines 83 to 120). The block is public: `mvp/entrance.html` replaces it to draw the sign-in pages.
The messages are drawn inside it too (`<c-messages :messages="messages" dismissible />`, line 113),
so a template that replaces the block has to draw them itself.

This package ships `mvp_sphinx/example.html`. It extends the host's `base.html`, replaces `app`
with a `main` element holding `{% block content %}` and the messages, and leaves everything else
of the base alone: the theme script, the stylesheets, the `extra_js` block. An example's template
extends it and fills `content`. Any view can use it, the packaged ones included, by naming such a
template.

Removed with it: the prototype's `mvp_sphinx/base.html`, the `?example=1` flag and the
`framed_address` built from it. The demo's `base.html` goes back to extending `mvp/base.html`.
"Start again" is a link to the example's address aimed at the frame, and "Open on its own" is the
same address with no target.

### R2. How an example is held in the docs build

The prototype wrote HTML comments into the page body and found them again with a regular
expression. The build writes elements instead:

```html
<div class="mvp-sphinx-example" data-address="/examples/contact/" data-title="The contact form">
  <div class="mvp-sphinx-example-source" data-name="forms.py">
    <div class="highlight-python notranslate">…</div>
  </div>
  …
</div>
```

The wrappers are `raw` nodes for the `html` format, with attribute values escaped by
`html.escape`. Between them sit ordinary `literal_block` nodes, which Sphinx highlights exactly as
it does a `code-block` of the same language (FR-005). A JSON build keeps raw HTML nodes in the
page body, which the prototype's own markers showed.

Three things recommend elements over comments. A build read by anything that does not know about
examples (a host that overrides the page template, another Sphinx builder of the HTML family)
shows the source as plain code blocks, which is the right fallback. Attribute escaping is the
standard one. And the served page reads them with `html.parser`, which the package already uses
for every body, in place of a regular expression over markup.

Serving: `LiveExamples` in `mvp_sphinx/examples.py` reads the rewritten body with an
`HTMLParser` subclass, tracking `div` depth to find where each example and each source ends, and
returns the body as parts in order: markup, example, markup. A body that does not contain the
text `mvp-sphinx-example` is not parsed again and is passed through whole, so a page without
examples costs one substring test (FR-017).

### R3. The marker

```rst
.. live-example:: /examples/contact/
   :title: The contact form

   ../../examples/forms.py
   ../../examples/views.py 12-25
   ../../templates/demo/examples/contact.html
```

- The argument is the example's address. It must start with one `/` and hold no scheme, no host,
  no backslash and no whitespace. `//host/` and `/\host/` are both ways a browser reaches
  another site and both are refused.
- `:title:` is optional. Without one the frame is named "Live example", translated.
- Each content line is a file, resolved as Sphinx's `literalinclude` resolves one
  (`env.relfn2path`): relative to the page's own file, or from the source directory with a leading
  `/`. An optional last word `first-last` or `n` limits it to those lines, counted from 1. The
  range is split off only when the last word has that shape, so a path with spaces still works.
- Each file is recorded with `env.note_dependency`, so an incremental build rewrites the page
  when the file changes.

Line ranges and not `literalinclude`'s other selectors (`:pyobject:`, `:start-after:`): one
selector is enough for what the specification asks, a part of a file, and Article II says to add
the others when someone needs them.

### R4. What a source is called

The file's name. When two sources of one example would read the same, each takes as many parent
folders as it needs to differ (`a/forms.py`, `b/forms.py`). When the same file is named twice with
different lines, the lines are added (`views.py 12-25`). The name is worked out at build time and
written to `data-name`.

### R5. The language of a source

Pygments' own table, by file name (`pygments.lexers.find_lexer_class_for_filename`), with one
override: `.html` is `html+django`, because in a Django project it is a template. No match is
`text`. Pygments is installed wherever Sphinx is, and this code runs only during a build.

### R6. Whether the site has the example's page

`django.urls.resolve` on the address's path, with the request's own urlconf, at the moment the
page is served. It asks the URL configuration and never requests the page, so a slow or failing
example costs the documentation page nothing (FR-012). The script prefix is taken off first.
Before resolving, the address is checked again with Django's
`url_has_allowed_host_and_scheme(address, allowed_hosts=None)`, so a docs build made by an older
or altered extension cannot put another site in the frame (FR-003).

What it cannot know: that the site will refuse the reader or fail. The frame then shows the
site's own answer, which is what the specification asks for (screen 7).

### R7. The frame, and the setup step

No `sandbox` attribute: the example is the same site and needs its forms, its scripts and the
reader's session. `loading="lazy"` is kept from the prototype.

The host sets `X_FRAME_OPTIONS = "SAMEORIGIN"` (planning note, adopted). A host that sends a
`Content-Security-Policy` with `frame-ancestors` needs `'self'` in it. Both go in the README. The
package cannot check either for the host: a system check cannot tell whether a docs build holds
examples, and a view can exempt itself with a decorator.

### R8. A stylesheet a browser does not keep an old copy of

The rules live in `example.css`, a file of their own (ruled by eye). It is linked only by a page
that holds an example, which also keeps a page without one as it was (FR-017). Cache busting for
static files in general is the host's static files storage, as for every other file the package
ships, and nothing is built for it here.

### R9. Which modules import Sphinx

Two: `mvp_sphinx.navigation`, the extension a host names, and `mvp_sphinx.live_example`, the
directive it registers. Article XII says the only code that imports Sphinx is the extension that
runs during the build, and a directive the extension registers is part of it. The notes that say
"the only module" (`navigation.py`, `AGENTS.md`) are corrected. `mvp_sphinx.examples`, which
serves, imports neither, and owns the class names and attribute names both sides use, so the
build module imports them from it and never the other way round.

### R10. What only a browser shows

Checked in a browser at convergence and recorded, because no test in this suite runs one: a form
sent inside the frame shows the site's answer and the documentation page's address does not
change (US1.4, SC-002); "Start again" returns the example without reloading the page (US2.4); two
examples do not affect each other (US1.7); at 320 pixels wide neither the example nor its source
makes the page scroll sideways (US2.6, FR-016); the dark theme reaches the example.

### What stays as the prototype had it

- The slow example sleeps three seconds. It is the demo of the waiting state and nothing in the
  suite requests it.
- The failing example shows Django's debug page, because the demo runs with `DEBUG` on. A host in
  production shows its own error page there.
