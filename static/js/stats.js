// Renders the live division-stats panel next to Composition. Reads the
// current selection straight off the DOM (data-battalion-key/data-support-key/
// data-rs-key, set by composition.js/support_companies.js/regimental_support.js
// respectively) rather than duplicating their internal state - see those
// files' matching comments on the CustomEvents this listens for.
//
// Calls the server (`POST /api/stats`) instead of reimplementing
// calculate_division_stats in JS - see Specification.md's note on
// JS/Python duplication: that rule is fine for simple picker logic, but
// Stats' aggregation rules (equipment lookups, tier resolution, five
// different per-field combination rules, doctrine bonuses) are complex
// enough that a second, untested copy in JS isn't worth it for a feature
// that doesn't need sub-millisecond feedback the way a picker dialog does.

const panel = document.getElementById("stats-panel");
const terrainBadgeEl = document.getElementById("terrain-modifier-display");

let researched = [];
document.addEventListener("research-changed", (event) => {
    researched = event.detail.researched;
    refreshStats();
});

// A completed special project can grant its own direct stat bonus (e.g.
// Large Caliber Kinetic Energy Sabot's Piercing bonus - see
// data/special_projects.py's "unit_bonuses" field, added 2026-10-07), so
// /api/stats needs this set the same way it already needs `researched`.
let completedSpecialProjects = [];
document.addEventListener("special-projects-changed", (event) => {
    completedSpecialProjects = [...event.detail.completed];
    refreshStats();
});

// null until the first doctrine change, matching how `researched` starts
// as [] - /api/stats treats a missing/null doctrine as "no doctrine bonuses".
let doctrine = null;
document.addEventListener("doctrine-changed", (event) => {
    doctrine = {
        active_grand_doctrines: event.detail.activeGrandDoctrines,
        track_subdoctrines: event.detail.trackSubdoctrines,
        claimed_rewards: event.detail.claimedRewards,
    };
    refreshStats();
});

// null until the first save, matching how `doctrine` starts null -
// /api/stats treats a missing/null tank_designs as "no custom designs,
// use default tier-based equipment everywhere". See tank_designer.js's
// notifyDesignsChanged for why this needs no per-slot matching: each key
// already IS the equipment_key every consuming battalion/support/
// regimental-support item looks up on its own.
let tankDesigns = null;
document.addEventListener("tank-designs-changed", (event) => {
    tankDesigns = event.detail;
    refreshStats();
});

// Starts empty, matching `researched` - an active Army Spirit can carry a
// real, confirmed division-wide bonus (so far just Operational Reserves'
// Max Strength boost - see logic/army_spirits.py's
// active_army_strength_factor), applied once at the division level, not
// per-item, so /api/stats needs the raw active-key list the same way it
// already needs `researched`/`completed_special_projects`.
let armySpirits = [];
document.addEventListener("army-spirits-changed", (event) => {
    armySpirits = event.detail.activeSpirits;
    refreshStats();
});

document.addEventListener("battalion-column-changed", refreshStats);
document.addEventListener("support-changed", refreshStats);
document.addEventListener("regimental-support-changed", refreshStats);

// Was purely local UI state with no CustomEvent (nothing else in the app
// needed to know which terrain is selected) - now dispatches one anyway,
// for static/js/persistence.js's own save-on-change to listen for (added
// 2026-10-06, see that file).
let terrainKey = "";
document.getElementById("terrain-select").addEventListener("change", (event) => {
    terrainKey = event.target.value;
    refreshStats();
    document.dispatchEvent(new CustomEvent("terrain-changed"));
});

// Guards against an older, slower request's response overwriting a newer
// one's (possible under rapid clicking, since fetch responses can arrive
// out of order).
let latestRequestId = 0;

function currentKeys(selector, datasetKey) {
    return [...document.querySelectorAll(selector)].map((cell) => cell.dataset[datasetKey]);
}

