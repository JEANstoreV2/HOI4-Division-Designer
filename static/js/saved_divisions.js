// Persistence Phase 2 (added 2026-11-02) - the named "save this division,
// list saved ones, load one back, compare two side by side" library, on
// top of Phase 1's session auto-save/restore (static/js/persistence.js).
// A save is always the FULL 8-section bundle persistence.js's
// getAllSectionsState()/restoreAllFromState() already know how to build/
// apply - reused here rather than duplicated, so Save/Load go through the
// exact same dependency-ordered restore sequence page-load restore does.

import { getAllSectionsState, restoreAllFromState } from "./persistence.js";
import { buildStatsRequestFromBundle, renderStats, renderTerrainBadge } from "./stats.js";

const nameInput = document.getElementById("save-division-name");
const saveButton = document.getElementById("save-division-button");
const listEl = document.getElementById("saved-divisions-list");

const compareArea = document.getElementById("compare-area");
const closeCompareButton = document.getElementById("close-compare-button");
const compareNameA = document.getElementById("compare-name-a");
const compareNameB = document.getElementById("compare-name-b");
const terrainBadgeA = document.getElementById("terrain-modifier-display-a");
const terrainBadgeB = document.getElementById("terrain-modifier-display-b");
const statsPanelA = document.getElementById("stats-panel-a");
const statsPanelB = document.getElementById("stats-panel-b");

// Names currently checked for comparison - capped at 2, same idea as
// regimental_support.js's own "disable everything else once full" idiom.
const selectedForCompare = [];

async function fetchSavedList() {
    const response = await fetch("/api/saved-divisions");
    return response.json();
}

async function renderSavedList() {
    const saves = await fetchSavedList();
    listEl.innerHTML = "";

    if (saves.length === 0) {
        listEl.innerHTML = '<p class="section-caption">No divisions saved yet.</p>';
        return;
    }

    const compareSelectedButtonNeeded = selectedForCompare.length === 2;

    for (const save of saves) {
        const row = document.createElement("div");
        row.className = "tech-row";
        row.style.cursor = "default";

        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.checked = selectedForCompare.includes(save.name);
        checkbox.disabled = !checkbox.checked && selectedForCompare.length >= 2;
        checkbox.addEventListener("change", () => {
            if (checkbox.checked) {
                selectedForCompare.push(save.name);
            } else {
                const index = selectedForCompare.indexOf(save.name);
                if (index !== -1) selectedForCompare.splice(index, 1);
            }
            renderSavedList();
        });
        row.appendChild(checkbox);

        const textWrap = document.createElement("span");
        textWrap.className = "tech-row-text";
        const nameEl = document.createElement("span");
        nameEl.className = "tech-row-name";
        nameEl.textContent = save.name;
        textWrap.appendChild(nameEl);
        const savedAtEl = document.createElement("span");
        savedAtEl.className = "tech-row-reason";
        savedAtEl.textContent = `Saved ${new Date(save.saved_at).toLocaleString()}`;
        textWrap.appendChild(savedAtEl);
        row.appendChild(textWrap);

        const loadButton = document.createElement("button");
        loadButton.type = "button";
        loadButton.className = "battalion-option";
        loadButton.textContent = "Load";
        loadButton.addEventListener("click", () => loadSavedDivision(save.name));
        row.appendChild(loadButton);

        const deleteButton = document.createElement("button");
        deleteButton.type = "button";
        deleteButton.className = "battalion-option";
        deleteButton.textContent = "Delete";
        deleteButton.addEventListener("click", () => deleteSavedDivision(save.name));
        row.appendChild(deleteButton);

        listEl.appendChild(row);
    }

    const caption = document.createElement("p");
    caption.className = "section-caption";
    caption.textContent = `${selectedForCompare.length}/2 selected for comparison`;
    listEl.appendChild(caption);

    if (compareSelectedButtonNeeded) {
        const compareButton = document.createElement("button");
        compareButton.type = "button";
        compareButton.className = "battalion-option";
        compareButton.textContent = "Compare Selected";
        compareButton.addEventListener("click", () => compareSelected());
        listEl.appendChild(compareButton);
    }
}

async function saveCurrentDivision() {
    const name = nameInput.value.trim();
    if (!name) {
        return;
    }

    const saves = await fetchSavedList();
    if (saves.some((save) => save.name === name)) {
        if (!confirm(`Overwrite the existing save "${name}"?`)) {
            return;
        }
    }

    await fetch(`/api/saved-divisions/${encodeURIComponent(name)}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(getAllSectionsState()),
    });
    nameInput.value = "";
    renderSavedList();
}

async function loadSavedDivision(name) {
    if (!confirm(`Load "${name}"? This replaces your current unsaved session.`)) {
        return;
    }
    const response = await fetch(`/api/saved-divisions/${encodeURIComponent(name)}`);
    const saved = await response.json();
    restoreAllFromState(saved.data);
}

async function deleteSavedDivision(name) {
    await fetch(`/api/saved-divisions/${encodeURIComponent(name)}`, { method: "DELETE" });
    const index = selectedForCompare.indexOf(name);
    if (index !== -1) selectedForCompare.splice(index, 1);
    renderSavedList();
}

// Read-only: fetches both selected saves' bundles, runs each through
// /api/stats via buildStatsRequestFromBundle, and renders two independent
// panels via stats.js's own renderStats/renderTerrainBadge - never touches
// the live Composition/Research/etc. module state, so comparing never
// disturbs the in-progress division actually being edited.
async function compareSelected() {
    const [nameA, nameB] = selectedForCompare;
    await renderComparisonColumn(nameA, compareNameA, terrainBadgeA, statsPanelA);
    await renderComparisonColumn(nameB, compareNameB, terrainBadgeB, statsPanelB);
    compareArea.hidden = false;
}

async function renderComparisonColumn(name, nameEl, terrainBadgeEl, statsPanelEl) {
    nameEl.textContent = name;

    const response = await fetch(`/api/saved-divisions/${encodeURIComponent(name)}`);
    const saved = await response.json();
    const bundle = saved.data;

    const statsResponse = await fetch("/api/stats", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(buildStatsRequestFromBundle(bundle)),
    });
    const stats = await statsResponse.json();

    if (stats === null) {
        // /api/stats returns a bare null body for an empty-composition
        // bundle (app.py's own early return) - the live UI never hits
        // this (refreshStats short-circuits earlier), but a save with no
        // battalions at all is a real possibility here.
        terrainBadgeEl.innerHTML = "";
        statsPanelEl.innerHTML = '<p class="section-caption">This division has no battalions.</p>';
        return;
    }

    renderStats(statsPanelEl, stats);
    // bundle.terrain (this division's OWN saved terrain selection), not
    // the live Composition view's current one - see stats.js's
    // renderTerrainBadge docstring for why this parameter exists at all.
    renderTerrainBadge(terrainBadgeEl, stats.terrain, bundle.terrain);
}

saveButton.addEventListener("click", saveCurrentDivision);
closeCompareButton.addEventListener("click", () => {
    compareArea.hidden = true;
});

renderSavedList();
