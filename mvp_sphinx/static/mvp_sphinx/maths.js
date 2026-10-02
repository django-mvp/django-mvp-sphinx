// Typeset only what Sphinx marked as maths, and leave the rest of the page alone:
// nothing outside those elements is scanned, the host project's shell included.
window.MathJax = {
  startup: {
    elements: [".math"],
  },
  options: {
    ignoreHtmlClass: "mvp-sphinx-content",
    processHtmlClass: "math",
  },
  // An unknown command shows in the theme's error colour, not MathJax's red.
  tex: {
    noundefined: { color: "var(--mvp-sphinx-code-error)" },
  },
};
