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
