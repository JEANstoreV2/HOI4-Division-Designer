// Patch Impact Preview (added 2026-11-03) - Intial_problem.md's own
// "grabs suggested changes from the open beta's published for testing how
// they will effect previous designs" goal. Ingestion itself stays manual
// (Ollie brings real patch-note text to a Claude Code session, Claude
// hand-writes a staged entry into data/patches.py - the same process
// already used for the real 1.19.3/1.19.4 data edits, just staged instead
// of applied) - this file is purely the "preview a staged patch's impact
// on every saved division" UI, reusing static/js/saved_divisions.js's own
// "fetch each saved division, build an /api/stats request" pattern and
// static/js/item_stats_preview.js's "only show what changed, with a
// signed delta" renderStatBlock (built for Tank Designer's own picker
// previews, exported for reuse here).

import { buildStatsRequestFromBundle, KEY_STAT_FIELDS, REMAINING_FIELD_LABELS } from "./stats.js";
import { renderStatBlock } from "./item_stats_preview.js";

const STAGED_PATCHES = JSON.parse(document.getElementById("staged-patches-data").textContent);

// Every tracked stat field, not just the curated 7 KEY_STAT_FIELDS - a
// staged patch can touch anything (manpower, armor, hardness, ...),
// unlike a pre-selection preview that only cares about a handful.
const ALL_STAT_FIELDS = [...KEY_STAT_FIELDS, ...Object.entries(REMAINING_FIELD_LABELS)];

const patchSelect = document.getElementById("patch-select");
const sourceNotesEl = document.getElementById("patch-source-notes");
const previewButton = document.getElementById("preview-patch-impact-button");
const resultsEl = document.getElementById("patch-impact-results");

function selectedPatch() {
    return STAGED_PATCHES.find((patch) => patch.key === patchSelect.value);
}

function updateSourceNotes() {
    const patch = selectedPatch();
    sourceNotesEl.textContent = patch ? patch.source_notes : "";
}

function renderPatchOptions() {
    if (STAGED_PATCHES.length === 0) {
        resultsEl.innerHTML = '<p class="section-caption">No staged patches yet - bring Claude the real patch notes and ask for one to be staged here first.</p>';
        previewButton.disabled = true;
        return;
    }
    for (const patch of STAGED_PATCHES) {
        const option = document.createElement("option");
        option.value = patch.key;
        option.textContent = patch.label;
        patchSelect.appendChild(option);
    }
    updateSourceNotes();
}

async function fetchDivisionStats(statsRequest) {
    const response = await fetch("/api/stats", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(statsRequest),
    });
    return response.json();
}

async function previewPatchImpact() {
    const patch = selectedPatch();
    if (!patch) {
        return;
    }

    previewButton.disabled = true;
    previewButton.textContent = "Previewing…";
    resultsEl.innerHTML = "";

    try {
        const saves = await (await fetch("/api/saved-divisions")).json();

        if (saves.length === 0) {
            resultsEl.innerHTML = '<p class="section-caption">No saved divisions yet - save one from the Composition tab first.</p>';
            return;
        }

        for (const save of saves) {
            const card = document.createElement("div");
            card.className = "patch-impact-card";
            card.innerHTML = `<h3>${save.name}</h3>`;
            const panel = document.createElement("div");
            card.appendChild(panel);
            resultsEl.appendChild(card);

            const saved = await (await fetch(`/api/saved-divisions/${encodeURIComponent(save.name)}`)).json();
            const baseRequest = buildStatsRequestFromBundle(saved.data);

            const [before, after] = await Promise.all([
                fetchDivisionStats(baseRequest),
                fetchDivisionStats({
                    ...baseRequest,
                    equipment_overrides: patch.equipment_overrides,
                    battalion_overrides: patch.battalion_overrides,
                }),
            ]);

            if (before === null || after === null) {
                panel.innerHTML = '<p class="section-caption">This division has no battalions.</p>';
                continue;
            }

            renderStatBlock(panel, after, ALL_STAT_FIELDS, before);
        }
    } catch (error) {
        // Mirrors design_search.js's own catch - a server error or network
        // hiccup must never silently look like "nothing happened."
        console.error("Patch impact preview failed:", error);
        resultsEl.innerHTML = `<p class="stats-warning">Something went wrong previewing this patch: ${error.message}. Check the browser console for details.</p>`;
    } finally {
        previewButton.disabled = false;
        previewButton.textContent = "Preview Impact on Saved Divisions";
    }
}

patchSelect.addEventListener("change", updateSourceNotes);
previewButton.addEventListener("click", previewPatchImpact);
renderPatchOptions();
