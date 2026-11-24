import os
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request

from storage import (
    clear_all_sections,
    delete_saved_division,
    ensure_db_directory,
    get_all_sections,
    get_saved_division,
    list_saved_divisions,
    save_division,
    set_section,
)
from data.battalions import BATTALIONS, CATEGORIES, CATEGORY_LABELS
from data.support_companies import SUPPORT_COMPANIES
from data.regimental_support import REGIMENTAL_SUPPORT
from data.special_projects import SPECIAL_PROJECTS
from data.technologies import EXTERNAL_DEPENDENCIES, TECHNOLOGIES
from data.doctrines import DOCTRINE_TRACKS, GRAND_DOCTRINES, SUBDOCTRINES
from data.army_spirits import ARMY_SPIRIT_CATEGORIES, ARMY_SPIRITS
from data.tank_chassis import TANK_CHASSIS, TANK_ROLES
from data.tank_modules import TANK_MODULES
from data.tank_upgrades import TANK_UPGRADES
from data.terrain import TERRAIN_TYPES
from data.patches import STAGED_PATCHES
from logic.design_search import generate_best_designs
from logic.doctrines import active_unit_bonuses
from logic.research import ALWAYS_UNLOCKED_MODULES, ALWAYS_UNLOCKED_SUBUNITS, researched_keys_by_year
from logic.stats import calculate_division_stats, calculate_item_stats
from logic.tank_designer import build_candidate_design, calculate_tank_design_stats, validate_design
from logic.terrain import ATTACK_SIDE_FIELDS, DEFENCE_SIDE_FIELDS, division_terrain_percentage

app = Flask(__name__)
# Jinja2's own `tojson` filter hardcodes `sort_keys: True` as a policy
# kwarg (jinja2.filters.do_tojson's json.dumps_kwargs default) - independent
# of and NOT overridden by Flask's own app.json.sort_keys setting, since the
# explicit kwarg wins inside DefaultJSONProvider.dumps either way. This
# silently reordered every `| tojson` script tag alphabetically - harmless
# for most of this app's data, but real for data/tank_chassis.py's own
# `module_slots` dicts, whose insertion order IS meaningful (it drives the
# Tank Designer module grid's left-to-right layout,
# static/js/tank_designer.js's renderModuleGrid). land_cruiser_chassis's own
# slot names (lc_additional_armament_slot_1 alphabetically precedes
# lc_main_armament_slot) is what actually exposed this - every other
# chassis's slot names happened to already sort into a sensible order by
# coincidence. Disabled app-wide rather than special-cased per chassis,
# since Python's own dict order (exactly as data/*.py writes it) is the one
# the rest of this codebase already trusts everywhere else.
app.jinja_env.policies["json.dumps_kwargs"]["sort_keys"] = False

# Session persistence (Phase 1, added 2026-10-06) - see storage.py's own
# header and CLAUDE.md's Persistence section for the full design.
# instance/ is Flask's own conventional per-instance data folder (already
# `.gitignore`'d - never created until now, since nothing wrote to it
# before this).
DB_PATH = os.path.join(app.instance_path, "division_designer.db")
ensure_db_directory(DB_PATH)


@app.route("/")
def home():
    return render_template(
        "index.html",
        battalions=BATTALIONS,
        categories=CATEGORIES,
        category_labels=CATEGORY_LABELS,
        support_companies=SUPPORT_COMPANIES,
        regimental_support=REGIMENTAL_SUPPORT,
        technologies=TECHNOLOGIES,
        external_dependencies=list(EXTERNAL_DEPENDENCIES),
        always_unlocked_subunits=list(ALWAYS_UNLOCKED_SUBUNITS),
        special_projects=SPECIAL_PROJECTS,
        doctrine_tracks=DOCTRINE_TRACKS,
        grand_doctrines=GRAND_DOCTRINES,
        subdoctrines=SUBDOCTRINES,
        army_spirit_categories=ARMY_SPIRIT_CATEGORIES,
        army_spirits=ARMY_SPIRITS,
        tank_chassis=TANK_CHASSIS,
        tank_roles=TANK_ROLES,
        tank_modules=TANK_MODULES,
        tank_upgrades=TANK_UPGRADES,
        always_unlocked_modules=list(ALWAYS_UNLOCKED_MODULES),
        terrain_types=TERRAIN_TYPES,
        staged_patches=STAGED_PATCHES,
    )


