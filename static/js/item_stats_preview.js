// Lets any picker option show its own stats BEFORE it's selected - a small
// toggle next to the option; clicking/tapping it opens the stat panel,
// clicking/tapping it again closes it (a real toggle, not a hover reveal -
// an earlier hover-to-open version was dropped 2026-10-27 after Ollie found
// it popped open just from moving the mouse near the row, and never gave a
// clean way back to closed). One shared module for Composition's 3 pickers
// and Tank Designer's chassis/tier/role/module pickers, built once rather than
// duplicating the fetch/render/toggle logic 4 times - see Specification.md's
// "JS may duplicate a *simple* Python rule" precedent; this isn't that, it's
// plain DOM wiring, the same category of thing composition.js's
// bindLongPress already shares across callers.
//
// The default view (just the option's name) never changes - nothing here
// adds latency to opening a dialog or rendering a list. Each caller fires
// exactly ONE batch fetch covering every option it's about to show, and
// passes that single shared Promise into every attachStatPreview call for
// that render - a stat block is only actually drawn once a given option is
// first expanded (lazy), and cached after that so re-toggling never re-fetches
// or re-renders.

import { KEY_STAT_FIELDS, formatNumber } from "./stats.js";

// --- Global show/hide-all toggle (added 2026-11-01, see
// static/js/preview_toggle.js for the button that drives this) ---
// A single page-level flag, read by every attachStatPreview/
// attachBonusPreview call at the moment it's created, so a freshly-built
// preview always starts in whatever state the toggle last left. Flipping
// it dispatches a CustomEvent rather than keeping a live registry of
// every mounted instance - Research/Special Projects/Doctrine (the only
// previews that live outside a modal <dialog>, so they're the only ones
// that could even be visible while this button is clicked - a <dialog>
// blocks interacting with the rest of the page while open) each listen
// for it and simply re-render, which rebuilds every one of their preview
// wrappers from scratch against the new flag. Composition/Support
// Companies/Regimental Support/Tank Designer need no listener at all -
// their previews only ever get built inside a dialog's own openPicker,
// which already reads the flag fresh every time it's opened.
let allPreviewsExpanded = false;

export function toggleAllPreviews() {
    allPreviewsExpanded = !allPreviewsExpanded;
    document.dispatchEvent(new CustomEvent("all-previews-toggled"));
    return allPreviewsExpanded;
}

export async function fetchItemStatPreviews(items, context) {
    const response = await fetch("/api/item-stats", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ items, ...context }),
    });
    return response.json();
}

export async function fetchTankDesignPreviews(baseDesign, candidates) {
    const response = await fetch("/api/tank-designer/preview-stats", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...baseDesign, candidates }),
    });
    return response.json();
}

// Exported 2026-11-03 for the Patch Impact Preview feature
// (static/js/patch_preview.js) - a pure function (only touches its own
// parameters, formatNumber, and formatSignedNumber below; never reads
// allPreviewsExpanded or anything else module-private), so it's safe to
// call standalone from outside this module's own attachStatPreview flow.
export function renderStatBlock(panel, stats, statFields, baselineStats) {
    panel.innerHTML = "";

    // Composition's own stat shape (calculate_item_stats) always sets this
    // explicitly to true/false - a real "equipment data gap" warning. Tank
    // Designer's own shape (calculate_tank_design_stats) never has this
    // field at all, which made `!stats.combat_stats_available` true for
    // EVERY Tank Designer preview regardless of the real data (a real bug
    // Ollie found, 2026-11-02 - every tank/module info box always showed
    // "not available"). Checking `=== false` only fires the warning when a
    // caller actually SAYS there's a gap, not merely when the field is
    // absent.
    if (stats.combat_stats_available === false) {
        const warning = document.createElement("p");
        warning.className = "stat-preview-warning";
        warning.textContent = "Equipment stats not available for this item yet.";
        panel.appendChild(warning);
        return;
    }

    // baselineStats (Tank Designer's 4 pickers only, added 2026-11-02): when
    // given, only show fields a candidate would actually CHANGE relative to
    // the design as it currently stands - Ollie's own report that e.g.
    // Sloped Armor's info box showed every stat, including ones it has no
    // effect on (soft_attack staying put), unlike every other preview in
    // this app, which only ever lists what it actually bears on. Compared
    // via the same rounding `formatNumber` itself uses, so two values that
    // only differ beyond display precision don't show as a "change" with
    // nothing visibly different about them. A field missing from one side
    // (e.g. a role conversion that drops air_attack entirely) counts as 0
    // on that side, matching how the rest of this app already treats an
    // absent stat field.
    const fieldsToShow = baselineStats
        ? statFields.filter(([field]) => formatNumber(stats[field] ?? 0) !== formatNumber(baselineStats[field] ?? 0))
        : statFields;

    if (fieldsToShow.length === 0) {
        const none = document.createElement("p");
        none.className = "stat-preview-warning";
        none.textContent = "No change to these stats.";
        panel.appendChild(none);
        return;
    }

    for (const [field, label] of fieldsToShow) {
        const total = formatNumber(stats[field] ?? 0);
        // When diffing against a baseline (Tank Designer's 4 pickers),
        // show how much THIS candidate changes the stat alongside the
        // resulting total, e.g. "21 (+2)" - Ollie's own follow-up request
        // (2026-11-02), keeping the existing label/value row layout rather
        // than adding a third element per stat.
        const valueText = baselineStats
            ? `${total} (${formatSignedNumber(total - formatNumber(baselineStats[field] ?? 0))})`
            : total;
        panel.innerHTML += `<div class="stat-preview-panel-item">
            <span class="stat-preview-panel-label">${label}</span>
            <span class="stat-preview-panel-value">${valueText}</span>
        </div>`;
    }
}

