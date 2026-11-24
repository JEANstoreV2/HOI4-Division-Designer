import { attachStatPreview, fetchTankDesignPreviews } from "./item_stats_preview.js";

// A sentinel id for the one extra, non-real candidate each of the 4
// previews below adds to its own batch fetch - `{"type": "baseline"}`
// resolves to the design exactly as it currently stands (see
// logic/tank_designer.py's build_candidate_design), giving each preview
// something to diff against so it only shows what a candidate would
// actually CHANGE, matching every other preview in this app (added
// 2026-11-02, see item_stats_preview.js's own comments).
const BASELINE_CANDIDATE_ID = "__baseline__";

// JS mirror of logic/tank_designer.py's pure lookup helpers - see that
// module for the authoritative, tested version. Only the cheap, per-slot
// filtering rules are mirrored here (category legality, allow/forbid
// equipment type, named/category count limits) so the module picker dialog
// can offer just the legal choices, the same "picker only lists what's
// actually selectable" convention support_companies.js/doctrines.js already
// use. The two heavier calculations - full validate_design (including the
// rarer turret-vs-category cross-slot rule) and calculate_tank_design_stats
// itself - are NOT duplicated here; every change re-fetches both from the
// new POST /api/tank-designer/stats route instead, mirroring stats.js's own
// "complex aggregation stays server-side" precedent for calculate_division_stats.

export function equipmentTypeTags(roleKey, roles) {
    if (!roleKey) {
        return new Set(["armor"]);
    }
    const role = roles.find((r) => r.key === roleKey);
    return new Set(["armor", role.role]);
}

// Widens (union) each slot's allowed categories - see
// logic/tank_designer.py's matching function for why this is a union, not
// a replace (a real turret's own gun-size category ADDS to what the
// chassis's base slot already allowed; it doesn't take away the smaller
// category a plain, role-less tank actually needs). A Flame role is the one
// exception to the union: it locks main_armament_slot to tank_flamethrower
// only, a hidden role-level restriction found nowhere in the source files -
// see logic/tank_designer.py's matching docstring.
export function effectiveModuleSlots(chassis, chosenModules, modulesByKey, roleKey, roles) {
    const effective = {};
    for (const [slotName, slot] of Object.entries(chassis.module_slots)) {
        effective[slotName] = [...slot.allowed_module_categories];
    }

    for (const [slotName, moduleKey] of Object.entries(chosenModules)) {
        if (!moduleKey) {
            continue;
        }
        const module = modulesByKey[moduleKey];
        if (!module) {
            continue;
        }
        for (const [targetSlot, categories] of Object.entries(module.allowed_module_categories ?? {})) {
            if (targetSlot === slotName) {
                continue;
            }
            if (targetSlot in effective) {
                for (const category of categories) {
                    if (!effective[targetSlot].includes(category)) {
                        effective[targetSlot].push(category);
                    }
                }
            }
        }
    }

    const role = roleKey ? roles.find((r) => r.key === roleKey) : null;
    if (role && role.role === "flame" && "main_armament_slot" in effective) {
        effective.main_armament_slot = ["tank_flamethrower"];
    }

    return effective;
}

// Mirrors logic/tank_designer.py's max_tick_level.
export function maxTickLevel(upgrade, researched) {
    const checkpoints = [...upgrade.level_requirements].sort((a, b) => a.level - b.level);
    for (const checkpoint of checkpoints) {
        if (!researched.has(checkpoint.tech)) {
            return checkpoint.level - 1;
        }
    }
    return upgrade.max_level;
}

// --- UI layer: the Tank Designer tab itself. ---

const tankChassis = JSON.parse(document.getElementById("tank-chassis-data").textContent);
const tankRoles = JSON.parse(document.getElementById("tank-role-data").textContent);
const tankModules = JSON.parse(document.getElementById("tank-module-data").textContent);
const tankUpgrades = JSON.parse(document.getElementById("tank-upgrade-data").textContent);
const alwaysUnlockedModules = JSON.parse(document.getElementById("always-unlocked-module-data").textContent);
const technologies = JSON.parse(document.getElementById("technology-data").textContent);
const specialProjects = JSON.parse(document.getElementById("special-projects-data").textContent);

