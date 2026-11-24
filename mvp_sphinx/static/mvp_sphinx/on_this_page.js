// On this page: the heading being read is marked as the reader scrolls, in the
// column beside the page and in the panel above it, and following a heading
// from the panel closes the panel. Ported from sphinx-daisyui's page-toc.js.
(() => {
  // A boosted page brings the script again. The listeners belong to the
  // window and the document, so they go on once, and each pass reads the lists
  // of the page that is showing.
  const root = document.documentElement;
  if (root.hasAttribute("data-mvp-sphinx-on-this-page")) return;
  root.setAttribute("data-mvp-sphinx-on-this-page", "");

  const READING_LINE = 120;

  document.addEventListener("click", (event) => {
    const link = event.target.closest('[data-mvp-sphinx-toc="panel"] a');
    if (link) link.closest("details").open = false;
  });

  const mark = () => {
    const links = Array.from(document.querySelectorAll('[data-mvp-sphinx-toc="column"] a'));
    const marked = Array.from(document.querySelectorAll("[data-mvp-sphinx-toc] a"));
    const headings = [];
    links.forEach((link) => {
      const href = link.getAttribute("href") || "";
      const id = decodeURIComponent(href.replace(/^#/, ""));
      const heading = id && document.getElementById(id);
      if (heading) headings.push({ heading, href });
    });
    let current = null;
    headings.forEach((entry) => {
      if (entry.heading.getBoundingClientRect().top < READING_LINE) current = entry;
    });
    // At the foot of the page the last heading is the one being read, even if it never reached the line.
    if (
      headings.length &&
      window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4
    ) {
      current = headings[headings.length - 1];
    }
    marked.forEach((link) => link.removeAttribute("aria-current"));
    document
      .querySelectorAll(".mvp-sphinx-toc-on-path")
      .forEach((item) => item.classList.remove("mvp-sphinx-toc-on-path"));
    if (!current) return;
    marked
      .filter((link) => link.getAttribute("href") === current.href)
      .forEach((link) => {
        link.setAttribute("aria-current", "location");
        for (let item = link.closest("li"); item; item = item.parentElement && item.parentElement.closest("li")) {
          item.classList.add("mvp-sphinx-toc-on-path");
        }
      });
  };

  window.addEventListener("scroll", () => window.requestAnimationFrame(mark), { passive: true });
  // The page settles its height once styles and fonts load, which can bring its foot into view.
  window.addEventListener("load", mark);
  window.addEventListener("resize", mark);
  document.addEventListener("htmx:afterSettle", mark);
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mark);
  } else {
    mark();
  }
})();
