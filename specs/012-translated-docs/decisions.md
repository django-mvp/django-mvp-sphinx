# Decisions: Serve documentation translated with Sphinx in the reader's Django language

Rationale too long to sit in the spec, and the choices made while specifying it. The feature was
specified from an approved prototype, so its behaviour and the maintainer's decisions recorded on
the prototype were taken as agreed. Each decision below fills a place the issue and the prototype
left open.

## D1. One setting-free layout, chosen on disk

The maintainer decided on the prototype that a `build_dir` per language was too much configuration:
one `build_dir`, the languages are Django's `LANGUAGES`, and `build_docs` builds whichever of them
the documentation is translated into. The spec follows that. Serving tells the two layouts apart by
what is on disk: a `build_dir` holding a build of its own is served as it is, otherwise its
language folders are the builds. That needs no flag, and documentation that is never translated is
untouched.

**ADR:** none. Constitution Article XII, amended on 2026-11-23, already records the decision to
allow one build per language.

## D2. The function form of `build_dir` gets no language choice

A function of the request already chooses the build for each request, and `build_docs` refuses to
build for it. Adding a language choice on top would mean the package second-guessing the project's
own choice. A project that needs a build per site and per language returns the right folder from
its function. Kept as the prototype has it.

**ADR:** none. Local to this feature.

## D3. The source language's catalogues are not a translation

Sphinx lets an author keep catalogues for the source language, for corrections. Counting them as a
translation would build the source language twice. It is built once, as the source, as on the
prototype.

**ADR:** none.

## D4. The fallback order

The exact language, its base language, the same two for `LANGUAGE_CODE`, then the source language.
This is Django's own order for message catalogues with the source language added at the end, so a
reader is never left without a build. A missing translation of one page is not a case, because a
language build always holds every page (untranslated paragraphs stay in the source language).

**ADR:** none.

## D5. `build_docs` clears the layout it no longer writes

On the prototype an old single build in `build_dir` won over new language folders, and the
developer had to delete `build_dir` by hand. The issue asks that switching layouts leaves nothing
stale. The command removes only what belongs to the other layout: the single build's files when it
writes language folders, the language folders when it writes a single build. It never removes the
language folders it is about to rebuild, because Sphinx's incremental build reuses them.

**ADR:** none.

## D6. German first for the package's own strings

Article VIII asks for a `locale/` a host project can extend. The package ships English already. A
German catalogue is added because the demo's documentation is translated into German, so the demo
shows the whole page in one language. Other languages are catalogues added later.

**ADR:** none.

## D7. The issue is accepted without a grilling round

The maintainer handed the work over on 2026-11-24, with the prototype approved and its decisions
recorded. The interpretation in the spec's overview was written from the issue and `PROTOTYPE.md`
and treated as confirmed. Every place it fills a gap is one of the decisions above or a line under
the spec's Assumptions.

**ADR:** none.

## D8. The layout listing reads the disk on every call, in two small classes

The prototype listed a build directory's language folders through a class with a lock and a cache
keyed on the directory's modification time. A build that writes into a language folder does not
change the directory's modification time, so the cache could miss a language that is being built
for the first time. The documentation app already reads the build from disk on every request
(ADR 0001), and listing a handful of folders costs less than any of those reads. `languages.py`
holds two classes with no cache and no lock: `SphinxSource` (what `conf.py` says, and the
translations) and `LanguageBuilds` (a build directory's language folders and the choice among them).
Article X puts functions sharing a subject on a class, which the design review pointed out.

**ADR:** none. Local to this feature.

## D9. `build_docs` clears only what belongs to the layout it is not writing

When it writes language folders it removes the single build (every child of `build_dir`, when
`globalcontext.json` is in `build_dir`) and any language build folder that is not in the new set,
so a language dropped from `LANGUAGES` stops being served. When it writes a single build it
removes every language build folder. A `build_dir` holding neither is left as it is, so a
`build_dir` pointed at an unrelated folder loses nothing.

**ADR:** none. Local to this feature.

## D10. The build is made directly, not dispatched

Nine tasks in two stories, each small, each building on the one before it in the same few files.
A dispatch's brief and receipts would cost more than the tasks do. This session already runs on
the Sonnet tier the pipeline dispatches implementation to, so the cost tier the rule protects is
the one used. The design review and the code review are Opus dispatches as usual.

**ADR:** none.

## D11. `build_docs` clears the other layout before it builds, as FR-005 says

The design review noted that a build which fails after the clearing leaves the app with no build,
where clearing after the last build succeeds would keep the old one. FR-005 says "before building"
and the specification is approved, so the order stays and the window is recorded here and in the
README. Reported to the orchestrator as a possible change to the specification.

**ADR:** none.

## D12. Design review findings, how each was answered

- Verified high: Sphinx keeps the first language's catalogues for the life of a process, so the
  fixture's builds run in one process each, as `build_docs` runs them. Done in T002 and `conftest.py`.
- Verified high: Article X, two classes. Done, see D8.
- Medium: source-language catalogues alone leave the documentation untranslated, so it builds
  straight into `build_dir`. `SphinxSource.translations` leaves the source language out. Tested.
- Medium: one rule for a language folder on both sides, `LanguageBuilds.is_language_build`: it holds
  a build and is named for a language Django knows or the project offers. A build of something else
  beside the languages is neither served nor removed. Tested.
- Medium: the fallback steps are each tested with their own `LANGUAGE_CODE`. Done.
- Likely: the fixture's section title is translated and the section has no explicit label, so the
  anchor test proves the anchor does not follow the translation. The page with an untranslated
  paragraph holds a translated one too. Done.
- Low: a symlinked language folder is unlinked, not followed. Done. A `source_dir` inside `build_dir`
  is not guarded: a project that does that has pointed the build over its source and `build_docs`
  already fails on it.
- Low: a `None` language falls to `LANGUAGE_CODE`. Tested.
- Low: the German catalogue test also checks the message ids match the English catalogue, and
  `babel` joins the dev dependencies with it (Article VII). `tests/test_locale.py` joins the
  conformance list of tests that do not mirror a module.
- Low: the without-Sphinx test runs in a subprocess with Sphinx blocked, as the menu's does.
- Low: T008 adds the contents branch address and the site search kind.
- `build_for` ends at the first build when the source language has none, so a reader is served where
  `source_dir` is absent (SC-003). The command's builder is named `planned_builds`.

**ADR:** none.
