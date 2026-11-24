// JS mirror of logic/research.py's gating rules - see that module for the
// authoritative, tested version and the reasoning behind each rule. These
// three functions take the technologies list/researched set/etc. as
// explicit parameters rather than reading the DOM themselves, so they stay
// easy to reason about in isolation - the UI layer below reads the actual
// script-tag data once and passes it in.
//
// Renders the Research tab and, via the "research-changed" CustomEvent,
// drives what composition.js/support_companies.js/regimental_support.js
// offer in their pickers - see those files' matching comments.

import { attachBonusPreview } from "./item_stats_preview.js";

// completedSpecialProjects mirrors logic/research.py's is_researchable - a
// flat, caller-owned set of data/special_projects.py keys the 18 Special
// Project technologies (compiled 2026-10-01) gate on via their own
// special_project_requires field. Defaults to an empty Set so every
// existing call site (none of which track this state yet - that's Special
// Projects' own UI phase, not yet built) stays byte-identical; only the 18
// gated technologies are affected.
export function isResearchable(techKey, technologies, researched, externalDependencies, completedSpecialProjects = new Set()) {
    const tech = technologies.find((t) => t.key === techKey);

    if (researched.has(techKey)) {
        return false;
    }

    if (tech.unlocked_by.length > 0 && !tech.unlocked_by.some((prereq) => researched.has(prereq))) {
        return false;
    }

    if (!tech.requires.every((dep) => researched.has(dep) || externalDependencies.has(dep))) {
        return false;
    }

    if (tech.mutually_exclusive_with.some((other) => researched.has(other))) {
        return false;
    }

    if (tech.special_project_requires !== null && !completedSpecialProjects.has(tech.special_project_requires)) {
        return false;
    }

    return true;
}

export function researchableTechnologies(technologies, researched, externalDependencies, completedSpecialProjects = new Set()) {
    return technologies.filter((tech) =>
        isResearchable(tech.key, technologies, researched, externalDependencies, completedSpecialProjects)
    );
}

export function dependentTechnologies(techKey, technologies, researched, externalDependencies) {
    const hypothetical = new Set(researched);
    hypothetical.delete(techKey);

    const dependents = [];
    for (const otherKey of researched) {
        if (otherKey === techKey) {
            continue;
        }
        const other = technologies.find((t) => t.key === otherKey);

        const orBroken = other.unlocked_by.length > 0 && !other.unlocked_by.some((p) => hypothetical.has(p));
        const andBroken = !other.requires.every((dep) => hypothetical.has(dep) || externalDependencies.has(dep));
        if (orBroken || andBroken) {
            dependents.push(otherKey);
        }
    }

    return dependents;
}

export function canUnresearch(techKey, technologies, researched, externalDependencies) {
    return (
        researched.has(techKey) &&
        dependentTechnologies(techKey, technologies, researched, externalDependencies).length === 0
    );
}

export function unlockedSubunitKeys(technologies, researched, alwaysUnlocked) {
    const unlocked = new Set(alwaysUnlocked);

    for (const tech of technologies) {
        if (!researched.has(tech.key)) {
            continue;
        }
        for (const key of tech.unlocks_subunits) {
            unlocked.add(key);
        }
    }

    return unlocked;
}

// --- UI layer: the Research tab itself. ---
// Everything below is what was deferred when this file was first written -
// composition.js/support_companies.js/regimental_support.js don't call any
// of this directly; they only ever see its effect via the "research-changed"
// CustomEvent dispatched from researchTech() below.

const technologies = JSON.parse(document.getElementById("technology-data").textContent);
const externalDependencies = new Set(JSON.parse(document.getElementById("external-dependency-data").textContent));
const alwaysUnlockedSubunits = new Set(JSON.parse(document.getElementById("always-unlocked-subunit-data").textContent));
const specialProjects = JSON.parse(document.getElementById("special-projects-data").textContent);

const BRANCHES = ["infantry", "armor", "artillery", "support"];
const BRANCH_LABELS = { infantry: "Infantry", armor: "Armor", artillery: "Artillery", support: "Support" };