const chassisByKey = Object.fromEntries(tankChassis.map((c) => [c.key, c]));
const roleByKey = Object.fromEntries(tankRoles.map((r) => [r.key, r]));
const moduleByKey = Object.fromEntries(tankModules.map((m) => [m.key, m]));
const upgradeByKey = Object.fromEntries(tankUpgrades.map((u) => [u.key, u]));

// Kept in sync via research-changed/special-projects-changed, same
// seed-from-"nothing done yet" baseline every other file starts from -
// several real Tank Designer modules (e.g. Land Cruiser's own naval guns)
// are gated directly by a Special Project's own completion, separate from
// anything a gated technology unlocks. See data/special_projects.py's
// header.
let researched = new Set();
let completedSpecialProjects = new Set();
let unlockedModules = new Set(alwaysUnlockedModules);
document.addEventListener("research-changed", (event) => {
    researched = new Set(event.detail.researched);
    unlockedModules = unlockedModuleKeys(researched, completedSpecialProjects);
    renderModuleGrid();
    renderTickList();
    refreshStats();
});
document.addEventListener("special-projects-changed", (event) => {
    completedSpecialProjects = event.detail.completed;
    unlockedModules = unlockedModuleKeys(researched, completedSpecialProjects);
    renderModuleGrid();
    renderTickList();
    refreshStats();
});

function unlockedModuleKeys(researchedSet, completedSpecialProjectsSet) {
    const unlocked = new Set(alwaysUnlockedModules);
    for (const tech of technologies) {
        if (!researchedSet.has(tech.key)) {
            continue;
        }
        for (const key of tech.unlocks_equipment_modules ?? []) {
            unlocked.add(key);
        }
    }
    for (const project of specialProjects) {
        if (!completedSpecialProjectsSet.has(project.key)) {
            continue;
        }
        for (const key of project.unlocks_equipment_modules) {
            unlocked.add(key);
        }
    }
    return unlocked;
}

// The chassis's tick types live only on whichever tier entry actually lists
// them (its lowest tier, per data/tank_chassis.py's header) - applicable
// regardless of which tier is currently selected, since ticks are a
// mechanic layered on the chassis, not on one specific tier's stat block.
function chassisTicks(chassis) {
    const tierWithUpgrades = chassis.tiers.find((t) => t.upgrades.length > 0);
    return tierWithUpgrades ? tierWithUpgrades.upgrades : [];
}

function labelWords(text) {
    return text
        .split("_")
        .map((word) => (word.toLowerCase() === "lc" ? "LC" : word[0].toUpperCase() + word.slice(1)))
        .join(" ");
}

function slotLabel(slotName) {
    return labelWords(slotName.split("_").filter((part) => part !== "slot").join("_"));
}

function fieldLabel(field) {
    return labelWords(field);
}

// fuel_capacity (Expanded Fuel Tank / Internal Fuel Tanks) is real,
// correctly-transcribed HOI4 module data (tank_info/00_tank_modules_copy.txt),
// and calculate_tank_design_stats sums it like any other add_stats field -
// but nothing downstream ever reads it: it's not one of Division Stats'
// own DIVISION_SUM_FIELDS/DIVISION_AVERAGE_FIELDS/etc. (logic/stats.py),
// and this app models no operational-range/fuel-capacity mechanic anywhere
// else (same scope boundary as the already-closed-out "Essential Equipment
// Blocks" item). Ollie flagged the module's own description showing "Fuel
// Capacity: 100" as misleading, since picking it has zero further effect -
// labeled here rather than hidden, matching this project's own standing
// "compiled but unapplied" disclosure convention (e.g. Officer Corps'
// equipment_bonus entries).
const _INERT_FIELD_NOTES = {
    fuel_capacity: "not used elsewhere in this app",
};

function moduleName(key) {
    return moduleByKey[key]?.name ?? key;
}

function formatNumber(value) {
    return Math.round(value * 100) / 100;
}

// Reliability is the one stat HOI4 itself displays as a percentage rather
// than a raw decimal - every other field still uses formatNumber.
function formatStatValue(field, value) {
    if (field === "reliability") {
        return `${Math.round(value * 1000) / 10}%`;
    }
    return formatNumber(value);
}

// --- Design-in-progress state. ---

