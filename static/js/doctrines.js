// JS mirror of logic/doctrines.py's selection/progression rules - see that
// module for the authoritative, tested version and the reasoning behind
// each rule. Not mirrored: active_unit_bonuses - that one only ever needs
// to run server-side inside /api/stats (see stats.js), same reasoning as
// why calculate_division_stats itself isn't duplicated in JS.
//
// Renders the Doctrine tab and, via the "doctrine-changed" CustomEvent,
// drives what composition.js/support_companies.js/regimental_support.js
// offer (unlocked subunits, plus composition.js's 5th battalion row) and
// what stats.js sends to /api/stats - see those files' matching comments.

import { attachBonusPreview } from "./item_stats_preview.js";

export function isGrandDoctrineSelectable(grandDoctrineKey, grandDoctrines, activeGrandDoctrines) {
    if (activeGrandDoctrines.has(grandDoctrineKey)) {
        return false;
    }
    const folder = grandDoctrines.find((gd) => gd.key === grandDoctrineKey).folder;
    return ![...activeGrandDoctrines].some(
        (key) => grandDoctrines.find((gd) => gd.key === key).folder === folder
    );
}

export function isSubdoctrineSelectable(
    subdoctrineKey, trackKey, grandDoctrines, subdoctrines, activeGrandDoctrines, trackSubdoctrines, researched
) {
    const subdoctrine = subdoctrines.find((sd) => sd.key === subdoctrineKey);

    const trackIsAvailable = [...activeGrandDoctrines].some((gdKey) =>
        grandDoctrines.find((gd) => gd.key === gdKey).tracks.includes(trackKey)
    );
    if (!trackIsAvailable) {
        return false;
    }

    if (!subdoctrine.tracks.includes(trackKey)) {
        return false;
    }

    for (const [otherTrack, otherSubdoctrineKey] of Object.entries(trackSubdoctrines)) {
        if (otherTrack === trackKey) {
            continue;
        }
        // Real bug, found 2026-11-02 while building AI Design
        // Comparison's own Doctrine search - a Special Forces
        // subdoctrine's own `tracks` lists BOTH Special Forces tracks as
        // eligible (real HOI4 lets you put it on either), but nothing
        // here stopped the SAME subdoctrine being assigned to both at
        // once. Re-assigning this exact track to the key already there
        // is still fine (guarded by the `otherTrack === trackKey`
        // continue above).
        if (otherSubdoctrineKey === subdoctrineKey) {
            return false;
        }
        if (subdoctrine.xor.includes(otherSubdoctrineKey)) {
            return false;
        }
    }

    if (subdoctrine.requires_technology !== null && !researched.has(subdoctrine.requires_technology)) {
        return false;
    }

    return true;
}

export function canClaimNextReward(subdoctrineKey, subdoctrines, claimedRewards) {
    const subdoctrine = subdoctrines.find((sd) => sd.key === subdoctrineKey);
    const alreadyClaimed = claimedRewards[subdoctrineKey] ?? 0;
    return alreadyClaimed < subdoctrine.rewards.length;
}

export function isTrackMastered(trackKey, subdoctrines, trackSubdoctrines, claimedRewards) {
    const subdoctrineKey = trackSubdoctrines[trackKey];
    if (!subdoctrineKey) {
        return false;
    }
    const subdoctrine = subdoctrines.find((sd) => sd.key === subdoctrineKey);
    return (claimedRewards[subdoctrineKey] ?? 0) >= subdoctrine.rewards.length;
}

export function unlocksFifthBattalionRow(grandDoctrines, subdoctrines, activeGrandDoctrines, trackSubdoctrines, claimedRewards) {
    for (const grandDoctrineKey of activeGrandDoctrines) {
        const grandDoctrine = grandDoctrines.find((gd) => gd.key === grandDoctrineKey);
        for (let i = 0; i < grandDoctrine.tracks.length; i++) {
            const trackKey = grandDoctrine.tracks[i];
            const milestone = grandDoctrine.milestones[i];
            if (!("additional_brigade_column_size" in (milestone.modifiers ?? {}))) {
                continue;
            }
            if (isTrackMastered(trackKey, subdoctrines, trackSubdoctrines, claimedRewards)) {
                return true;
            }
        }
    }
    return false;
}

