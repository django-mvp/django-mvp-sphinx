// Typeset only what Sphinx marked as maths, and leave the rest of the page alone:
// nothing outside those elements is scanned, the host project's shell included.
// The theme puts an equation's notation in a `math` element inside the equation's
// own, and one that holds another is skipped so the notation is set once.
window.MathJax = {
  startup: {
    elements: [".math:not(:has(.math))"],
  },
  options: {
    ignoreHtmlClass: "daisy-sphinx-content",
    processHtmlClass: "math",
  },
  // An unknown command shows in the theme's error colour, not MathJax's red.
  tex: {
    noundefined: { color: "var(--color-error)" },
  },
};