let chassisKey = tankChassis[0].key;
let tier = tankChassis[0].tiers[0].tier;
let roleKey = null;
let chosenModules = { ...tankChassis[0].default_modules };
let tickLevels = {};
const savedDesigns = {};

// The in-progress design, in the snake_case shape both
// /api/tank-designer/stats and /api/tank-designer/preview-stats take -
// shared by refreshStats() and every preview candidate list below, so a
// chassis/tier/role/module preview always merges onto exactly what's
// currently on screen.
function currentBaseDesign() {
    return {
        chassis_key: chassisKey,
        tier,
        role_key: roleKey,
        chosen_modules: chosenModules,
        tick_levels: tickLevels,
    };
}

function selectChassis(key) {
    chassisKey = key;
    const chassis = chassisByKey[key];
    tier = chassis.tiers[0].tier;
    roleKey = null;
    chosenModules = { ...chassis.default_modules };
    tickLevels = {};
    renderAll();
    refreshStats();
}

function selectTier(newTier) {
    tier = newTier;
    renderTierRow();
    renderRoleRow();
    refreshStats();
}

function selectRole(key) {
    roleKey = key;
    chosenModules = { ...chassisByKey[chassisKey].default_modules };
    renderAll();
    refreshStats();
}

function legalModulesForSlot(slotName) {
    const chassis = chassisByKey[chassisKey];
    const typeTags = equipmentTypeTags(roleKey, tankRoles);
    const effectiveSlots = effectiveModuleSlots(chassis, chosenModules, moduleByKey, roleKey, tankRoles);
    const allowedCategories = effectiveSlots[slotName];

    return tankModules.filter((module) => {
        if (!allowedCategories.includes(module.category)) {
            return false;
        }
        if (!unlockedModules.has(module.key)) {
            return false;
        }
        if (module.allow_equipment_type && !typeTags.has(module.allow_equipment_type)) {
            return false;
        }
        if ((module.forbid_equipment_type ?? []).some((t) => typeTags.has(t))) {
            return false;
        }
        if (module.forbid_equipment_type_exact_match) {
            const isExactMatch = typeTags.size === 1 && typeTags.has(module.forbid_equipment_type_exact_match);
            if (isExactMatch) {
                return false;
            }
        }

        const hypothetical = { ...chosenModules, [slotName]: module.key };
        const chosenKeys = Object.values(hypothetical).filter(Boolean);
        for (const limit of chassis.module_count_limits) {
            if ("module" in limit) {
                if (limit.module !== module.key) {
                    continue;
                }
                if (chosenKeys.filter((k) => k === limit.module).length > limit.max_count) {
                    return false;
                }
            } else {
                if (limit.category !== module.category) {
                    continue;
                }
                const count = chosenKeys.filter((k) => moduleByKey[k]?.category === limit.category).length;
                if (count > limit.max_count) {
                    return false;
                }
            }
        }

        return true;
    });
}

function describeViolation(v) {
    switch (v.type) {
        case "missing_required_module":
            return `${slotLabel(v.slot)}: no module chosen`;
        case "unknown_module":
            return `${slotLabel(v.slot)}: unknown module ${v.module}`;
        case "invalid_category":
            return `${slotLabel(v.slot)}: ${moduleName(v.module)} isn't allowed here`;
        case "requires_equipment_type":
            return `${moduleName(v.module)} requires a ${labelWords(v.required_type)} design`;
        case "forbidden_equipment_type":
            return `${moduleName(v.module)} isn't allowed on a ${v.forbidden_types.map(labelWords).join("/")} design`;
        case "forbidden_for_exact_equipment_type":
            return `${moduleName(v.module)} isn't allowed on a plain ${labelWords(v.equipment_type)} design`;
        case "category_forbidden_for_exact_equipment_type":
            return `${moduleName(v.module)} can't be combined with ${moduleName(v.via_module)} on a plain ${labelWords(v.equipment_type)} design`;
        case "count_limit_exceeded":
            return `Too many ${labelWords(v.limit)} (${v.count}/${v.max_count})`;
        default:
            return v.type;
    }
}

// --- Rendering. ---