def _parse_doctrine(raw):
    # Shared by /api/stats and /api/item-stats - both receive the identical
    # {active_grand_doctrines, track_subdoctrines, claimed_rewards} shape
    # stats.js's "doctrine-changed" listener already builds.
    if raw is None:
        return None
    return {
        "active_grand_doctrines": set(raw.get("active_grand_doctrines", [])),
        "track_subdoctrines": raw.get("track_subdoctrines", {}),
        "claimed_rewards": raw.get("claimed_rewards", {}),
    }


@app.route("/api/stats", methods=["POST"])
def stats():
    data = request.get_json()

    if not data["battalions"]:
        # Nothing selected yet - calculate_division_stats isn't meaningful
        # (and its min()/average calls would error) on an empty division.
        return jsonify(None)

    doctrine = _parse_doctrine(data.get("doctrine"))

    def division_stats(terrain=None):
        return calculate_division_stats(
            data["battalions"],
            data.get("support_companies", []),
            data.get("regimental_support", []),
            researched=set(data.get("researched", [])),
            completed_special_projects=set(data.get("completed_special_projects", [])),
            doctrine=doctrine,
            tank_designs=data.get("tank_designs"),
            terrain=terrain,
            army_spirits=data.get("army_spirits", []),
            equipment_overrides=data.get("equipment_overrides"),
            battalion_overrides=data.get("battalion_overrides"),
        )

    result = division_stats()

    # terrain_key requests two things: the compact attack/defense percentage
    # badge (division_terrain_percentage - a single representative average,
    # since a mixed division has no one "the" terrain percentage) AND the
    # real per-field attacking/defending values, using the exact same
    # terrain parameter calculate_division_stats' own per-item application
    # already takes (unused by this route until now) - so e.g. a field like
    # soft_attack, affected by both sides, gets its own real recomputed
    # number for each side, not just one blended percentage.
    terrain_key = data.get("terrain_key")
    result["terrain"] = None
    if terrain_key:
        items = (
            list(data["battalions"])
            + list(data.get("support_companies", []))
            + list(data.get("regimental_support", []))
        )
        # Doctrine's own terrain-nested unit_bonuses (e.g. marines_2's
        # Pioneer Support/Amphibious bonus - see logic/terrain.py's
        # _doctrine_terrain_percentage, added 2026-10-07) feed into the
        # badge percentage too, not just the per-field attacking_stats/
        # defending_stats below - otherwise the two would disagree with
        # each other whenever a doctrine like this is active.
        doctrine_bonuses = active_unit_bonuses(**doctrine) if doctrine is not None else None
        attacking = division_stats({"terrain_key": terrain_key, "is_attacking": True})
        defending = division_stats({"terrain_key": terrain_key, "is_attacking": False})
        result["terrain"] = {
            "attack_percentage": division_terrain_percentage(
                items, terrain_key, is_attacking=True, doctrine_bonuses=doctrine_bonuses
            ),
            "defense_percentage": division_terrain_percentage(
                items, terrain_key, is_attacking=False, doctrine_bonuses=doctrine_bonuses
            ),
            "attacking_stats": {field: attacking[field] for field in ATTACK_SIDE_FIELDS},
            "defending_stats": {field: defending[field] for field in DEFENCE_SIDE_FIELDS},
        }

    return jsonify(result)


