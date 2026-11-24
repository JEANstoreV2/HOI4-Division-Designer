// AI Design Comparison (punch-list step 8, added 2026-11-02) -
// Intial_problem.md's own stretch goal: generate and rank several
// candidate divisions by a chosen metric (e.g. "highest Organisation per
// Production Cost"), rather than showing the stats of one already-chosen
// division the way stats.js does. The actual generation/ranking is a
// server-side search (logic/design_search.py's generate_best_designs,
// POST /api/design-search) - this file is just the form + results UI,
// mirroring static/js/saved_divisions.js's own "fetch, then
// renderStats(container, stats) per result" pattern rather than
// reimplementing any of it.
//
// Constraints extension (added 2026-11-02, same day - see the plan file's
// "AI Design Comparison - Constraints Extension" section): a Constraints
// section lets the user add min/max bounds on any stat, a Research Year
// cutoff, and require one or more battalion types (each either "at least
// one" or "dominant" - Ollie's own distinction between "a division WITH a
// Marine battalion" and "a MARINE division"). All of it is optional and
// purely additive to the request body - the server does the real work
// (logic/design_search.py), this file only collects the form state.

import { KEY_STAT_FIELDS, REMAINING_FIELD_LABELS, formatNumber, getCurrentDivisionContext, renderStats } from "./stats.js";
import { restoreState as restoreCompositionState } from "./composition.js";
import { restoreState as restoreSupportState } from "./support_companies.js";
import { restoreState as restoreRegimentalSupportState } from "./regimental_support.js";
import { restoreState as restoreArmySpiritsState } from "./army_spirits.js";
import { restoreState as restoreDoctrineState } from "./doctrines.js";

const METRIC_FIELDS = [
    ["max_organisation", "Organisation"],
    ...KEY_STAT_FIELDS,
    ["ap_attack", "Piercing"],
    ["armor_value", "Armor"],
    ["max_speed", "Max Speed"],
    ["supply_consumption", "Supply Consumption"],
];

// Every real stat field this app tracks, for the stat-bound picker -
// broader than METRIC_FIELDS (which is just a curated "optimize for"
// shortlist) since a constraint can reasonably target any of them.
// Dedupes against METRIC_FIELDS' own entries rather than listing some
// fields twice.
const BOUND_FIELDS = [...METRIC_FIELDS];
const _METRIC_FIELD_KEYS = new Set(METRIC_FIELDS.map(([field]) => field));
for (const [field, label] of Object.entries(REMAINING_FIELD_LABELS)) {
    if (!_METRIC_FIELD_KEYS.has(field)) {
        BOUND_FIELDS.push([field, label]);
    }
}

const NAME_LOOKUP = (() => {
    const lookup = {};
    for (const id of ["battalion-data", "support-company-data", "regimental-support-data", "army-spirit-data"]) {
        const el = document.getElementById(id);
        if (!el) {
            continue;
        }
        for (const item of JSON.parse(el.textContent)) {
            lookup[item.key] = item.name;
        }
    }
    return lookup;
})();

function itemName(key) {
    return NAME_LOOKUP[key] ?? key;
}

const BOUND_FIELD_LABELS = Object.fromEntries(BOUND_FIELDS);

function fieldLabel(field) {
    return BOUND_FIELD_LABELS[field] ?? field;
}

// Turns the raw {unavailable_battalions, too_many_required_categories,
// unmet_bounds, unmet_dominant} shape generate_best_designs returns
// (added 2026-11-02, Ollie's own request: "add an error message as to
// what the contradiction is") into real sentences - the backend
// deliberately returns only field keys/numbers, since every display-
// label lookup already lives here (battalion/support/regimental names,
// stat field labels), not duplicated server-side.
function describeInfeasibleReason(reason) {
    const sentences = [];

    for (const key of reason.unavailable_battalions ?? []) {
        sentences.push(`${itemName(key)} is not currently unlocked under this Research/Doctrine/Special Projects state.`);
    }

    if (reason.too_many_required_categories?.length > 0) {
        sentences.push(
            `The required battalions span ${reason.too_many_required_categories.length} different categories, but a division only has 5 columns - they can't all fit at once.`
        );
    }

    for (const bound of reason.unmet_bounds ?? []) {
        const label = fieldLabel(bound.field);
        const target = bound.violated === "min" ? bound.min : bound.max;
        const relation = bound.violated === "min" ? "at least" : "at most";
        sentences.push(
            `${label} needs to be ${relation} ${formatNumber(target)} - the closest any design reached was ${formatNumber(bound.closest_value)}.`
        );
    }

    for (const dominant of reason.unmet_dominant ?? []) {
        sentences.push(
            `${itemName(dominant.key)} needs to be the single largest type in the division - the closest attempt had ${dominant.closest_count} against ${dominant.needed_more_than} for the largest other type.`
        );
    }

    return sentences;
}

