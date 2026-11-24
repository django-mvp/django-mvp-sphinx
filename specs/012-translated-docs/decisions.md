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
