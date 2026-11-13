// The sidebar's contents: a toggle opens an entry's pages in place, fetching
// them the first time, and the page being read is scrolled into the middle of
// the sidebar when the page loads and when the sidebar opens on a phone.
(() => {
  // The script comes with every sidebar the renderer draws, and a boosted page
  // brings it again. The listeners belong to the document, so they go on once.
  const root = document.documentElement;
  if (root.hasAttribute("data-mvp-sphinx-contents")) return;
  root.setAttribute("data-mvp-sphinx-contents", "");

  document.addEventListener("click", async (event) => {
    const toggle = event.target.closest("[data-mvp-sphinx-branch]");
    if (!toggle) return;
    event.preventDefault();
    const list = toggle.nextElementSibling;
    if (toggle.getAttribute("aria-expanded") === "true") {
      list.hidden = true;
      toggle.setAttribute("aria-expanded", "false");
      return;
    }
    if (!list.children.length) {
      toggle.setAttribute("aria-busy", "true");
      try {
        const response = await fetch(toggle.dataset.mvpSphinxBranch);
        if (!response.ok) return;
        list.innerHTML = await response.text();
      } finally {
        toggle.removeAttribute("aria-busy");
      }
    }
    list.hidden = false;
    toggle.setAttribute("aria-expanded", "true");
  });

  // The page being read sits in the middle of the box the sidebar scrolls in,
  // so a deep page isn't left below the fold.
  const showCurrent = () => {
    const current = document.querySelector(".mvp-sphinx-entry > [aria-current=page]");
    if (!current) return;
    let box = current.parentElement;
    while (box && box !== document.body) {
      const overflow = getComputedStyle(box).overflowY;
      const scrolls = overflow === "auto" || overflow === "scroll";
      if (scrolls && box.scrollHeight > box.clientHeight) break;
      box = box.parentElement;
    }
    if (!box || box === document.body) return;
    const offset = current.getBoundingClientRect().top - box.getBoundingClientRect().top;
    box.scrollTop += offset - box.clientHeight / 2 + current.offsetHeight / 2;
  };

  document.addEventListener("change", (event) => {
    if (event.target.matches(".drawer-toggle") && event.target.checked) {
      requestAnimationFrame(showCurrent);
    }
  });
  document.addEventListener("htmx:afterSettle", showCurrent);
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", showCurrent);
  } else {
    showCurrent();
  }
})();