// "3x Infantry, 2x Mountaineers" - tallies duplicate keys (battalions and
// Regimental Support can both repeat across columns; Support Companies
// never do, same_support_type already rules that out server-side) rather
// than listing every instance separately.
function tally(keys) {
    const counts = new Map();
    for (const key of keys) {
        counts.set(key, (counts.get(key) ?? 0) + 1);
    }
    return [...counts.entries()].map(([key, count]) => (count > 1 ? `${count}x ${itemName(key)}` : itemName(key)));
}

function compositionSummary(candidate) {
    const parts = [tally(candidate.battalions).join(", ") || "(no battalions)"];
    if (candidate.support_companies.length > 0) {
        parts.push(tally(candidate.support_companies).join(", "));
    }
    if (candidate.regimental_support.length > 0) {
        parts.push(tally(candidate.regimental_support).join(", "));
    }
    const activeSpirits = candidate.army_spirits?.active_spirits ?? [];
    if (activeSpirits.length > 0) {
        parts.push(`Officer Corps: ${activeSpirits.map(itemName).join(", ")}`);
    }
    const doctrineNames = [
        ...(candidate.doctrine?.active_grand_doctrines ?? []),
        ...Object.values(candidate.doctrine?.track_subdoctrines ?? {}),
    ].map(doctrineName);
    if (doctrineNames.length > 0) {
        parts.push(`Doctrine: ${doctrineNames.join(", ")}`);
    }
    return parts.join(" | ");
}

function populateMetricSelect(select, includeNoneOption) {
    if (includeNoneOption) {
        const none = document.createElement("option");
        none.value = "";
        none.textContent = "(none)";
        select.appendChild(none);
    }
    for (const [field, label] of METRIC_FIELDS) {
        const option = document.createElement("option");
        option.value = field;
        option.textContent = label;
        select.appendChild(option);
    }
}

const numeratorSelect = document.getElementById("design-search-numerator");
const denominatorSelect = document.getElementById("design-search-denominator");
populateMetricSelect(numeratorSelect, false);
populateMetricSelect(denominatorSelect, true);
numeratorSelect.value = "max_organisation";

// --- Stat bound constraints: an addable/removable list of
// {field select, min input, max input} rows. A row with both inputs
// blank is simply never collected (see collectStatBounds) rather than
// needing its own explicit "disabled" state.

let statBoundRows = [];

function addStatBoundRow() {
    const row = document.createElement("div");
    row.className = "design-search-bound-row";

    const select = document.createElement("select");
    for (const [field, label] of BOUND_FIELDS) {
        const option = document.createElement("option");
        option.value = field;
        option.textContent = label;
        select.appendChild(option);
    }

    const minInput = document.createElement("input");
    minInput.type = "number";
    minInput.placeholder = "min";

    const maxInput = document.createElement("input");
    maxInput.type = "number";
    maxInput.placeholder = "max";

    const removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.className = "battalion-option";
    removeButton.textContent = "Remove";
    removeButton.addEventListener("click", () => {
        row.remove();
        statBoundRows = statBoundRows.filter((entry) => entry.row !== row);
    });

    row.append(select, minInput, maxInput, removeButton);
    document.getElementById("design-search-stat-bounds").appendChild(row);
    statBoundRows.push({ row, select, minInput, maxInput });
}

document.getElementById("design-search-add-bound-button").addEventListener("click", addStatBoundRow);

function collectStatBounds() {
    return statBoundRows
        .map(({ select, minInput, maxInput }) => ({
            field: select.value,
            min: minInput.value === "" ? null : Number(minInput.value),
            max: maxInput.value === "" ? null : Number(maxInput.value),
        }))
        .filter((bound) => bound.min !== null || bound.max !== null);
}

