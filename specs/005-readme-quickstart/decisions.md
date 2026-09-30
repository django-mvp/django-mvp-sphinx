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

## D9. No spec-against-spec re-read, and what "not shipped yet" now covers (S3)

**Ambiguous:** The queue row's `delivered_since` is empty, so the pipeline skips the re-read. But
the spec was written before #9 (who can read the docs, FS-006) and #10 (search, FS-007) were built,
and US2's third scenario gives both as examples of features not yet shipped.

**Chosen:** Both have shipped and are on main, so the README describes them, and the public surface
lists what they added. The only feature in scope of FR-010 now is #11, the build command, which the
README does not mention.

**Why:** The spec's own clarification decides it: the list covers "what exists when this feature
merges", and each later feature documents itself. The examples in US2.3 were true when written. The
rule they illustrate is unchanged.

**ADR:** none — a reading of this feature's spec, nothing downstream inherits it.

## D10. Public means listed, and the Sphinx and Django hooks are internal (S3)

**Ambiguous:** SC-003 needs an exact list, and several module-level names (`NavigationWriter`,
`write_navigation`, `setup`, `MvpSphinxConfig`) are importable without being anything a host calls.

**Chosen:** The public surface section lists what a host project mounts, passes, subclasses,
overrides, adds to `conf.py` or may call from a view or template of its own (plan, *Public
surface*). The extension's hooks and the app config are internal. The section ends by saying that
anything unlisted is internal.

**Why:** A host never calls those four names. Sphinx and Django do. Listing them would make internal
plumbing part of the compatibility promise of Article XI.

**ADR:** none — the list itself is the record, and it lives in the README.

## D11. The quickstart's app module reads `settings.BASE_DIR` from `django.conf` (S3)

**Ambiguous:** The README's example imported `BASE_DIR` from `yourproject.settings`, and the demo
does the same.

**Chosen:** The quickstart imports `from django.conf import settings` and uses
`settings.BASE_DIR`. The demo keeps its own import.

**Why:** FR-002 asks for code that runs with only names and paths changed. A project whose settings
are split into a package (`settings/base.py`) has no `yourproject.settings.BASE_DIR` to import, but
every project has `django.conf.settings`.

**ADR:** none — an example's wording.

## D12. The starter component is removed, with its test class (S3)

**Ambiguous:** `mvp_sphinx/templates/cotton/mvp_sphinx/example.html` is the project template's
placeholder component. It is a public name that exists, so SC-003 either lists it or it goes.

**Chosen:** It goes, with `TestStarterComponent` and `EXAMPLE_TAG` in `tests/test_smoke.py` and the
demo overview's section that shows it. This is a declared edit of a pre-existing test, authorised for
T002 only. The CHANGELOG records the removal.

**Why:** The test class says "Delete this class along with the starter component it covers", and the
component says "Replace it with the first real component". Four real components now exist. Listing a
placeholder as supported surface would be the kind of accident the public surface list exists to
prevent. Version 0.0.1, nothing depends on it, no alias kept.

**ADR:** none — removing a template placeholder, no design content.

## D13. The demo guide is rewritten in the demo site's voice, and the prototype's text is not reused (S3)

**Ambiguous:** The demo guide already shows every state US3 names, but its prose describes the
package (the extension, the build). The prototype's guide describes an invented inventory site.

**Chosen:** Rewrite the pages as a user guide for the demo site as it exists: signing in with the
demo accounts, finding your way around, the staff guide, and a reference part. Every state keeps its
place (plan, *The demo's user guide*). The prototype gives shape and tone only.

**Why:** Spec decision 3: the demo guide is what a host project would write for its users, the
package's first audience. A guide about an inventory site that isn't there would read like filler,
and a guide about the package duplicates the README.

**ADR:** none — demo content, not distributed.

## D14. Two dispatches: US1 and US2 together, then US3 (S3)

**Ambiguous:** The pipeline dispatches one implementer per story.

**Chosen:** US1 and US2 go to one implementer, because both restructure the README and would
conflict in parallel. US3 goes to a second implementer after both are accepted. Each story is still
accepted on its own with `forge story-done`.

**Why:** FS-007 precedent (US2 and US3 in one dispatch). It saves one cold start on a file the two
stories share, and loses no separate acceptance.

**ADR:** none — run mechanics.

## D15. Design review: approved, seven findings carried into the plan (S3R)

**Ambiguous:** The design reviewer approved the plan with two medium and five low findings (none
critical or high), so nothing forces a re-plan.

**Chosen:** DR-001 (step 5's file is an installed app's `menus.py`), DR-002 (groups and pages
asserted on the processed menu tree, not on markup), DR-003 (the `render` fixture goes with the
starter component), DR-004 (build through `build_main` with step 3's arguments, not a subprocess),
DR-005 (no CHANGELOG *Removed* line for a component that was never released) and DR-006 (the
templates' blocks, class and context are listed) are applied to `plan.md` and `tasks.md`. DR-007 is
declined: it asks to narrow the list to `PageView` and `BodyRewriter.rewrite`, but the README on
main already invites a host to call `PageHeadings.from_toc`, `BodyRewriter.rewrite` and to
subclass `PageView`, and FS-002 and FS-007 named `DocumentationMenu`, `DocsBuild`, `SearchView`,
`DocsSearch` and `PageText` as new public names under Article XI. Narrowing now would withdraw what
earlier features promised. The reviewer's notes on one `BASE_DIR` idiom and the `-W` wording are
applied too.

**Why:** Each applied remedy is an edit to the plan, verified by the orchestrator against the
finding's evidence. The declined one would change the promise of shipped features, which is not
this feature's call.

**ADR:** none — review disposition local to this feature.

## D16. One word in a search test changes with the starter component's removal (S4, US2)

**Ambiguous:** `TestSearchResults.test_a_word_only_in_the_hosts_pages_lists_nothing` (FS-007) picks
the word "starter" because the demo overview carried it. D12 removes that section, so the test's
premise check fails. Editing it is outside the D12 authorisation, and the implementer stopped
there, as it should.

**Chosen:** Forge changes the word to "demonstration". It is on the overview page and in no page
of the search fixture, so the test asserts exactly what it asserted before. Nothing else changes.

**Why:** The test's subject is "a word only on the host's pages", not that word. A one-word change
with no design content does not justify a re-dispatch. It is recorded here as a declared edit of a
pre-existing test.

**ADR:** none — a fixture word in one test.
