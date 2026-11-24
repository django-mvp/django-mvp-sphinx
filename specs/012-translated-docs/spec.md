# Feature Specification: Serve documentation translated with Sphinx in the reader's Django language

**Feature Branch**: `012-translated-docs`

**Created**: 2026-11-24

**Status**: Draft

**Serves**: G1 · **Roadmap**: — · **Issue**: [#153](https://github.com/django-mvp/django-mvp-sphinx/issues/153)

**Input**: "A project that translates its Sphinx documentation with Sphinx's own tools (`locale_dirs`,
`sphinx-build -b gettext`, `sphinx-intl`) wants its readers to get the docs in the language Django
has already chosen for them, without configuring the package for it."

## Overview

A host project whose site is offered in several languages already lets Django choose each reader's
language: from the language cookie, a URL prefix or the browser's `Accept-Language`. Its
documentation app ignores that choice today. Every reader gets the one docs build, so a reader who
uses the site in German reads the documentation in English.

Sphinx already has a complete translation workflow. The author extracts the messages with
`sphinx-build -b gettext`, keeps one catalogue per language under `conf.py`'s `locale_dirs` with
`sphinx-intl`, and builds each language with `-D language=<code>`. What is missing is the step
between that workflow and the reader: building every language the site offers, and serving each
reader the one Django has chosen.

With this feature, the developer gives the documentation app one `build_dir`, exactly as for
untranslated documentation, and runs `build_docs`. The command finds the translations under
`conf.py`'s `locale_dirs`, builds the language the documentation is written in and every
translation whose language is in the project's `LANGUAGES`, each into a folder of `build_dir` named
for the language. The documentation app then serves each request from the folder for Django's
active language, and everything the reader sees follows it: the pages, the contents, the search, page
extracts, images and downloads. The package's own words around the page, such as "On this page",
are translated too, starting with German.

The package adds no setting of its own and no language switcher. The languages the documentation is
offered in are the project's `LANGUAGES`, and the reader's language is the one Django has already
chosen. Translating stays with the host project and Sphinx: the package never extracts messages,
keeps catalogues or translates anything (Constitution Article XII, as amended on 2026-11-23).

Documentation with no translations is built and served exactly as it is today.

This feature builds on the pages served by
[#4](https://github.com/django-mvp/django-mvp-sphinx/issues/4), the contents in the sidebar, the
search, page extracts and the `build_docs` management command. It leaves out:

- a documentation app whose `build_dir` is a function of the request: that function already chooses
  the build for each request, and `build_docs` does not build for it
- a language switcher of the package's own (django-mvp's language switcher and Django's
  `set_language` view already exist)