async function refreshStats() {
    const battalions = currentKeys(".battalion-cell.filled[data-column]", "battalionKey");

    if (battalions.length === 0) {
        panel.innerHTML = `<p class="section-caption">Select at least one battalion to see division stats.</p>`;
        document.getElementById("terrain-modifier-display").innerHTML = "";
        return;
    }

    const requestId = ++latestRequestId;
    const supportCompanies = currentKeys(".support-cell.filled[data-slot]", "supportKey");
    const regimentalSupport = currentKeys(".regimental-support-cell.filled[data-rs-column]", "rsKey");

    try {
        const response = await fetch("/api/stats", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                battalions,
                support_companies: supportCompanies,
                regimental_support: regimentalSupport,
                researched,
                completed_special_projects: completedSpecialProjects,
                doctrine,
                tank_designs: tankDesigns,
                terrain_key: terrainKey || null,
                army_spirits: armySpirits,
            }),
        });
        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }
        const stats = await response.json();

        if (requestId !== latestRequestId) {
            return; // a newer request has since been sent - discard this one
        }
        renderStats(panel, stats);
        renderTerrainBadge(terrainBadgeEl, stats.terrain, terrainKey);
    } catch (error) {
        // Previously unguarded - a server error here (e.g. the real
        // bug found 2026-11-02, a stale persisted army_spirits key
        // crashing /api/stats with a 500) left response.json() throwing
        // an uncaught rejection, which meant this panel just silently
        // froze on whatever it last successfully rendered - no visible
        // sign anything was wrong. Now a failure is always visible.
        if (requestId === latestRequestId) {
            console.error("Failed to refresh division stats:", error);
            panel.innerHTML = `<p class="stats-warning">Couldn't load Division Stats: ${error.message}. Check the browser console for details.</p>`;
        }
    }
}

// Field -> display label, for every field not already called out by name in
// the headline/secondary rows below. Exported (2026-11-02) for
// static/js/design_search.js's stat-bound picker, which needs every real
// stat field this app tracks, not just the curated KEY_STAT_FIELDS
// shortlist below.
export const REMAINING_FIELD_LABELS = {
    manpower: "Manpower",
    training_time: "Training Time",
    supply_consumption: "Supply Consumption",
    ap_attack: "Piercing",
    air_attack: "Air Attack",
    armor_value: "Armor",
    hardness: "Hardness",
    max_speed: "Max Speed",
    suppression: "Suppression",
};

// Exported for static/js/item_stats_preview.js (added 2026-10-08) - its
// compact pre-selection preview reuses this exact field/label/rounding
// convention rather than inventing a second one.
export const KEY_STAT_FIELDS = [
    ["max_strength", "Strength"],
    ["soft_attack", "Soft Attack"],
    ["hard_attack", "Hard Attack"],
    ["breakthrough", "Breakthrough"],
    ["defense", "Defense"],
    ["combat_width", "Combat Width"],
    ["production_cost", "Production Cost"],
];

export function formatNumber(value) {
    return Math.round(value * 100) / 100;
}

function formatPercentage(value) {
    const pct = Math.round(value * 1000) / 10; // one decimal, matching HOI4's own tooltip style
    return `${pct > 0 ? "+" : ""}${pct}%`;
}

// A compact "Attack: X% | Defense: Y%" readout, replacing the real game's
// hover-to-reveal terrain icon with something always visible - see
// logic/terrain.py's division_terrain_percentage docstring for why this is
// an AVERAGE across the division's item types, not a recompute of the main
// Division Stats numbers above (which terrain selection never changes).
// Amphibious Assault is the one terrain selection where the badge/per-field
// numbers above are structurally unable to show the real achievable result
// (added 2026-10-07, per Ollie's own report). data/terrain.py's "amphibious"
// entries are HOI4's real per-UNIT-TYPE terrain modifier (e.g. Marines
// +50%, plain Armor -40% to -90%) and are applied correctly - but the real
// game ALSO applies a completely separate, universal, hardcoded engine
// constant on top of every amphibious invasion regardless of unit type
// (NDefines.NNavy.AMPHIBIOUS_LANDING_PENALTY = -0.5, confirmed via the HOI4
// wiki's Land battle page) that this app doesn't model at all - there's
// nothing in units_copy/ or terrain_copy/ for it to be compiled FROM, it's
// a pure engine value. In practice this means even a unit whose own
// amphibious modifier looks positive here (e.g. amphibious_armor's shown
// +60%) rarely or never nets a real positive combat modifier once actually
// invading, since that separate -50% still applies on top - exactly the
// "excess in the menu" Ollie flagged. Scoped deliberately as a disclaimer
// only, not a computed clamp - the exact multiplicative interaction with
// every other combat factor isn't independently verified against a
// screenshot the way every other Terrain rule in this app already is, and
// Ollie's own call was "show the user", not "guess at a new formula."
const AMPHIBIOUS_PENALTY_NOTE =
    "Real amphibious invasions also apply HOI4's own separate, universal " +
    "-50% Amphibious Landing Penalty on top of the per-unit modifier shown " +
    "above - not modeled here. In practice this means most units never " +
    "reach a real positive combat modifier when actually naval invading, " +
    "even when the numbers above look favorable.";

