---
myst:
  html_meta:
    description: Every element a page of this guide can hold, in one place, as it looks on the site.
---

(kitchen-sink)=
# Kitchen sink

This page holds every element a page of the guide can be written with, each shown once
as it looks on the site. It is written in Markdown with MyST, the way most pages of a
project's guide are. Read it top to bottom to see how a page is laid out, or jump to an
element from the list on the right.

The text between the elements is ordinary prose on purpose. How a heading sits against the
paragraph under it, and how far a list stands from the text around it, matter as much as
how each element looks on its own.

## Text

A paragraph is the unit everything else is measured against. Lines are kept short enough
to read without losing your place, and paragraphs are separated by a gap rather than an
indent, the way people expect on the web.

Inline, text can be *emphasised*, **strong**, or ***both***. It can hold `inline code`, a
[link to another page](first-visit/signing-in), a [link off the site](https://www.sphinx-doc.org),
and a reference to a {ref}`labelled place <kitchen-sink-tables>`. Text can be
~~struck through~~, written H{sub}`2`O or E = mc{sup}`2`, and an abbreviation such as
{abbr}`MyST (Markedly Structured Text)` explains itself when you point at it. A term like
{term}`staff account` links to the glossary, and a footnote[^tone] sits as a small number.
Inline attributes give a span of text a class of its own: [highlighted words]{.mark}.

Interface text has roles of its own. Press {kbd}`Ctrl+K` to search, choose
{guilabel}`Save changes`, go to {menuselection}`Account --> Settings --> Sign-in`, open
{file}`demo/settings.py`, run {command}`uv sync`, or type {samp}`build_docs {name}`. A
substitution fills in a name set once for the whole guide: {{ product }}.

[^tone]: A footnote holds an aside that would break the sentence it belongs to. Its
    text is gathered at the foot of the page.

### A third-level heading

Headings step down in size and weight, and each sits closer to the text it introduces than
to the text above it, so a section reads as one block.

#### A fourth-level heading

Below the third level, a heading is mostly a label for a short run of text.

##### A fifth-level heading

Pages rarely need a fifth level.

###### A sixth-level heading

And almost never a sixth, but it still looks like a heading when they do.

## Lists

A bulleted list holds items in no particular order:

- A list item is usually one line.
- Items can hold more than one paragraph when they need to.

  This second paragraph belongs to the item above.
- Lists nest:
  - a second level, with a different marker
  - and its own spacing
    - down to a third level
- And they carry on afterwards.

A numbered list holds steps that happen in order:

1. Install the package.
2. Add it to the installed apps, after `mvp`.
3. Mount a documentation app:
   1. name its build directory
   2. name its source directory
4. Build the guide and open it.

A task list shows what is done and what is left:

- [x] Write the guide
- [x] Build it
- [ ] Ask someone new to read it

A list of loose items, each with a paragraph or more, spaces its items further apart:

- **Signing in.** You only need to sign in to read the staff guide. Everything else
  is open to everyone.

- **Finding your way.** The sidebar lists every page. The list on the right lists the
  headings on the page you are reading.

- **Searching.** The search box in the bar at the top finds pages and headings.

A definition list pairs terms with what they mean:

Build
: The files Sphinx writes from the guide's source, which the site reads.

Source
: The text files the guide is written in, in Markdown or reStructuredText.

  A definition can run to more than one paragraph.

Documentation app
: The part of the site that serves one guide, under one address.

A field list pairs short labels with values:

:Author: The documentation team
:Version: 0.8
:Status: Draft, waiting for review

```{eval-rst}
An option list documents command-line options:

-a            Build every guide.
-q, --quiet   Print nothing but errors.
--builder=NAME
              Build with the named builder instead of the default.
```

## Quotes

> A block quote sets someone else's words apart from the guide's own. It can run to
> more than one line, and to more than one paragraph.
>
> This is its second paragraph.

```{epigraph}
Documentation is a love letter that you write to your future self.

-- Damian Conway
```

```{pull-quote}
A pull quote repeats a line from the page to draw the eye to it.
```

```{highlights}
Highlights sum up the points of a section in a few lines.
```

```{eval-rst}
A line block keeps its line breaks, for an address or a verse:

| The Documentation Team
| 1 Example Street
| Exampletown
```

## Notices

A notice sets something apart from the text around it. Each kind has its own colour and
icon, so you can tell what it means before you read it.

```{note}
A note holds something worth knowing.
```

```{tip}
A tip holds a shortcut or a better way.
```

```{hint}
A hint looks like a tip, and means the same.
```

```{important}
An important notice asks you to read it before going on.
```

```{warning}
A warning says something can go wrong.
```

```{caution}
A caution looks like a warning, and means the same.
```

```{attention}
An attention notice looks like a warning too.
```

```{danger}
A danger is the strongest: it says something cannot be undone.
```

```{error}
An error looks like a danger.
```

:::{admonition} A notice with a title of its own
A titled notice names no kind, so it reads as information. It can hold anything a page
can: a second paragraph, a list, or code.

- a list inside a notice
- keeps the notice's spacing

```python
print("and code")
```
:::

:::{warning}
A notice can hold another, and each keeps its own meaning.

```{tip}
A tip inside a warning.
```
:::

```{seealso}
{doc}`first-visit/signing-in`, where the accounts are introduced.
```

```{todo}
A to-do notice marks something the authors still have to write.
```

When something changed, a version note says in which version:

```{versionadded} 0.1
A way to do something was added.
```

```{versionchanged} 0.2
How it is done changed.
```

```{deprecated} 0.3
Do it the other way instead.
```

```{versionremoved} 0.4
The old way is gone.
```

## Asides

```{topic} A topic
A topic is a self-contained block that stands apart from the flow of the page, such as
a summary at the start of a long section.
```

```{sidebar} A sidebar
A sidebar holds something related to the text beside it. On a narrow screen it sits
above the text instead.
```

The text beside a sidebar wraps around it, so a short aside does not interrupt the
reading. This paragraph is long enough to show how the text flows beside the sidebar and
then carries on under it once the sidebar ends. Keep a sidebar short: it is for a fact the
reader might want while reading this paragraph, not for a second thread of argument.

A second paragraph keeps flowing round the sidebar until the sidebar ends, and then the
text takes the full width again.

```{rubric} A rubric
```

A rubric is a heading that does not appear in the contents, for a short run of text such as
a list of notes.

---

A horizontal rule, above, marks a change of subject that does not need a heading.

## Code

Code sits in a block of its own, coloured by language:

```python
from mvp_sphinx.mounted import DocumentationApp

docs = DocumentationApp(
    build_dir=BASE_DIR / "docs" / "_build" / "json",
    source_dir=BASE_DIR / "docs",
)  # The guide is served at /docs/.
```

A block can carry a caption, line numbers, and lines picked out:

```{code-block} python
:caption: yourproject/urls.py
:linenos:
:emphasize-lines: 4,5

from django.urls import include, path
from yourproject.mounted import docs

urlpatterns = [
    path("docs/", include(docs.urls)),
]
```

A terminal session shows the prompt apart from what you type:

```console
$ uv run python manage.py build_docs
Building the guide in docs/ ...
build succeeded.
```

A long line scrolls inside its block rather than widening the page:

```text
https://example.com/docs/reference/who-sees-what-when-they-sign-in-and-why-the-sidebar-differs/#a-heading-far-down-the-page
```

A change to a file is shown as a diff:

```diff
 INSTALLED_APPS = [
     "mvp",
-    "old_docs",
+    "mvp_sphinx",
 ]
```

Interactive Python sessions keep their prompts:

```pycon
>>> from demo.links import page_address
>>> page_address("first-visit/signing-in")
'/docs/first-visit/signing-in/'
```

## Tables

(kitchen-sink-tables)=
A Markdown table, with its columns aligned:

| Account               | Can read the staff guide | Pages |
|:----------------------|:------------------------:|------:|
| `regular.user`        | No                       |    14 |
| `staff.user`          | Yes                      |    16 |
| `super.user`          | Yes                      |    16 |

A table with a caption, a header column and a header row:

```{list-table} Who can do what
:header-rows: 1
:stub-columns: 1

* - Reader
  - Read the guide
  - Read the staff guide
  - Search
* - Signed out
  - Yes
  - No
  - Yes
* - Signed in
  - Yes
  - No
  - Yes
* - Staff
  - Yes
  - Yes
  - Yes
```

A table read from a file of values:

```{csv-table} The demo accounts
:file: accounts.csv
:header-rows: 1
```

A table too wide for the page scrolls on its own, and the page stays put. On a phone, swipe it sideways:

| Setting | Default | Read by | Changed by | Since | Notes |
|---|---|---|---|---|---|
| `build_dir` | none | every page | the project | 0.1 | The JSON build the documentation app serves, written by `sphinx-build -b json`. |
| `source_dir` | none | `build_docs` | the project | 0.3 | The guide's source, which the management command builds when you ask it to. |
| `namespace` | `docs` | the address | the project | 0.2 | Names the app's addresses, so two guides can be mounted side by side. |

## Pictures

A picture scales down to fit the text, keeping its shape:

```{image} landscape.svg
:alt: Hills under a blue sky with a yellow sun
```

A figure keeps its caption with its picture:

```{figure} landscape.svg
:alt: Hills under a blue sky with a yellow sun
:width: 70%

A caption says what the picture shows.

A legend, under the caption, explains the picture in more detail when it needs it.
```

## Maths

Inline maths sits in the sentence: the area of a circle is $A = \pi r^2$, and a
fraction such as $\frac{1}{2}$ keeps to the line.

An equation on its own line is centred, and can carry a number to refer to:

$$
e^{i\pi} + 1 = 0
$$ (euler)

Equation {eq}`euler` is referred to by its number.

## Cards, tabs and dropdowns

These come from sphinx-design, which most MyST guides load alongside it.

:::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} Signing in
:link: first-visit/signing-in
:link-type: doc

