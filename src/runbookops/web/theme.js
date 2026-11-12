try {
  document.documentElement.dataset.theme =
    localStorage.getItem("runbookops-theme") || "dark";
} catch {
  /* Storage may be disabled. */
}