@app.route("/api/design-search", methods=["POST"])
def design_search():
    # Punch-list step 8, Intial_problem.md's own "AI design comparison"
    # stretch goal - generates and ranks several candidate divisions
    # instead of computing one already-chosen division's stats. Same
    # context shape /api/stats already takes (researched/
    # completed_special_projects/doctrine/tank_designs/terrain_key/
    # army_spirits) - all fixed, held constant across every generated
    # candidate - but no battalions/support_companies/regimental_support
    # in the request, since those are what's being searched FOR, not given.
    # No persistence side effect, same as /api/stats/item-stats.
    #
    # constraints (added 2026-11-02, same day - see the plan file's "AI
    # Design Comparison - Constraints Extension" section) arrives as one
    # nested object alongside the existing top-level fields -
    # {stat_bounds, required_battalions, research_year_cutoff}, all
    # optional. research_year_cutoff is resolved HERE, not inside
    # generate_best_designs - "only use tech up to 1940" REPLACES the
    # client's own researched set entirely (Ollie's own call: the intent
    # is "pretend it's 1940," not "whatever I've researched that also
    # happens to be early"), via the new researched_keys_by_year helper.
    # completed_special_projects is passed through completely unchanged
    # regardless of any cutoff - Special Projects have no calendar year
    # anywhere in this app's data, so there's no principled way to decide
    # which ones "existed" by a given year (also Ollie's own call).
    #
    # vary_army_spirits (added 2026-11-02, the plan file's "AI Design
    # Comparison - Phase 2" Phase 1) - when true, Officer Corps becomes a
    # real search variable instead of fixed context; `army_spirits` is
    # still sent either way (used as the fixed baseline when false, same
    # as before this flag existed). excluded_battalions is the inverse of
    # required_battalions, added the same day; excluded_categories
    # (added 2026-11-03) is the same idea one level up ("exclude all
    # Armored Combat Support"), and required_battalions' "only" mode
    # (also 2026-11-03) is a step up from "dominant" ("ONLY be a certain
    # battalion" rather than merely its largest share) - see
    # logic/design_search.py's own docstring for both. vary_doctrine/
    # required_doctrines (Phase 2, same day) are the identical pattern for
    # Doctrine - `doctrine` is still sent either way (used as the fixed
    # baseline when vary_doctrine is false).
    data = request.get_json()
    doctrine = _parse_doctrine(data.get("doctrine"))

    raw_constraints = data.get("constraints") or {}
    cutoff = raw_constraints.get("research_year_cutoff")
    researched = researched_keys_by_year(cutoff) if cutoff is not None else set(data.get("researched", []))

    results, infeasible_reason = generate_best_designs(
        data["numerator"],
        data.get("denominator"),
        researched=researched,
        completed_special_projects=set(data.get("completed_special_projects", [])),
        doctrine=doctrine,
        tank_designs=data.get("tank_designs"),
        terrain={"terrain_key": data["terrain_key"], "is_attacking": True} if data.get("terrain_key") else None,
        army_spirits=data.get("army_spirits", []),
        vary_army_spirits=bool(data.get("vary_army_spirits")),
        vary_doctrine=bool(data.get("vary_doctrine")),
        constraints={
            "stat_bounds": raw_constraints.get("stat_bounds", []),
            "required_battalions": raw_constraints.get("required_battalions", []),
            "excluded_battalions": raw_constraints.get("excluded_battalions", []),
            "excluded_categories": raw_constraints.get("excluded_categories", []),
            "required_doctrines": raw_constraints.get("required_doctrines", []),
        },
    )
    # infeasible_reason (added 2026-11-02, Ollie's own request for an
    # actual explanation rather than just "try loosening something") is
    # None unless `results` is empty AND a constraint genuinely explains
    # why - see generate_best_designs' own docstring for the 3 possible
    # shapes. static/js/design_search.js turns this into real wording;
    # this route just passes the raw data straight through.
    return jsonify({"candidates": results, "infeasible_reason": infeasible_reason})


@app.route("/api/item-stats", methods=["POST"])
def item_stats():
    # Lets a picker dialog show a candidate's stats BEFORE it's selected -
    # one batch call per dialog-open, covering every option currently
    # listed, rather than one call per item. Mirrors /api/stats' own
    # context shape (researched/completed_special_projects/doctrine/
    # tank_designs) but calls calculate_item_stats per item instead of
    # calculate_division_stats on a whole division - no aggregation, no
    # terrain (that's a division-wide/attack-defense concept, out of scope
    # for "this item's own stats").
    data = request.get_json()
    doctrine = _parse_doctrine(data.get("doctrine"))
    researched = set(data.get("researched", []))
    completed_special_projects = set(data.get("completed_special_projects", []))
    tank_designs = data.get("tank_designs")

    result = {}
    for item in data["items"]:
        result[item["item_key"]] = calculate_item_stats(
            item["item_key"],
            is_support_type=item.get("is_support_type", False),
            researched=researched,
            completed_special_projects=completed_special_projects,
            doctrine=doctrine,
            tank_designs=tank_designs,
        )
    return jsonify(result)


@app.route("/api/tank-designer/stats", methods=["POST"])
def tank_designer_stats():
    # Mirrors /api/stats's shape: JS sends the raw design-in-progress state,
    # the server runs the real, already-tested calculate_tank_design_stats/
    # validate_design (see logic/tank_designer.py) rather than reimplementing
    # either in JS - the same "complex aggregation stays server-side" call
    # stats.js's own header comment already documents for calculate_division_stats.
    data = request.get_json()
    chosen_modules = {slot: key for slot, key in data.get("chosen_modules", {}).items() if key}
    role_key = data.get("role_key")

    violations = validate_design(data["chassis_key"], chosen_modules, role_key=role_key)
    design_stats = calculate_tank_design_stats(
        data["chassis_key"], data["tier"], chosen_modules,
        role_key=role_key, tick_levels=data.get("tick_levels", {}),
    )
    return jsonify({"stats": design_stats, "violations": violations})