How to sign in, and which accounts the demo site has.
:::

:::{grid-item-card} Finding your way
:link: first-visit/finding-your-way
:link-type: doc

The sidebar, the list of headings and the search.
:::

::::{grid-item-card}

:::{card-header}
A card with a header
:::

A card can have a header and a footer, separated from its body.

:::{card-footer}
A footer
:::
::::

:::{grid-item-card} A card with no link

A card that only holds text, for a short summary in a grid.
:::
:::::

::::{tab-set}

:::{tab-item} uv
```console
$ uv add django-mvp-sphinx
```
:::

:::{tab-item} pip
```console
$ pip install django-mvp-sphinx
```
:::

:::{tab-item} Poetry
```console
$ poetry add django-mvp-sphinx
```
:::

::::

:::{dropdown} A dropdown hides detail until you open it
It holds anything a page can, and stays closed until a reader asks for it.
:::

:::{dropdown} A dropdown that starts open
:open:

Open by default, so the reader sees it first and can close it.
:::

Badges label a word, and buttons lead somewhere:
{bdg-primary}`primary` {bdg-secondary}`secondary` {bdg-success}`success`
{bdg-info}`info` {bdg-warning}`warning` {bdg-danger}`danger` {bdg-light}`light`
{bdg-dark}`dark` {bdg-primary-line}`outlined`