// --- Required/excluded battalions: reuses composition.js's own
// category-grouped picker look (.category-group > .battalion-option-list
// of .battalion-option buttons), but each button cycles through 5 states
// on repeated clicks instead of composition.js's own single-pick
// behavior - unselected -> "Required" (at least one instance, rest of the
// division stays free) -> "Dominant" (this type should be the single
// largest contributor to the whole division - Ollie's own distinction
// between "a division WITH a Marine battalion" and "a MARINE division")
// -> "Only" (added 2026-11-03, a step up from "Dominant" - every
// battalion in the division must be one of the "Only"-marked types, not
// merely the largest share) -> "Excluded" (added 2026-11-02, the inverse
// - never include this type at all, e.g. "make sure it doesn't include
// Rangers") -> back to unselected. Multiple battalions can each carry
// their own state at once (unlike composition.js's own per-column
// exclusivity), so this is a Map, not a single selection.

const battalions = JSON.parse(document.getElementById("battalion-data").textContent);
const categoryLabels = JSON.parse(document.getElementById("category-label-data").textContent);
const battalionsByCategory = {};
for (const battalion of battalions) {
    (battalionsByCategory[battalion.category] ??= []).push(battalion);
}

const BATTALION_MODE_LABELS = { include: "Required", dominant: "Dominant", only: "Only", exclude: "Excluded" };

const battalionModes = new Map(); // key -> "include" | "dominant" | "only" | "exclude"
const requiredBattalionsContainer = document.getElementById("design-search-required-battalions");

function cycleBattalionMode(key) {
    const current = battalionModes.get(key);
    if (current === undefined) {
        battalionModes.set(key, "include");
    } else if (current === "include") {
        battalionModes.set(key, "dominant");
    } else if (current === "dominant") {
        battalionModes.set(key, "only");
    } else if (current === "only") {
        battalionModes.set(key, "exclude");
    } else {
        battalionModes.delete(key);
    }
    renderRequiredBattalionPicker();
}

function renderRequiredBattalionPicker() {
    requiredBattalionsContainer.innerHTML = "";

    for (const [category, items] of Object.entries(battalionsByCategory)) {
        const group = document.createElement("div");
        group.className = "category-group";

        const heading = document.createElement("h3");
        heading.textContent = categoryLabels[category];
        group.appendChild(heading);

        const list = document.createElement("div");
        list.className = "battalion-option-list";

        for (const battalion of items) {
            const mode = battalionModes.get(battalion.key);
            const button = document.createElement("button");
            button.type = "button";
            button.className = "battalion-option" + (mode ? " filled" : "");
            button.title = "Click to require at least one, click again to make it the dominant type, click again to make it the ONLY type in the whole division, click again to exclude it entirely, click again to clear";
            button.textContent = mode ? `${battalion.name} (${BATTALION_MODE_LABELS[mode]})` : battalion.name;
            button.addEventListener("click", () => cycleBattalionMode(battalion.key));
            list.appendChild(button);
        }

        group.appendChild(list);
        requiredBattalionsContainer.appendChild(group);
    }
}

renderRequiredBattalionPicker();

// --- Exclude an entire category (added 2026-11-03) - e.g. "exclude all
// Armored Combat Support" - removes every battalion type in that
// category from the search, not just one type at a time like the picker
// above. Independent of it: a battalion can carry its own Required/
// Dominant/Only/Excluded state AND its whole category can separately be
// excluded here - any resulting contradiction (e.g. requiring a
// battalion whose own category is also excluded here) is caught
// server-side by the existing "unavailable_battalions" infeasibility
// check, same as every other required/excluded interaction already is.

const excludedCategories = new Set();
const excludedCategoriesContainer = document.getElementById("design-search-excluded-categories");

function toggleExcludedCategory(category) {
    if (excludedCategories.has(category)) {
        excludedCategories.delete(category);
    } else {
        excludedCategories.add(category);
    }
    renderExcludedCategoriesPicker();
}

function renderExcludedCategoriesPicker() {
    excludedCategoriesContainer.innerHTML = "";

    const list = document.createElement("div");
    list.className = "battalion-option-list";

    for (const [category, label] of Object.entries(categoryLabels)) {
        const isExcluded = excludedCategories.has(category);
        const button = document.createElement("button");
        button.type = "button";
        button.className = "battalion-option" + (isExcluded ? " filled" : "");
        button.title = "Click to exclude every battalion in this category entirely, click again to clear";
        button.textContent = isExcluded ? `${label} (Excluded)` : label;
        button.addEventListener("click", () => toggleExcludedCategory(category));
        list.appendChild(button);
    }

    excludedCategoriesContainer.appendChild(list);
}

renderExcludedCategoriesPicker();

const yearCutoffInput = document.getElementById("design-search-year-cutoff");

