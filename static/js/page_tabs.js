// Top-level Composition/Research tab switching. Kept separate from
// research.js since it's just view visibility, not research logic - the
// two views stay mounted in the DOM the whole time (never removed), which
// is exactly why research state (owned entirely inside research.js) survives
// switching back and forth without needing any persistence.
document.querySelectorAll(".page-tab").forEach((tab) => {
    tab.addEventListener("click", () => {
        document.querySelectorAll(".page-tab").forEach((t) => t.classList.remove("active"));
        tab.classList.add("active");

        const targetId = tab.dataset.view;
        document.querySelectorAll(".view").forEach((view) => {
            view.hidden = view.id !== targetId;
        });
    });
});
