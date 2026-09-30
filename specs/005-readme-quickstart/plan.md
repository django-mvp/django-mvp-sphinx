# Implementation Plan: Get a project from install to a working docs page by following the README

**Branch**: `005-readme-quickstart` | **Date**: 2026-09-30 | **Spec**: [spec.md](spec.md) ·
**Research**: [research.md](research.md) · **Tasks**: [tasks.md](tasks.md)

## Summary

Everything this feature describes is already built and on main (FS-001 to FS-004, FS-006,
FS-007). What is missing is the path through it. The README documents each feature in the order
the features landed, puts the Sphinx configuration line after the mount, and still carries the
template's empty `Quickstart` and `Public surface` sections. This feature reorganises the README
around a five-step quickstart (install, the Sphinx line, build, mount, menu entry). It fills the
public surface section with every name a host project can use, and removes the template's starter
component, which is the one public name nothing should use. It also rewrites the demo's guide as
a user guide for the demo site, keeping every state the earlier features draw reachable from the
sidebar. The package's code does not change, apart from removing that starter component.

Two tests prove the path. `tests/test_quickstart.py` follows the quickstart's steps against a
small Sphinx source of its own: it writes the configuration line, runs the build command, mounts a
`DocumentationApp` at a prefix of its own choosing and adds its menu entry, then reads the site the
way a person would. A new class in `tests/test_demo.py` builds the demo's guide and walks it from
the sidebar, finding every state US3 names by structure, never by wording.

The prototype on django-mvp's `wip/sphinx-docs-in-sidebar` branch contributes the demo guide's
shape (contents groups, a nested branch, a long title). Its design notes contribute nothing new:
every decision in them already shipped with FS-001 to FS-004.

## Technical Context

**Language/Version**: Python 3.12+, Django 5.2 / 6.0 / 6.1

**Primary Dependencies**: unchanged. django-mvp 0.25.0 (`mount`, `AppMenu`), django-flex-menus
(discovers each installed app's `menus` module, research R2), Sphinx ≥ 8.1 in the dev group only.

**Storage**: none.

**Testing**: pytest + pytest-django. Real `sphinx-build -b json` builds into `tmp_path`, pages
requested through `client`, markup read with BeautifulSoup by landmark, role, `href` and the
element structure Sphinx writes.

**Constraints**: FR-010 (nothing unshipped described as available; #11, the build command, is the
one unshipped feature the README could be tempted to describe). Article VI (absolute links, humanized
public markdown). Sam's code standards for every brief: no leading-underscore names; line length 88;
no compatibility aliases; no test of text content or of design preferences; Cotton components, never
Cotton's template tags.

**Scale/Scope**: README, the demo's guide sources, the demo's overview template, two test modules and `tests/conftest.py`,
one package template and its test class removed.

## Constitution Check

| Article | How the plan meets it |
|---|---|
| I Testing | The quickstart and the demo's states are acceptance tests through `client` on real builds. README prose is not tested (testing standard: no assertion on wording). Its accuracy is checked by the reviewer's documentation pass and by the orchestrator at each story's acceptance. |
| II Simplicity | No new code. One starter template removed. |
| IV Integration-first | Both new test classes drive the site as a reader does: follow links from the sidebar and the menu, never call the view directly. |
| VI Documentation | This feature *is* Article VI's README. Links absolute (FR-014). CHANGELOG *Added* entry for the quickstart and public surface list. |
| XI Compatibility | `mvp_sphinx.example` (the starter component) is removed. It was never documented as public and was a template placeholder whose own test said to delete it with its first real sibling. It was never released (no tag, no release), so the CHANGELOG records nothing about it (DR-005). No alias is kept. |
| XII Scope | Unchanged: the README describes serving a build and never building one. |

## The README

Final section order (headings may be reworded; order and content may not):

1. Title, one-line description, **Scope & philosophy** (unchanged).
2. **Quickstart**, which replaces today's *Installation* and the opening of *Usage*:
   - *Before you start*: a django-mvp project whose shell already works (link to django-mvp), and a
     Sphinx source directory for the user guide, `docs/` in the examples. No source directory yet:
     Sphinx's own `sphinx-quickstart` creates one (absolute link to Sphinx's documentation for it,
     FR-007). One sentence, not a Sphinx tutorial.
   - Five numbered steps, each a complete code block (FR-001, FR-002):
     1. **Install**: `pip install django-mvp-sphinx`, and `"mvp_sphinx"` after `"mvp"` in
        `INSTALLED_APPS`.
     2. **The Sphinx line**: `extensions = ["mvp_sphinx.navigation"]` in `docs/conf.py`, with what
        it is for: it writes the contents the sidebar shows, and without it the sidebar holds only
        the front page's entry (FR-006, edge case "skips the line"). A project that already lists
        extensions adds this one to its list.
     3. **Build**: `sphinx-build -b json docs docs/_build/json`. Sphinx is needed only where this
        runs, and serving never builds and never imports Sphinx (FR-004). The build comes before the
        mount. Until the build exists, every address under the prefix answers 404, and the rest of
        the site is unaffected (edge case "mounts before building"). The output folder is the
        project's choice: a CI step or a folder outside the project works the same (edge case).
     4. **Mount**: a module creating the `DocumentationApp` with `build_dir`, and the `mount()` line
        in the project's `urls.py`, at the prefix the project chooses.
     5. **Menu entry**: `AppMenu.append(docs.menu_item())` in the `menus.py` of one of the
        project's installed apps. django-flex-menus imports that module when Django starts (R2),
        which is why it has to live in an installed app. The snippet's file label is an installed app's module (`yourapp/menus.py`), never `yourproject/menus.py` (DR-001).
   - What the reader now has: the front page at `/docs/` in the shell, the contents in the app sidebar,
     the menu entry, and no template written (FR-003).
   - *Changing the docs*: run step 3 again and reload; pages, contents and search follow with no
     restart (FR-005).
   Every path in the code is the project's own (`BASE_DIR / "docs" / "_build" / "json"`), so the only
   things to change are names and paths (FR-002). The module holding the app imports `settings` from
   `django.conf` rather than the project's settings module, so the code runs whatever the project
   calls its settings.