const chassisListEl = document.getElementById("td-chassis-list");
const tierRowEl = document.getElementById("td-tier-row");
const roleRowEl = document.getElementById("td-role-row");
const moduleGridEl = document.getElementById("td-module-grid");
const tickListEl = document.getElementById("td-tick-list");
const savedListEl = document.getElementById("td-saved-list");
const statsPanelEl = document.getElementById("td-stats-panel");
const saveButton = document.getElementById("td-save-button");

const dialog = document.getElementById("tank-module-dialog");
const dialogTitle = document.getElementById("tank-module-dialog-title");
const dialogBody = document.getElementById("tank-module-dialog-body");
const dialogCancel = document.getElementById("tank-module-dialog-cancel");
dialogCancel.addEventListener("click", () => dialog.close());

function renderChassisList() {
    chassisListEl.innerHTML = "";

    const previewsPromise = fetchTankDesignPreviews(
        currentBaseDesign(),
        [
            { id: BASELINE_CANDIDATE_ID, type: "baseline" },
            ...tankChassis.map((chassis) => ({ id: chassis.key, type: "chassis", chassis_key: chassis.key })),
        ]
    );

    for (const chassis of tankChassis) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "battalion-option" + (chassis.key === chassisKey ? " filled" : "");
        button.textContent = chassis.name;
        button.addEventListener("click", () => selectChassis(chassis.key));
        chassisListEl.appendChild(
            attachStatPreview(button, {
                previewsPromise, lookupKey: chassis.key, getStats: (entry) => entry.stats,
                statFields: PREVIEW_STAT_FIELDS, baselineLookupKey: BASELINE_CANDIDATE_ID,
            })
        );
    }
}

function renderTierRow() {
    tierRowEl.innerHTML = "";
    const chassis = chassisByKey[chassisKey];
    if (chassis.tiers.length <= 1) {
        return;
    }

    const heading = document.createElement("h3");
    heading.textContent = "Tier";
    tierRowEl.appendChild(heading);

    const list = document.createElement("div");
    list.className = "battalion-option-list";

    const previewsPromise = fetchTankDesignPreviews(
        currentBaseDesign(),
        [
            { id: BASELINE_CANDIDATE_ID, type: "baseline" },
            ...chassis.tiers.map((tierEntry) => ({ id: tierEntry.tier, type: "tier", tier: tierEntry.tier })),
        ]
    );

    for (const tierEntry of chassis.tiers) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "battalion-option" + (tierEntry.tier === tier ? " filled" : "");
        button.textContent = `Tier ${tierEntry.tier}`;
        button.addEventListener("click", () => selectTier(tierEntry.tier));
        list.appendChild(
            attachStatPreview(button, {
                previewsPromise, lookupKey: tierEntry.tier, getStats: (entry) => entry.stats,
                statFields: PREVIEW_STAT_FIELDS, baselineLookupKey: BASELINE_CANDIDATE_ID,
            })
        );
    }
    tierRowEl.appendChild(list);
}

function renderRoleRow() {
    roleRowEl.innerHTML = "";
    const roles = tankRoles.filter((r) => r.base_chassis === chassisKey);

    const heading = document.createElement("h3");
    heading.textContent = "Role";
    roleRowEl.appendChild(heading);

    const list = document.createElement("div");
    list.className = "battalion-option-list";

    const noneButton = document.createElement("button");
    noneButton.type = "button";
    noneButton.className = "battalion-option" + (roleKey === null ? " filled" : "");
    noneButton.textContent = "None (Plain)";
    noneButton.addEventListener("click", () => selectRole(null));
    list.appendChild(noneButton);

    const previewsPromise = fetchTankDesignPreviews(
        currentBaseDesign(),
        [
            { id: BASELINE_CANDIDATE_ID, type: "baseline" },
            ...roles.map((role) => ({ id: role.key, type: "role", role_key: role.key })),
        ]
    );

    for (const role of roles) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "battalion-option" + (role.key === roleKey ? " filled" : "");
        button.textContent = labelWords(role.role);
        button.addEventListener("click", () => selectRole(role.key));
        list.appendChild(
            attachStatPreview(button, {
                previewsPromise, lookupKey: role.key, getStats: (entry) => entry.stats,
                statFields: PREVIEW_STAT_FIELDS, baselineLookupKey: BASELINE_CANDIDATE_ID,
            })
        );
    }

    roleRowEl.appendChild(list);
}

