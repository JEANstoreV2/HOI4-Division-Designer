import { attachStatPreview, fetchItemStatPreviews } from "./item_stats_preview.js";
import { getCurrentStatsContext } from "./stats.js";

const supportCompanies = JSON.parse(document.getElementById("support-company-data").textContent);

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

const groupsByKey = {};
for (const company of supportCompanies) {
    groupsByKey[company.key] = new Set(company.same_support_type);
}

// Five independent slots; each holds a company key or null. Mirrors the
// auto-replace rule in logic/support_companies.py's select_support_company,
// adapted for fixed slot positions instead of a flat list.
const supportSlots = [null, null, null, null, null];

const dialog = document.getElementById("support-dialog");
const dialogTitle = document.getElementById("support-dialog-title");
const dialogBody = document.getElementById("support-dialog-body");
const dialogCancel = document.getElementById("support-dialog-cancel");

let activeSlotIndex = null;

document.querySelectorAll(".support-cell").forEach((cell) => {
    cell.addEventListener("click", () => openPicker(cell));
});

dialogCancel.addEventListener("click", () => dialog.close());

function openPicker(cell) {
    activeSlotIndex = Number(cell.dataset.slot);

    dialogTitle.textContent = `Select Support Company — Slot ${activeSlotIndex + 1}`;
    dialogBody.innerHTML = "";

    if (supportSlots[activeSlotIndex] !== null) {
        const removeButton = document.createElement("button");
        removeButton.type = "button";
        removeButton.className = "battalion-option";
        removeButton.textContent = "Remove company";
        removeButton.addEventListener("click", () => {
            supportSlots[activeSlotIndex] = null;
            renderSlot(activeSlotIndex);
            dialog.close();
            notifySupportChanged();
        });
        dialogBody.appendChild(removeButton);
    }

    const list = document.createElement("div");
    list.className = "battalion-option-list";

    const unlockedCompanies = supportCompanies.filter(
        (company) =>
            unlockedByResearch.has(company.key) ||
            unlockedByDoctrine.has(company.key) ||
            unlockedBySpecialProjects.has(company.key)
    );

    // Every company is a support-type item (its own combat fields are
    // percentage modifiers on equipment, not flat adds - see CLAUDE.md).
    const previewsPromise = fetchItemStatPreviews(
        unlockedCompanies.map((company) => ({ item_key: company.key, is_support_type: true })),
        getCurrentStatsContext()
    );

    for (const company of unlockedCompanies) {
        const option = document.createElement("button");
        option.type = "button";
        option.className = "battalion-option";
        option.textContent = company.name;
        option.addEventListener("click", () => selectCompany(company.key));
        list.appendChild(attachStatPreview(option, { previewsPromise, lookupKey: company.key }));
    }

    dialogBody.appendChild(list);
    dialog.showModal();
}

function selectCompany(newKey) {
    const newGroups = groupsByKey[newKey];

    supportSlots.forEach((key, index) => {
        if (index === activeSlotIndex || key === null) {
            return;
        }
        const conflicts = key === newKey || [...groupsByKey[key]].some((group) => newGroups.has(group));
        if (conflicts) {
            supportSlots[index] = null;
            renderSlot(index);
        }
    });

    supportSlots[activeSlotIndex] = newKey;
    renderSlot(activeSlotIndex);

    dialog.close();
    notifySupportChanged();
}

function renderSlot(index) {
    const cell = document.querySelector(`.support-cell[data-slot="${index}"]`);
    const key = supportSlots[index];

    if (key === null) {
        cell.textContent = "+";
        cell.classList.remove("filled");
        delete cell.dataset.supportKey;
        return;
    }

    cell.textContent = supportCompanies.find((company) => company.key === key).name;
    cell.classList.add("filled");
    cell.dataset.supportKey = key;
}

// Lets stats.js react to support company changes without needing to know
// anything about this file's internals - same CustomEvent pattern as
// composition.js's notifyColumnChanged.
function notifySupportChanged() {
    document.dispatchEvent(new CustomEvent("support-changed"));
}

// --- Session persistence (added 2026-10-06) - see static/js/persistence.js
// for the load/save orchestration and why Support Companies must restore
// after Research/Special Projects/Doctrine (its own picker gates on their
// unlock sets, same as the one openPicker already uses).

export function getState() {
    return [...supportSlots];
}

export function restoreState(slots) {
    for (let index = 0; index < slots.length; index++) {
        supportSlots[index] = slots[index];
        renderSlot(index);
    }
    notifySupportChanged();
}