// Genuinely optional (added 2026-11-02, Ollie's own request) - a blank
// field (or anything that doesn't parse to a real number) is treated as
// "no limit," never as 0 or some other accidental value, and the Clear
// button gives an explicit one-click way back to blank rather than
// relying on backspacing through a number input's own spinner quirks.
document.getElementById("design-search-clear-year-cutoff-button").addEventListener("click", () => {
    yearCutoffInput.value = "";
});

// --- Require a Doctrine (added 2026-11-02, Phase 2 of the plan file's
// "AI Design Comparison - Phase 2" section) - only meaningful once "Let
// AI choose Doctrine" is checked, but collected regardless (the server
// already treats an empty/irrelevant required_doctrines list as a no-op
// when vary_doctrine is false, same "harmless either way" convention
// every other optional field here already follows). A single click
// toggles membership - no "dominant"/"exclude" modes here, since Ollie's
// own ask was only ever "require a specific doctrine."

const grandDoctrines = JSON.parse(document.getElementById("grand-doctrine-data").textContent);
const subdoctrines = JSON.parse(document.getElementById("subdoctrine-data").textContent);
const requiredDoctrineKeys = new Set();
const requiredDoctrinesContainer = document.getElementById("design-search-required-doctrines");

function doctrineName(key) {
    return grandDoctrines.find((d) => d.key === key)?.name ?? subdoctrines.find((d) => d.key === key)?.name ?? key;
}

function toggleRequiredDoctrine(key) {
    if (requiredDoctrineKeys.has(key)) {
        requiredDoctrineKeys.delete(key);
    } else {
        requiredDoctrineKeys.add(key);
    }
    renderRequiredDoctrinePicker();
}

function renderDoctrineGroup(heading, items) {
    const group = document.createElement("div");
    group.className = "category-group";

    const headingEl = document.createElement("h4");
    headingEl.textContent = heading;
    group.appendChild(headingEl);

    const list = document.createElement("div");
    list.className = "battalion-option-list";
    for (const item of items) {
        const required = requiredDoctrineKeys.has(item.key);
        const button = document.createElement("button");
        button.type = "button";
        button.className = "battalion-option" + (required ? " filled" : "");
        button.textContent = required ? `${item.name} (Required)` : item.name;
        button.addEventListener("click", () => toggleRequiredDoctrine(item.key));
        list.appendChild(button);
    }
    group.appendChild(list);
    return group;
}

function renderRequiredDoctrinePicker() {
    requiredDoctrinesContainer.innerHTML = "";
    requiredDoctrinesContainer.appendChild(renderDoctrineGroup("Grand Doctrines", grandDoctrines));
    requiredDoctrinesContainer.appendChild(renderDoctrineGroup("Subdoctrines", subdoctrines));
}

renderRequiredDoctrinePicker();

const varyDoctrineCheckbox = document.getElementById("design-search-vary-doctrine");
const useSavedTankDesignsCheckbox = document.getElementById("design-search-use-tank-designs");

function getConstraints() {
    const cutoffValue = Number(yearCutoffInput.value);
    const required = [];
    const excluded = [];
    for (const [key, mode] of battalionModes.entries()) {
        if (mode === "exclude") {
            excluded.push(key);
        } else {
            required.push({ key, mode });
        }
    }
    return {
        stat_bounds: collectStatBounds(),
        required_battalions: required,
        excluded_battalions: excluded,
        excluded_categories: [...excludedCategories],
        required_doctrines: [...requiredDoctrineKeys],
        research_year_cutoff: yearCutoffInput.value === "" || Number.isNaN(cutoffValue) ? null : cutoffValue,
    };
}

// --- "Let AI choose Officer Corps" (added 2026-11-02) - when checked,
// Officer Corps picks become a real search variable (logic/design_search.py's
// vary_army_spirits) instead of staying fixed to whatever's live.
const varyArmySpiritsCheckbox = document.getElementById("design-search-vary-army-spirits");

// --- Generating and rendering results.

const generateButton = document.getElementById("design-search-generate-button");
const resultsEl = document.getElementById("design-search-results");