@app.route("/api/tank-designer/preview-stats", methods=["POST"])
def tank_designer_preview_stats():
    # Lets the chassis/tier/role/module pickers show what a candidate
    # choice would actually produce BEFORE it's picked - a true merged-
    # design result (build_candidate_design), not a module's raw static
    # deltas, since multiply_stats percentages sum across chassis + role +
    # every chosen module and can't be read off one module's own data in
    # isolation. One batch call per picker render, covering every
    # candidate currently listed - mirrors /api/item-stats' own "one call,
    # not one per option" shape.
    data = request.get_json()
    base_design = {
        "chassis_key": data["chassis_key"],
        "tier": data["tier"],
        "role_key": data.get("role_key"),
        "chosen_modules": {slot: key for slot, key in data.get("chosen_modules", {}).items() if key},
        "tick_levels": data.get("tick_levels", {}),
    }

    result = {}
    for candidate in data["candidates"]:
        design = build_candidate_design(base_design, candidate)
        violations = validate_design(design["chassis_key"], design["chosen_modules"], role_key=design["role_key"])
        design_stats = calculate_tank_design_stats(
            design["chassis_key"], design["tier"], design["chosen_modules"],
            role_key=design["role_key"], tick_levels=design["tick_levels"],
        )
        # str() - a tier candidate's own id is a bare number (JS's
        # tierEntry.tier), and Flask's JSON provider sorts response dict
        # keys by default, which raises a TypeError comparing a str id
        # (chassis/role/module candidates) against an int one in the same
        # response. Every id is opaque to this route anyway (JS looks it
        # back up via the same value it sent), so coercing to str here is
        # free and makes every id type safe to mix.
        result[str(candidate["id"])] = {"stats": design_stats, "violations": violations}
    return jsonify(result)


@app.route("/api/state", methods=["GET"])
def get_state():
    # Every currently-saved section at once - static/js/persistence.js
    # calls this exactly once, on page load, then restores each
    # state-owning file in the dependency order its own module comment
    # documents. Sections nothing has saved yet are simply absent from the
    # response, not null-padded - every restoreState() already treats "no
    # section" the same as "no event has fired yet this page load".
    return jsonify(get_all_sections(DB_PATH))


@app.route("/api/state/<section>", methods=["POST"])
def save_state(section):
    # One section per call (not the whole state at once) - persistence.js
    # fires this per CustomEvent, debounced, so e.g. a single battalion
    # pick only ever rewrites the `composition` row, not every section.
    set_section(DB_PATH, section, request.get_json())
    return jsonify({"ok": True})


@app.route("/api/state", methods=["DELETE"])
def reset_state():
    # Backs the "Reset All" control - wipes every section back to a fresh
    # install's "nothing saved yet" state. Deliberately does NOT touch
    # saved_divisions - a named save is a separate, intentional library,
    # not part of the session's live scratch state this clears.
    clear_all_sections(DB_PATH)
    return jsonify({"ok": True})


# Persistence Phase 2 (added 2026-11-02) - the named "save this division,
# list saved ones, load one back, compare two side by side" library, on top
# of Phase 1's session auto-save/restore above. A save is always the FULL
# 8-section bundle static/js/persistence.js's getAllSectionsState() builds
# (the exact same shape GET /api/state already returns) - never a partial
# one - so loading a save reproduces the exact stats it had when saved,
# regardless of what's since changed elsewhere.


@app.route("/api/saved-divisions", methods=["GET"])
def get_saved_divisions():
    # Metadata only (name + saved_at) - static/js/saved_divisions.js's list
    # view never needs every full bundle just to render rows.
    return jsonify(list_saved_divisions(DB_PATH))


@app.route("/api/saved-divisions/<name>", methods=["GET"])
def get_saved_division_route(name):
    saved = get_saved_division(DB_PATH, name)
    if saved is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(saved)


@app.route("/api/saved-divisions/<name>", methods=["POST"])
def save_division_route(name):
    # saved_at is set here, server-side, never trusting a client-supplied
    # timestamp - the request body is just the raw 8-section bundle.
    save_division(DB_PATH, name, request.get_json(), datetime.now(timezone.utc).isoformat())
    return jsonify({"ok": True})


@app.route("/api/saved-divisions/<name>", methods=["DELETE"])
def delete_saved_division_route(name):
    delete_saved_division(DB_PATH, name)
    return jsonify({"ok": True})


if __name__ == "__main__":
    # host="0.0.0.0" binds to every network interface, not just localhost,
    # so a phone on the same Wi-Fi can reach it via this PC's LAN IP - see
    # Activity_Log.md for the debug-mode-on-a-network tradeoff this implies.
    # Only safe on a trusted home network, never anything shared/public.
    app.run(debug=True, host="0.0.0.0")