// Exported alongside renderStatBlock above, same reason.
export function formatSignedNumber(value) {
    const rounded = formatNumber(value);
    return rounded >= 0 ? `+${rounded}` : `${rounded}`;
}

// Wraps optionButton (not yet appended anywhere) in a sibling toggle +
// lazily-rendered panel, and returns the WRAPPER node - callers append the
// wrapper instead of optionButton directly.
//
// previewsPromise: the single shared batch-fetch Promise for this dialog/
// list render, resolving to {[lookupKey]: entry}.
// lookupKey: this option's own key into that resolved map.
// getStats: pulls the stat dict out of one resolved entry - defaults to the
// entry itself (Composition's /api/item-stats shape); Tank Designer passes
// (entry) => entry.stats, since /api/tank-designer/preview-stats wraps each
// candidate's stats alongside its violations.
// statFields: an array of [field, label] pairs to render, defaulting to
// Division Stats' own KEY_STAT_FIELDS (Composition's 3 pickers all use this
// shape) - Tank Designer passes its own field list instead, since its stats
// use different field names entirely (e.g. "maximum_speed" not "max_speed",
// "build_cost_ic" not "production_cost", no "combat_width" at all).
// baselineLookupKey: optional - another key into the same resolved map,
// looked up and passed to renderStatBlock as the "current design" to diff
// against (see renderStatBlock's own comment). Composition's 3 pickers
// never pass this - an item being considered isn't replacing anything, so
// its full stat block is the relevant thing to show, not a delta. Tank
// Designer's 4 pickers do, each including a `{"type": "baseline"}`
// candidate in their own batch fetch for exactly this purpose.
export function attachStatPreview(optionButton, {
    previewsPromise, lookupKey, getStats = (entry) => entry, statFields = KEY_STAT_FIELDS,
    baselineLookupKey,
}) {
    const wrapper = document.createElement("div");
    wrapper.className = "option-with-preview";

    const row = document.createElement("div");
    row.className = "option-with-preview-row";
    row.appendChild(optionButton);

    const toggle = document.createElement("button");
    toggle.type = "button";
    toggle.className = "stat-preview-toggle";
    toggle.setAttribute("aria-expanded", "false");
    toggle.title = "Show stats";
    toggle.textContent = "ⓘ";
    row.appendChild(toggle);

    const panel = document.createElement("div");
    panel.className = "stat-preview-panel";

    wrapper.appendChild(row);
    wrapper.appendChild(panel);

    let expanded = false;
    let rendered = false;

    function setExpanded(value) {
        expanded = value;
        panel.hidden = !expanded;
        toggle.setAttribute("aria-expanded", String(expanded));
        if (expanded && !rendered) {
            rendered = true;
            panel.textContent = "Loading…";
            previewsPromise.then((result) => {
                const baselineStats = baselineLookupKey !== undefined
                    ? getStats(result[baselineLookupKey])
                    : undefined;
                renderStatBlock(panel, getStats(result[lookupKey]), statFields, baselineStats);
            });
        }
    }

    toggle.addEventListener("click", () => setExpanded(!expanded));
    setExpanded(allPreviewsExpanded);

    return wrapper;
}

