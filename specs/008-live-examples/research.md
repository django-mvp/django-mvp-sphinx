# Research: FS-008 Show working examples live next to their source code

Research for the build, against main as of 2026-10-02 (django-mvp 0.25.1). It answers each of the
maintainer's planning notes under his own words. The first one stops the build for his decision,
so the rest of the research (the marker's syntax, how examples are held in the docs build, source
names) is not written yet.

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

With that in django-mvp, this package needs nothing for FR-009 beyond a higher minimum version of
django-mvp, and the demo's `base.html` goes back to extending `mvp/base.html`.

**Decision needed from the maintainer** before the plan is written: whether django-mvp gains this,
and if so whether FS-008 waits for that release.

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
