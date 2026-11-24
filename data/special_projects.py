# The 8 distinct Special Project keys gating the 18 Special-Project
# technologies in data/technologies.py's "special_project_requires" field
# (added 2026-10-01). technologies_copy/special_projects_tech.txt turned out
# to be unrelated (6 misc hidden techs, mostly nuclear-bomb production, not
# these 8 projects). The real source, found 2026-10-02 (Ollie relocated his
# local reference copies under a new Copies/ folder, including the genuine
# common/special_projects/ files - Copies/special_projects_copy/projects/
# {land,air,naval}_projects.txt): each project's own block, keyed identically
# to how every gated technology already references it via
# `is_special_project_completed = sp:<key>`.
#
# "name" (added 2026-10-02) is the real in-game generic (non-country-specific)
# display name, pulled directly from the actual HOI4 install's own
# localisation/english/special_projects_l_english.yml on this machine - not
# a guess, and more authoritative than a screenshot (zero transcription
# risk, it's the literal string the game renders). Country-specific
# overrides (e.g. USA's "M3 Satan" for sp_land_flamethrower_tank, confirmed
# by Ollie's own screenshots) are deliberately not modeled - this app
# doesn't track country selection at all.
#
# "unlocks_subunits"/"unlocks_equipment"/"unlocks_equipment_modules" (added
# 2026-10-02) mirror data/technologies.py's own three fields exactly, but
# compiled from each PROJECT's own `project_output` block - a real, separate
# unlock layer this project hadn't modeled at all until Ollie's screenshots
# of "M3 Satan" (the US flamethrower tank project) showed a direct
# "Sub units(s): Light Flame Tank Company" grant with no technology
# involved. Reading all 8 projects' full `project_output` blocks confirmed
# the same pattern repeats: 8 subunits and 11 Tank Designer modules already
# compiled elsewhere in this project were, until this compile, sitting in
# ALWAYS_UNLOCKED_SUBUNITS/ALWAYS_UNLOCKED_MODULES (logic/research.py) with
# no gate modeled at all - now correctly gated behind their project's
# completion. `generic_prototype_rewards`/`unique_prototype_rewards` are
# deliberately NOT compiled - random per-playthrough bonus rolls (RNG
# options like a 0.1 build-cost/soft-attack swing either direction on
# sp_land_super_heavy_howitzer's own prototype), not deterministic
# completion effects like `project_output`, so there is nothing
# reproducible to compile.
#
# A handful of `enable_equipments` keys in the raw source
# (armored_support_vehicle_1, land_cruiser_chassis_1/land_cruiser_equipment_1,
# super_heavy_artillery_equipment_1, self_propelled_super_heavy_artillery_equipment_1,
# helicopter_equipment_1) don't exist as separate data/equipment.py entries -
# confirmed NOT a gap (same "_1 tier suffix" pattern as
# sp_armored_motorized_military_police_tech's own motorbike_equipment_1,
# data/technologies.py's header) - each aliases to the already-compiled base
# key data/equipment_needs.py already uses for that subunit
# (armored_support_vehicle, land_cruiser_chassis, super_heavy_artillery_equipment,
# self_propelled_super_heavy_artillery_equipment, helicopter_equipment
# respectively; land_cruiser's own two source keys are a DLC-branch
# duplicate of the same equipment family, not two different ones - this
# project doesn't model DLC presence, so both collapse to the one real key).
#
# "requires" (added 2026-10-02) is the project's own `special_project_parent`
# dependency - which OTHER special projects must be completed first. Empty
# for 7 of the 8; sp_land_self_propelled_super_heavy_howitzer requires BOTH
# sp_land_military_engineering_vehicles AND sp_land_super_heavy_howitzer, an
# AND list (mirrors data/technologies.py's own "requires" shape, not
# "unlocked_by" - this is a real, hard AND gate confirmed directly in the
# source, not a cosmetic path marker like unlocked_by's deliberate [] on
# every Special-Project-gated technology). Enforced by
# logic/special_projects.py's is_special_project_completable, the project-
# level mirror of logic/research.py's is_researchable - same gating
# discipline, just without the unlocked_by/mutually_exclusive_with/
# EXTERNAL_DEPENDENCIES machinery special projects don't have.
#
# "unit_bonuses" (added 2026-10-07) is a THIRD, previously-missed unlock
# layer, found while cross-checking Ollie's full Special_Projects_Screenshots/
# set (all 8 projects, 39 screenshots) against this file - every subunit/
# equipment/module shown matched exactly for 7 of the 8 projects, but Large
# Caliber Kinetic Energy Sabot's own in-game Project Output screen showed
# direct stat bonuses (Piercing/Fort Attack on Artillery, Support Artillery,
# Motorized Artillery, Self-Propelled Artillery, Super-Heavy Artillery,
# Self-Propelled Super-Heavy Artillery, Field Guns) nowhere in the compiled
# data. Tracing it to source: the project's own `project_output` doesn't
# grant these through `sp_advance_sabot_shells` (the one real, player-visible
# technology it unlocks, already correctly modeled via
# data/technologies.py's special_project_requires) - it separately and
# silently auto-grants a completely hidden, unresearchable technology
# (`allow = { always = no }`) the instant the project completes
# (`hidden_effect = { set_technology = { sp_land_large_caliber_kinetic_energy_sabot_gd_tech = 1 } }`,
# Copies/special_projects_copy/projects/land_projects.txt), and THAT hidden
# tech - found in technologies_copy/artillery.txt, never compiled into
# data/technologies.py since it's `always = no` (can't be researched,
# correctly excluded by the same hidden-tech rule as every other
# `is_special_project_tech`) - is what actually carries the bonus. Checked
# all other 7 projects for the same `hidden_effect`/`set_technology` pattern:
# only sp_naval_proximity_fuze also has one (+25% Naval AA attack,
# MTG_naval.txt - correctly out of scope, this app doesn't model Navy).
# Picked the DLC-gated `_gd_tech` variant (not `_no_gd_tech`) to match this
# project's existing "assume the full DLC stack" convention (Land Cruiser's
# No Step Back content, Helicopter's Gotterdammerung-gated module) - also
# the variant Ollie's own screenshot actually showed (it includes Super-Heavy
# Artillery/Self-Propelled Super-Heavy Artillery, only present in `_gd_tech`).
# Shape mirrors data/technologies.py's own unit_bonuses exactly, `{}` on the
# other 7 projects via the same setdefault normalization-loop precedent.
# `fort` is a terrain-nested sub-dict (HOI4's "Fort" is one of Terrain's own
# 3 situational TERRAIN_TYPES, not a combat-stat field) - compiled here but
# deliberately left unapplied, matching the identical precedent already set
# for Doctrine's and Technology's own terrain-nested unit_bonuses.
# `sp_land_multi_charge_large_caliber_gun_speed_factor` (a research-speed
# modifier) and `experience_gain_artillery_combat_factor` (an army-wide
# experience modifier) are also on the hidden tech but have no tracked
# equivalent anywhere in this app - silently dropped, not guessed at, same
# treatment as every other untracked unit_bonuses field.
# See Activity_Log.md, 2026-10-01, 2026-10-02, and 2026-10-07, for the full
# investigation.
SPECIAL_PROJECTS = [
    {
        "key": "sp_land_land_cruiser", "name": "Land Cruiser", "requires": [],
        "unlocks_subunits": ["land_cruiser"],
        "unlocks_equipment": ["land_cruiser_chassis"],
        "unlocks_equipment_modules": [
            "lc_heavy_naval_guns", "lc_medium_naval_guns", "lc_super_heavy_howitzer",
            "lc_aircraft_catapult", "lc_internal_fuel_tanks", "lc_internal_ammunition_compartments",
            "lc_wet_ammunition_storage", "lc_smoke_generators", "lc_stabilizers",
        ],
    },
    {
        "key": "sp_land_military_engineering_vehicles", "name": "Military Engineering Vehicles", "requires": [],
        "unlocks_subunits": ["assault_engineer"],
        "unlocks_equipment": ["armored_support_vehicle"],
        "unlocks_equipment_modules": [],
    },
    {
        "key": "sp_air_helicopter", "name": "Helicopter", "requires": [],
        "unlocks_subunits": ["helicopter_brigade"],
        "unlocks_equipment": ["helicopter_equipment"],
        "unlocks_equipment_modules": ["lc_helipad"],
    },
    {
        "key": "sp_naval_proximity_fuze", "name": "Proximity Fuze", "requires": [],
        "unlocks_subunits": [], "unlocks_equipment": [], "unlocks_equipment_modules": [],
    },
    {
        "key": "sp_land_flamethrower_tank", "name": "Flamethrower Tank", "requires": [],
        "unlocks_subunits": ["light_flame_tank", "medium_flame_tank", "heavy_flame_tank"],
        "unlocks_equipment": [],
        "unlocks_equipment_modules": ["flamethrower", "lc_flamethrower_turret"],
    },
    {
        "key": "sp_land_large_caliber_kinetic_energy_sabot", "name": "Large Caliber Kinetic Energy Sabot",
        "requires": [],
        "unlocks_subunits": [], "unlocks_equipment": [], "unlocks_equipment_modules": [],
        "unit_bonuses": {
            "artillery_brigade": {"ap_attack": 0.15, "fort": {"attack": 0.15}},
            "artillery": {"ap_attack": 0.15, "fort": {"attack": 0.15}},
            "mot_artillery_brigade": {"ap_attack": 0.15, "fort": {"attack": 0.15}},
            "category_self_propelled_artillery": {"ap_attack": 0.15, "fort": {"attack": 0.15}},
            "super_heavy_artillery": {"ap_attack": 0.15, "fort": {"attack": 0.15}},
            "self_propelled_super_heavy_artillery": {"ap_attack": 0.15, "fort": {"attack": 0.15}},
            "field_guns": {"ap_attack": 0.1},
        },
    },
    {
        "key": "sp_land_self_propelled_super_heavy_howitzer", "name": "Self-Propelled Super-Heavy Howitzer",
        "requires": ["sp_land_military_engineering_vehicles", "sp_land_super_heavy_howitzer"],
        "unlocks_subunits": ["self_propelled_super_heavy_artillery"],
        "unlocks_equipment": ["self_propelled_super_heavy_artillery_equipment"],
        "unlocks_equipment_modules": [],
    },
    {
        "key": "sp_land_super_heavy_howitzer", "name": "Super-Heavy Howitzer", "requires": [],
        "unlocks_subunits": ["super_heavy_artillery"],
        "unlocks_equipment": ["super_heavy_artillery_equipment"],
        "unlocks_equipment_modules": [],
    },
]

for _project in SPECIAL_PROJECTS:
    _project.setdefault("unit_bonuses", {})
del _project
