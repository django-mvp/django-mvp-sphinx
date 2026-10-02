# Progress — 008 Show working examples live next to their source code

## 2026-10-02T15:58:33Z · S3 plan

Did: the queue row read in-flight on this session's own claim. The build continues on pull request
#67 and its branch, merged with origin/main (ddcbfc1, which carries FS-009; one conflict in
`mvp_sphinx/views.py`, both sides kept; 678 passed). The specification was read against FS-009,
delivered since: no contradiction (research). Gates: spec shut and passed (Sam, 2026-10-02, commit
a76abb8), sketch shut and passed (Sam, 2026-10-02, commit e244c12), plan open, merge shut.
The earlier run's research had stopped for a decision on how a page shows without the shell. Sam
decided it in the session: an example's page is written without the shell (D11). The
specification's FR-008 and FR-009 were reworded with his approval. research.md completed (R1 to
R10), plan.md and tasks.md written: 3 stories, 8 tasks. Decisions D11 to D16 appended, and every
decision carries its ADR verdict.
Analyze: FR-001 to FR-018 and SC-001 to SC-005 each map to a task or, where only a browser can
show it (US1.4 and SC-002 inside the frame, US2.4, US2.6 and FR-016 at 320 pixels, the dark
theme), to the browser check at convergence (research R10). Every item under "What the prototype
faked" has a task or is kept on purpose (plan, table). No CRITICAL findings.
Next: design review.

## 2026-10-02T16:05:07Z · S3R design review

Did: one reviewer, three lenses, on plan.md, tasks.md and research.md at 8a4caee. Verdict approve:
no critical or high finding, one medium and four low, all verified. Each was applied as an edit to
the plan or the tasks and checked against the finding's own evidence (ledger, gates.design_review).
The reviewer confirmed by running them that a raw HTML node reaches a JSON build's page body, that
`mvp/base.html` draws the messages inside the `app` block, and that `uv run deptry .` fails today
on the prototype's docutils import.
Next: build US1.