// A technology can be un-researched (unresearchTech below) as long as
// nothing else already-researched depends on it (canUnresearch) - this
// lets a misclick be undone freely right after it happens, while still
// stopping an earlier tech from being pulled out from under something
// already built on top of it.
const researched = new Set();

// Read-only tracking of Special Projects state (special_projects.js alone
// owns it) - needed for isResearchable's special_project_requires check and
// for lockReason's own text. Starts empty, matching every other cross-file
// state in this app starting from its "nothing done yet" baseline.
let completedSpecialProjects = new Set();
document.addEventListener("special-projects-changed", (event) => {
    completedSpecialProjects = event.detail.completed;
    renderAll();
});

// The global show/hide-all-info toggle (static/js/preview_toggle.js) -
// this view's tech rows live outside any <dialog>, so a re-render is the
// only way for their already-mounted previews to pick up the new state.
document.addEventListener("all-previews-toggled", renderAll);

let activeBranch = BRANCHES[0];

const branchTabsEl = document.getElementById("branch-tabs");
const researchListEl = document.getElementById("research-list");

function nameOf(techKey) {
    return technologies.find((t) => t.key === techKey)?.name ?? techKey;
}

function specialProjectNameOf(projectKey) {
    return specialProjects.find((p) => p.key === projectKey)?.name ?? projectKey;
}

// Only called for a tech isResearchable() already said is currently locked -
// figures out WHICH of the four gating rules is the reason, so the UI can
// tell the player what to go research next instead of just saying "locked".
function lockReason(tech) {
    if (tech.unlocked_by.length > 0 && !tech.unlocked_by.some((prereq) => researched.has(prereq))) {
        return `Requires: ${tech.unlocked_by.map(nameOf).join(" or ")}`;
    }

    const missingRequires = tech.requires.filter(
        (dep) => !researched.has(dep) && !externalDependencies.has(dep)
    );
    if (missingRequires.length > 0) {
        return `Requires: ${missingRequires.map(nameOf).join(", ")}`;
    }

    const conflictingChoice = tech.mutually_exclusive_with.find((other) => researched.has(other));
    if (conflictingChoice) {
        return `Already researched ${nameOf(conflictingChoice)} instead`;
    }

    if (tech.special_project_requires !== null && !completedSpecialProjects.has(tech.special_project_requires)) {
        return `Requires Special Project: ${specialProjectNameOf(tech.special_project_requires)}`;
    }

    return "Locked";
}

function renderBranchTabs() {
    branchTabsEl.innerHTML = "";

    for (const branch of BRANCHES) {
        const branchTechs = technologies.filter((t) => t.branch === branch);
        const doneCount = branchTechs.filter((t) => researched.has(t.key)).length;

        const tab = document.createElement("button");
        tab.type = "button";
        tab.className = "branch-tab" + (branch === activeBranch ? " active" : "");
        tab.textContent = `${BRANCH_LABELS[branch]} (${doneCount}/${branchTechs.length})`;
        tab.addEventListener("click", () => {
            activeBranch = branch;
            renderAll();
        });
        branchTabsEl.appendChild(tab);
    }
}