// A compact "Attack: X% | Defense: Y%" readout, replacing the real game's
// hover-to-reveal terrain icon with something always visible - see
// logic/terrain.py's division_terrain_percentage docstring for why this is
// an AVERAGE across the division's item types, not a recompute of the main
// Division Stats numbers above (which terrain selection never changes).
//
// Takes an explicit container + terrainKeyForThisDivision (not the module-
// level terrainKey closure variable) since Persistence Phase 2's Compare
// view (added 2026-11-02) renders two independent panels, each for a saved
// division with its OWN saved terrain selection, which may differ from
// whatever the live Composition view's terrain selector currently shows -
// reading the closure variable here would show the wrong (or missing)
// amphibious disclaimer for a compared division.
export function renderTerrainBadge(container, terrain, terrainKeyForThisDivision) {
    if (!terrain) {
        container.innerHTML = "";
        return;
    }
    container.innerHTML = `<div class="stats-secondary terrain-modifier">
        <div class="stats-secondary-item">
            <span class="stats-secondary-value">${formatPercentage(terrain.attack_percentage)}</span>
            <span class="stats-secondary-label">Attack (Terrain)</span>
        </div>
        <div class="stats-secondary-item">
            <span class="stats-secondary-value">${formatPercentage(terrain.defense_percentage)}</span>
            <span class="stats-secondary-label">Defense (Terrain)</span>
        </div>
    </div>`;
    if (terrainKeyForThisDivision === "amphibious") {
        container.innerHTML += `<p class="stats-warning">${AMPHIBIOUS_PENALTY_NOTE}</p>`;
    }
}

// For a field terrain actually affects (soft_attack/hard_attack are
// affected by both sides; breakthrough by attacking only; defense by
// defending only - see logic/terrain.py's ATTACK_SIDE_FIELDS/
// DEFENCE_SIDE_FIELDS), returns " (Atk X / Def Y)" using the real
// recomputed per-side division values from the /api/stats response -
// not the top summary badge's average percentage. Returns "" for every
// other field, or when no terrain is selected at all.
function terrainValueSuffix(field, terrain) {
    if (!terrain) {
        return "";
    }
    const parts = [];
    if (field in terrain.attacking_stats) {
        parts.push(`Atk ${formatNumber(terrain.attacking_stats[field])}`);
    }
    if (field in terrain.defending_stats) {
        parts.push(`Def ${formatNumber(terrain.defending_stats[field])}`);
    }
    return parts.length > 0
        ? ` <span class="stats-secondary-suffix">(${parts.join(" / ")})</span>`
        : "";
}

