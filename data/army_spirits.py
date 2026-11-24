# Officer Corps' "Army Spirits" - compiled directly from
# Copies/army_spirits_copy.txt (HOI4's real common/ideas/00_army_spirits.txt,
# 1318 lines). The file holds 44 raw `ideas = { <category> = { <spirit> =
# {...} } }` entries across 3 categories (academy_spirit/army_spirit/
# division_command_spirit, matching the real in-game Officer Corps panel's
# 3 columns). 3 carry a country-tag prefix (NOR_flexible_officers_
# academy_spirit, CHI_whampoa_military_academy_spirit, CZE_legacy_of_the_
# czechoslovak_legion_army_spirit - real country-specific content, excluded
# same as Tank Designer's own Norway-only modules), and
# subsidized_contracts_no_lar_army_spirit is a DLC-variant duplicate of
# subsidized_contracts_army_spirit (excluded, Ollie owns every DLC) - 40
# generic entries after both exclusions.
#
# **Re-scoped the same day it was first built (2026-11-02)**: Ollie
# reviewed the live Officer Corps tab and flagged that the overwhelming
# majority of those 40 are country/army-wide meta (leader XP gain,
# advisor/design-cost factors, political/war stability, intel, manpower,
# dig-in, resistance, command power, training time, supply grace) with
# zero concept anywhere in this app's Stats to attach to - the exact same
# "country-wide modifiers, no attachment point" exclusion this project's
# own Doctrine compile already established (data/doctrines.py's own
# `modifiers` field, e.g. `planning_speed`). Cut down to only the entries
# that bear on a stat this app actually computes:
#
# - **4 entries with a real, per-EQUIPMENT `equipment_bonus`** (targets a
#   real data/equipment.py key directly, the same structurally-applicable
#   shape Doctrine's own `equipment_bonus` field - siege_artillery - has,
#   just never wired up either): subsidized_contracts_army_spirit,
#   all_arms_at_defense_army_spirit, direct_fire_support_army_spirit,
#   rapid_emplacement_army_spirit. **Applied 2026-11-03**: Ollie supplied
#   real in-game tooltip screenshots for all 4 - every one showed an
#   explicit `%` sign (e.g. All-Arms Anti-tank Defense: "Infantry
#   Equipment: Hard Attack: +25%"), confirming these are percentage
#   bonuses on the target equipment's own resolved stat, applied at
#   logic/stats.py's own equipment-resolution step - see
#   logic/army_spirits.py's active_equipment_bonuses and
#   logic/stats.py's _apply_equipment_bonus.
# - **5 entries whose own country-wide `modifiers` dict happens to use a
#   field name matching a stat this app tracks** (breakthrough_factor,
#   supply_consumption_factor, army_strength_factor, army_speed_factor x2):
#   smoke_and_fire_spirit, logistical_focus_spirit, operational_reserve_spirit,
#   flexible_organization_spirit, maneuver_warfare_spirit. Kept per Ollie's
#   explicit call ("keep them, we will apply them later") even though these
#   are structurally a DIFFERENT kind of bonus from the 4 above - a flat
#   value applying to the whole army/division uniformly, not a per-item/
#   category-matched bonus. **All 5 are now applied** (army_strength_factor
#   confirmed 2026-11-02; the other 4 confirmed 2026-11-03, same real-
#   tooltip-screenshot method, every one also a percentage) - see
#   logic/army_spirits.py's active_army_strength_factor/
#   active_breakthrough_factor/active_supply_consumption_factor/
#   active_army_speed_factor and logic/stats.py's calculate_division_stats.
#
# Every other field these 9 entries also carry alongside the one that
# matters (e.g. flexible_organization_spirit's own org_loss_when_moving/
# choose_preferred_tactics_cost) is still compiled as-is in `modifiers` -
# not stripped out - since the dict is a faithful transcription of the
# source block, not a filtered one.
#
# This drops `academy_spirit` to zero surviving entries (none of its 13
# bore on a tracked stat) - removed from ARMY_SPIRIT_CATEGORIES entirely,
# since a UI section with nothing ever selectable in it has no purpose.
# Final count: **9 entries across 2 categories** (1 army_spirit, 8
# division_command_spirit).
#
# `name` is pulled directly from the real installed game's own localisation
# (C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV\
# localisation\english\{nsb,SEA}_ideas_l_english.yml) - the same
# ground-truth-over-guesswork standard every other named entity in this
# project already got.
#
# `available` is each entry's own `available = { has_doctrine = X }` /
# `OR = { has_doctrine = X ... }` block, flattened to a plain list of
# doctrine/subdoctrine keys (OR semantics - real HOI4's `has_doctrine`
# matches either a Grand Doctrine or a Subdoctrine once adopted). Every
# reference below resolves to a real key in data/doctrines.py.
#
# `rapid_emplacement_army_spirit`'s own `motorized_rocket_equipment`
# sub-bonus targets an equipment key this app doesn't model at all
# (confirmed absent from data/equipment.py) - stays permanently inert even
# now that the other 4 keys in that same entry are applied (2026-11-03;
# see logic/army_spirits.py's active_equipment_bonuses), since no item in
# this app ever needs that equipment key and so can never match it.