function openModulePicker(slotName) {
    dialogTitle.textContent = `Select Module — ${slotLabel(slotName)}`;
    dialogBody.innerHTML = "";

    if (chosenModules[slotName]) {
        const removeButton = document.createElement("button");
        removeButton.type = "button";
        removeButton.className = "battalion-option";
        removeButton.textContent = "Remove module";
        removeButton.addEventListener("click", () => {
            chosenModules[slotName] = null;
            dialog.close();
            renderModuleGrid();
            renderTierRow();
            refreshStats();
        });
        dialogBody.appendChild(removeButton);
    }

    const list = document.createElement("div");
    list.className = "battalion-option-list";

    const legalModules = legalModulesForSlot(slotName);
    const previewsPromise = fetchTankDesignPreviews(
        currentBaseDesign(),
        [
            { id: BASELINE_CANDIDATE_ID, type: "baseline" },
            ...legalModules.map((module) => ({ id: module.key, type: "module", slot: slotName, module_key: module.key })),
        ]
    );

    for (const module of legalModules) {
        const option = document.createElement("button");
        option.type = "button";
        option.className = "battalion-option";
        option.textContent = module.name;
        option.addEventListener("click", () => {
            chosenModules[slotName] = module.key;
            dialog.close();
            renderModuleGrid();
            renderTierRow();
            refreshStats();
        });
        list.appendChild(
            attachStatPreview(option, {
                previewsPromise, lookupKey: module.key, getStats: (entry) => entry.stats,
                statFields: PREVIEW_STAT_FIELDS, baselineLookupKey: BASELINE_CANDIDATE_ID,
            })
        );
    }
    dialogBody.appendChild(list);

    dialog.showModal();
}

function renderModuleGrid() {
    moduleGridEl.innerHTML = "";
    const chassis = chassisByKey[chassisKey];

    for (const slotName of Object.keys(chassis.module_slots)) {
        const cell = document.createElement("button");
        cell.type = "button";
        cell.className = "battalion-cell doctrine-track-slot" + (chosenModules[slotName] ? " filled" : "");

        const chosenKey = chosenModules[slotName];
        cell.innerHTML = `<span class="doctrine-track-label">${slotLabel(slotName)}</span>
            <span class="doctrine-track-value">${chosenKey ? moduleName(chosenKey) : "+"}</span>`;
        cell.addEventListener("click", () => openModulePicker(slotName));
        moduleGridEl.appendChild(cell);
    }
}

function renderTickList() {
    tickListEl.innerHTML = "";
    const chassis = chassisByKey[chassisKey];
    const tickKeys = chassisTicks(chassis);

    if (tickKeys.length === 0) {
        tickListEl.innerHTML = '<p class="section-caption">No tick upgrades apply to this chassis.</p>';
        return;
    }

    for (const tickKey of tickKeys) {
        const upgrade = upgradeByKey[tickKey];
        const level = tickLevels[tickKey] ?? 0;
        const cap = maxTickLevel(upgrade, researched);

        const row = document.createElement("div");
        row.className = "tick-row";

        const name = document.createElement("span");
        name.className = "tick-row-name";
        name.textContent = upgrade.name;
        row.appendChild(name);

        const minusButton = document.createElement("button");
        minusButton.type = "button";
        minusButton.textContent = "-";
        minusButton.disabled = level <= 0;
        minusButton.addEventListener("click", () => {
            tickLevels[tickKey] = Math.max(0, level - 1);
            renderTickList();
            renderTierRow();
            renderRoleRow();
            refreshStats();
        });
        row.appendChild(minusButton);

        const levelEl = document.createElement("span");
        levelEl.className = "tick-row-level";
        levelEl.textContent = `${level} / ${cap}`;
        row.appendChild(levelEl);

        const plusButton = document.createElement("button");
        plusButton.type = "button";
        plusButton.textContent = "+";
        plusButton.disabled = level >= cap;
        plusButton.addEventListener("click", () => {
            tickLevels[tickKey] = Math.min(cap, level + 1);
            renderTickList();
            renderTierRow();
            renderRoleRow();
            refreshStats();
        });
        row.appendChild(plusButton);

        tickListEl.appendChild(row);
    }
}