export function unlockedSubunitKeys(grandDoctrines, subdoctrines, activeGrandDoctrines, trackSubdoctrines, claimedRewards) {
    const unlocked = new Set();

    for (const grandDoctrineKey of activeGrandDoctrines) {
        const grandDoctrine = grandDoctrines.find((gd) => gd.key === grandDoctrineKey);
        for (const key of grandDoctrine.effects.unlocks_subunits ?? []) {
            unlocked.add(key);
        }
    }

    for (const subdoctrineKey of Object.values(trackSubdoctrines)) {
        if (!subdoctrineKey) {
            continue;
        }
        const subdoctrine = subdoctrines.find((sd) => sd.key === subdoctrineKey);
        for (const key of subdoctrine.effects.unlocks_subunits ?? []) {
            unlocked.add(key);
        }

        const claimed = claimedRewards[subdoctrineKey] ?? 0;
        for (const reward of subdoctrine.rewards.slice(0, claimed)) {
            for (const key of reward.effects.unlocks_subunits ?? []) {
                unlocked.add(key);
            }
        }
    }

    return unlocked;
}

// --- UI layer: the Doctrine tab itself. ---

const doctrineTracks = JSON.parse(document.getElementById("doctrine-track-data").textContent);
const grandDoctrines = JSON.parse(document.getElementById("grand-doctrine-data").textContent);
const subdoctrines = JSON.parse(document.getElementById("subdoctrine-data").textContent);

const FOLDERS = ["land", "special_forces"];
const FOLDER_LABELS = { land: "Land Doctrine", special_forces: "Special Forces Doctrine" };

function humanizeKey(key) {
    return key
        .split("_")
        .map((word) => word[0].toUpperCase() + word.slice(1))
        .join(" ");
}

const TRACK_LABELS = {};
for (const track of doctrineTracks) {
    TRACK_LABELS[track.key] = humanizeKey(track.key);
}

// Caller-owned state, exactly matching logic/doctrines.py's shape.
const activeGrandDoctrines = new Set();
const trackSubdoctrines = {};
const claimedRewards = {};

// Kept in sync via research-changed, seeded from the same "no research
// done yet" baseline every other file starts from - needed for
// isSubdoctrineSelectable's Special Forces requires_technology check.
let researched = new Set();
document.addEventListener("research-changed", (event) => {
    researched = new Set(event.detail.researched);
});

// The global show/hide-all-info toggle (static/js/preview_toggle.js) -
// this view's buttons/rows live outside any <dialog>, so a re-render is
// the only way for their already-mounted previews to pick up the new
// state.
document.addEventListener("all-previews-toggled", renderAll);

const foldersEl = document.getElementById("doctrine-folders");
const progressEl = document.getElementById("doctrine-progress");

const dialog = document.getElementById("doctrine-dialog");
const dialogTitle = document.getElementById("doctrine-dialog-title");
const dialogBody = document.getElementById("doctrine-dialog-body");
const dialogCancel = document.getElementById("doctrine-dialog-cancel");
dialogCancel.addEventListener("click", () => dialog.close());

function selectGrandDoctrine(grandDoctrineKey) {
    if (!isGrandDoctrineSelectable(grandDoctrineKey, grandDoctrines, activeGrandDoctrines)) {
        return;
    }
    const folder = grandDoctrines.find((gd) => gd.key === grandDoctrineKey).folder;
    for (const activeKey of [...activeGrandDoctrines]) {
        if (grandDoctrines.find((gd) => gd.key === activeKey).folder === folder) {
            activeGrandDoctrines.delete(activeKey);
        }
    }
    activeGrandDoctrines.add(grandDoctrineKey);
    renderAll();
    notifyDoctrineChanged();
}

function openTrackPicker(trackKey) {
    dialogTitle.textContent = `Select Subdoctrine — ${TRACK_LABELS[trackKey]}`;
    dialogBody.innerHTML = "";

    const list = document.createElement("div");
    list.className = "battalion-option-list";

    const eligible = subdoctrines.filter(
        (sd) =>
            sd.tracks.includes(trackKey) &&
            isSubdoctrineSelectable(sd.key, trackKey, grandDoctrines, subdoctrines, activeGrandDoctrines, trackSubdoctrines, researched)
    );

    for (const subdoctrine of eligible) {
        const option = document.createElement("button");
        option.type = "button";
        option.className = "battalion-option";
        option.textContent = subdoctrine.name;
        option.addEventListener("click", () => {
            trackSubdoctrines[trackKey] = subdoctrine.key;
            dialog.close();
            renderAll();
            notifyDoctrineChanged();
        });
        // Immediate effect first (no heading, matching the Grand Doctrine
        // button's own convention above), then every mastery reward in
        // order, each labeled by its own name - added 2026-11-03 per
        // Ollie's own report that the picker only ever showed the
        // immediate bonus, leaving every reward invisible until actually
        // assigned and opened in the Progress section below.
        list.appendChild(
            attachBonusPreview(option, () => [
                subdoctrine.effects,
                ...subdoctrine.rewards.map((reward) => ({
                    heading: reward.name ?? humanizeKey(reward.key),
                    ...reward.effects,
                })),
            ])
        );
    }

    dialogBody.appendChild(list);
    dialog.showModal();
}

