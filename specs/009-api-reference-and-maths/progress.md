# Progress — 009 Make API reference pages and maths look like the rest of the site

## 2026-10-02T09:16:07Z · S3 plan

Did: the queue row read in-flight on this session's own claim, taken when the prototype was
approved; the build continues on pull request #66 and its branch, already level with origin/main
(7cc536c). `delivered_since` is empty, so the spec-against-spec check is skipped. Gates: spec
shut and passed (Sam, 2026-10-02, commit 8b0e846), sketch shut and passed (Sam, 2026-10-02, commit
09994ec), plan open, merge shut. Research read from Sphinx 9.1.0, a real JSON build of the demo
guide, and the prototype in a browser with MathJax 4.1.3. plan.md, research.md, tasks.md: 5
stories, 7 tasks. Decisions D12–D17 appended.
Analyze: FR-001–FR-022 and SC-001–SC-007 each map to a task or, where only a browser can show it
(SC-003 typeset output, SC-004 at 320 pixels, FR-013, FR-017), to the browser check at
convergence (research R9). Every item under "What the prototype faked" has a task except the
`?typeset=off` switch, which T004 removes, and `demo/links.py`, which stays a demo fixture and
is documented in T002. No CRITICAL findings.
Next: design review.

## 2026-10-02T09:30:07Z · Implementer US1 · T001

Did: wrote the whole fixture source `tests/sphinx/reference/` (conf.py, index.rst, api.rst, maths.rst, plain.rst) and the `reference_build` and `reference_app` fixtures in `tests/conftest.py`. api.rst opens with `.. py:module:: demo.links`, so its entries carry the same ids and a `sig-prename` as the autodoc'd ones in the demo guide. Added `TestSphinxHooks` and `TestReferenceStylesheet` to `tests/test_static/test_content_css.py`.
Verified: `uv run pytest tests/test_static/test_content_css.py -q -p no:warnings` → 39 passed (24 new). The fixture builds with no warnings. Every new test passed on its first run: they pin what the approved prototype already does. Each was then shown able to fail, by breaking one thing and restoring it: renaming `.default_value` in the stylesheet failed the selector test; pointing the `.sig-return-icon` rule and the `dl.field-list > dt` rule at `--color-base-200` / `--color-base-100` failed the contrast tests in both themes; removing the `py:module` line failed the `sig-prename` and same-classes tests; renaming the `dt.sig-object em` selector failed the tag test. Not mutated: the `js:function` test, the demo guide hook tests and the `em` test. They are plain presence checks on the build output.
Next: T002.
Watch: `sig-param` is not a selector in the stylesheet. The approved rule is `dt.sig-object em`, so the hooks test ties it by tag instead (D19).

## 2026-10-02T09:32:38Z · Implementer US1 · T002

Did: added six tests to `TestDemoGuideStates` in `tests/test_demo.py`, on the link-helpers page of the demo guide build, found by entry id and class hook: a function entry with a field list; a class entry whose description holds entries; a class nested in it holding an entry (three levels); an entry with an empty description; an entry holding a deprecation; the page links the package stylesheet and none from the build. Wrote the README paragraph under "How pages look and the page template", a CHANGELOG entry under Unreleased/Added, "Reference entry" and "Signature" in CONTEXT.md, and the AGENTS.md note on `demo/links.py`. Nothing under `docs/` (ROADMAP, adr, agents) describes this behaviour, so no page there changed.
Verified: `uv run pytest tests/test_demo.py -q -p no:warnings -k TestDemoGuideStates` → 21 passed (6 new), exit 0. All six passed on their first run: they pin states the approved prototype's demo pages already hold. Each was then shown able to fail, by breaking one thing and restoring it: a docstring on `strip_heading` failed the empty-description test; removing the `deprecated` directive failed the deprecation test; removing `:members:` from the `autoclass` failed the class and nested-class tests; removing `page_address`'s `Args` section failed the field-list test; pointing the template's stylesheet link elsewhere failed the stylesheet test.
Next: T003.
Watch: none.