function designDisplayName(key) {
    const role = roleByKey[key];
    if (role) {
        return `${chassisByKey[role.base_chassis].name} (${labelWords(role.role)})`;
    }
    return chassisByKey[key].name;
}

function saveDesign() {
    const key = roleKey ?? chassisKey;
    savedDesigns[key] = {
        chassisKey, tier, roleKey,
        chosenModules: { ...chosenModules },
        tickLevels: { ...tickLevels },
    };
    renderSavedList();
    notifyDesignsChanged();
}

function loadDesign(key) {
    const saved = savedDesigns[key];
    chassisKey = saved.chassisKey;
    tier = saved.tier;
    roleKey = saved.roleKey;
    chosenModules = { ...saved.chosenModules };
    tickLevels = { ...saved.tickLevels };
    renderAll();
    refreshStats();
}

function deleteDesign(key) {
    delete savedDesigns[key];
    renderSavedList();
    notifyDesignsChanged();
}

// Each saved design is a chassis+role combination's equipment_key (see
// data/equipment_needs.py - a design saved under e.g.
// "light_tank_destroyer_chassis" already IS the equipment key every
// consumer of that chassis/role looks up, with zero translation needed),
// converted to the snake_case shape calculate_tank_design_stats actually
// takes - the same conversion refreshStats() already does for
// /api/tank-designer/stats, just applied per saved design instead of the
// one in-progress design. Shared by notifyDesignsChanged and getState
// (session persistence, below) - both need the identical conversion.
function savedDesignsAsSnakeCase() {
    const tankDesigns = {};
    for (const [key, design] of Object.entries(savedDesigns)) {
        tankDesigns[key] = {
            chassis_key: design.chassisKey,
            tier: design.tier,
            role_key: design.roleKey,
            chosen_modules: design.chosenModules,
            tick_levels: design.tickLevels,
        };
    }
    return tankDesigns;
}

// Lets stats.js react to saved-design changes without needing to know
// anything about this file's internals - same CustomEvent pattern as
// composition.js's notifyColumnChanged/support_companies.js's
// notifySupportChanged. Sends the full current set every time (not a
// delta), matching research.js/doctrines.js's own "always send the whole
// current state" convention.
function notifyDesignsChanged() {
    document.dispatchEvent(new CustomEvent("tank-designs-changed", { detail: savedDesignsAsSnakeCase() }));
}

function renderSavedList() {
    savedListEl.innerHTML = "";
    const keys = Object.keys(savedDesigns);

    if (keys.length === 0) {
        savedListEl.innerHTML = '<p class="section-caption">No designs saved yet. Saving a chassis+role combination again overwrites its previous save - a different role (e.g. Flame) always gets its own save.</p>';
        return;
    }

    for (const key of keys) {
        const row = document.createElement("div");
        row.className = "tech-row";
        row.style.cursor = "default";

        const textWrap = document.createElement("span");
        textWrap.className = "tech-row-text";
        const nameEl = document.createElement("span");
        nameEl.className = "tech-row-name";
        nameEl.textContent = designDisplayName(key);
        textWrap.appendChild(nameEl);
        row.appendChild(textWrap);

        const loadButton = document.createElement("button");
        loadButton.type = "button";
        loadButton.className = "battalion-option";
        loadButton.textContent = "Load";
        loadButton.addEventListener("click", () => loadDesign(key));
        row.appendChild(loadButton);

        const deleteButton = document.createElement("button");
        deleteButton.type = "button";
        deleteButton.className = "battalion-option";
        deleteButton.textContent = "Delete";
        deleteButton.addEventListener("click", () => deleteDesign(key));
        row.appendChild(deleteButton);

        savedListEl.appendChild(row);
    }
}

// The tank-design equivalent of stats.js's own highlighted secondary row
// (Strength/Soft Attack/Hard Attack/Breakthrough/Defense/Combat Width/
// Production Cost) - Ollie asked for the same "highlight the key stats"
// treatment here. Not every field applies to every design (a Flame design
// has no ap_attack, a plain design has no air_attack, etc. - see
// calculate_tank_design_stats's own docstring), so this list is filtered
// down to whatever fields this specific design's response actually has;
// anything left over still shows in the plain list below, nothing is
// dropped.
const KEY_STAT_FIELDS = [
    "armor_value", "breakthrough", "soft_attack", "hard_attack",
    "ap_attack", "reliability", "max_strength", "maximum_speed", "build_cost_ic",
];