function claimReward(subdoctrineKey) {
    if (!canClaimNextReward(subdoctrineKey, subdoctrines, claimedRewards)) {
        return;
    }
    claimedRewards[subdoctrineKey] = (claimedRewards[subdoctrineKey] ?? 0) + 1;
    renderAll();
    notifyDoctrineChanged();
}

function renderFolders() {
    foldersEl.innerHTML = "";

    for (const folder of FOLDERS) {
        const section = document.createElement("section");

        const heading = document.createElement("h2");
        heading.textContent = FOLDER_LABELS[folder];
        section.appendChild(heading);

        const pickerList = document.createElement("div");
        pickerList.className = "battalion-option-list";
        for (const grandDoctrine of grandDoctrines.filter((gd) => gd.folder === folder)) {
            const button = document.createElement("button");
            button.type = "button";
            button.className = "battalion-option" + (activeGrandDoctrines.has(grandDoctrine.key) ? " filled" : "");
            button.textContent = grandDoctrine.name;
            button.addEventListener("click", () => selectGrandDoctrine(grandDoctrine.key));
            // Immediate effects first, then every track's own milestone
            // (what mastering that track grants) labeled by track name -
            // Ollie's own call (2026-11-01) to show mastery bonuses here,
            // alongside the doctrine's other bonuses, rather than in the
            // Progress section where they'd been shown right after being
            // built.
            pickerList.appendChild(
                attachBonusPreview(button, () => [
                    grandDoctrine.effects,
                    ...grandDoctrine.tracks.map((trackKey, index) => ({
                        heading: `${TRACK_LABELS[trackKey]} Milestone`,
                        ...grandDoctrine.milestones[index],
                    })),
                ])
            );
        }
        section.appendChild(pickerList);

        const activeKey = [...activeGrandDoctrines].find(
            (key) => grandDoctrines.find((gd) => gd.key === key).folder === folder
        );
        if (activeKey) {
            const activeGrandDoctrine = grandDoctrines.find((gd) => gd.key === activeKey);
            const trackGrid = document.createElement("div");
            trackGrid.className = "doctrine-track-grid";

            activeGrandDoctrine.tracks.forEach((trackKey, trackIndex) => {
                const slot = document.createElement("button");
                slot.type = "button";
                slot.className = "battalion-cell doctrine-track-slot";

                const assignedKey = trackSubdoctrines[trackKey];
                const mastered = isTrackMastered(trackKey, subdoctrines, trackSubdoctrines, claimedRewards);
                if (assignedKey) {
                    slot.classList.add("filled");
                }

                slot.innerHTML = `<span class="doctrine-track-label">${TRACK_LABELS[trackKey]}</span>
                    <span class="doctrine-track-value">${assignedKey ? subdoctrines.find((sd) => sd.key === assignedKey).name : "+"}</span>
                    ${mastered ? '<span class="doctrine-track-mastered">★ Mastered</span>' : ""}`;
                slot.addEventListener("click", () => openTrackPicker(trackKey));

                // Shows what MASTERING this track grants (the milestone),
                // not the currently-assigned subdoctrine's own effects -
                // those are already previewable from the track picker
                // dialog/Progress section below.
                const milestone = activeGrandDoctrine.milestones[trackIndex];
                trackGrid.appendChild(attachBonusPreview(slot, () => [milestone]));
            });
            section.appendChild(trackGrid);
        }

        foldersEl.appendChild(section);
    }
}

