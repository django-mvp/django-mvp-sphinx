// Ctrl+K, or Cmd+K on a Mac, opens the search dialog through the first search
// toggle on the page, so the dialog opens the same way a click opens it.
(() => {
  const isMac = /Mac|iPhone|iPad/.test(navigator.platform);
  if (isMac) {
    for (const key of document.querySelectorAll("[data-mvp-sphinx-modifier]")) {
      key.textContent = "⌘";
    }
  }
  document.addEventListener("keydown", (event) => {
    const modifier = isMac ? event.metaKey : event.ctrlKey;
    if (!modifier || event.key.toLowerCase() !== "k") return;
    const toggle = document.querySelector("[data-mvp-sphinx-search]");
    if (!toggle) return;
    event.preventDefault();
    toggle.click();
  });
})();