// Takes an explicit container (not the module-level panel constant) so
// Persistence Phase 2's Compare view (added 2026-11-02) can render two
// independent panels into its own two containers, reusing this exact
// rendering rather than a second, parallel copy.
export function renderStats(container, stats) {
    container.innerHTML = "";

    if (!stats.combat_stats_available) {
        const warning = document.createElement("p");
        warning.className = "stats-warning";
        warning.textContent = "Some equipment has no confirmed combat stats yet — numbers may be incomplete.";
        container.appendChild(warning);
    }

    const headline = document.createElement("div");
    headline.className = "stats-headline";
    headline.innerHTML = `<span class="stats-headline-value">${formatNumber(stats.max_organisation)}</span>
        <span class="stats-headline-label">Organisation</span>`;
    container.appendChild(headline);

    const secondary = document.createElement("div");
    secondary.className = "stats-secondary";
    for (const [field, label] of KEY_STAT_FIELDS) {
        secondary.innerHTML += `<div class="stats-secondary-item">
            <span class="stats-secondary-value">${formatNumber(stats[field])}${terrainValueSuffix(field, stats.terrain)}</span>
            <span class="stats-secondary-label">${label}</span>
        </div>`;
    }
    container.appendChild(secondary);

    const list = document.createElement("dl");
    list.className = "stats-list";
    for (const [field, label] of Object.entries(REMAINING_FIELD_LABELS)) {
        list.innerHTML += `<dt>${label}</dt><dd>${formatNumber(stats[field])}</dd>`;
    }
    container.appendChild(list);
}

// Exported for static/js/item_stats_preview.js (added 2026-10-08) - this
// file is the only one that already tracks the full context
// calculate_item_stats needs, so a preview reads it from here rather than
// every picker file re-tracking researched/doctrine/tank_designs itself.
// Deliberately omits terrain_key - a preview shows an item's own stats,
// not a terrain-side recompute (Ollie's own scope call).
export function getCurrentStatsContext() {
    return {
        researched,
        completed_special_projects: completedSpecialProjects,
        doctrine,
        tank_designs: tankDesigns,
    };
}

// Exported for static/js/design_search.js (added 2026-11-02) - the AI
// Design Comparison feature searches over Composition itself, so unlike
// an item preview it DOES need terrain/army_spirits as part of the fixed
// context every generated candidate is scored under (the same fixed
// context /api/stats already uses for the live division) - hence a
// separate export rather than widening getCurrentStatsContext itself,
// which deliberately omits them for its own, different use case.
export function getCurrentDivisionContext() {
    return {
        ...getCurrentStatsContext(),
        terrain_key: terrainKey || null,
        army_spirits: armySpirits,
    };
}

// Converts a saved-division bundle (static/js/persistence.js's
// getAllSectionsState() shape, as returned by GET /api/saved-divisions/<name>)
// into the request body /api/stats expects - used by static/js/
// saved_divisions.js's Compare feature (added 2026-11-02), which has no
// live DOM to read battalions/support_companies/regimental_support/
// terrain_key off of the way refreshStats() above does, since it's
// rendering a SAVED division's stats, not the one currently being edited.
//
// composition.js's own getState() returns an Array[5] of per-column arrays
// of battalionKey|null - .flat() collapses the 5 columns into one flat
// list exactly like refreshStats()'s own currentKeys() does, and the
// .filter(key => key !== null) matches currentKeys()'s own ".filled"-only
// DOM selection (composition.js's array can hold nulls for empty cells;
// the live DOM query never does, since it only selects already-filled
// cells). support_companies.js/regimental_support.js's own getState() are
// already flat but CAN contain null entries for empty slots the same way -
// calculate_division_stats does no null-filtering itself, so a raw saved
// array reaching /api/stats without this filter would 500.
export function buildStatsRequestFromBundle(bundle) {
    return {
        battalions: (bundle.composition || []).flat().filter((key) => key !== null),
        support_companies: (bundle.support_companies || []).filter((key) => key !== null),
        regimental_support: (bundle.regimental_support || []).filter((key) => key !== null),
        researched: bundle.research || [],
        completed_special_projects: bundle.special_projects || [],
        doctrine: bundle.doctrine || null,
        tank_designs: bundle.tank_designs || null,
        terrain_key: bundle.terrain || null,
        army_spirits: (bundle.army_spirits || {}).active_spirits || [],
    };
}

// --- Session persistence (added 2026-10-06) - see static/js/persistence.js
// for the load/save orchestration. Terrain has no dependency on the other
// sections (Stats itself already recomputes once everything else has
// restored), so it's fine to restore last.

export function getState() {
    return terrainKey;
}

export function restoreState(key) {
    terrainKey = key;
    document.getElementById("terrain-select").value = key;
    refreshStats();
}

refreshStats();