ARMY_SPIRIT_CATEGORIES = [
    {"key": "army_spirit", "label": "Army"},
    {"key": "division_command_spirit", "label": "Division Command"},
]

ARMY_SPIRITS = [
    # --- army_spirit (1) ---
    {
        "key": "subsidized_contracts_army_spirit", "name": "Subsidized Contracts", "category": "army_spirit",
        "available": ["new_mobile_warfare", "armored_cavalry"],
        "modifiers": {},
        "equipment_bonus": {
            "armored_car_equipment": {"build_cost_ic": -0.15},
            "light_tank_chassis": {"build_cost_ic": -0.10},
            "armored_support_vehicle": {"build_cost_ic": -0.10},
        },
    },

    # --- division_command_spirit (8) ---
    {
        "key": "smoke_and_fire_spirit", "name": "Smoke and Fire", "category": "division_command_spirit",
        "available": ["superior_firepower"],
        "modifiers": {"breakthrough_factor": 0.06},
        "equipment_bonus": {},
    },
    {
        "key": "logistical_focus_spirit", "name": "Logistical Focus", "category": "division_command_spirit",
        "available": ["grand_battleplan"],
        "modifiers": {
            "supply_consumption_factor": -0.10, "air_fuel_consumption_factor": -0.10,
            "navy_fuel_consumption_factor": -0.10,
        },
        "equipment_bonus": {},
    },
    {
        "key": "operational_reserve_spirit", "name": "Operational Reserves", "category": "division_command_spirit",
        "available": ["mass_assault"],
        "modifiers": {"army_strength_factor": 0.1},
        "equipment_bonus": {},
    },
    {
        "key": "flexible_organization_spirit", "name": "Flexible Organization", "category": "division_command_spirit",
        "available": ["new_mobile_warfare", "infiltration_tactics"],
        "modifiers": {"org_loss_when_moving": -0.15, "army_speed_factor": 0.05, "choose_preferred_tactics_cost": -15},
        "equipment_bonus": {},
    },
    {
        "key": "maneuver_warfare_spirit", "name": "Maneuver Warfare", "category": "division_command_spirit",
        "available": ["new_mobile_warfare"],
        "modifiers": {"army_speed_factor": 0.05, "coordination_bonus": 0.05},
        "equipment_bonus": {},
    },
    {
        "key": "all_arms_at_defense_army_spirit", "name": "All-Arms Anti-tank Defense", "category": "division_command_spirit",
        "available": ["superior_firepower", "tank_destroyer_force"],
        "modifiers": {},
        "equipment_bonus": {"infantry_equipment": {"hard_attack": 0.25}},
    },
    {
        "key": "direct_fire_support_army_spirit", "name": "Direct Fire Support", "category": "division_command_spirit",
        "available": ["superior_firepower", "self_propelled_support"],
        "modifiers": {},
        "equipment_bonus": {
            "light_tank_artillery_chassis": {"hard_attack": 0.50, "ap_attack": 1},
            "medium_tank_artillery_chassis": {"hard_attack": 0.50, "ap_attack": 1},
            "heavy_tank_artillery_chassis": {"hard_attack": 0.50, "ap_attack": 1},
            "modern_tank_artillery_chassis": {"hard_attack": 0.50, "ap_attack": 1},
        },
    },
    {
        "key": "rapid_emplacement_army_spirit", "name": "Rapid Emplacement", "category": "division_command_spirit",
        "available": ["superior_firepower", "flying_batteries"],
        "modifiers": {},
        "equipment_bonus": {
            "artillery_equipment": {"breakthrough": 0.10, "defense": 0.10},
            "rocket_artillery_equipment": {"breakthrough": 0.10, "defense": 0.10},
            # Not modeled anywhere in data/equipment.py - stays permanently
            # inert even once the other keys here are someday applied.
            "motorized_rocket_equipment": {"breakthrough": 0.10, "defense": 0.10},
            "anti_tank_equipment": {"breakthrough": 0.10, "defense": 0.10},
            "anti_air_equipment": {"breakthrough": 0.10, "defense": 0.10},
        },
    },
]