// --- Raw-bonus-data preview (Research/Doctrine/Special Projects, added
// 2026-11-01) ---
// A simpler sibling to attachStatPreview above: a technology/doctrine/
// special-project entry already carries its own unit_bonuses/modifiers/
// unlocks data right in the page (technology-data/grand-doctrine-data/
// subdoctrine-data/special-projects-data script tags) - there's no
// computed stat to resolve server-side, so this renders synchronously
// from whatever's already loaded, no fetch/Promise involved. Ollie's own
// scope call (AskUserQuestion, 2026-11-01): show the item's raw bonus
// data, not a computed division-wide delta.

const BONUS_ITEM_NAME_LOOKUP = (() => {
    const lookup = {};
    for (const id of ["battalion-data", "support-company-data", "regimental-support-data", "tank-module-data"]) {
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

// Officer Corps' own "available" list (added 2026-11-02) is a list of
// doctrine/subdoctrine KEYS, not category/item keys - a separate lookup
// from the one above, built the same way from the grand-doctrine-data/
// subdoctrine-data tags already in the page.
const DOCTRINE_NAME_LOOKUP = (() => {
    const lookup = {};
    for (const id of ["grand-doctrine-data", "subdoctrine-data"]) {
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

function doctrineOrSubdoctrineName(key) {
    return DOCTRINE_NAME_LOOKUP[key] ?? humanizeBonusKey(key);
}

// Fields known to be flat adds rather than percentages - mirrors
// logic/stats.py's own small, stable, documented flat-field sets
// (_DOCTRINE_FLAT_FIELDS/_APPLICABLE_TECH_FIELDS's "max_organisation"
// entry) rather than re-deriving the rule; everything else defaults to
// percentage, matching how the overwhelming majority of unit_bonuses/
// modifiers fields in this game actually are.
const FLAT_BONUS_FIELDS = new Set(["max_organisation", "combat_width", "max_strength", "suppression_factor"]);

function humanizeBonusKey(key) {
    const prefix = ["category_", "tactic_"].find((p) => key.startsWith(p));
    const stripped = prefix ? key.slice(prefix.length) : key;
    return stripped.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

// Real in-game display names for a handful of modifier fields whose
// humanized key reads nothing like the actual in-game wording - confirmed
// field by field against a real tooltip, not guessed (e.g.
// army_strength_factor's own tooltip literally reads "HP: +10.00%", not
// "Army Strength Factor" - see logic/army_spirits.py's
// active_army_strength_factor). Falls back to humanizeBonusKey's generic
// title-casing for every field without an override here.
const BONUS_FIELD_DISPLAY_NAMES = {
    army_strength_factor: "HP",
    // Added 2026-11-03 once the remaining 7 Officer Corps formula items
    // were confirmed via real in-game tooltips - same "use the exact real
    // wording, not a generic title-case guess" standard as army_strength_factor
    // above (e.g. ap_attack's own real wording is "Piercing" everywhere
    // else in this app too, not "Ap Attack").
    breakthrough_factor: "Breakthrough",
    supply_consumption_factor: "Supply Consumption",
    army_speed_factor: "Divisions Speed",
    ap_attack: "Piercing",
    build_cost_ic: "Production Cost",
};

function bonusFieldLabel(field) {
    return BONUS_FIELD_DISPLAY_NAMES[field] ?? humanizeBonusKey(field);
}

function bonusTargetName(key) {
    return BONUS_ITEM_NAME_LOOKUP[key] ?? humanizeBonusKey(key);
}

function formatBonusFieldValue(field, value, forcePercentage = false) {
    const sign = value >= 0 ? "+" : "";
    if (FLAT_BONUS_FIELDS.has(field)) {
        return `${sign}${formatNumber(value)}`;
    }
    // forcePercentage (equipment_bonus only, see appendBonusFieldLines'
    // own comment) skips the magnitude heuristic below - needed because
    // Direct Fire Support's real ap_attack: 1 is a confirmed +100%, not a
    // flat +1, which the `abs(value) < 1` guess would otherwise get wrong.
    if (forcePercentage || Math.abs(value) < 1) {
        return `${sign}${formatNumber(value * 100)}%`;
    }
    return `${sign}${formatNumber(value)}`;
}

// One <li> per field in a bonus's own stat dict - handles the two nested
// shapes a dict can carry (battalion_mult: a list of aura dicts; a
// terrain key like "jungle": another {attack, defence, movement} dict)
// alongside plain flat/percentage fields. forcePercentage (added
// 2026-11-03): Officer Corps' own equipment_bonus fields are confirmed
// 100% percentage via real in-game tooltips (unlike unit_bonuses, whose
// flat-vs-percentage split still relies on the `abs(value) < 1` guess
// below for anything not in FLAT_BONUS_FIELDS) - a value of exactly 1
// (e.g. Direct Fire Support's own ap_attack: 1, really "+100%") would
// otherwise be guessed as a flat +1.
function appendBonusFieldLines(list, statDict, forcePercentage = false) {
    for (const [field, value] of Object.entries(statDict)) {
        if (field === "battalion_mult") {
            for (const aura of value) {
                const { category, ...auraFields } = aura;
                for (const [auraField, auraValue] of Object.entries(auraFields)) {
                    const li = document.createElement("li");
                    li.textContent = `Aura to ${bonusTargetName(category)}: ${bonusFieldLabel(auraField)} ${formatBonusFieldValue(auraField, auraValue, forcePercentage)}`;
                    list.appendChild(li);
                }
            }
        } else if (value && typeof value === "object") {
            for (const [nestedField, nestedValue] of Object.entries(value)) {
                const li = document.createElement("li");
                li.textContent = `${bonusFieldLabel(field)} terrain: ${bonusFieldLabel(nestedField)} ${formatBonusFieldValue(nestedField, nestedValue, forcePercentage)}`;
                list.appendChild(li);
            }
        } else {
            const li = document.createElement("li");
            li.textContent = `${bonusFieldLabel(field)}: ${formatBonusFieldValue(field, value, forcePercentage)}`;
            list.appendChild(li);
        }
    }
}

// effectsList: an array of {heading?, unit_bonuses?, modifiers?,
// unlocks_subunits?, unlocks_equipment_modules?} objects - the exact
// "effects" shape every Research/Doctrine/Special Project entry already
// uses, plus an optional `heading` to label an entry when several are
// shown together in one panel (e.g. a grand doctrine's own immediate
// effects followed by every track's own milestone, each labeled by track
// name - doctrines.js's own grand-doctrine-button preview).
function renderBonusPanel(panel, effectsList) {
    panel.innerHTML = "";

    const nonEmpty = effectsList.filter(
        (effects) =>
            effects &&
            ((effects.unit_bonuses && Object.keys(effects.unit_bonuses).length) ||
                (effects.modifiers && Object.keys(effects.modifiers).length) ||
                (effects.equipment_bonus && Object.keys(effects.equipment_bonus).length) ||
                (effects.unlocks_subunits && effects.unlocks_subunits.length) ||
                (effects.unlocks_equipment_modules && effects.unlocks_equipment_modules.length) ||
                (effects.available && effects.available.length) ||
                (effects.enable_tactics && effects.enable_tactics.length))
    );

    if (nonEmpty.length === 0) {
        const none = document.createElement("p");
        none.className = "stat-preview-warning";
        none.textContent = "No modeled bonuses.";
        panel.appendChild(none);
        return;
    }

    for (const effects of nonEmpty) {
        // An optional group heading (e.g. "Infantry Milestone") distinguishing
        // this entry from the others in the list - used when effectsList
        // mixes several distinct sources in one panel (a grand doctrine's
        // own immediate effects plus every track's milestone). Entries with
        // no heading (the common case - a single technology/subdoctrine/
        // reward/project) render exactly as before.
        if (effects.heading) {
            const groupHeading = document.createElement("p");
            groupHeading.className = "stat-preview-panel-heading";
            groupHeading.textContent = effects.heading;
            panel.appendChild(groupHeading);
        }

        // Officer Corps' Army Spirits (added 2026-11-02) - which doctrine
        // or subdoctrine unlocks this spirit. Real HOI4's `has_doctrine`
        // matches either, OR semantics (only one needs to be active) -
        // shown here, up front, same spot Research's own "🔒 Required by"
        // reason occupies, since it's the unlock requirement rather than
        // a bonus this spirit itself grants.
        if (effects.available && effects.available.length > 0) {
            const heading = document.createElement("p");
            heading.className = "stat-preview-panel-sub-heading";
            heading.textContent = "Requires Doctrine (any of)";
            panel.appendChild(heading);

            const list = document.createElement("ul");
            list.className = "stat-preview-bonus-list";
            for (const key of effects.available) {
                const li = document.createElement("li");
                li.textContent = doctrineOrSubdoctrineName(key);
                list.appendChild(li);
            }
            panel.appendChild(list);
        }

        for (const [target, statDict] of Object.entries(effects.unit_bonuses ?? {})) {
            const heading = document.createElement("p");
            heading.className = "stat-preview-panel-sub-heading";
            heading.textContent = bonusTargetName(target);
            panel.appendChild(heading);

            const list = document.createElement("ul");
            list.className = "stat-preview-bonus-list";
            appendBonusFieldLines(list, statDict);
            panel.appendChild(list);
        }

        if (effects.modifiers && Object.keys(effects.modifiers).length > 0) {
            const heading = document.createElement("p");
            heading.className = "stat-preview-panel-sub-heading";
            heading.textContent = "Modifiers";
            panel.appendChild(heading);

            const list = document.createElement("ul");
            list.className = "stat-preview-bonus-list";
            appendBonusFieldLines(list, effects.modifiers);
            panel.appendChild(list);
        }

        // Officer Corps' Army Spirits (added 2026-11-02, applied
        // 2026-11-03 once Ollie's own real in-game tooltips confirmed
        // every one of these is a percentage bonus on the target
        // equipment's own stat - see logic/army_spirits.py's
        // active_equipment_bonuses). Still shown as its own labeled
        // sub-section (distinct from unit_bonuses above, which targets an
        // item/category rather than an equipment family) since it's a
        // structurally different mechanism, not because it's inert.
        for (const [target, statDict] of Object.entries(effects.equipment_bonus ?? {})) {
            const heading = document.createElement("p");
            heading.className = "stat-preview-panel-sub-heading";
            heading.textContent = `${bonusTargetName(target)} (Equipment Bonus)`;
            panel.appendChild(heading);

            const list = document.createElement("ul");
            list.className = "stat-preview-bonus-list";
            appendBonusFieldLines(list, statDict, true);
            panel.appendChild(list);
        }

        // enable_tactics (Doctrine only - grand doctrine milestones and
        // subdoctrine effects/rewards) was compiled from the very first
        // Doctrine build (data/doctrines.py's own header) but never
        // rendered anywhere - a real gap, not a deliberate deferral, found
        // 2026-11-03 when Ollie reported several subdoctrines (Armored
        // Spearhead, Armored Infantry Support) looked like they had no
        // data at all: their own immediate effect is ONLY a tactic unlock,
        // so with nothing else to show, the panel showed nothing.
        if (effects.enable_tactics && effects.enable_tactics.length > 0) {
            const heading = document.createElement("p");
            heading.className = "stat-preview-panel-sub-heading";
            heading.textContent = "Unlocks Combat Tactic";
            panel.appendChild(heading);

            const list = document.createElement("ul");
            list.className = "stat-preview-bonus-list";
            for (const tactic of effects.enable_tactics) {
                const li = document.createElement("li");
                li.textContent = humanizeBonusKey(tactic);
                list.appendChild(li);
            }
            panel.appendChild(list);
        }

        const unlocks = [...(effects.unlocks_subunits ?? []), ...(effects.unlocks_equipment_modules ?? [])];
        if (unlocks.length > 0) {
            const heading = document.createElement("p");
            heading.className = "stat-preview-panel-sub-heading";
            heading.textContent = "Unlocks";
            panel.appendChild(heading);

            const list = document.createElement("ul");
            list.className = "stat-preview-bonus-list";
            for (const key of unlocks) {
                const li = document.createElement("li");
                li.textContent = bonusTargetName(key);
                list.appendChild(li);
            }
            panel.appendChild(list);
        }
    }
}

// Wraps rowElement in a sibling toggle + lazily-rendered panel, mirroring
// attachStatPreview's own structure, but synchronous (no fetch) since this
// data is already loaded in the page. Returns the WRAPPER node - callers
// append the wrapper instead of rowElement directly.
//
// getEffectsList: called fresh on every expand (not cached) rather than
// once up front - every caller's own renderAll() already rebuilds this
// whole row tree on every state change, so there's no stale-data risk to
// guard against, and re-reading a few already-loaded local objects is
// free.
export function attachBonusPreview(rowElement, getEffectsList) {
    const wrapper = document.createElement("div");
    wrapper.className = "option-with-preview";

    const row = document.createElement("div");
    row.className = "option-with-preview-row";
    row.appendChild(rowElement);

    const toggle = document.createElement("button");
    toggle.type = "button";
    toggle.className = "stat-preview-toggle";
    toggle.setAttribute("aria-expanded", "false");
    toggle.title = "Show bonuses";
    toggle.textContent = "ⓘ";
    row.appendChild(toggle);

    const panel = document.createElement("div");
    panel.className = "stat-preview-panel";

    wrapper.appendChild(row);
    wrapper.appendChild(panel);

    let expanded = false;

    function setExpanded(value) {
        expanded = value;
        panel.hidden = !expanded;
        toggle.setAttribute("aria-expanded", String(expanded));
        if (expanded) {
            renderBonusPanel(panel, getEffectsList());
        }
    }

    toggle.addEventListener("click", () => setExpanded(!expanded));
    setExpanded(allPreviewsExpanded);

    return wrapper;
}
