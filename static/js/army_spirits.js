// JS mirror of logic/army_spirits.py's selection rule - see that module
// for the authoritative, tested version. Renders the Officer Corps tab:
// 3 categories (Academy/Army/Division Command), each a flat list of
// Army Spirit buttons, one active per category at a time - mirrors
// static/js/doctrines.js's own Grand Doctrine "one per folder" picker
// exactly, simplified (no tracks, no progression/rewards - Army Spirits
// are a plain instant swap in this app, matching the real game's own
// mechanic of replacing one idea for another, just without the political
// power cost this app doesn't simulate).
//
// Deliberately does NOT feed into /api/stats or dispatch anything Stats
// needs to read - none of the 40 compiled entries' modifiers/equipment_bonus
// fields are applied anywhere yet (see data/army_spirits.py's own header).
// Selection state still persists (session autosave + Persistence Phase 2
// saves), since it's real user input worth remembering even though
// nothing downstream consumes it yet.

import { attachBonusPreview } from "./item_stats_preview.js";

const armySpiritCategories = JSON.parse(document.getElementById("army-spirit-category-data").textContent);
const armySpirits = JSON.parse(document.getElementById("army-spirit-data").textContent);

export function isArmySpiritSelectable(spiritKey, activeGrandDoctrines, trackSubdoctrines) {
    const spirit = armySpirits.find((s) => s.key === spiritKey);
    if (spirit.available.length === 0) {
        return true;
    }
    const active = new Set([...activeGrandDoctrines, ...Object.values(trackSubdoctrines)]);
    return spirit.available.some((key) => active.has(key));
}

// Caller-owned state: one active spirit key per category, at most.
const activeSpirits = new Set();

// Kept in sync via doctrine-changed, seeded empty like every other file
// that listens for it - needed for isArmySpiritSelectable's gating.
let activeGrandDoctrines = new Set();
let trackSubdoctrines = {};
document.addEventListener("doctrine-changed", (event) => {
    activeGrandDoctrines = new Set(event.detail.activeGrandDoctrines);
    trackSubdoctrines = { ...event.detail.trackSubdoctrines };
    renderAll();
});

document.addEventListener("all-previews-toggled", renderAll);

const CATEGORY_LIST_IDS = {
    army_spirit: "army-spirit-list-army",
    division_command_spirit: "army-spirit-list-division-command",
};

function activeKeyInCategory(category) {
    // A key in activeSpirits that no longer exists in the current
    // armySpirits compile (a real case, found 2026-11-02: the same-day
    // rescope from 40 to 9 entries left stale keys like
    // bold_attack_spirit sitting in already-persisted sessions) would
    // otherwise throw here (.find() returning undefined, then reading
    // .category off it) - skip it instead of crashing.
    return [...activeSpirits].find((key) => armySpirits.find((s) => s.key === key)?.category === category);
}

function selectArmySpirit(spiritKey) {
    if (!isArmySpiritSelectable(spiritKey, activeGrandDoctrines, trackSubdoctrines)) {
        return;
    }
    const spirit = armySpirits.find((s) => s.key === spiritKey);
    const currentlyActive = activeKeyInCategory(spirit.category);
    if (currentlyActive) {
        activeSpirits.delete(currentlyActive);
    }
    activeSpirits.add(spiritKey);
    renderAll();
    notifyArmySpiritsChanged();
}

function renderAll() {
    for (const category of armySpiritCategories) {
        const listEl = document.getElementById(CATEGORY_LIST_IDS[category.key]);
        if (!listEl) {
            continue;
        }
        listEl.innerHTML = "";

        for (const spirit of armySpirits.filter((s) => s.category === category.key)) {
            const button = document.createElement("button");
            button.type = "button";
            button.className = "battalion-option" + (activeSpirits.has(spirit.key) ? " filled" : "");
            const selectable = isArmySpiritSelectable(spirit.key, activeGrandDoctrines, trackSubdoctrines);
            button.disabled = !selectable && !activeSpirits.has(spirit.key);
            button.textContent = spirit.name;
            button.addEventListener("click", () => selectArmySpirit(spirit.key));
            listEl.appendChild(attachBonusPreview(button, () => [spirit]));
        }
    }
}

function notifyArmySpiritsChanged() {
    document.dispatchEvent(
        new CustomEvent("army-spirits-changed", { detail: { activeSpirits: [...activeSpirits] } })
    );
}

// --- Session persistence (added 2026-11-02) - see static/js/persistence.js
// for the load/save orchestration. No other section depends on this one's
// state, so where it restores relative to the others doesn't matter.

export function getState() {
    return { active_spirits: [...activeSpirits] };
}

export function restoreState(state) {
    // Clears first (real bug, found 2026-11-02 via AI Design Comparison's
    // "Load" button starting to call this with a result meant to REPLACE
    // the live picks, not merge with them - the same class of bug already
    // fixed in composition.js's own restoreState this same session).
    activeSpirits.clear();

    // Drop any key that no longer exists in the current armySpirits
    // compile (real, found 2026-11-02: the same-day rescope from 40 to 9
    // entries can leave an already-persisted session referencing a
    // removed key, e.g. bold_attack_spirit) - restoring it anyway would
    // silently corrupt activeSpirits with a ghost key that later crashes
    // activeKeyInCategory/the server's own active_army_strength_factor.
    // Dropping it here and then notifyArmySpiritsChanged() (which
    // persistence.js's save-on-change listener is already wired to)
    // self-heals the saved state the next time this page loads, with no
    // manual data cleanup needed.
    for (const key of state.active_spirits ?? []) {
        if (armySpirits.some((s) => s.key === key)) {
            activeSpirits.add(key);
        }
    }
    renderAll();
    notifyArmySpiritsChanged();
}

renderAll();
