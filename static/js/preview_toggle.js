// Global "show/hide all info boxes" toggle, sitting beside Reset All in
// the page-tab bar. Deliberately its own tiny file, mirroring
// page_tabs.js's own precedent for a single page-level UI concern that
// doesn't belong to any one view - and deliberately NOT given the
// "page-tab" class, since that would also wire it into page_tabs.js's
// generic view-switching click handler (the same reason Reset All's own
// button needed a dedicated persistence.js listener rather than relying
// on anything generic).
import { toggleAllPreviews } from "./item_stats_preview.js";

const button = document.getElementById("toggle-all-previews-button");

function render(expanded) {
    button.textContent = expanded ? "Hide All Info" : "Show All Info";
    button.setAttribute("aria-pressed", String(expanded));
}

button.addEventListener("click", () => {
    render(toggleAllPreviews());
});
