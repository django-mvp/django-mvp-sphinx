# Tasks — 005 Get a project from install to a working docs page by following the README

**Branch**: `005-readme-quickstart` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I where it has behaviour to test. A task
is done when its tests pass, the tree is green, and the work is committed. No test asserts wording,
CSS classes of the design, widths or placement (testing standard). No test reads the README.
Elements are found by landmark, role, accessible name, `href`, and the element structure Sphinx
writes (`div.admonition.note`, `dl.glossary`, `a.download`).

Code standards for every task: no leading-underscore names anywhere (functions, methods, helpers,
constants, templates, fixtures); line length 88; no compatibility aliases; Cotton components written
as `<c-…>` components, never through Cotton's template tags. README, CHANGELOG and the demo guide are
public text: humanize them (`kit/checklists/public-md.md`) and keep every link absolute.

## Order

**(US1 + US2) → US3**, sequential, in the feature worktree `wt-sphinx-005` (plan, *Story order*).

---

## US1 — Follow the quickstart to a working documentation page (P1)

Issue: #26. Delivers FR-001 – FR-007, FR-014; SC-001, SC-002.

### T001 — The quickstart, proven by following it

**Files**: `tests/sphinx/quickstart/**`, `tests/test_quickstart.py`, `tests/urls_quickstart.py`
(or a urlconf built inside the test module), `README.md`

Plan, *The README* (items 1–3) and *Fixtures and tests* (`tests/sphinx/quickstart/`,
`TestQuickstart`). Red first: `TestQuickstart` against the new source. Its build runs the step-3
command as a subprocess (`sphinx-build -b json <src> <out>`, `-W`), the app is mounted at a prefix
other than `docs/` under a namespace of its own, and the menu entry is appended to `AppMenu` and
removed in teardown. Tests: front page 200 in the shell at the chosen prefix (US1.1); the sidebar
lists the group and both pages, each link answering 200 (US1.1); a host page's menu entry leads to
the front page (US1.2); edit the source (add a page to the toctree), rerun the build into the same
folder, and the new page is served and in the sidebar on the next request (US1.5). US1.4 is
`TestServingWithoutSphinx`, already on main: cite it, do not repeat it.

Then the README: write *Quickstart* (before-you-start, five numbered steps, what you now have,
changing the docs) and move today's *Installation* and *Usage* content into it and into *Using it*,
exactly per the plan. The code in the five steps is the code the test runs, with the project's own
names in place of the test's. Before you finish, list every subsection heading and every
fact-bearing paragraph of the README on origin/main and confirm each one is still in the README,
moved or kept. Report the list in `progress.md`. Nothing FS-001 to FS-007 documented may be dropped.
Remove the template comment in *Quickstart*. Every link absolute (FR-014). Do not mention a build
management command anywhere (FR-010).

---

## US2 — See everything a project can use, in one list (P2)

Issue: #29. Delivers FR-008 – FR-010, FR-014; SC-003.

### T002 — The public surface section, and the starter component removed

**Files**: `README.md`, `CHANGELOG.md`, `mvp_sphinx/templates/cotton/mvp_sphinx/example.html`
(deleted), `tests/test_smoke.py`, `demo/templates/demo/overview.html`, `tests/test_demo.py` (only
if an overview test names the starter's section)

Plan, *Public surface*. Delete `example.html`. Remove `TestStarterComponent` and `EXAMPLE_TAG` from
`tests/test_smoke.py`: this is a declared edit of a pre-existing test, authorised by D12, and the
only one this story may make. Remove the overview page's "The starter component" section. Keep the
page valid, and use Cotton components only. Run the suite scope that covers smoke and demo.

Write *Public surface*, replacing its template comment. For every entry, check it against the source
before you write it: the import resolves, each `DocumentationApp` option is an attribute or `__init__`
keyword, each URL name reverses, each component's attributes are the ones its `@prop` lines declare,
each template exists. Record the check (command or read, per entry) in `progress.md`. A public name
you find that the plan's list lacks is added, and raised in `concerns`. End the section with the
sentence that anything unlisted is internal. State that there are no settings.

CHANGELOG, Unreleased: *Added* — the README quickstart and public surface list; *Removed* — the
starter component `mvp_sphinx.example`.

---

## US3 — See every state in the demo (P3)

Issue: #32. Delivers FR-011 – FR-013; SC-004.

### T003 — The demo's states, tested from the sidebar

**Files**: `tests/test_demo.py`, `tests/conftest.py`

Plan, *Fixtures and tests* (`TestDemoGuideStates`). Red first, against the demo guide **as it will
be**: write the tests before rewriting the guide. Those that pass on today's guide are recorded as
passing at red, which is acceptable here (FS-002 T005 precedent). Build `demo/docs` with `-W` into a
temporary folder and point `demo.mounted.docs` at it with `monkeypatch`. Walk every `/docs/` page
the front page's sidebar links. Assert each state in the plan's list by structure. Also assert that
`/docs/no-such-page/` answers 404 and that following the demo's menu entry for the guide lands on
its front page. Do not assert any page's wording or title text.

### T004 — The demo's user guide, rewritten for the demo site

**Files**: `demo/docs/**`, `demo/staff_guide/*.rst` (wording only), `README.md` (*Contributing* →
*The demo*), `AGENTS.md` (*The demo project*, only where it now disagrees)

Plan, *The demo's user guide*. Rewrite the guide's pages as a user guide for the demo site, placing
every state in the plan's table. Keep `shell.png` and a downloadable file. Keep the build clean
under `-W`. T003's tests go green. The README's demo instructions: `uv sync`, `migrate`,
`seed_demo`, the two `sphinx-build -b json` commands (the same command as quickstart step 3), then
`runserver`, then what to open (`/docs/`, `/staff-guide/`) and the three
accounts with the password `password`.