3. **Using it**: today's *Usage* subsections, kept, reordered to follow the quickstart: the contents
   in the sidebar (minus the configuration line, now in step 2), the page's own headings and the
   previous and next links, search, naming the documentation, choosing who can read it, several
   documentation apps, addresses and files served, how pages look and overriding the page template.
   Wording is edited only where the move demands it. Nothing FS-001 to FS-007 documented is dropped.
4. **Public surface** (FR-008, FR-009): see below.
5. **Contributing**, with **The demo** (FR-013): `uv sync`, `migrate`, `seed_demo`, then the two
   build commands the quickstart's step 3 teaches (the guide and the staff guide), then
   `runserver`, then what to open, and the three accounts with their password. The build comes before
   the server, and it is the same command as step 3.
6. **License**.

The template's HTML comments in *Quickstart* and *Public surface* go. Every link is absolute
(FR-014). Any relative link today becomes a `https://github.com/django-mvp/django-mvp-sphinx/blob/main/…` URL.
The build command (#11) is not mentioned. The README's *Scope & philosophy* already says "a command
that runs the build for you may come later", which is a statement of scope, not a claim that it
ships, and stays (FR-010).

## Public surface

One section, grouped the way a host project meets the names. Each entry is the name as code
and one sentence on what it does. It ends by saying that anything not listed is internal and may
change. The list, read from the package on origin/main at f8d30be (research R1):

- **Installed app**: `mvp_sphinx`.
- **Sphinx extension**: `mvp_sphinx.navigation` (writes `navigation.json` into a JSON build).
- **The documentation app**: `mvp_sphinx.mounted.DocumentationApp`, its keyword options
  `build_dir`, `name`, `icon`, `namespace`, `view_class`, `check`, and `menu_item()` (inherited from
  django-mvp's `MountedApp`). Its URL names, `<namespace>:front_page`, `<namespace>:page` (takes
  `path`) and `<namespace>:search`.
- **Views**: `mvp_sphinx.views.PageView` (subclass and pass as `view_class`),
  `mvp_sphinx.views.SearchView`.
- **Building blocks a custom view or template may use**: `mvp_sphinx.docs_build.DocsBuild`,
  `mvp_sphinx.menus.DocumentationMenu`, `mvp_sphinx.headings.PageHeadings` (`from_toc`),
  `mvp_sphinx.page_body.BodyRewriter` (`rewrite`), `mvp_sphinx.search.DocsSearch`,
  `mvp_sphinx.search.PageText`.
- **Templates a project may override**: `mvp_sphinx/page.html`, `mvp_sphinx/search.html`, and the
  context each receives, as the README already describes it for `page.html` (`body`, `headings`,
  `previous_page`, `next_page`; the `styles` and `content` blocks; the `mvp-sphinx-content` class)
  and `search.html`'s context as the view supplies it (DR-006).
- **Components**: `mvp_sphinx.on_this_page`, `mvp_sphinx.heading_list`, `mvp_sphinx.page_links`,
  `mvp_sphinx.search_form`, each with its attributes as its own `@prop` annotations state them.
- **Static file**: `mvp_sphinx/content.css`.
- **Settings**: none. Say so.

`NavigationWriter`, `write_navigation` and `setup` in `mvp_sphinx.navigation` are Sphinx's to
call, and `MvpSphinxConfig` is Django's. They are internal and not listed. The implementer checks
each entry against the source as the story is built (FR-009): every listed name imports, every
option exists, every component's attributes match its `@prop` lines. A name found public and not in
this list is added, and reported.

**The starter component goes.** `mvp_sphinx/templates/cotton/mvp_sphinx/example.html` is the
cookiecutter's placeholder. Its test class says "Delete this class along with the starter
component it covers", and the demo's overview page shows it under "The starter component". Listing
it as public surface would advertise a placeholder. Leaving it unlisted would break SC-003, since it
is a public name that exists. So the template, `TestStarterComponent` and `EXAMPLE_TAG` in
`tests/test_smoke.py`, the `render` fixture in `tests/conftest.py` that only it uses (DR-003), and the overview page's section that uses it are removed. That is a
declared edit of a pre-existing test, authorised here and recorded as D12. `TestPackagedApp` stays.

## The demo's user guide

`demo/docs/` is rewritten as a user guide **for the demo site**, written for the people using it
(D3 of the spec's decisions). It covers signing in with the demo's accounts, finding your way
around (the menu, the sidebar, breadcrumbs, the search box, the light and dark themes), what the
staff guide is and who can open it, and a reference part. It does not explain Sphinx, the
extension, the documentation app or this package: those belong to the README. The prototype's
`demo/sphinx_docs/` (django-mvp, branch `wip/sphinx-docs-in-sidebar`) is a model for tone and shape,
not text to copy. It documents an invented inventory site, and this guide documents the demo that
exists.

Every state US3 names stays reachable from the sidebar (FR-012). The content that shows each state
is moved into pages where it reads naturally in a user guide, rather than kept on a page about the
guide's own styling:

| State (US3) | Where it lives |
|---|---|
| Two or more captioned contents groups | Front page toctrees, e.g. "Using the site" and "Reference" |
| A page at the top level, in no group | An uncaptioned toctree (e.g. "About this site") |
| A page with pages of its own | A section index with at least two child pages (e.g. "Your first visit" with "Signing in" and "Finding your way") |
| A long page with several headings under "On this page", nested at least two levels | One reference page long enough to scroll |
| Previous and next links | Follow from the toctree order; first page has no previous, last has no next |
| Each admonition kind (note, tip, hint, important, warning, caution, attention, danger, error), a generic titled admonition, `seealso`, a nested admonition | Where each belongs in the guide's text. A "how this guide marks notices" reference page may hold the ones that do not arise naturally. |
| Version notes (`versionadded`, `versionchanged`, `deprecated`) | A reference page, as today's content tour has them |
| Highlighted code in several languages, a captioned block with line numbers, a plain-text block, a long line | A reference page (e.g. copying a link, a keyboard reference, an export format) |
| A table wider than the page, a table inside a list item | The accounts table (email, password, role, what each can open, and so on) is naturally wide |
| An image, an image wider than the page, a figure with a caption | `shell.png`, as today |
| A download | `:download:` of a file in the guide's sources (today's `notes.txt` or a replacement) |
| A glossary and `:term:` references to it | A glossary page |
| Cross-references between pages | `:doc:` and `:ref:` links in running text |
| A long page title | One page with a long title (prototype precedent), to see the heading and sidebar entry wrap |

The page for missing addresses (US3.4) needs no source: any address under `/docs/` with no page
behind it already answers the site's 404 (FS-001).

`demo/staff_guide/` stays as FS-006 left it, apart from wording that describes the package rather
than the site. The build stays gitignored (spec decision 4).

## Fixtures and tests

- **`tests/sphinx/quickstart/`**: a new, deliberately small Sphinx source: `conf.py` holding only
  `project` and the step-2 line, an `index.rst` with one captioned toctree of two pages. It is the
  "small Sphinx source directory" of US1's independent test. The existing sources are shaped for
  other features, so none is reused.
- **`tests/test_quickstart.py`**: `TestQuickstart`. The fixture copies the source to `tmp_path`
  and runs the build with step 3's arguments through `sphinx.cmd.build.build_main(["-b", "json", "-W",
  src, out])`, as `conftest.py` does (DR-004); `-W` is added so the test build must be clean. It creates a `DocumentationApp` with a `namespace` of its own
  and mounts it in a test urlconf at a prefix that is not `docs/`, the address "they chose"
  (`override_settings(ROOT_URLCONF=...)`). The menu entry is appended to `AppMenu` and removed again
  in teardown, since `AppMenu` is global. Tests:
  - the front page answers 200 at the chosen prefix, inside the shell (US1.1);
  - the app's processed menu tree holds the source's contents group and both pages, and each of
    their URLs answers 200 (US1.1, DR-002);
  - a host page's menu holds the app's entry, and its `href` is the front page (US1.2);
  - adding a page to the source and its toctree, then running step 3 again into the same folder,
    serves the new page and lists it in the sidebar on the next request, same process (US1.5);
  - no template was written: the test's project has no template directory of its own for
    `mvp_sphinx`, so the assertion is that the app renders with the package's templates alone.
    This is a fixture property, not an extra test.
  Serving without Sphinx (US1.4) is already `TestServingWithoutSphinx` (FS-001). It is not
  repeated. The quickstart test cites it in `progress.md`.
- **`tests/test_demo.py`**: `TestDemoGuideStates`. A module-scoped build of `demo/docs` into a
  temporary folder, and the demo's `docs` app pointed at it with `monkeypatch` (the
  `staff_guide_app` pattern). One test walks every page the front page's sidebar links under `/docs/`
  and collects what it finds. Each state is one assertion or one small test over that walk, and all
  of them are found by structure:
  - ≥ 2 captioned groups and ≥ 1 collapsible branch in the sidebar (US3.2), asserted on the processed menu
    tree (`docs.menu.process(rf.get("/docs/"))`, as `tests/test_menus.py`'s `processed` fixture
    does); the pages to walk come from that tree's URLs (DR-002);
  - some page whose "On this page" landmark lists ≥ 3 links and a nested list (US3.2);
  - some page with a previous link and a next link (US3);
  - `div.admonition` elements carrying each of the classes `note tip hint important warning caution
    attention danger error seealso` and a generic `admonition-*` one (US3.3);
  - `div.highlight` blocks (US3.3), a table inside the scroll region `BodyRewriter` adds (US3.3);
  - an `img` whose `src` answers 200 with an image content type, and an `a.download` whose `href`
    answers 200 (US3.3);
  - a `dl.glossary` and an `a` with class `reference internal` that links another page of the guide
    (US3.3);
  - `/docs/no-such-page/` answers 404 (US3.4);
  - the demo's menu has the guide's entry, and following it gives the front page (US3.1). The
    existing `TestDocumentationEntry` covers the entry, so this only adds the follow.
  The build must finish with no warnings (`-W`), so a broken cross-reference fails the test.
- `tests/test_smoke.py`: `TestStarterComponent` and `EXAMPLE_TAG` removed, and the `render` fixture
  in `tests/conftest.py` with its now-unused imports (D12, DR-003).

No test reads the README.

## Story order

**US1 → US2 → US3**, sequential in the feature worktree `wt-sphinx-005`. US1 and US2 both
restructure the README and go in one dispatch. US3 goes in a second dispatch once US1 and US2 are
accepted, because its README section (*The demo*) follows the structure US1 sets.

## Risk

- The README move could lose a sentence an earlier feature wrote to satisfy its own spec. The US1
  brief requires a before and after check of every subsection, and the reviewer's documentation pass
  opens the README against the code.
- `AppMenu` is process-global. The quickstart test's teardown removes its entry, or later tests
  see an extra item.
- The demo guide rewrite must keep a clean `-W` build. The staff guide is untouched.
