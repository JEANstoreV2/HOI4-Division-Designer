import { getCurrentStatsContext } from "./stats.js";
import { attachStatPreview, fetchItemStatPreviews } from "./item_stats_preview.js";

const battalions = JSON.parse(document.getElementById("battalion-data").textContent);
const categoryLabels = JSON.parse(document.getElementById("category-label-data").textContent);

// Seeded from the same "no research done yet" set research.js starts from,
// so this doesn't depend on research.js having run first - see that file's
// module comment on why state flows via "research-changed" rather than a
// shared import. Reassigned wholesale (not merged) on every event, since
// research.js always sends the full current set.
let unlockedByResearch = new Set(JSON.parse(document.getElementById("always-unlocked-subunit-data").textContent));
document.addEventListener("research-changed", (event) => {
    unlockedByResearch = event.detail.unlockedSubunits;
});

// Doctrine is a second, independent unlock source - a battalion only needs
// to be unlocked by research OR doctrine, not both. Also drives the 5th
// battalion row: real HOI4 rule, only usable once a doctrine track grants it.
let unlockedByDoctrine = new Set();
let fifthRowDoctrineUnlocked = false;
document.addEventListener("doctrine-changed", (event) => {
    unlockedByDoctrine = event.detail.unlockedSubunits;
    fifthRowDoctrineUnlocked = event.detail.unlocksFifthRow;
    for (let column = 0; column < 5; column++) {
        updateRowLocks(column);
    }
});

// Special Projects is a third, independent unlock source - several real
// subunits (e.g. Land Cruiser) are gated directly by a project's own
// completion, separate from anything a gated technology unlocks. See
// data/special_projects.py's header.
let unlockedBySpecialProjects = new Set();
document.addEventListener("special-projects-changed", (event) => {
    unlockedBySpecialProjects = event.detail.unlockedSubunits;
});

// Real HOI4 rule: a column fills top-down, no gaps - row N (other than the
// top row) stays locked (grayed out, same treatment as the 5th row's own
// pre-existing mastery lock) until row N-1 holds a battalion. The 5th row
// additionally needs doctrine mastery on top of that - both conditions, not
// either. Never touches a cell that's already filled (its own label stays).
function updateRowLocks(column) {
    const cells = cellsByColumn()[column];
    for (let row = 1; row < cells.length; row++) {
        const cell = cells[row];
        const previousFilled = cells[row - 1].classList.contains("filled");
        const isFifthRow = cell.classList.contains("fifth-battalion-cell");
        const unlocked = previousFilled && (!isFifthRow || fifthRowDoctrineUnlocked);

        cell.disabled = !unlocked;
        cell.classList.toggle("locked", !unlocked);
        if (!cell.classList.contains("filled")) {
            cell.textContent = unlocked ? "+" : "×";
        }
    }
}

const battalionsByCategory = {};
for (const battalion of battalions) {
    if (!battalionsByCategory[battalion.category]) {
        battalionsByCategory[battalion.category] = [];
    }
    battalionsByCategory[battalion.category].push(battalion);
}

// One entry per column: category stays null until the first battalion is placed.
const columnState = [0, 1, 2, 3, 4].map(() => ({ category: null }));

const dialog = document.getElementById("battalion-dialog");
const dialogTitle = document.getElementById("battalion-dialog-title");
const dialogBody = document.getElementById("battalion-dialog-body");
const dialogCancel = document.getElementById("battalion-dialog-cancel");

let activeCell = null;

// True while the currently-open dialog is in "fill the whole column"
// mode (shift-click/double-click/long-press an empty cell), rather than
// the normal "fill just this one cell" mode - see openPicker/
// fillColumnWithBattalion below.
let activeFillColumn = false;

// Bound to every battalion cell up front, including the (initially locked)
// rows 2-5 - the native `disabled` attribute, toggled by updateRowLocks
// above, is what actually blocks clicks. Mirrors regimental_support.js's
// own established pattern for its own initially-locked cells.
//
// Three ways to trigger "fill column" mode instead of the normal
// one-cell pick: shift-click (checked on the plain click event - no
// extra listener needed), double-click (a real double-click fires
// click, then click again, then dblclick - the first two already open
// the dialog normally, and this "upgrades" it in place), and long-press
// on touch devices, which have neither shift nor double-click
// (bindLongPress below).
document.querySelectorAll(".battalion-grid .battalion-cell[data-column]").forEach((cell) => {
    cell.addEventListener("click", (event) => openPicker(cell, event.shiftKey));
    cell.addEventListener("dblclick", () => openPicker(cell, true));
    bindLongPress(cell, () => openPicker(cell, true));
});

dialogCancel.addEventListener("click", () => dialog.close());

// Rows 2-5 start locked (the template only bakes the 5th row's lock markup
// in directly, since that one additionally needs a `title` explaining why -
// this brings rows 2-4 to the same visual/disabled state before anything's
// been picked).
for (let column = 0; column < 5; column++) {
    updateRowLocks(column);
}

