# Goals

These are the standing directions django-mvp-sphinx works toward. Each one is a capability or
quality to steer by, not a task that gets ticked off. Whether any goal has been served well enough
is decided in the roadmap, the feature specs, and review, never by the goal itself.

This file carries no version numbers or release plan; that lives in the roadmap. For what the
package is, what it stays out of, and the principles that settle a close call, read the
*Scope & philosophy* section of the [README](README.md).

Importance is a tag on each goal, not a ranking:

- **Essential** — not worth adopting without it.
- **Expected** — a complete, dependable version is expected to have it.
- **Aspirational** — a genuine want whose absence never makes the package incomplete.

| ID | Goal | Importance | Status | Notes |
|----|------|------------|--------|-------|
| G1 | A project's Sphinx docs read as pages of its own site: its shell, its theme, its sidebar | Essential | | |
| G2 | Readers can reach every page from the sidebar and always see where they are | Essential | | |
| G3 | Adopting it takes a mount and one line in the Sphinx config, with no templates to write | Essential | | |
| G4 | What a user guide is written with renders properly in the host's theme: admonitions, code, tables, images, glossaries and cross-references | Expected | | |
| G5 | The project decides who may read its docs, public or signed-in | Expected | | |
| G6 | Readers can search the docs | Expected | | |
| G7 | The project can build its docs from the site's own management commands | Aspirational | | |
| G8 | A page can show a working example running live next to its source code | Aspirational | | |
| G9 | Developer docs look right too: API reference pages and maths render properly in the host's theme | Aspirational | | |

_Written 2026-09-29. Revise as the goals change._
