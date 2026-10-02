# Research — 009 API reference pages and maths

Premises read from Sphinx 9.1.0 and django-mvp 0.25.0 as installed in the development
environment, from a real `sphinx-build -b json` of the demo guide (`demo/docs/`), and from the
approved prototype running in a browser with MathJax 4.1.3. Each is something the plan relies on.

There is no `planning-notes.md` for this feature. The inputs are `sketch.md` (what the screens
need, what the prototype faked) and the decisions already recorded, D6 above all.

## R1. What Sphinx writes for maths

With its default settings (`sphinx/ext/mathjax.py:152-155`, delimiters `\(` `\)` and `\[` `\]`),
the JSON build leaves the author's notation in the page body for the browser:

- inside a sentence: `<span class="math notranslate nohighlight">\(t = w / r\)</span>`
- on its own line: `<div class="math notranslate nohighlight">\n\[ ... \]</div>`
- numbered: the `div` carries `id="equation-<label>"` and starts with
  `<span class="eqno">(1)<a class="headerlink" href="#equation-<label>" title="Link to this
  equation">¶</a></span>`, followed by the notation as a bare text node
- a reference to a numbered equation: `<a class="reference internal" href="#equation-<label>">(1)</a>`

Nothing in the JSON build typesets it and no script reference is carried in the page's file. In
an HTML build Sphinx adds `https://cdn.jsdelivr.net/npm/mathjax@4/tex-mml-chtml.js` with `defer`
(`sphinx/ext/mathjax.py:31,137-139`). That is the address D6 accepts.

## R2. How a page knows it holds maths

The prototype searches the body for the characters `class="math`, which would also match a code
sample showing that markup. Two honest ways to know:

- **`has_maths_elements` in the page's file.** Sphinx 9.1 writes it (`True` on the maths page,
  `False` on the others, absent on Sphinx's own pages). It is template context the HTML builder
  happens to hand the JSON builder (`sphinx/builders/html/__init__.py:664`), alongside keys such
  as `alabaster_version`. It is not a documented part of the build, and the host builds with a
  Sphinx version of its own choosing. **Not adopted.**
- **`BodyRewriter` sees the element.** It already parses every body the view renders. An element
  whose class list holds `math` is maths; text inside a code sample is escaped and never an
  element. **Adopted.** One parse, no dependence on the Sphinx version, and the same parse is
  needed for R5.

A host project that tells Sphinx to render maths as images still gets `div.math` and
`span.math` around the images, so such a page loads the typesetting and finds nothing to typeset.
The spec's Assumptions leave that configuration to whatever it produces. Not worth a second rule.

## R3. Limiting typesetting to what Sphinx marked

MathJax reads `window.MathJax` when its script runs. `options.ignoreHtmlClass` and
`options.processHtmlClass` are matched against whole class names, so ignoring
`mvp-sphinx-content` and processing `math` means that inside the page content only `.math`
elements are typeset. Text outside the content, such as "On this page", is still scanned. Checked in the
browser: 21 containers on the demo maths page, all inside `.math`, and a dollar sign or backslash
elsewhere on the page is untouched. A wrapper with class `mvp-sphinx-scroll` inside `div.math`
(R5) is still processed, because that class name is not the ignored one.

The settings file is loaded with a plain `<script src>` and the library with `defer`, both in the
shell's `extra_js` block (`mvp/templates/mvp/base.html:134`). A plain script always runs before a
deferred one, so the order holds whatever else the host puts on the page, provided the two tags
keep those attributes. That is what a test pins.

## R4. What a reader sees when a formula is wrong

MathJax 4's default TeX packages include `noundefined`: an unknown command is shown as its own
name inside the typeset formula, coloured `red`, and the rest of the formula and of the page is
typeset. Checked in the browser with the demo's deliberate mistake: no `mjx-merror` element is
produced for an unknown command, so the prototype's `mjx-merror` rule did not apply to it and the
red is MathJax's own literal colour. That breaks FR-016.

