# Research — 004 Make user-guide content look like the rest of the site

Evidence behind the plan. Everything about Sphinx was read from a probe build made with the
Sphinx the dev group resolves (9.1.0); everything about django-mvp from the installed
`.venv/lib/python3.13/site-packages/mvp` (0.25.x).

## R1. What a page body looks like

`sphinx-build -b json` writes the page body as HTML in the `.fjson` file's `body` key. A probe
page carrying every construct in the spec produced:

| Construct | Markup |
|---|---|
| Heading | `<h2>Text<a class="headerlink" href="#id" title="Link to this heading">¶</a></h2>` inside `<section id="id">` |
| Admonition | `<div class="admonition note"><p class="admonition-title">Note</p>…</div>` |
| Generic admonition | `<div class="admonition-custom-title admonition">` (no kind class) |
| See also | `<div class="admonition seealso">` |
| Version notes | `<div class="versionadded">`, `<div class="versionchanged">`, `<div class="deprecated">`, each a `<p>` opening with `<span class="versionmodified added">` |
| Code | `<div class="highlight-python notranslate"><div class="highlight"><pre>` with Pygments short token classes (`k`, `nf`, `s2`, `c1`, `mi`, `o`, `p`, `w`, …) |
| Code caption | `<div class="literal-block-wrapper docutils container" id="id1"><div class="code-block-caption"><span class="caption-text">…</span><a class="headerlink" … title="Link to this code">¶</a></div>` |
| Line numbers | `<span class="linenos">1</span>` inline in the `pre` |
| Emphasised line | `<span class="hll">…</span>` wrapping the whole line |
| Table | `<table class="docutils align-default" id="id2">`, optional `<caption><span class="caption-text">…</span><a class="headerlink" … title="Link to this table">¶</a></caption>` |
| Figure | `<figure class="align-default"><img …><figcaption><p><span class="caption-text">…</span><a class="headerlink" … title="Link to this image">¶</a></p></figcaption></figure>` |
| Glossary | `<dl class="simple glossary"><dt id="term-Term">Term<a class="headerlink" href="#term-Term" title="Link to this term">¶</a></dt><dd>…</dd></dl>` |
| Cross-reference | `<a class="reference internal" href="…"><span class="xref std std-term">…</span></a>` |
| Key | `<kbd class="kbd docutils literal notranslate">Ctrl</kbd>+<kbd …>C</kbd>` |
| Label | `<span class="guilabel"><span class="accelerator">S</span>ave</span>` |
| Menu path | `<span class="menuselection">File ‣ Open</span>` |

Consequences for the plan:

- **Every headerlink's accessible name is "¶".** Its visible content is the pilcrow, and the
  `title` attribute is only a description. FR-010 needs a name, which CSS cannot give, so the
  body is rewritten before it is rendered (plan, *Body rewrite*).
- **Headerlinks are not only on headings.** Code captions, table captions, figure captions and
  glossary terms carry them too. One rule names them all from the text of the element that holds
  them.
- **The `title` attribute is already localised** by the docs build's own `language`, and it says
  what kind of thing the link points at ("heading", "term", "table"). The accessible name reuses it.
- **A table is not a scroll container.** Keyboard scrolling of an overflowing region needs an
  element that takes focus (`tabindex="0"`), and giving a `<table>` itself `display: block` and
  `role="region"` would override its table role. So each table is wrapped (FR-008).
- **Unknown admonition kinds still carry `admonition`.** A rule on `.admonition` alone gives every
  admonition the informational look, and meaning rules override it (FR-004's fallback).

## R2. django-mvp already styles ordinary text in the theme

The page template (FS-001) wraps the body in `<article class="prose …">`. django-mvp's packaged
stylesheet ships Tailwind Typography's `.prose` and daisyUI's `:root .prose` override, which sets
every `--tw-prose-*` variable from the theme (`--tw-prose-body: var(--color-base-content)` and so on;
read from `mvp/static/css/django-mvp.css`). Headings, paragraphs, lists, block quotes, links and
inline code therefore already read as the site's own text and follow the theme.

FR-001 needs no new styling for those elements: daisyUI's override also drops Typography's
backticks around inline code and draws it as a bordered chip from `--color-base-300`. What `prose`
does not cover is Sphinx's own class names (admonitions, Pygments tokens, captions, glossary,
labels, menu paths). The stylesheet adds those and nothing that `prose` already does.

