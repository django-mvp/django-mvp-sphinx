// A contents list in a page: each toggle opens and closes the pages under its entry.
document.addEventListener("click", (event) => {
  const toggle = event.target.closest(".toctree-wrapper .daisy-nav-toggle");
  if (!toggle) return;
  toggle.setAttribute(
    "aria-expanded",
    String(toggle.getAttribute("aria-expanded") !== "true"),
  );
});