`tex.noundefined.color` accepts any string and writes it into the element's `style`. Set to
`var(--mvp-sphinx-code-error)` it resolves on the page (checked: computed colour is the theme's).
A formula MathJax cannot parse at all (unbalanced braces) does produce `mjx-merror`, which the
stylesheet rule covers.

The prototype coloured a failed formula with `--mvp-sphinx-admonition-dangerous`, which is the
theme's error colour unmixed: 2.87:1 on the page background in the light theme. The existing role
`--mvp-sphinx-code-error` measures 9.2:1 (light) and 10.4:1 (dark) on the page background.

## R5. Keyboard access to a wide equation

MathJax 4 gives every typeset container `tabindex="0"`, speech text and Braille
(`data-semantic-speech`, an `mjx-speech` child with `role="tree"`). That meets FR-013 with nothing
from this package. It also means arrow keys inside a focused container explore the expression and
do not scroll it. The prototype made the container the scrolling area, so a keyboard reader could
not scroll a wide equation, and before typesetting the area had no focus at all.

The package already solves this for tables: `BodyRewriter` wraps each one in
`<div class="mvp-sphinx-scroll" role="region" tabindex="0" aria-label="...">`, which
`content.css` scrolls sideways and outlines on focus (ADR 0003: rewrite only what CSS cannot).
The same wrapper around an equation's notation works before and after typesetting and does not
depend on MathJax's internals. The number stays outside it, so it does not scroll away.

## R6. What Sphinx writes for reference entries

Every domain writes an entry as `<dl class="<domain> <kind>">` holding
`<dt class="sig sig-object <domain>" id="...">` and a `<dd>`. Inside the `dt`:
`span.sig-prename` (module or class path, absent on a nested member), `span.sig-name` (the
documented name), `span.sig-paren`, `em.sig-param`, `span.default_value`, `span.sig-return`,
leading `em.property` for keywords, then with `sphinx.ext.viewcode` an
`a.reference.internal > span.viewcode-link`, and last `a.headerlink` titled "Link to this
definition". Field groups are `dl.field-list` with `dt` labels ending in `span.colon`. A
deprecation inside an entry is the same `div.deprecated` FS-004 already styles. An autosummary
table is `table.autosummary`, which `BodyRewriter` already wraps like any table.

A hand-written entry (`.. py:function::`) and a generated one (`.. autofunction::`) come out
identical, and other domains (`js`, `c`) use the same `sig-object`, `sig-name` and `sig-param`
classes with a different domain class. The stylesheet keys on those shared classes only.

The `id` Sphinx gives a Python entry is its full dotted name (`demo.links.Guide.address`), and
a JavaScript entry's usually is (`$.getJSON` under a module becomes `jmod.-.getJSON`). Other
domains prefix or mangle it: C++ `_CPPv43Foo`, an option `cmdoption-v`, C `c.my_func`.

## R7. The entry link's accessible name

`BodyRewriter.name_heading_link` names a heading link from all the text before it in its holder.
For an entry that is the whole signature, parameters, return type and `[source]` included. The
entry's own name is in `sig-prename` + `sig-name`; a nested member has only `sig-name`, which two
classes on a page can share. The `id` is unique on the page and, where it ends with the
documented name, is the full dotted name a developer would say.

## R8. Contrast of the pairs the prototype created

Measured with the suite's own `ColourMath`, light / dark:

| Text on background | Ratio |
|---|---|
| muted on the code background (module path, return arrow) | 7.12 / 7.84 |
| keyword role on the code background | 12.93 / 9.3 |
| string role on the code background (default values) | 7.38 / 12.44 |
| muted on the page background (field labels, equation numbers) | covered by an existing test |
| theme error colour on the page background (prototype's failed formula) | **2.87** / 5.52 |
| code-error role on the page background | 9.2 / 10.4 |

Every signature colour is an existing `--mvp-sphinx-code-*` role or the muted role, which
`TestCodeStylesheet` already measures on the code background. What no test does yet is tie the
signature and maths rules to those roles, so a later edit could introduce an unmeasured pair.

## R9. What the suite can and cannot see

Typesetting happens in the reader's browser, so no server-side test sees typeset maths. Tests
cover what the server decides: which pages carry the two script tags and in what order, that the
notation reaches the page as written inside `.math`, the scroll region and its name, link names
and targets. What only a browser shows is checked in a browser before the pull request is marked ready, and
recorded in `progress.md`:

- typeset output on the maths page, with the equation region in place (SC-003), including that
  each container still carries speech (FR-013) and that the formula with a mistake does not stop
  the others (FR-011)
- no sideways scrolling of the page at 320 pixels, on the reference page and the maths page
  (SC-004)
- the switch between the light and dark themes (FR-017)
- what a reader sees in "On this page" for a heading that holds maths
- the source listing page and its links back to the documentation, in both themes