// The same field list, as [field, label] pairs - the shape
// item_stats_preview.js's attachStatPreview/renderStatBlock takes for its
// `statFields` option (mirroring Division Stats' own KEY_STAT_FIELDS
// shape), passed by all 4 of this file's own attachStatPreview calls
// below. Tank Designer's stat shape (calculate_tank_design_stats) uses
// different field names than Division Stats' own (e.g. "maximum_speed" not
// "max_speed", "build_cost_ic" not "production_cost", no "combat_width" at
// all) - using Division Stats' own field list here (the previous,
// unparameterized default) silently rendered every value as blank/NaN.
const PREVIEW_STAT_FIELDS = KEY_STAT_FIELDS.map((field) => [field, fieldLabel(field)]);

function renderStatsPanel(stats, violations) {
    statsPanelEl.innerHTML = "";

    if (violations.length > 0) {
        const warning = document.createElement("div");
        warning.className = "stats-warning";
        warning.innerHTML = `<strong>Design has issues:</strong><ul>${violations
            .map((v) => `<li>${describeViolation(v)}</li>`)
            .join("")}</ul>`;
        statsPanelEl.appendChild(warning);
    } else {
        const ok = document.createElement("p");
        ok.className = "section-caption";
        ok.textContent = "✅ Design is legal.";
        statsPanelEl.appendChild(ok);
    }

    const keyFields = KEY_STAT_FIELDS.filter((field) => field in stats);
    if (keyFields.length > 0) {
        const secondary = document.createElement("div");
        secondary.className = "stats-secondary";
        for (const field of keyFields) {
            secondary.innerHTML += `<div class="stats-secondary-item">
                <span class="stats-secondary-value">${formatStatValue(field, stats[field])}</span>
                <span class="stats-secondary-label">${fieldLabel(field)}</span>
            </div>`;
        }
        statsPanelEl.appendChild(secondary);
    }

    const list = document.createElement("dl");
    list.className = "stats-list";
    const remaining = Object.entries(stats)
        .filter(([field]) => !keyFields.includes(field))
        .sort(([a], [b]) => a.localeCompare(b));
    for (const [field, value] of remaining) {
        const note = _INERT_FIELD_NOTES[field];
        const noteHtml = note ? ` <span class="stat-field-note">(${note})</span>` : "";
        list.innerHTML += `<dt>${fieldLabel(field)}${noteHtml}</dt><dd>${formatStatValue(field, value)}</dd>`;
    }
    statsPanelEl.appendChild(list);
}

// Guards against an older, slower request's response overwriting a newer
// one's - same pattern as stats.js's refreshStats.
let latestRequestId = 0;

async function refreshStats() {
    const requestId = ++latestRequestId;

    const response = await fetch("/api/tank-designer/stats", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            chassis_key: chassisKey,
            tier,
            role_key: roleKey,
            chosen_modules: chosenModules,
            tick_levels: tickLevels,
        }),
    });
    const data = await response.json();

    if (requestId !== latestRequestId) {
        return;
    }
    renderStatsPanel(data.stats, data.violations);
}

function renderAll() {
    renderChassisList();
    renderTierRow();
    renderRoleRow();
    renderModuleGrid();
    renderTickList();
    renderSavedList();
}

saveButton.addEventListener("click", saveDesign);

// --- Session persistence (added 2026-10-06) - see static/js/persistence.js
// for the load/save orchestration. Only the SAVED designs persist, not
// whatever's currently being edited in-progress - matches "Save Design"'s
// own existing semantics (exploratory edits are ephemeral until saved).
export function getState() {
    return savedDesignsAsSnakeCase();
}

export function restoreState(tankDesigns) {
    for (const [key, design] of Object.entries(tankDesigns)) {
        savedDesigns[key] = {
            chassisKey: design.chassis_key,
            tier: design.tier,
            roleKey: design.role_key,
            chosenModules: { ...design.chosen_modules },
            tickLevels: { ...design.tick_levels },
        };
    }
    renderSavedList();
    notifyDesignsChanged();
}

renderAll();
refreshStats();