```{button-ref} first-visit/signing-in
:ref-type: doc
:color: primary

Start with signing in
```
```{button-link} https://www.sphinx-doc.org
:color: secondary
:outline:

Sphinx's own documentation
```

## Reference entries

Reference entries document a module's functions and classes. These are written by hand;
the {doc}`reference/link-helpers` page has entries read from the code itself.

```{py:function} page_address(path: str, heading: str | None = None) -> str

Return the address of a page of the guide.

:param path: The page's place in the sidebar, such as `first-visit/signing-in`.
:param heading: The name of a heading on the page.
:returns: The address, ending in a slash.
:raises ValueError: The path is empty.
```

````{py:class} GuideLink(path: str, title: str)

A link to a page of the guide, with the title to show for it.

```{py:attribute} path
:type: str

The page's place in the sidebar.
```

```{py:method} address() -> str

Return the link's address.
```
````

## Columns

A short list can run in columns:

```{hlist}
:columns: 3

* Text
* Lists
* Quotes
* Notices
* Asides
* Code
* Tables
* Pictures
* Maths
```

## Footnotes and citations

A footnote can be numbered[^1] or named[^named].

[^1]: A numbered footnote.
[^named]: A named footnote is numbered too, in the order it appears.

```{eval-rst}
A citation points at a source listed at the foot of the section [Conway2005]_.

.. [Conway2005] Damian Conway, *Perl Best Practices*. O'Reilly, 2005.
```