- running Sphinx's translation workflow (`gettext` builds, `sphinx-intl`, filling in catalogues)
- the navbar's fit at phone width in a language with long labels, which is
  [#154](https://github.com/django-mvp/django-mvp-sphinx/issues/154)

## Clarifications

### Session 2026-11-24

- Q: What counts as a translation of the documentation? → A: A `<locale_dir>/<code>/LC_MESSAGES`
  folder holding at least one `.po` catalogue, under any of `conf.py`'s `locale_dirs`, or under
  Sphinx's default `locales` when `conf.py` sets none. Catalogues for the language the documentation
  is written in are not a translation: that language is always built once, as the source.
  Integrated into FR-002 and FR-003.
- Q: Which language is the documentation written in? → A: The one `conf.py` sets as `language`, or
  English when it sets none, as Sphinx does. Integrated into FR-003 and FR-008.
- Q: What does a reader get when no build matches their language? → A: The first match of, in
  order: the exact language (`de-at`), its base language (`de`), the same two for `LANGUAGE_CODE`,
  then the build of the language the documentation is written in. A reader always gets a build, and
  never a missing page, because no build of the documentation is ever offered half-built. Integrated
  into FR-008 and User Story 2.
- Q: What happens to the build already in `build_dir` when the documentation gains or loses its
  translations? → A: `build_docs` clears the layout it no longer writes, so an old build never
  shadows the new one. Integrated into FR-005.
- Q: Does the language choice apply to a `build_dir` that is a function of the request? → A: No.
  That function already chooses the build for each request, and `build_docs` does not build for it.
  A project that serves a build per site and per language returns the right folder from its own
  function. Integrated into FR-011 and recorded under Assumptions.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer serves translated documentation in each reader's language (Priority: P1)

A developer has translated their Sphinx documentation with Sphinx's own tools and turned on Django's
language handling for the site. They keep the documentation app's one `build_dir`, run
`build_docs`, and the documentation app serves each reader the build for the language Django has
chosen for them. They configure nothing in the package to get there.

**Why this priority**: This is the feature. Without the per-language builds there is nothing for a
reader to be served.

**Independent Test**: Make a small Sphinx project with a German catalogue under `locales/`, mount
it as a documentation app with `LANGUAGES` holding English and German, run `build_docs`, and
request a page with German and then English as the active language.

**Acceptance Scenarios**:

1. **Given** documentation with a German translation and `LANGUAGES` holding English and German,
   **When** the developer runs `build_docs`, **Then** `build_dir` holds a build of the source
   language in a folder named for it and a German build in a folder named for German, and nothing
   built straight into `build_dir`.
2. **Given** documentation built in English and German, **When** a page is requested with German as
   Django's active language, **Then** it is served from the German build, and with English active,
   from the English build.
3. **Given** documentation with a translation whose language is not in `LANGUAGES`, **When** the
   developer runs `build_docs`, **Then** that translation is not built, and the command says so in
   one line naming the documentation app and the language.
4. **Given** a translation in Sphinx's form of a regional language (`pt_BR`) and `LANGUAGES` holding
   Django's form (`pt-br`), **When** the developer runs `build_docs`, **Then** that translation is
   built, and readers whose active language is `pt-br` are served from it.
5. **Given** a `conf.py` that sets no `locale_dirs`, **When** the developer runs `build_docs`,
   **Then** the translations under `locales/` beside `conf.py` are found.
6. **Given** a `conf.py` that sets `locale_dirs` to several folders, **When** the developer runs
   `build_docs`, **Then** the translations under each of them are found.
7. **Given** documentation with no translations, **When** the developer runs `build_docs`, **Then**
   the build is written straight into `build_dir` and served as it is today.
8. **Given** a `build_dir` holding a build from before the documentation was translated, **When**
   the developer runs `build_docs` on the translated documentation, **Then** readers are served the
   new language builds and no part of the old build remains in `build_dir`.
9. **Given** a `build_dir` holding language builds, **When** the documentation loses its
   translations and the developer runs `build_docs`, **Then** the new single build is served and no
   language folder remains in `build_dir`.
10. **Given** a `conf.py` that sets `language` to German and has an English translation, **When** the
    developer runs `build_docs`, **Then** German is built once as the source language and English as
    a translation.
11. **Given** catalogues for the language the documentation is written in, **When** the developer
    runs `build_docs`, **Then** that language is built once, and the catalogues are not counted as a
    translation.
12. **Given** two documentation apps, one translated and one not, **When** the developer runs
    `build_docs`, **Then** the translated one gets a build per language and the other one build,
    each served correctly.
13. **Given** readers in two languages requesting pages in turn, **When** the sidebar's contents are
    drawn, **Then** each language's contents are read from its build once and reused for later
    requests in that language, until that build changes.
14. **Given** a project that adds its own translation of one of the package's strings to its
    `LOCALE_PATHS`, **When** a reader in that language reads a page, **Then** the project's
    translation is shown.
15. **Given** language builds in `build_dir` and an environment where Sphinx is not installed,
    **When** a reader requests a page, **Then** it is served.

---

### User Story 2 - A reader reads the documentation in the language they use for the site (Priority: P1)

A reader uses the site in German, because they chose German with the site's language switcher, they
followed a German address, or their browser asks for German. They open the documentation and read
it in German: the page, the contents in the sidebar, the search and its results, the page extracts
in the site's info dialogs, and the package's own words around the page. Where a paragraph has not
been translated yet, it appears in the source language inside the German page. A reader whose
language the documentation has no translation for reads it in a language it has.

**Why this priority**: This is the result the developer's work in User Story 1 exists for. It is
what a person using the site sees, so it is a story of its own.

**Independent Test**: With documentation built in English and German, request each kind of page a
documentation app serves with German, Austrian German, Italian and no language preference, and
check which build each is served from.

**Acceptance Scenarios**:

1. **Given** documentation built in English and German, **When** a German reader opens a page,
   **Then** its title and body are the German build's, and so are the contents group captions and
   page titles in the sidebar.
2. **Given** a German reader, **When** they search the documentation, **Then** the search uses the
   German build's search data, so a German word finds the German pages holding its other forms,
   and German stopwords are ignored.
3. **Given** a view whose page info dialog holds a page extract, **When** a German reader opens the
   view, **Then** the extract is taken from the German build.
4. **Given** a page showing an image or linking to a download, **When** a German reader opens it,
   **Then** the image and the download are the German build's.
5. **Given** a link to a section of a page by its anchor, **When** a German reader follows it,
   **Then** it reaches the same section in the German page, because a section's anchor is the same
   in every language.
6. **Given** a page whose German catalogue leaves a paragraph untranslated, **When** a German
   reader opens it, **Then** that paragraph appears in the source language within the German page.
7. **Given** a reader whose active language is `de-at` and a German build, **When** they open a
   page, **Then** it is served from the German build.
8. **Given** a reader whose active language has no build, and a build of the language in
   `LANGUAGE_CODE`, **When** they open a page, **Then** it is served from the `LANGUAGE_CODE` build.
9. **Given** a reader whose active language has no build, and no build for `LANGUAGE_CODE` either,
   **When** they open a page, **Then** it is served from the build of the language the
   documentation is written in.
10. **Given** a German reader, **When** they open a page, **Then** the package's own words on the
    page and around it (the On this page heading, the link-to-this-heading label and the search's
    labels) are in German.
11. **Given** a reader who changes the site's language between two requests, **When** they open the
    next page, **Then** it is served from the build for the new language.

---

### Edge Cases

- A `build_dir` that does not exist yet, or holds neither a build nor any language folder, is
  served as a missing build is today.
- A folder in `build_dir` that holds no build is not a language build and is never served.
- A `locale_dirs` entry that names a folder that does not exist is passed over.
- A `<code>/LC_MESSAGES` folder holding no `.po` file is not a translation.
- `conf.py` that cannot be read, or sets `language` or `locale_dirs` to something other than a
  literal value, is treated as setting neither.
- With Django's translation turned off, the active language is `LANGUAGE_CODE`, and the fallback
  order applies to it as to any other.
- A project that leaves `LANGUAGES` unset has Django's default list, which holds every language
  Django knows, so every translation is built.
- A source document added in a rebuild appears in every language build, untranslated where its
  catalogue does not exist yet.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The package MUST NOT add a setting or a `DocumentationApp` argument for translated
  documentation. A developer MUST get the behaviour of this feature from `build_dir`, `source_dir`,
  Django's `LANGUAGES` and the Sphinx source alone. (US1)
- **FR-002**: `build_docs` MUST treat as a translation every `<locale_dir>/<code>/LC_MESSAGES`
  folder holding at least one `.po` file, under each folder `conf.py`'s `locale_dirs` names,
  relative to `source_dir`, or under `locales` when `conf.py` sets no `locale_dirs`. (US1)
- **FR-003**: For documentation with at least one translation, `build_docs` MUST build the language
  the documentation is written in and every translation whose language is in `LANGUAGES`, each
  into a folder of `build_dir` named for the language as Sphinx names it, with Sphinx's `language`
  set to that language. The source language MUST be built once, whether or not it has catalogues of
  its own. (US1)
- **FR-004**: `build_docs` MUST skip a translation whose language is not in `LANGUAGES`, and MUST
  report each documentation app's skipped languages in one line, unless run quietly. (US1)
- **FR-005**: For documentation with no translations, `build_docs` MUST build straight into
  `build_dir`, as before this feature. Once every build of the run has succeeded, `build_docs` MUST remove from `build_dir`
  whatever belongs to the layout it is not writing: a single build when it writes language folders,
  and the language folders when it writes a single build. A run in which a build fails MUST leave
  the layout that was being served as it was. (US1)
- **FR-006**: Languages MUST be matched between Sphinx's form and Django's form using Django's own
  conversion, so that Sphinx's `pt_BR` and Django's `pt-br` are the same language. (US1)
- **FR-007**: When `build_dir` holds a build of its own, the documentation app MUST serve it for
  every request. When it does not, the documentation app MUST serve each request from one of the
  language builds in its folders, chosen for Django's active language. The layout MUST be read from
  disk, and a change to it MUST be seen without restarting the site. (US1, US2)
- **FR-008**: The build for a request MUST be the first of: the active language's build, its base
  language's build, the build for `LANGUAGE_CODE`, the build for `LANGUAGE_CODE`'s base language,
  then the build of the language the documentation is written in. (US2)
- **FR-009**: Every part of a documentation app that reads a build MUST read the build chosen for
  the request: pages, files such as images and downloads, the contents in the sidebar, the search
  and its results, and page extracts. (US2)
- **FR-010**: The sidebar's contents MUST be cached for each build folder they are read from, so
  that requests alternating between languages reuse each language's cached contents. A change to a
  build MUST still be seen without restarting the site. This MUST hold for every form `build_dir`
  takes. (US1)
- **FR-011**: A `build_dir` that is a function of the request MUST keep serving whatever build the
  function returns, with no language choice made by the package. (US1)
- **FR-012**: Serving a translated documentation app MUST NOT import Sphinx or start a build.
  (US1)
- **FR-013**: The package's own user-facing strings MUST ship with a German translation, in a
  `locale/` directory within the package that a host project can compile and override in the usual
  Django way. (US1, US2)
- **FR-014**: The README MUST describe how to serve translated documentation: the Sphinx workflow
  it starts from, the layout `build_docs` writes, how a reader's build is chosen, and the fallback
  order. The CHANGELOG MUST record the feature. (US1)

### Key Entities

- **Language build**: one docs build of a documentation app in one language, in a folder of
  `build_dir` named for the language as Sphinx names it. A translated documentation app has one for
  its source language and one for each translation the project's `LANGUAGES` offers.
- **Translation**: the catalogues of one language under one of `conf.py`'s `locale_dirs`, which
  Sphinx uses to build that language.
- **Source language**: the language the documentation is written in, `conf.py`'s `language`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer whose documentation is translated with Sphinx's own tools serves it in
  each reader's language by changing nothing in the package's configuration: one `build_dir` and
  one `build_docs` run.
- **SC-002**: Every page, search, page extract, image and download a reader reaches in a
  documentation app comes from the build for their language, for every language the project offers
  and the documentation is translated into.
- **SC-003**: A reader whose language has no translation always gets a page, never a missing one,
  for every page the documentation holds.
- **SC-004**: A link to a section of a page by its anchor reaches the same section in every language
  build.
- **SC-005**: After any successful rebuild, `build_dir` holds only the layout the latest `build_docs`
  wrote. After a failed one, the layout that was served before it is still served.
- **SC-006**: Documentation with no translations builds and serves exactly as before: the existing
  tests pass unchanged.

## Assumptions

- The host project translates its documentation with Sphinx's own workflow, and runs it before
  `build_docs`. The package reads only the catalogues that workflow leaves under `locale_dirs`.
- The reader's language is whatever Django's active language is for the request. How the project
  sets it (`LocaleMiddleware` with a cookie, URL prefixes or `Accept-Language`) is the project's
  choice and needs nothing from the package.
- `source_dir` is set wherever the source language is needed to choose a build. Without it, the
  source language is taken to be English.
- A project serving a build per site and per language uses the function form of `build_dir` and
  returns the right folder itself.
- German is the first translation of the package's own strings because it is the language the
  demo's documentation is translated into. More languages are added as catalogues later, with no
  change to the feature.
