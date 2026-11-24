import { attachStatPreview, fetchItemStatPreviews } from "./item_stats_preview.js";
import { getCurrentStatsContext } from "./stats.js";

const regimentalSupportOptions = JSON.parse(document.getElementById("regimental-support-data").textContent);

// See composition.js's matching comment - same seed-then-listen pattern,
// research and doctrine as two independent unlock sources.
let unlockedByResearch = new Set(JSON.parse(document.getElementById("always-unlocked-subunit-data").textContent));
document.addEventListener("research-changed", (event) => {
    unlockedByResearch = event.detail.unlockedSubunits;
});

let unlockedByDoctrine = new Set();
document.addEventListener("doctrine-changed", (event) => {
    unlockedByDoctrine = event.detail.unlockedSubunits;
});

let unlockedBySpecialProjects = new Set();
document.addEventListener("special-projects-changed", (event) => {
    unlockedBySpecialProjects = event.detail.unlockedSubunits;
});

// Mirrors logic/composition.py's regimental_support_unlocked() - see
// Specification.md for why this small rule is duplicated in JS rather than
// calling the Python version (the Composition UI is entirely client-side).
const MINIMUM_BATTALIONS_FOR_REGIMENTAL_SUPPORT = 3;

function regimentalSupportUnlocked(battalionCount) {
    return battalionCount >= MINIMUM_BATTALIONS_FOR_REGIMENTAL_SUPPORT;
}

// One entry per battalion column.
const columnUnlocked = [false, false, false, false, false];
const columnCategory = [null, null, null, null, null];
const selectedKey = [null, null, null, null, null];

const dialog = document.getElementById("regimental-support-dialog");
const dialogTitle = document.getElementById("regimental-support-dialog-title");
const dialogBody = document.getElementById("regimental-support-dialog-body");
const dialogCancel = document.getElementById("regimental-support-dialog-cancel");

let activeColumn = null;

dialogCancel.addEventListener("click", () => dialog.close());

document.addEventListener("battalion-column-changed", (event) => {
    const { column, count, category } = event.detail;
    const wasUnlocked = columnUnlocked[column];

    columnUnlocked[column] = regimentalSupportUnlocked(count);
    columnCategory[column] = category;

    if (wasUnlocked && !columnUnlocked[column]) {
        // Column dropped back below the threshold - it no longer qualifies
        // for whatever regimental support was chosen for it.
        selectedKey[column] = null;
    }

    renderCell(column);
    notifyRegimentalSupportChanged();
});

function renderCell(column) {
    const cell = document.querySelector(`.regimental-support-cell[data-rs-column="${column}"]`);

    if (!columnUnlocked[column]) {
        cell.disabled = true;
        cell.classList.add("locked");
        cell.classList.remove("filled");
        cell.textContent = "×";
        return;
    }

    cell.disabled = false;
    cell.classList.remove("locked");

    const key = selectedKey[column];
    if (key === null) {
        cell.textContent = "+";
        cell.classList.remove("filled");
        delete cell.dataset.rsKey;
    } else {
        cell.textContent = regimentalSupportOptions.find((option) => option.key === key).name;
        cell.classList.add("filled");
        cell.dataset.rsKey = key;
    }
}

// Lets stats.js react to regimental support changes without needing to know
// anything about this file's internals - same CustomEvent pattern as
// composition.js's notifyColumnChanged.
function notifyRegimentalSupportChanged() {
    document.dispatchEvent(new CustomEvent("regimental-support-changed"));
}

// Bound to every regimental-support cell up front, even the (initially all)
// locked ones - the native `disabled` attribute, toggled by renderCell() as
// columns cross the 3-battalion threshold, is what actually blocks clicks.
document.querySelectorAll(".regimental-support-cell").forEach((cell) => {
    cell.addEventListener("click", () => openPicker(cell));
});

function openPicker(cell) {
    activeColumn = Number(cell.dataset.rsColumn);

    dialogTitle.textContent = `Select Regimental Support — Column ${activeColumn + 1}`;
    dialogBody.innerHTML = "";

    if (selectedKey[activeColumn] !== null) {
        const removeButton = document.createElement("button");
        removeButton.type = "button";
        removeButton.className = "battalion-option";
        removeButton.textContent = "Remove regimental support";
        removeButton.addEventListener("click", () => {
            selectedKey[activeColumn] = null;
            renderCell(activeColumn);
            dialog.close();
            notifyRegimentalSupportChanged();
        });
        dialogBody.appendChild(removeButton);
    }

    const list = document.createElement("div");
    list.className = "battalion-option-list";

    const category = columnCategory[activeColumn];
    const eligibleOptions = regimentalSupportOptions.filter(
        (option) =>
            option.allowed_battalion_groups.includes(category) &&
            (unlockedByResearch.has(option.key) ||
                unlockedByDoctrine.has(option.key) ||
                unlockedBySpecialProjects.has(option.key))
    );

    // Regimental support is a support-type item (its own combat fields are
    // percentage modifiers on equipment, not flat adds - see CLAUDE.md).
    const previewsPromise = fetchItemStatPreviews(
        eligibleOptions.map((option) => ({ item_key: option.key, is_support_type: true })),
        getCurrentStatsContext()
    );

    for (const option of eligibleOptions) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "battalion-option";
        button.textContent = option.name;
        button.addEventListener("click", () => {
            selectedKey[activeColumn] = option.key;
            renderCell(activeColumn);
            dialog.close();
            notifyRegimentalSupportChanged();
        });
        list.appendChild(attachStatPreview(button, { previewsPromise, lookupKey: option.key }));
    }

    dialogBody.appendChild(list);
    dialog.showModal();
}

// --- Session persistence (added 2026-10-06) - see static/js/persistence.js
// for the load/save orchestration. Must restore AFTER Composition - relies
// on columnUnlocked/columnCategory already being correct by then (both are
// derived purely from the "battalion-column-changed" events Composition's
// own restore already dispatches per column, not separately persisted).

export function getState() {
    return [...selectedKey];
}

export function restoreState(keys) {
    for (let column = 0; column < keys.length; column++) {
        selectedKey[column] = keys[column];
        renderCell(column);
    }
    notifyRegimentalSupportChanged();
}
