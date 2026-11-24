// JS mirror of logic/special_projects.py's gating rules - see that module
// for the authoritative, tested version and the reasoning behind each rule.
// Deliberately kept separate from research.js (Ollie's own call, 2026-10-01
// - "keep special research separate but similar to research"), even though
// the two cross-reference each other's state via CustomEvents: a Special
// Project's own "requires" list only ever points at another Special
// Project (never a technology), and research.js's own technologies can
// require a Special Project (special_project_requires) but never the
// reverse - completing a project is a prerequisite OF research, not the
// other way around.
//
// Also drives, via the "special-projects-changed" CustomEvent,
// composition.js/support_companies.js/regimental_support.js/tank_designer.js
// - several real subunits/Tank Designer modules are gated DIRECTLY by a
// project's own completion (data/special_projects.py's unlocks_subunits/
// unlocks_equipment_modules - e.g. Land Cruiser the subunit, or the base
// "flamethrower" module), separate from anything a gated technology itself
// unlocks. See data/special_projects.py's header for the full story.

import { attachBonusPreview } from "./item_stats_preview.js";

export function isCompletable(projectKey, projects, completed) {
    const project = projects.find((p) => p.key === projectKey);

    if (completed.has(projectKey)) {
        return false;
    }

    return project.requires.every((parent) => completed.has(parent));
}

export function completableSpecialProjects(projects, completed) {
    return projects.filter((project) => isCompletable(project.key, projects, completed));
}

export function dependentSpecialProjects(projectKey, projects, completed) {
    const hypothetical = new Set(completed);
    hypothetical.delete(projectKey);

    const dependents = [];
    for (const otherKey of completed) {
        if (otherKey === projectKey) {
            continue;
        }
        const other = projects.find((p) => p.key === otherKey);
        if (!other.requires.every((parent) => hypothetical.has(parent))) {
            dependents.push(otherKey);
        }
    }

    return dependents;
}

export function canUncomplete(projectKey, projects, completed, technologies, researched) {
    if (!completed.has(projectKey)) {
        return false;
    }

    if (dependentSpecialProjects(projectKey, projects, completed).length > 0) {
        return false;
    }

    return !technologies.some(
        (tech) => tech.special_project_requires === projectKey && researched.has(tech.key)
    );
}

export function unlockedSubunitKeysFromProjects(projects, completed) {
    const unlocked = new Set();
    for (const project of projects) {
        if (!completed.has(project.key)) {
            continue;
        }
        for (const key of project.unlocks_subunits) {
            unlocked.add(key);
        }
    }
    return unlocked;
}

export function unlockedModuleKeysFromProjects(projects, completed) {
    const unlocked = new Set();
    for (const project of projects) {
        if (!completed.has(project.key)) {
            continue;
        }
        for (const key of project.unlocks_equipment_modules) {
            unlocked.add(key);
        }
    }
    return unlocked;
}

// --- UI layer: the Special Projects tab itself. ---

const projects = JSON.parse(document.getElementById("special-projects-data").textContent);
const technologies = JSON.parse(document.getElementById("technology-data").textContent);

const completed = new Set();

// Read-only tracking of Research state, needed only for canUncomplete's
// cross-system check (a project can't be uncompleted while an
// already-researched technology still needs it) - this file never writes
// to `researched` itself, research.js alone owns that.
let researched = new Set();
document.addEventListener("research-changed", (event) => {
    researched = new Set(event.detail.researched);
    renderList();
});

// The global show/hide-all-info toggle (static/js/preview_toggle.js) -
// this view's rows live outside any <dialog>, so a re-render is the only
// way for their already-mounted previews to pick up the new state.
document.addEventListener("all-previews-toggled", renderList);

const listEl = document.getElementById("special-projects-list");

function nameOf(projectKey) {
    return projects.find((p) => p.key === projectKey)?.name ?? projectKey;
}

function lockReason(project) {
    const missingParents = project.requires.filter((parent) => !completed.has(parent));
    if (missingParents.length > 0) {
        return `Requires: ${missingParents.map(nameOf).join(", ")}`;
    }
    return "Locked";
}