function renderResultCard(candidate, rank) {
    const card = document.createElement("div");
    card.className = "design-result-card";

    const header = document.createElement("div");
    header.className = "design-result-header";
    header.innerHTML = `<span class="design-result-rank">#${rank}</span>
        <span class="design-result-score">Score: ${formatNumber(candidate.score)}</span>`;

    const loadButton = document.createElement("button");
    loadButton.type = "button";
    loadButton.className = "battalion-option";
    loadButton.textContent = "Load Design";
    loadButton.title = "Applies everything this search actually varied - Composition, Officer Corps, and Doctrine";
    loadButton.addEventListener("click", () => {
        restoreCompositionState(candidate.columns);
        restoreSupportState(candidate.support_slots);
        restoreRegimentalSupportState(candidate.regimental_support_by_column);
        // Both always present (even when this search didn't vary them -
        // generate_best_designs still returns the fixed baseline in each
        // shape), so Load is a consistent full apply either way - Ollie's
        // own call, 2026-11-02.
        restoreArmySpiritsState(candidate.army_spirits);
        restoreDoctrineState(candidate.doctrine);
        document.querySelector('.page-tab[data-view="composition-view"]').click();
    });
    header.appendChild(loadButton);

    const toggleButton = document.createElement("button");
    toggleButton.type = "button";
    toggleButton.className = "stat-preview-toggle";
    toggleButton.textContent = "Show Full Stats";
    const statsPanel = document.createElement("div");
    statsPanel.hidden = true;
    toggleButton.addEventListener("click", () => {
        statsPanel.hidden = !statsPanel.hidden;
        toggleButton.textContent = statsPanel.hidden ? "Show Full Stats" : "Hide Full Stats";
        if (!statsPanel.hidden && statsPanel.childElementCount === 0) {
            renderStats(statsPanel, candidate.stats);
        }
    });
    header.appendChild(toggleButton);

    const summary = document.createElement("p");
    summary.className = "design-result-summary";
    summary.textContent = compositionSummary(candidate);

    card.appendChild(header);
    card.appendChild(summary);
    card.appendChild(statsPanel);
    return card;
}

async function generateDesigns() {
    // The current Composition selection is never read here - the search
    // starts fresh from what's unlocked, not from whatever's currently
    // placed (it's a design search, not an optimizer tweaking the live
    // division).
    generateButton.disabled = true;
    generateButton.textContent = "Generating…";
    resultsEl.innerHTML = "";

    const constraints = getConstraints();

    // Phase 3 (added 2026-11-02) - per the plan file's own scope finding,
    // tank_designs never needed to become a new search dimension: it's
    // always been forwarded as fixed context, and calculate_division_stats
    // already prioritizes a saved template over tier-based equipment for
    // any item that needs it, regardless of which battalions the search
    // happens to choose. The only thing actually missing was a way to
    // turn that off for one search, to see what's achievable with
    // default equipment alone - this is that toggle, nothing more.
    const divisionContext = getCurrentDivisionContext();
    if (!useSavedTankDesignsCheckbox.checked) {
        divisionContext.tank_designs = null;
    }

    try {
        const response = await fetch("/api/design-search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                numerator: numeratorSelect.value,
                denominator: denominatorSelect.value || null,
                constraints,
                vary_army_spirits: varyArmySpiritsCheckbox.checked,
                vary_doctrine: varyDoctrineCheckbox.checked,
                ...divisionContext,
            }),
        });

        if (!response.ok) {
            // A server-side error (e.g. a 500) still has a body, but it's
            // an HTML traceback page, not JSON - report the status instead
            // of letting response.json() throw its own, less useful error.
            throw new Error(`Server returned ${response.status}`);
        }

        const { candidates, infeasible_reason: infeasibleReason } = await response.json();

        if (candidates.length === 0) {
            const sentences = infeasibleReason ? describeInfeasibleReason(infeasibleReason) : [];
            resultsEl.innerHTML = sentences.length > 0
                ? `<div class="stats-warning">No design satisfied every constraint:<ul>${sentences.map((s) => `<li>${s}</li>`).join("")}</ul></div>`
                : `<p class="section-caption">No candidates found - either nothing is unlocked yet, or the chosen "per" stat was 0 for every design generated. Try a different metric.</p>`;
            return;
        }

        candidates.forEach((candidate, index) => {
            resultsEl.appendChild(renderResultCard(candidate, index + 1));
        });
    } catch (error) {
        // Previously this had no catch at all - any thrown error (a
        // network hiccup, a malformed response) was swallowed by the
        // finally block below with zero visible feedback: the button
        // would just flash "Generating…" and silently revert, which is
        // exactly what "the button does nothing" looks like. Now it's
        // impossible for a failure here to be invisible.
        console.error("Design search failed:", error);
        resultsEl.innerHTML = `<p class="stats-warning">Something went wrong generating designs: ${error.message}. Check the browser console for details.</p>`;
    } finally {
        generateButton.disabled = false;
        generateButton.textContent = "Generate Designs";
    }
}

generateButton.addEventListener("click", generateDesigns);