function renderList() {
    researchListEl.innerHTML = "";

    const branchTechs = technologies.filter((t) => t.branch === activeBranch);

    for (const tech of branchTechs) {
        const alreadyDone = researched.has(tech.key);
        const researchable = !alreadyDone && isResearchable(
            tech.key, technologies, researched, externalDependencies, completedSpecialProjects
        );
        const dependents = alreadyDone
            ? dependentTechnologies(tech.key, technologies, researched, externalDependencies)
            : [];
        const unresearchable = alreadyDone && dependents.length === 0;

        const row = document.createElement("label");
        row.className = "tech-row" + (!alreadyDone && !researchable ? " locked" : "");

        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.checked = alreadyDone;

        if (alreadyDone) {
            checkbox.disabled = !unresearchable;
        } else {
            checkbox.disabled = !researchable;
        }
        checkbox.addEventListener("change", () => {
            if (checkbox.checked) {
                researchTech(tech.key);
            } else {
                unresearchTech(tech.key);
            }
        });

        const textWrap = document.createElement("span");
        textWrap.className = "tech-row-text";

        const nameEl = document.createElement("span");
        nameEl.className = "tech-row-name";
        // tech.year is the real historical HOI4 unlock year (added
        // 2026-11-02, data/technologies.py's own "year" field) - null for
        // the one technology (gw_artillery) with no start_year in the
        // real game data at all, which falls back to the bare name rather
        // than showing "(null)".
        nameEl.textContent = tech.year ? `${tech.name} (${tech.year})` : tech.name;
        textWrap.appendChild(nameEl);

        if (!alreadyDone && !researchable) {
            const reasonEl = document.createElement("span");
            reasonEl.className = "tech-row-reason";
            reasonEl.textContent = `🔒 ${lockReason(tech)}`;
            textWrap.appendChild(reasonEl);
        } else if (alreadyDone && !unresearchable) {
            const reasonEl = document.createElement("span");
            reasonEl.className = "tech-row-reason";
            reasonEl.textContent = `🔒 Required by: ${dependents.map(nameOf).join(", ")}`;
            textWrap.appendChild(reasonEl);
        }

        row.appendChild(checkbox);
        row.appendChild(textWrap);
        researchListEl.appendChild(attachBonusPreview(row, () => [tech]));
    }
}

function renderAll() {
    renderBranchTabs();
    renderList();
}

function researchTech(techKey) {
    researched.add(techKey);
    renderAll();
    notifyResearchChanged();
}

// Repeatedly researches every currently-researchable technology until none
// are left - a single pass isn't enough since researching one technology
// can make another researchable (an unlocked_by/requires chain), the same
// reason researchableTechnologies takes the CURRENT researched set rather
// than a fixed snapshot.
//
// Also completes every Special Project first (added 2026-11-02, Ollie's
// own request: "Research All" should include Special Projects and their
// technologies, not just plain technologies) - dispatched as a
// CustomEvent special_projects.js listens for, rather than importing it
// directly (this project's established cross-file convention). The
// dispatch is synchronous, and the "special-projects-changed" listener
// below already keeps completedSpecialProjects current, so by the time
// the technology loop runs it already reflects every completed project -
// letting the 18 special-project-gated technologies become researchable
// in the same click, not a separate one.
function researchAllTech() {
    document.dispatchEvent(new CustomEvent("complete-all-special-projects-requested"));

    while (true) {
        const next = researchableTechnologies(technologies, researched, externalDependencies, completedSpecialProjects);
        if (next.length === 0) {
            break;
        }
        for (const tech of next) {
            researched.add(tech.key);
        }
    }
    renderAll();
    notifyResearchChanged();
}

function unresearchTech(techKey) {
    // Guard even though the checkbox is only ever enabled when this is
    // safe - canUnresearch is cheap and this keeps researchTech/
    // unresearchTech symmetric rather than trusting the DOM state alone.
    if (!canUnresearch(techKey, technologies, researched, externalDependencies)) {
        return;
    }
    researched.delete(techKey);
    renderAll();
    notifyResearchChanged();
}

function notifyResearchChanged() {
    document.dispatchEvent(
        new CustomEvent("research-changed", {
            detail: {
                unlockedSubunits: unlockedSubunitKeys(technologies, researched, alwaysUnlockedSubunits),
                // Raw researched tech keys, for stats.js's /api/stats calls
                // (equipment tier resolution needs the tech keys themselves,
                // not the subunits they unlock).
                researched: [...researched],
            },
        })
    );
}

document.getElementById("research-all-button").addEventListener("click", researchAllTech);

// --- Session persistence (added 2026-10-06) - see static/js/persistence.js
// for the load/save orchestration and why Research must restore before
// Composition/Support Companies/Regimental Support (their pickers gate on
// the unlock set researchTech below produces).

export function getState() {
    return [...researched];
}

export function restoreState(keys) {
    for (const key of keys) {
        researched.add(key);
    }
    renderAll();
    notifyResearchChanged();
}

renderAll();