// Press-and-hold equivalent of a desktop double-click/shift-click, for touch
// devices that have neither. touchend fires a synthetic click right after a
// tap (including after a long-press's finger-lift) - preventDefault() on the
// touchend that actually fired the long press suppresses that trailing
// click, so whatever the long press just did doesn't immediately get
// re-triggered in normal mode right after. Generic over any element/callback
// so it covers both a battalion cell (fill the whole column) and the picker
// dialog's "Remove battalion" button (clear the whole column).
function bindLongPress(element, onLongPress) {
    const LONG_PRESS_MS = 500;
    let pressTimer = null;
    let didFire = false;

    element.addEventListener("touchstart", () => {
        didFire = false;
        pressTimer = setTimeout(() => {
            didFire = true;
            onLongPress();
        }, LONG_PRESS_MS);
    });

    const cancelPress = () => clearTimeout(pressTimer);
    element.addEventListener("touchmove", cancelPress);
    element.addEventListener("touchcancel", cancelPress);
    element.addEventListener("touchend", (event) => {
        cancelPress();
        if (didFire) {
            event.preventDefault();
        }
    });
}

function openPicker(cell, fillColumn = false) {
    activeCell = cell;
    activeFillColumn = fillColumn;
    const column = Number(cell.dataset.column);
    const lockedCategory = columnState[column].category;

    dialogTitle.textContent = fillColumn
        ? `Select Battalion — Column ${column + 1} (fills entire column)`
        : `Select Battalion — Column ${column + 1}`;
    dialogBody.innerHTML = "";

    if (cell.classList.contains("filled")) {
        const removeButton = document.createElement("button");
        removeButton.type = "button";
        removeButton.className = "battalion-option";
        removeButton.textContent = "Remove battalion";
        removeButton.title = "Shift-click (or long-press on touch) to remove the whole column";
        removeButton.addEventListener("click", (event) => removeBattalion(event.shiftKey));
        bindLongPress(removeButton, () => removeBattalion(true));
        dialogBody.appendChild(removeButton);
    }

    const categoriesToShow = lockedCategory ? [lockedCategory] : Object.keys(battalionsByCategory);

    const unlockedByCategory = categoriesToShow.map((category) => battalionsByCategory[category].filter(
        (battalion) =>
            unlockedByResearch.has(battalion.key) ||
            unlockedByDoctrine.has(battalion.key) ||
            unlockedBySpecialProjects.has(battalion.key)
    ));

    // One batch fetch per dialog-open, covering every battalion about to be
    // listed - not one fetch per option. attachStatPreview only actually
    // renders a given option's stats once that option is expanded.
    const previewsPromise = fetchItemStatPreviews(
        unlockedByCategory.flat().map((battalion) => ({ item_key: battalion.key, is_support_type: false })),
        getCurrentStatsContext()
    );

    categoriesToShow.forEach((category, index) => {
        const unlockedBattalions = unlockedByCategory[index];
        if (unlockedBattalions.length === 0) {
            return;
        }

        const group = document.createElement("div");
        group.className = "category-group";

        const heading = document.createElement("h3");
        heading.textContent = categoryLabels[category];
        group.appendChild(heading);

        const list = document.createElement("div");
        list.className = "battalion-option-list";

        for (const battalion of unlockedBattalions) {
            const option = document.createElement("button");
            option.type = "button";
            option.className = "battalion-option";
            option.textContent = battalion.name;
            option.addEventListener("click", () => {
                if (activeFillColumn) {
                    fillColumnWithBattalion(battalion);
                } else {
                    selectBattalion(battalion);
                }
            });
            list.appendChild(attachStatPreview(option, { previewsPromise, lookupKey: battalion.key }));
        }

        group.appendChild(list);
        dialogBody.appendChild(group);
    });

    // A real double-click's second click has already opened this dialog
    // normally a moment earlier - showModal() throws if called again on an
    // already-open <dialog>, so only call it the first time.
    if (!dialog.open) {
        dialog.showModal();
    }
}

function selectBattalion(battalion) {
    const column = Number(activeCell.dataset.column);
    columnState[column].category = battalion.category;

    activeCell.textContent = battalion.name;
    activeCell.classList.add("filled");
    activeCell.dataset.battalionKey = battalion.key;

    updateRowLocks(column);
    dialog.close();
    notifyColumnChanged(column);
}

// Fills every currently-EMPTY cell in the column with the same battalion -
// triggered via shift-click/double-click/long-press (see openPicker). Never
// overwrites a cell that already holds a (possibly different) battalion,
// including the clicked cell itself if it was already filled - a column can
// legitimately mix battalions within one locked category (e.g. Infantry +
// Mountaineers), so filling must never silently discard an earlier
// deliberate choice. Processes rows top-down and unlocks each row as the one
// above it gets filled, rather than checking the (now stale-until-updated)
// `disabled` attribute - the one row this can still never force open is the
// 5th, which stays gated behind doctrine mastery regardless.
function fillColumnWithBattalion(battalion) {
    const column = Number(activeCell.dataset.column);
    columnState[column].category = battalion.category;

    for (const cell of cellsByColumn()[column]) {
        if (cell.classList.contains("filled")) {
            continue;
        }
        if (cell.classList.contains("fifth-battalion-cell") && !fifthRowDoctrineUnlocked) {
            break;
        }
        cell.textContent = battalion.name;
        cell.classList.add("filled");
        cell.dataset.battalionKey = battalion.key;
    }

    updateRowLocks(column);
    dialog.close();
    notifyColumnChanged(column);
}

