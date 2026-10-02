# Planning notes: FS-008 Show working examples live next to their source code

Constraints the maintainer set when he reviewed the prototype on 2026-10-02. The research for the
build answers each one by name.

## Host base template

"I don't really understand what you mean by 'the host's base.html extend a new package template'.
Why? MVP project's are supposed to extend mvp/base.html."

A host project's `base.html` keeps extending `mvp/base.html`. The build must not ask a host to
extend a template of this package. The prototype's `mvp_sphinx/base.html` is therefore not the
answer, and research has to find another means of showing a page of the site without the
application shell around it. If the right home for that is django-mvp itself, research says so and
stops for a decision. It is not to be worked around in this package.

## Frame setting

"X_FRAME settings is fine as long as we document it."

`X_FRAME_OPTIONS = "SAMEORIGIN"` is accepted as a setup step for a host project that uses live
examples. The README has to document it.

## Frame height

"We can talk about frame height later if we need to."

The frame keeps one fixed height for now, and a taller example scrolls inside it. Growing to fit
the example is not part of this build.