function renderList() {
    listEl.innerHTML = "";

    for (const project of projects) {
        const alreadyDone = completed.has(project.key);
        const startable = !alreadyDone && isCompletable(project.key, projects, completed);
        const uncompletable = alreadyDone && canUncomplete(project.key, projects, completed, technologies, researched);

        const row = document.createElement("label");
        row.className = "tech-row" + (!alreadyDone && !startable ? " locked" : "");

        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.checked = alreadyDone;
        checkbox.disabled = alreadyDone ? !uncompletable : !startable;
        checkbox.addEventListener("change", () => {
            if (checkbox.checked) {
                completeProject(project.key);
            } else {
                uncompleteProject(project.key);
            }
        });

        const textWrap = document.createElement("span");
        textWrap.className = "tech-row-text";

        const nameEl = document.createElement("span");
        nameEl.className = "tech-row-name";
        nameEl.textContent = project.name;
        textWrap.appendChild(nameEl);

        if (!alreadyDone && !startable) {
            const reasonEl = document.createElement("span");
            reasonEl.className = "tech-row-reason";
            reasonEl.textContent = `🔒 ${lockReason(project)}`;
            textWrap.appendChild(reasonEl);
        } else if (alreadyDone && !uncompletable) {
            const dependents = dependentSpecialProjects(project.key, projects, completed);
            const reasonText = dependents.length > 0
                ? `Required by: ${dependents.map(nameOf).join(", ")}`
                : "Required by a researched technology";
            const reasonEl = document.createElement("span");
            reasonEl.className = "tech-row-reason";
            reasonEl.textContent = `🔒 ${reasonText}`;
            textWrap.appendChild(reasonEl);
        }

        row.appendChild(checkbox);
        row.appendChild(textWrap);
        listEl.appendChild(attachBonusPreview(row, () => [project]));
    }
}

function completeProject(projectKey) {
    completed.add(projectKey);
    renderList();
    notifySpecialProjectsChanged();
}

function uncompleteProject(projectKey) {
    if (!canUncomplete(projectKey, projects, completed, technologies, researched)) {
        return;
    }
    completed.delete(projectKey);
    renderList();
    notifySpecialProjectsChanged();
}

// Repeatedly completes every currently-completable project until none are
// left - mirrors research.js's own researchAllTech loop exactly (needed
// for the identical reason: completing one project can make another
// completable, via the one real project-to-project `requires` dependency,
// sp_land_self_propelled_super_heavy_howitzer).
function completeAllProjects() {
    while (true) {
        const next = completableSpecialProjects(projects, completed);
        if (next.length === 0) {
            break;
        }
        for (const project of next) {
            completed.add(project.key);
        }
    }
    renderList();
    notifySpecialProjectsChanged();
}

// Triggered by research.js's own "Research All" button (added 2026-11-02,
// Ollie's own request: "Research All" should also complete every Special
// Project, not just the technologies they gate) - dispatched BEFORE
// research.js's own technology loop runs, so special_project_requires
// gating already reflects every completed project by the time that loop
// starts. CustomEvents dispatch synchronously, and research.js already
// listens for "special-projects-changed" (fired by notifySpecialProjectsChanged
// above) to update its own completedSpecialProjects tracked set - so by
// the time this listener returns, research.js's own state is current.
document.addEventListener("complete-all-special-projects-requested", completeAllProjects);

function notifySpecialProjectsChanged() {
    document.dispatchEvent(
        new CustomEvent("special-projects-changed", {
            detail: {
                unlockedSubunits: unlockedSubunitKeysFromProjects(projects, completed),
                unlockedModules: unlockedModuleKeysFromProjects(projects, completed),
                // Raw completed project keys, for research.js's own
                // isResearchable calls (special_project_requires gating).
                completed: new Set(completed),
            },
        })
    );
}

// --- Session persistence (added 2026-10-06) - see static/js/persistence.js
// for the load/save orchestration and why Special Projects must restore
// after Research but before Composition/Support Companies/Regimental
// Support (their pickers gate on the unlock set completeProject below
// produces).

export function getState() {
    return [...completed];
}

export function restoreState(keys) {
    for (const key of keys) {
        completed.add(key);
    }
    renderList();
    notifySpecialProjectsChanged();
}

renderList();