function renderProgress() {
    progressEl.innerHTML = "";

    const assignedEntries = Object.entries(trackSubdoctrines).filter(([, key]) => key);
    if (assignedEntries.length === 0) {
        progressEl.innerHTML = '<p class="section-caption">Assign a subdoctrine to a track to start claiming its rewards.</p>';
        return;
    }

    for (const [trackKey, subdoctrineKey] of assignedEntries) {
        const subdoctrine = subdoctrines.find((sd) => sd.key === subdoctrineKey);
        const claimed = claimedRewards[subdoctrineKey] ?? 0;

        const block = document.createElement("div");
        block.className = "doctrine-progress-block";

        const heading = document.createElement("h3");
        heading.textContent = `${subdoctrine.name} (${TRACK_LABELS[trackKey]})`;
        block.appendChild(heading);

        subdoctrine.rewards.forEach((reward, index) => {
            const row = document.createElement("div");
            row.className = "tech-row";

            const textWrap = document.createElement("span");
            textWrap.className = "tech-row-text";
            const nameEl = document.createElement("span");
            nameEl.className = "tech-row-name";
            // (2026-11-01) every reward now has a real compiled name
            // (data/doctrines.py, audited against the real game's own
            // localisation) - humanizeKey(reward.key) kept only as a
            // fallback for the unlikely case a future reward is added
            // without one.
            nameEl.textContent = reward.name ?? humanizeKey(reward.key);
            textWrap.appendChild(nameEl);
            row.appendChild(textWrap);

            if (index < claimed) {
                const statusEl = document.createElement("span");
                statusEl.className = "tech-row-reason";
                statusEl.textContent = "✅ Claimed";
                row.appendChild(statusEl);
            } else if (index === claimed) {
                const claimButton = document.createElement("button");
                claimButton.type = "button";
                claimButton.className = "battalion-option";
                claimButton.textContent = "Claim Next Reward";
                claimButton.addEventListener("click", () => claimReward(subdoctrineKey));
                row.appendChild(claimButton);
            } else {
                row.classList.add("locked");
                const statusEl = document.createElement("span");
                statusEl.className = "tech-row-reason";
                statusEl.textContent = "🔒 Locked";
                row.appendChild(statusEl);
            }

            block.appendChild(attachBonusPreview(row, () => [reward.effects]));
        });

        progressEl.appendChild(block);
    }
}

function renderAll() {
    renderFolders();
    renderProgress();
}

function notifyDoctrineChanged() {
    document.dispatchEvent(
        new CustomEvent("doctrine-changed", {
            detail: {
                unlockedSubunits: unlockedSubunitKeys(grandDoctrines, subdoctrines, activeGrandDoctrines, trackSubdoctrines, claimedRewards),
                unlocksFifthRow: unlocksFifthBattalionRow(grandDoctrines, subdoctrines, activeGrandDoctrines, trackSubdoctrines, claimedRewards),
                activeGrandDoctrines: [...activeGrandDoctrines],
                trackSubdoctrines: { ...trackSubdoctrines },
                claimedRewards: { ...claimedRewards },
            },
        })
    );
}

// --- Session persistence (added 2026-10-06) - see static/js/persistence.js
// for the load/save orchestration and why Doctrine must restore after
// Research but before Composition/Support Companies/Regimental Support
// (their pickers gate on the unlock set selectGrandDoctrine/openTrackPicker/
// claimReward above produce). Shape matches /api/stats' own `doctrine`
// field exactly (snake_case) - the same object stats.js already builds
// from "doctrine-changed", reused here rather than inventing a second shape.

export function getState() {
    return {
        active_grand_doctrines: [...activeGrandDoctrines],
        track_subdoctrines: { ...trackSubdoctrines },
        claimed_rewards: { ...claimedRewards },
    };
}

export function restoreState(state) {
    // Clears first (real bug, found 2026-11-02 via AI Design Comparison's
    // "Load" button starting to call this with a result meant to REPLACE
    // the live picks, not merge with them - the same class of bug already
    // fixed in composition.js's/army_spirits.js's own restoreState this
    // same session). trackSubdoctrines/claimedRewards are plain objects,
    // not Sets - delete each existing key individually rather than
    // reassigning (these are `const`, captured by closures elsewhere in
    // this file, so the binding itself can't be replaced).
    activeGrandDoctrines.clear();
    for (const key of Object.keys(trackSubdoctrines)) {
        delete trackSubdoctrines[key];
    }
    for (const key of Object.keys(claimedRewards)) {
        delete claimedRewards[key];
    }

    for (const key of state.active_grand_doctrines ?? []) {
        activeGrandDoctrines.add(key);
    }
    Object.assign(trackSubdoctrines, state.track_subdoctrines ?? {});
    Object.assign(claimedRewards, state.claimed_rewards ?? {});
    renderAll();
    notifyDoctrineChanged();
}

renderAll();
