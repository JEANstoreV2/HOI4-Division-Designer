// Session persistence (Phase 1, added 2026-10-06) - see storage.py and
// CLAUDE.md's Persistence section for the full design. The first file in
// this project to use real ES module imports across files (every other
// cross-file link so far is a CustomEvent) - deliberate here, since the
// restore sequence below needs to call each file's restoreState in a
// specific, deterministic order, which an event chain can't guarantee the
// way a plain sequence of awaited calls can.
import { getState as getCompositionState, restoreState as restoreCompositionState } from "./composition.js";
import { getState as getSupportState, restoreState as restoreSupportState } from "./support_companies.js";
import {
    getState as getRegimentalSupportState,
    restoreState as restoreRegimentalSupportState,
} from "./regimental_support.js";
import { getState as getResearchState, restoreState as restoreResearchState } from "./research.js";
import {
    getState as getSpecialProjectsState,
    restoreState as restoreSpecialProjectsState,
} from "./special_projects.js";
import { getState as getDoctrineState, restoreState as restoreDoctrineState } from "./doctrines.js";
import { getState as getArmySpiritsState, restoreState as restoreArmySpiritsState } from "./army_spirits.js";
import { getState as getTankDesignsState, restoreState as restoreTankDesignsState } from "./tank_designer.js";
import { getState as getTerrainState, restoreState as restoreTerrainState } from "./stats.js";

// Order matters: Research/Special Projects/Doctrine all populate unlock
// sets Composition/Support Companies/Regimental Support's own pickers gate
// on (and Doctrine's restore is what unlocks the 5th battalion row before
// Composition tries to fill it) - restoring them first matches the exact
// same dependency chain the live CustomEvents already enforce during
// normal interactive use. Regimental Support must follow Composition (it
// derives columnUnlocked/columnCategory from Composition's own
// "battalion-column-changed" dispatches, not from anything persisted
// separately). Tank Designer's saved designs and Terrain have no
// dependency on anything else, so they're restored last.
//
// Extracted (2026-11-02, Persistence Phase 2) so static/js/saved_divisions.js
// can reuse the exact same assembly/restore logic for "Save Current
// Division"/"Load" - a named save is the identical section bundle
// GET /api/state already returns, and loading one is exactly this
// dependency-ordered restore sequence applied to a different source.
// (army_spirits added 2026-11-02, Officer Corps - no other section
// depends on it, so its exact position in this list doesn't matter;
// placed right after doctrine since Army Spirit eligibility gating reads
// Doctrine state.)
export function getAllSectionsState() {
    return {
        research: getResearchState(),
        special_projects: getSpecialProjectsState(),
        doctrine: getDoctrineState(),
        army_spirits: getArmySpiritsState(),
        composition: getCompositionState(),
        support_companies: getSupportState(),
        regimental_support: getRegimentalSupportState(),
        tank_designs: getTankDesignsState(),
        terrain: getTerrainState(),
    };
}

export function restoreAllFromState(state) {
    if (state.research) restoreResearchState(state.research);
    if (state.special_projects) restoreSpecialProjectsState(state.special_projects);
    if (state.doctrine) restoreDoctrineState(state.doctrine);
    if (state.army_spirits) restoreArmySpiritsState(state.army_spirits);
    if (state.composition) restoreCompositionState(state.composition);
    if (state.support_companies) restoreSupportState(state.support_companies);
    if (state.regimental_support) restoreRegimentalSupportState(state.regimental_support);
    if (state.tank_designs) restoreTankDesignsState(state.tank_designs);
    if (state.terrain) restoreTerrainState(state.terrain);
}

async function restoreAll() {
    const response = await fetch("/api/state");
    restoreAllFromState(await response.json());
}

// Debounced per section (not one global debounce) so e.g. rapid composition
// clicks don't delay a doctrine save that happened to land in between.
// Each restoreState call above also fires its own normal CustomEvent (the
// same one an interactive change would), which means restoreAll's own
// calls land right back here and re-save each section once - harmless
// (idempotent, writes back exactly what was just read) and cheap enough
// locally not to be worth extra "don't save during restore" bookkeeping.
const SAVE_DEBOUNCE_MS = 300;
const pendingSaves = {};

function saveSection(section, value) {
    clearTimeout(pendingSaves[section]);
    pendingSaves[section] = setTimeout(() => {
        fetch(`/api/state/${section}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(value),
        });
    }, SAVE_DEBOUNCE_MS);
}

document.addEventListener("research-changed", () => saveSection("research", getResearchState()));
document.addEventListener("special-projects-changed", () => saveSection("special_projects", getSpecialProjectsState()));
document.addEventListener("doctrine-changed", () => saveSection("doctrine", getDoctrineState()));
document.addEventListener("army-spirits-changed", () => saveSection("army_spirits", getArmySpiritsState()));
document.addEventListener("battalion-column-changed", () => saveSection("composition", getCompositionState()));
document.addEventListener("support-changed", () => saveSection("support_companies", getSupportState()));
document.addEventListener("regimental-support-changed", () =>
    saveSection("regimental_support", getRegimentalSupportState())
);
document.addEventListener("tank-designs-changed", () => saveSection("tank_designs", getTankDesignsState()));
document.addEventListener("terrain-changed", () => saveSection("terrain", getTerrainState()));

document.getElementById("reset-all-button").addEventListener("click", async () => {
    if (!confirm("Reset ALL saved progress - Composition, Research, Special Projects, Doctrine, Officer Corps, and saved Tank Designer designs? This can't be undone.")) {
        return;
    }
    await fetch("/api/state", { method: "DELETE" });
    location.reload();
});

restoreAll();