Keys come nearly free: Sphinx writes `:kbd:` as `<kbd class="kbd …">`, and django-mvp's stylesheet
ships daisyUI's `.kbd` component (bordered, `--color-base-200` background, `--radius-field`), so
keys already render as the site's own key caps.

## R3. How a stylesheet can reach the page with no adoption step

`mvp/base.html` has a `{% block styles %}` holding django-mvp's own `<link>`. The package's page
template extends the host's `base.html`, so it can extend that block with `{{ block.super }}` and
one more `<link>` to a static file shipped inside `mvp_sphinx/static/`. Every host project on
django-mvp already has `django.contrib.staticfiles` and runs `collectstatic` for django-mvp's own
stylesheet, so the file is served with no step by the host (FR-017, SC-006), and only pages the
documentation app renders load it (FR-016).

The prototype put its rules in django-mvp's Tailwind source instead. That is not available to a
separate package, and a Tailwind build inside this package would be a build step for us and a
second copy of Tailwind's reset on the page. The stylesheet is plain CSS: its rules key off
Sphinx's class names and the theme's `--color-*` custom properties, and it needs nothing Tailwind
generates.

## R4. The theme's colours, and the two default themes

django-mvp's stylesheet defines `[data-theme=light]` and `[data-theme=dark]` blocks with the
daisyUI 5 colour roles as `oklch()` values: `--color-base-100/200/300`, `--color-base-content`,
`--color-primary`, `--color-info`, `--color-success`, `--color-warning`, `--color-error`,
`--color-accent`, `--color-secondary`, `--color-neutral` and their `-content` pairs. The theme
switcher changes `data-theme` on `<html>` without a reload, so anything written as
`var(--color-*)` follows it (FR-014).

Measured from those values, the prototype's choices fail FR-015 in the light theme: status
colours are light (success L 76%, warning L 82%, info L 74%), so a token coloured
`var(--color-success)` on `--color-base-200` (L 98%) is well under 3:1. Mixing each token colour
toward `--color-base-content` (`color-mix(in oklab, var(--color-success) N%, var(--color-base-content))`)
darkens it in the light theme and lightens it in the dark theme, because base-content is the
theme's own text colour. The mix keeps FR-002 (every input is a theme colour) and SC-001 (no
literal).

## R5. Measuring contrast without a browser

The repository has no browser tests (onboarding: `browser_tests=no`). Contrast is a computation,
so it is tested as one: parse the two default themes' `--color-*` values from django-mvp's
installed stylesheet, resolve the package stylesheet's colour custom properties against them
(`var()` and `color-mix(in oklab, …)` are the only forms it uses), convert OKLab to sRGB, and
compute WCAG relative luminance and contrast.

- OKLCH → OKLab: `a = C·cos h`, `b = C·sin h`. OKLab → linear sRGB: Björn Ottosson's published
  matrices. Linear sRGB → WCAG luminance: `0.2126 R + 0.7152 G + 0.0722 B` on the linear values,
  clamped to [0, 1].
- `color-mix(in oklab, A p%, B)` of opaque colours is a linear interpolation of L, a and b
  (CSS Color 5 §2). The package never mixes toward `transparent`, so premultiplication never arises.
- Clamping out-of-gamut channels differs slightly from a browser's gamut mapping. The mixes the
  plan uses are between in-gamut theme colours, and each pair carries headroom above 4.5:1, so the
  difference cannot flip a result.

## R6. Anchors under the fixed top bar

django-mvp's header is sticky at the top of the viewport when `layout.navbar.sticky` is on
(`cotton/app/header/index.html`: `sticky z-10 top-0`). An element reached by its anchor is
scrolled to the viewport's top edge and lands under it. `scroll-margin-top` on the anchored
elements themselves (headings, glossary terms, and anything else with an `id` in the body) moves
it clear. The prototype used `5rem`, which Sam saw working. It sits on the content's own elements,
not on `html`, so the shell is untouched (FR-016).