// Clears a column from `fromRow` downward - used both for removing a single
// battalion (cascading to the rows below it, since a column can't have gaps
// - they were only ever unlocked because this row was filled) and for
// removing the whole column at once (fromRow = 0, see removeBattalion).
function clearCellsFrom(column, fromRow) {
    const cells = cellsByColumn()[column];
    for (let row = fromRow; row < cells.length; row++) {
        cells[row].classList.remove("filled");
        delete cells[row].dataset.battalionKey;
        // updateRowLocks (below) resets rows 1+ to "+"/"×" based on the new
        // lock state, but it deliberately never touches row 0 (it has no
        // "previous row" to depend on) - reset the label here too so a
        // cleared row 0 doesn't keep showing its old battalion's name.
        cells[row].textContent = "+";
    }

    const columnStillHasBattalions = cells.some((cell) => cell.classList.contains("filled"));
    if (!columnStillHasBattalions) {
        columnState[column].category = null;
    }

    updateRowLocks(column);
}

// removeColumn (true when the "Remove battalion" button was shift-clicked or
// long-pressed, see openPicker) clears the whole column from the top instead
// of just the one cell that was clicked.
function removeBattalion(removeColumn = false) {
    const column = Number(activeCell.dataset.column);
    const row = removeColumn ? 0 : cellsByColumn()[column].indexOf(activeCell);

    clearCellsFrom(column, row);
    dialog.close();
    notifyColumnChanged(column);
}

// Lets regimental_support.js react to battalion changes without composition.js
// needing to know anything about regimental support (each JS file - an ES
// module - has its own isolated scope, so a CustomEvent is how they talk).
function notifyColumnChanged(column) {
    const count = document.querySelectorAll(
        `.battalion-cell.filled[data-column="${column}"]`
    ).length;
    document.dispatchEvent(
        new CustomEvent("battalion-column-changed", {
            detail: { column, count, category: columnState[column].category },
        })
    );
}

// --- Session persistence (added 2026-10-06) - see static/js/persistence.js
// for the load/save orchestration and why Composition must restore after
// Research/Special Projects/Doctrine (its own picker gates on their unlock
// sets, and the 5th row's disabled state must already reflect Doctrine's
// restored state before this runs). The battalion grid's real state lives
// in the DOM (`dataset.battalionKey`), not a JS variable - see this file's
// own module comment - so getState/restoreState read/write cells directly,
// in the same per-column, DOM order the grid is already rendered in.

function cellsByColumn() {
    const byColumn = [[], [], [], [], []];
    document.querySelectorAll(".battalion-grid .battalion-cell[data-column]").forEach((cell) => {
        byColumn[Number(cell.dataset.column)].push(cell);
    });
    return byColumn;
}

export function getState() {
    return cellsByColumn().map((cells) => cells.map((cell) => cell.dataset.battalionKey ?? null));
}

export function restoreState(columns) {
    const byColumn = cellsByColumn();

    columns.forEach((rowKeys, column) => {
        // Real bug, found 2026-11-02 via AI Design Comparison's "Load into
        // Composition": this only ever SET whatever rows rowKeys covered -
        // if the column being restored onto already had MORE rows filled
        // than the new rowKeys provides (e.g. loading a 2-battalion design
        // over a column that already had 4), those extra rows were never
        // touched, so the old battalions stayed - "adds" instead of
        // "replaces". clearCellsFrom already exists for exactly this
        // (removeBattalion's own "remove whole column" case) - clearing
        // first makes this a true replace for every caller (Session
        // restore, Saved Divisions' Load, and this one), not just a merge.
        clearCellsFrom(column, 0);

        rowKeys.forEach((key, row) => {
            const cell = byColumn[column][row];
            // Defensive, not expected in practice: a saved key for a cell
            // that's still disabled (e.g. the 5th row, if Doctrine's own
            // restore somehow didn't unlock it) - skip rather than force a
            // state the UI itself would never have allowed interactively.
            if (!key || !cell || cell.disabled) {
                return;
            }
            const battalion = battalions.find((b) => b.key === key);
            if (!battalion) {
                return;
            }
            columnState[column].category = battalion.category;
            cell.textContent = battalion.name;
            cell.classList.add("filled");
            cell.dataset.battalionKey = battalion.key;
            // Unlocks the next row in this same forEach pass - rowKeys is
            // already in top-down order, so by the time row+1 is reached
            // its own `cell.disabled` check above reflects row's fill.
            updateRowLocks(column);
        });
        notifyColumnChanged(column);
    });
}
