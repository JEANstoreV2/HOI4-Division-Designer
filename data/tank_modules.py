# Hand-curated from tank_info/00_tank_modules_copy.txt (HOI4 game file, No
# Step Back module system - see CLAUDE.md's DLC-content stance), compiled
# 2026-09-16 for the Tank Designer's Phase 2 (module data). This is the
# single biggest data compile in the project - every module read directly
# from the source file in this session (not reconstructed from memory), 100
# real entries total: 70 main-tank modules + 30 Land Cruiser modules (the
# roadmap's "~99 + ~45" was a rough estimate made before this file was read
# in full - the real counts are smaller).
#
# Excluded, not overlooked: NOR_tank_rikstanken_armor and
# NOR_rikstanken_turret. Both carry HOI4's country-tag naming convention
# (NOR = Norway) and are not referenced or gated anywhere else in the
# reference files this project has copied - the same "hidden/focus-locked
# content is out of scope" call already made for data/technologies.py's
# excluded hidden focus/event techs.
#
# Schema, per TANK_MODULES entry (only keys the source actually sets are
# present - nothing invented/defaulted, matching data/tank_chassis.py's
# "stat_overrides only lists real overrides" precedent):
# - "key", "name" (hand-written display name; the source only has a 3-4
#   letter UI abbreviation, not a real name)
# - "category": the exact string data/tank_chassis.py's module_slots'
#   "allowed_module_categories" values use - this is what makes a module
#   legal (or not) in a given chassis slot.
# - "add_stats": flat per-field additions.
# - "multiply_stats": percentage-of-base per-field bonuses (present only
#   when the source's block is non-empty).
# - "xp_cost" / "dismantle_cost_ic" / "build_cost_resources": present only
#   when the source sets them - most engine/suspension modules have no
#   xp_cost at all, for example, and that's a real fact worth keeping
#   rather than a gap to fill with 0.
# - "allow_equipment_type": the single role tag (anti_air/artillery/
#   anti_tank/flame/amphibious) this module REQUIRES the design to be, if
#   any - e.g. amphibious_drive only fits an amphibious-role design.
# - "forbid_equipment_type": list of role tags this module is barred from
#   (normalized to a list even where the source gives one bare value, e.g.
#   `forbid_equipment_type = anti_air` on the fixed-superstructure
#   turrets - matches TANK_ROLES' own "feeds" always-a-list normalization).
# - "forbid_equipment_type_exact_match": a single equipment TYPE (not role
#   tag) this module can't appear on - only "armor" appears in the source,
#   used on the four tank_..._cannon anti-air weapons to bar them from a
#   plain (non-role) armor design.
# - "forbid_equipment_type_exact_match_for_category": {main_armament
#   category: equipment_type} - the fixed-superstructure turrets' way of
#   saying "you can mount a bigger gun class here, but not on plain armor".
# - "allowed_module_categories": a module-level override widening which
#   categories another slot on the SAME chassis will accept (e.g. a
#   fixed-superstructure turret permits a bigger main-armament category
#   than the chassis's own turret slot normally would).
# - "can_convert_from": {"module" | "module_category": key,
#   "convert_cost_ic": n} - production-line conversion costs, compiled but
#   not yet consumed by any logic (Phase 3+ concern).
# - "parent": the module this one is a direct upgrade of, where the source
#   sets it - present on some but not all Mk2/Mk3 weapons/radios (e.g.
#   tank_high_velocity_cannon_2/_3 have no "parent" field in the source at
#   all, unlike tank_auto_cannon_2 - a real source inconsistency, kept
#   as-is rather than "fixed").
#
# Two confirmed duplicate-block cases, resolved and noted here rather than
# silently picked one way:
# - tank_heavy_two_man_tank_turret's source declares
#   `allowed_module_categories` TWICE, the second narrowing
#   main_armament_slot from [medium, heavy] down to just [heavy] alone -
#   Clausewitz's script parser takes the LAST declaration for a scalar/
#   container key, so only [tank_heavy_main_armament] is kept here.
# - tank_super_heavy_three_man_tank_turret's source declares
#   `multiply_stats` TWICE with different, non-overlapping keys
#   (build_cost_ic in the first, hard_attack in the second) - merged here
#   into one dict since there's no actual key conflict to resolve either
#   way.

TANK_MODULES = [
    # ============================================================
    # Engine types (category: tank_engine_type)
    # ============================================================
    {
        "key": "tank_gasoline_engine", "name": "Gasoline Engine", "category": "tank_engine_type",
        "add_stats": {"build_cost_ic": 1, "fuel_consumption": 2, "maximum_speed": 0.5},
        "multiply_stats": {"maximum_speed": 0.15},
    },
    {
        "key": "tank_diesel_engine", "name": "Diesel Engine", "category": "tank_engine_type",
        "add_stats": {"build_cost_ic": 1, "fuel_consumption": 2, "reliability": 0.25},
    },
    {
        "key": "tank_petrol_electric_engine", "name": "Petrol-Electric Engine", "category": "tank_engine_type",
        "add_stats": {
            "fuel_consumption": 2, "build_cost_ic": 2, "reliability": -0.5,
            "breakthrough": 2, "defense": 2,
        },
        "multiply_stats": {"breakthrough": 0.15, "defense": 0.15, "build_cost_ic": 0.15},
    },
    {
        "key": "tank_gas_turbine_engine", "name": "Gas Turbine Engine", "category": "tank_engine_type",
        "add_stats": {
            "build_cost_ic": 3, "fuel_consumption": 4, "reliability": -0.1, "maximum_speed": 0.5,
        },
        "multiply_stats": {"maximum_speed": 0.25},
    },

    # ============================================================
    # Armor types (category: tank_armor_type)
    # ============================================================
    {
        "key": "tank_riveted_armor", "name": "Riveted Armor", "category": "tank_armor_type",
        "add_stats": {"defense": 2, "breakthrough": 2},
        "xp_cost": 8,
        "multiply_stats": {"build_cost_ic": -0.2},
    },
    {
        "key": "tank_cast_armor", "name": "Cast Armor", "category": "tank_armor_type",
        "add_stats": {"defense": 3, "breakthrough": 3, "hardness": 0.02},
        "dismantle_cost_ic": 1, "xp_cost": 8,
        "multiply_stats": {"build_cost_ic": 0.2, "armor_value": 0.3},
    },
    {
        "key": "tank_welded_armor", "name": "Welded Armor", "category": "tank_armor_type",
        "add_stats": {"defense": 4, "breakthrough": 4},
        "dismantle_cost_ic": 1, "xp_cost": 8,
        "multiply_stats": {"armor_value": 0.3},
        "build_cost_resources": {"chromium": 1},
    },

    # ============================================================
    # Suspension types (category: tank_suspension_type /
    # tank_non_tracked_suspension_type)
    # ============================================================
    {
        "key": "tank_torsion_bar_suspension", "name": "Torsion Bar Suspension", "category": "tank_suspension_type",
        "add_stats": {"build_cost_ic": 1, "reliability": 0.15},
        "dismantle_cost_ic": 2,
    },
    {
        "key": "tank_christie_suspension", "name": "Christie Suspension", "category": "tank_suspension_type",
        "add_stats": {"build_cost_ic": 1},
        "dismantle_cost_ic": 2,
        "multiply_stats": {"maximum_speed": 0.2},
    },
    {
        "key": "tank_bogie_suspension", "name": "Bogie Suspension", "category": "tank_suspension_type",
        "add_stats": {},
        "dismantle_cost_ic": 1,
    },
    {
        "key": "tank_interleaved_suspension", "name": "Interleaved Suspension", "category": "tank_suspension_type",
        "add_stats": {"build_cost_ic": 2, "breakthrough": 4},
        "dismantle_cost_ic": 2,
        "can_convert_from": {"module": "tank_torsion_bar_suspension", "convert_cost_ic": 0.5},
    },
    {
        "key": "tank_wheeled_suspension", "name": "Wheeled Suspension", "category": "tank_non_tracked_suspension_type",
        "add_stats": {"reliability": -0.2},
        "dismantle_cost_ic": 0.5,
        "multiply_stats": {"build_cost_ic": -0.1, "hardness": -0.4},
    },
    {
        "key": "tank_half_track_suspension", "name": "Half-Track Suspension", "category": "tank_non_tracked_suspension_type",
        "add_stats": {"reliability": -0.1},
        "dismantle_cost_ic": 0.5,
        "multiply_stats": {"build_cost_ic": -0.05, "hardness": -0.3},
        "can_convert_from": {"module": "tank_wheeled_suspension", "convert_cost_ic": 0.5},
    },

    # ============================================================
    # Turret types, light (category: tank_light_turret_type)
    # ============================================================
    {
        "key": "tank_light_one_man_tank_turret", "name": "Light One-Man Turret", "category": "tank_light_turret_type",
        "add_stats": {"build_cost_ic": 1, "breakthrough": 7},
        "dismantle_cost_ic": 0.5, "xp_cost": 2,
    },
    {
        "key": "tank_light_two_man_tank_turret", "name": "Light Two-Man Turret", "category": "tank_light_turret_type",
        "add_stats": {"build_cost_ic": 1.25, "breakthrough": 10},
        "xp_cost": 2, "dismantle_cost_ic": 0.5,
    },
    {
        "key": "tank_light_three_man_tank_turret", "name": "Light Three-Man Turret", "category": "tank_light_turret_type",
        "add_stats": {"build_cost_ic": 1.5, "maximum_speed": -0.1, "breakthrough": 14},
        "dismantle_cost_ic": 0.5, "xp_cost": 2,
    },
    {
        "key": "tank_light_fixed_superstructure_turret", "name": "Light Fixed Superstructure", "category": "tank_light_turret_type",
        "forbid_equipment_type": ["anti_air"],
        "allowed_module_categories": {"main_armament_slot": ["tank_medium_main_armament"]},
        "forbid_equipment_type_exact_match_for_category": {
            "tank_medium_main_armament": "armor",
            "tank_heavy_main_armament": "armor",
            "tank_super_heavy_main_armament": "armor",
        },
        "xp_cost": 2, "dismantle_cost_ic": 0.5,
        "add_stats": {"build_cost_ic": 1, "reliability": 0.2, "defense": 3},
        "multiply_stats": {"breakthrough": -0.25},
        "can_convert_from": {"module_category": "tank_light_turret_type", "convert_cost_ic": 0.75},
    },

    # ============================================================
    # Turret types, medium (category: tank_medium_turret_type)
    # ============================================================
    {
        "key": "tank_medium_one_man_tank_turret", "name": "Medium One-Man Turret", "category": "tank_medium_turret_type",
        "allowed_module_categories": {"main_armament_slot": ["tank_medium_main_armament"]},
        "add_stats": {"build_cost_ic": 1.25, "breakthrough": 8},
        "dismantle_cost_ic": 1, "xp_cost": 2,
        "multiply_stats": {"hard_attack": -0.05, "soft_attack": -0.05},
    },
    {
        "key": "tank_medium_two_man_tank_turret", "name": "Medium Two-Man Turret", "category": "tank_medium_turret_type",
        "allowed_module_categories": {"main_armament_slot": ["tank_medium_main_armament"]},
        "add_stats": {"build_cost_ic": 1.75, "breakthrough": 16},
        "dismantle_cost_ic": 1, "xp_cost": 2,
    },
    {
        "key": "tank_medium_three_man_tank_turret", "name": "Medium Three-Man Turret", "category": "tank_medium_turret_type",
        "allowed_module_categories": {"main_armament_slot": ["tank_medium_main_armament"]},
        "add_stats": {"build_cost_ic": 2.25, "maximum_speed": -0.25, "breakthrough": 24},
        "dismantle_cost_ic": 1, "xp_cost": 2,
    },
    {
        "key": "tank_medium_fixed_superstructure_turret", "name": "Medium Fixed Superstructure", "category": "tank_medium_turret_type",
        "forbid_equipment_type": ["anti_air"],
        "allowed_module_categories": {"main_armament_slot": ["tank_medium_main_armament", "tank_heavy_main_armament"]},
        "forbid_equipment_type_exact_match_for_category": {
            "tank_heavy_main_armament": "armor",
            "tank_super_heavy_main_armament": "armor",
        },
        "xp_cost": 2, "dismantle_cost_ic": 1,
        "add_stats": {"build_cost_ic": 1.5, "reliability": 0.2, "defense": 3},
        "multiply_stats": {"breakthrough": -0.25},
        "can_convert_from": {"module_category": "tank_medium_turret_type", "convert_cost_ic": 1.5},
    },

    # ============================================================
    # Turret types, heavy (category: tank_heavy_turret_type)
    # ============================================================
    {
        "key": "tank_heavy_two_man_tank_turret", "name": "Heavy Two-Man Turret", "category": "tank_heavy_turret_type",
        # Source declares allowed_module_categories twice; the second
        # (narrower) declaration wins - see module header note.
        "allowed_module_categories": {"main_armament_slot": ["tank_heavy_main_armament"]},
        "xp_cost": 2, "dismantle_cost_ic": 1,
        "add_stats": {"build_cost_ic": 5, "breakthrough": 18},
    },
    {
        "key": "tank_heavy_three_man_tank_turret", "name": "Heavy Three-Man Turret", "category": "tank_heavy_turret_type",
        "allowed_module_categories": {"main_armament_slot": ["tank_medium_main_armament", "tank_heavy_main_armament"]},
        "dismantle_cost_ic": 1, "xp_cost": 2,
        "add_stats": {"build_cost_ic": 5.5, "maximum_speed": -0.25, "breakthrough": 22},
    },
    {
        "key": "tank_heavy_fixed_superstructure_turret", "name": "Heavy Fixed Superstructure", "category": "tank_heavy_turret_type",
        "forbid_equipment_type": ["anti_air"],
        "allowed_module_categories": {
            "main_armament_slot": ["tank_medium_main_armament", "tank_heavy_main_armament", "tank_super_heavy_main_armament"]
        },
        "forbid_equipment_type_exact_match_for_category": {"tank_super_heavy_main_armament": "armor"},
        "dismantle_cost_ic": 1, "xp_cost": 2,
        "add_stats": {"build_cost_ic": 5, "reliability": 0.2, "defense": 3},
        "multiply_stats": {"breakthrough": -0.25},
        "can_convert_from": {"module_category": "tank_heavy_turret_type", "convert_cost_ic": 5},
    },

    # ============================================================
    # Turret types, super heavy / modern
    # ============================================================
    {
        "key": "tank_super_heavy_three_man_tank_turret", "name": "Super Heavy Three-Man Turret", "category": "tank_super_heavy_turret_type",
        "allowed_module_categories": {
            "main_armament_slot": ["tank_medium_main_armament", "tank_heavy_main_armament", "tank_super_heavy_main_armament"]
        },
        "add_stats": {"build_cost_ic": 10, "reliability": -0.1, "maximum_speed": -0.2, "breakthrough": 24},
        # Source declares multiply_stats twice with non-overlapping keys -
        # merged, see module header note.
        "multiply_stats": {"build_cost_ic": 0.50, "hard_attack": -0.1},
        "dismantle_cost_ic": 1, "xp_cost": 2,
    },
    {
        "key": "tank_super_heavy_four_man_tank_turret", "name": "Super Heavy Four-Man Turret", "category": "tank_super_heavy_turret_type",
        "allowed_module_categories": {
            "main_armament_slot": ["tank_medium_main_armament", "tank_heavy_main_armament", "tank_super_heavy_main_armament"]
        },
        "add_stats": {"build_cost_ic": 12, "reliability": -0.25, "maximum_speed": -0.5, "breakthrough": 35},
        "multiply_stats": {"build_cost_ic": 0.50},
        "dismantle_cost_ic": 1, "xp_cost": 2,
    },
    {
        "key": "tank_modern_tank_turret", "name": "Modern Tank Turret", "category": "tank_modern_turret_type",
        "allowed_module_categories": {"main_armament_slot": ["tank_medium_main_armament", "tank_heavy_main_armament"]},
        "add_stats": {"build_cost_ic": 8, "breakthrough": 24},
        "dismantle_cost_ic": 1, "xp_cost": 2,
    },

    # ============================================================
    # Main armament, small (category: tank_small_main_armament)
    # ============================================================
    {
        "key": "tank_heavy_machine_gun", "name": "Heavy Machine Gun", "category": "tank_small_main_armament",
        "add_stats": {"soft_attack": 8, "hard_attack": 2, "ap_attack": 6, "build_cost_ic": 0.5},
        "dismantle_cost_ic": 0.5,
        "can_convert_from": {"module_category": "tank_small_main_armament", "convert_cost_ic": 0.5},
        "xp_cost": 1,
    },
    {
        "key": "tank_auto_cannon", "name": "Auto-Cannon", "category": "tank_small_main_armament",
        "add_stats": {
            "soft_attack": 15, "hard_attack": 5, "ap_attack": 20,
            "build_cost_ic": 1.5, "maximum_speed": -0.1, "reliability": -0.1,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "tank_small_main_armament", "convert_cost_ic": 1.5},
    },
    {
        "key": "tank_auto_cannon_2", "name": "Improved Auto-Cannon", "category": "tank_small_main_armament",
        "parent": "tank_auto_cannon",
        "add_stats": {
            "soft_attack": 20, "hard_attack": 7, "ap_attack": 35,
            "build_cost_ic": 2, "maximum_speed": -0.1, "reliability": -0.1,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "tank_small_main_armament", "convert_cost_ic": 2},
    },
    {
        "key": "tank_anti_air_cannon", "name": "Anti-Air Cannon", "category": "tank_small_main_armament",
        "allow_equipment_type": "anti_air", "forbid_equipment_type_exact_match": "armor",
        "add_stats": {
            "soft_attack": 6, "hard_attack": 2, "ap_attack": 10, "air_attack": 18,
            "build_cost_ic": 2, "reliability": -0.1,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "tank_small_main_armament", "convert_cost_ic": 2},
    },
    {
        "key": "tank_anti_air_cannon_2", "name": "Improved Anti-Air Cannon", "category": "tank_small_main_armament",
        "allow_equipment_type": "anti_air", "forbid_equipment_type_exact_match": "armor",
        "parent": "tank_anti_air_cannon",
        "add_stats": {
            "soft_attack": 8, "hard_attack": 5, "ap_attack": 18, "air_attack": 31,  # (1.19.4) 32->31
            "build_cost_ic": 3, "reliability": -0.1,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "tank_small_main_armament", "convert_cost_ic": 3},
        "build_cost_resources": {"steel": 2, "tungsten": 1},
    },
    {
        "key": "tank_small_cannon", "name": "Small Cannon", "category": "tank_small_main_armament",
        "add_stats": {
            "soft_attack": 10, "hard_attack": 6, "ap_attack": 25,
            "build_cost_ic": 1.5, "maximum_speed": -0.1, "reliability": -0.1,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "tank_small_main_armament", "convert_cost_ic": 1.5},
    },
    {
        "key": "tank_small_cannon_2", "name": "Improved Small Cannon", "category": "tank_small_main_armament",
        "parent": "tank_small_cannon",
        "add_stats": {
            "soft_attack": 15, "hard_attack": 15, "ap_attack": 50,
            "build_cost_ic": 3, "maximum_speed": -0.1, "reliability": -0.1,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "tank_small_main_armament", "convert_cost_ic": 3},
    },
    {
        "key": "tank_close_support_gun", "name": "Close Support Gun", "category": "tank_small_main_armament",
        "allow_equipment_type": "artillery",
        "add_stats": {
            "soft_attack": 22, "hard_attack": 5, "ap_attack": 10,
            "build_cost_ic": 4, "maximum_speed": -0.2, "reliability": -0.1,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "tank_small_main_armament", "convert_cost_ic": 4},
        "build_cost_resources": {"steel": 1},
    },
    {
        "key": "tank_high_velocity_cannon", "name": "High-Velocity Cannon", "category": "tank_small_main_armament",
        "allow_equipment_type": "anti_tank",
        "add_stats": {
            "soft_attack": 10, "hard_attack": 26, "ap_attack": 68,
            "build_cost_ic": 3, "maximum_speed": -0.1, "reliability": -0.05,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "tank_small_main_armament", "convert_cost_ic": 3},
        "build_cost_resources": {"tungsten": 2, "steel": 2},
    },

    # ============================================================
    # Main armament, medium (category: tank_medium_main_armament)
    # ============================================================
    {
        "key": "tank_anti_air_cannon_3", "name": "Advanced Anti-Air Cannon", "category": "tank_medium_main_armament",
        "allow_equipment_type": "anti_air", "forbid_equipment_type_exact_match": "armor",
        "parent": "tank_anti_air_cannon_2",
        "add_stats": {
            "soft_attack": 10, "hard_attack": 5, "ap_attack": 24, "air_attack": 44,  # (1.19.4) 46->44
            "build_cost_ic": 4, "reliability": -0.1,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "tank_medium_main_armament", "convert_cost_ic": 4},
        "build_cost_resources": {"steel": 3, "tungsten": 1},
    },
    {
        "key": "tank_medium_cannon", "name": "Medium Cannon", "category": "tank_medium_main_armament",
        "allow_equipment_type": "anti_tank",
        "add_stats": {
            "soft_attack": 20, "hard_attack": 15, "ap_attack": 60, "build_cost_ic": 3,
            "maximum_speed": -0.2, "reliability": -0.15, "breakthrough": 2,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "tank_medium_main_armament", "convert_cost_ic": 3},
        "build_cost_resources": {"tungsten": 1, "steel": 1},
    },
    {
        "key": "tank_medium_cannon_2", "name": "Improved Medium Cannon", "category": "tank_medium_main_armament",
        "allow_equipment_type": "anti_tank", "parent": "tank_medium_cannon",
        "add_stats": {
            "soft_attack": 32, "hard_attack": 20, "ap_attack": 90, "build_cost_ic": 4,
            "maximum_speed": -0.3, "reliability": -0.15, "breakthrough": 4,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "tank_medium_main_armament", "convert_cost_ic": 4},
        "build_cost_resources": {"tungsten": 1, "steel": 2, "chromium": 1},
    },
    {
        "key": "tank_medium_howitzer", "name": "Medium Howitzer", "category": "tank_medium_main_armament",
        "allow_equipment_type": "artillery",
        "add_stats": {
            "soft_attack": 35, "hard_attack": 1, "ap_attack": 20, "build_cost_ic": 4,
            "maximum_speed": -0.3, "reliability": -0.2, "breakthrough": -2,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "tank_medium_main_armament", "convert_cost_ic": 4},
        "build_cost_resources": {"tungsten": 1, "steel": 2},
    },
    {
        "key": "tank_medium_howitzer_2", "name": "Improved Medium Howitzer", "category": "tank_medium_main_armament",
        "allow_equipment_type": "artillery", "parent": "tank_medium_howitzer",
        "add_stats": {
            "soft_attack": 45, "hard_attack": 2, "ap_attack": 30, "build_cost_ic": 5.5,
            "maximum_speed": -0.4, "reliability": -0.2, "breakthrough": -2,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "tank_medium_main_armament", "convert_cost_ic": 5.5},
        "build_cost_resources": {"tungsten": 1, "steel": 3, "chromium": 1},
    },
    {
        "key": "tank_rocket_launcher", "name": "Rocket Launcher", "category": "tank_medium_main_armament",
        "allow_equipment_type": "artillery", "forbid_equipment_type_exact_match": "armor",
        # (1.19.4) breakthrough -2->4 (now a bonus, not a penalty), hard_attack
        # 1->4, defense 0->4 (new field).
        "add_stats": {
            "soft_attack": 25, "hard_attack": 4, "ap_attack": 2, "build_cost_ic": 4,
            "maximum_speed": -0.1, "reliability": -0.1, "breakthrough": 4, "defense": 4,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "tank_medium_main_armament", "convert_cost_ic": 4},
        "build_cost_resources": {"tungsten": 2, "steel": 1},
    },
    {
        "key": "tank_rocket_launcher_2", "name": "Improved Rocket Launcher", "category": "tank_medium_main_armament",
        "allow_equipment_type": "artillery", "parent": "tank_rocket_launcher",
        "forbid_equipment_type_exact_match": "armor",
        # (1.19.4) breakthrough -2->8, hard_attack 1->6, defense 0->8 (new field).
        "add_stats": {
            "soft_attack": 35, "hard_attack": 6, "ap_attack": 2, "build_cost_ic": 5,
            "maximum_speed": -0.2, "reliability": -0.1, "breakthrough": 8, "defense": 8,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "tank_medium_main_armament", "convert_cost_ic": 5},
        "build_cost_resources": {"tungsten": 2, "steel": 1},
    },
    {
        "key": "tank_high_velocity_cannon_2", "name": "Improved High-Velocity Cannon", "category": "tank_medium_main_armament",
        "allow_equipment_type": "anti_tank",
        "add_stats": {
            "soft_attack": 20, "hard_attack": 35, "ap_attack": 125, "build_cost_ic": 5,
            "maximum_speed": -0.3, "reliability": -0.175,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "tank_medium_main_armament", "convert_cost_ic": 5},
        "build_cost_resources": {"tungsten": 2, "chromium": 1, "steel": 2},
    },

    # ============================================================
    # Main armament, heavy (category: tank_heavy_main_armament)
    # ============================================================
    {
        "key": "tank_high_velocity_cannon_3", "name": "Advanced High-Velocity Cannon", "category": "tank_heavy_main_armament",
        "allow_equipment_type": "anti_tank",
        "add_stats": {
            "soft_attack": 25, "hard_attack": 45, "ap_attack": 200, "build_cost_ic": 7,
            "maximum_speed": -0.4, "reliability": -0.2,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "tank_heavy_main_armament", "convert_cost_ic": 7},
        "build_cost_resources": {"tungsten": 2, "chromium": 1, "steel": 3},
    },
    {
        "key": "tank_heavy_cannon", "name": "Heavy Cannon", "category": "tank_heavy_main_armament",
        "allow_equipment_type": "anti_tank",
        "add_stats": {
            "soft_attack": 20, "hard_attack": 20, "ap_attack": 90, "build_cost_ic": 6,
            "maximum_speed": -0.3, "reliability": -0.25,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "tank_heavy_main_armament", "convert_cost_ic": 6},
        "build_cost_resources": {"tungsten": 1, "chromium": 1, "steel": 2},
    },
    {
        "key": "tank_heavy_cannon_2", "name": "Improved Heavy Cannon", "category": "tank_heavy_main_armament",
        "allow_equipment_type": "anti_tank", "parent": "tank_heavy_cannon",
        "add_stats": {
            "soft_attack": 25, "hard_attack": 35, "ap_attack": 125, "build_cost_ic": 7,
            "maximum_speed": -0.4, "reliability": -0.25,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "tank_heavy_main_armament", "convert_cost_ic": 7},
        "build_cost_resources": {"tungsten": 2, "chromium": 1, "steel": 2},
    },
    {
        "key": "tank_heavy_cannon_3", "name": "Advanced Heavy Cannon", "category": "tank_heavy_main_armament",
        "allow_equipment_type": "anti_tank", "parent": "tank_heavy_cannon_2",
        "add_stats": {
            "soft_attack": 30, "hard_attack": 40, "ap_attack": 170, "build_cost_ic": 8,
            "maximum_speed": -0.5, "reliability": -0.3,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "tank_heavy_main_armament", "convert_cost_ic": 8},
        "build_cost_resources": {"tungsten": 3, "chromium": 1, "steel": 3},
    },
    {
        "key": "tank_heavy_howitzer", "name": "Heavy Howitzer", "category": "tank_heavy_main_armament",
        "allow_equipment_type": "artillery",
        "add_stats": {
            "soft_attack": 55, "hard_attack": 2, "ap_attack": 60, "build_cost_ic": 7,
            "maximum_speed": -0.5, "reliability": -0.3, "breakthrough": -2,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "tank_heavy_main_armament", "convert_cost_ic": 7},
        "build_cost_resources": {"tungsten": 1, "chromium": 1, "steel": 3},
    },

    # ============================================================
    # Main armament, super heavy (category: tank_super_heavy_main_armament)
    # ============================================================
    {
        "key": "tank_super_heavy_cannon", "name": "Super Heavy Cannon", "category": "tank_super_heavy_main_armament",
        "allow_equipment_type": "anti_tank",
        "add_stats": {
            "soft_attack": 35, "hard_attack": 45, "ap_attack": 225, "build_cost_ic": 12.5,
            "maximum_speed": -0.6, "reliability": -0.35,
        },
        "xp_cost": 1,
        "build_cost_resources": {"tungsten": 5, "chromium": 2},
    },

    # ============================================================
    # Flame weapons (category: tank_flamethrower)
    # ============================================================
    {
        "key": "flamethrower", "name": "Flamethrower", "category": "tank_flamethrower",
        "allow_equipment_type": "flame",
        "add_stats": {"soft_attack": 5, "build_cost_ic": 0.5, "reliability": -0.05},
        "dismantle_cost_ic": 0.5,
        "can_convert_from": {"module_category": "tank_small_main_armament", "convert_cost_ic": 0.5},
        "xp_cost": 1,
    },
    {
        "key": "advanced_flamethrower", "name": "Advanced Flamethrower", "category": "tank_flamethrower",
        "allow_equipment_type": "flame",
        "add_stats": {"soft_attack": 12, "breakthrough": 6, "build_cost_ic": 1.2, "reliability": -0.05},
        "dismantle_cost_ic": 0.5,
        "can_convert_from": {"module_category": "tank_small_main_armament", "convert_cost_ic": 1},
        "xp_cost": 1,
    },

    # ============================================================
    # Radio modules (category: tank_radio_module)
    # ============================================================
    {
        "key": "tank_radio_1", "name": "Radio I", "category": "tank_radio_module",
        "add_stats": {"build_cost_ic": 0.5},
        "xp_cost": 1,
        "multiply_stats": {"defense": 0.20, "breakthrough": 0.15},
    },
    {
        "key": "tank_radio_2", "name": "Radio II", "category": "tank_radio_module",
        "parent": "tank_radio_1",
        "add_stats": {"build_cost_ic": 1.5},
        "xp_cost": 1,
        "multiply_stats": {"defense": 0.40, "breakthrough": 0.25},
    },
    {
        "key": "tank_radio_3", "name": "Radio III", "category": "tank_radio_module",
        "parent": "tank_radio_2",
        "add_stats": {"build_cost_ic": 2.5},
        "xp_cost": 1,
        "multiply_stats": {"defense": 0.60, "breakthrough": 0.40},
    },

    # ============================================================
    # Secondary turrets (category: tank_secondary_turret)
    # ============================================================
    {
        "key": "secondary_turret_hmg", "name": "Secondary Turret (HMG)", "category": "tank_secondary_turret",
        "add_stats": {"build_cost_ic": 1.5, "soft_attack": 4},
        "xp_cost": 1,
        "multiply_stats": {"soft_attack": -0.04},  # (1.19.4) new -4% Soft Attack penalty
    },
    {
        "key": "secondary_turret_small_cannon", "name": "Secondary Turret (Small Cannon)", "category": "tank_secondary_turret",
        "add_stats": {"soft_attack": 5, "hard_attack": 3, "build_cost_ic": 3, "reliability": -0.1, "breakthrough": 2},
        "xp_cost": 1,
        "multiply_stats": {"soft_attack": -0.05, "hard_attack": -0.05},  # (1.19.4) new -5%/-5% penalty
    },

    # ============================================================
    # Special modules (category: tank_special_module)
    # ============================================================
    {
        "key": "amphibious_drive", "name": "Amphibious Drive", "category": "tank_special_module",
        "allow_equipment_type": "amphibious", "forbid_equipment_type_exact_match": "armor",
        "forbid_equipment_type": ["anti_air", "artillery", "anti_tank", "flame"],
        "add_stats": {"build_cost_ic": 2, "reliability": -0.15},
        "xp_cost": 1,
        "multiply_stats": {"build_cost_ic": 0.1},
    },
    {
        "key": "sloped_armor", "name": "Sloped Armor", "category": "tank_special_module",
        "add_stats": {},
        "dismantle_cost_ic": 1, "xp_cost": 10,
        "multiply_stats": {"armor_value": 0.25, "build_cost_ic": 0.1},
    },
    {
        "key": "stabilizer", "name": "Stabilizer", "category": "tank_special_module",
        "add_stats": {"build_cost_ic": 2, "breakthrough": 5},
        "xp_cost": 1,
        "multiply_stats": {"hard_attack": 0.04},  # (1.19.4) new +4% Hard Attack
    },
    {
        "key": "smoke_launchers", "name": "Smoke Launchers", "category": "tank_special_module",
        "add_stats": {"build_cost_ic": 0.5, "defense": 2, "breakthrough": 2},  # (1.19.4) breakthrough 1->2
        "xp_cost": 1,
    },
    {
        "key": "extra_ammo_storage", "name": "Extra Ammo Storage", "category": "tank_special_module",
        "add_stats": {"reliability": -0.1, "breakthrough": 2, "defense": 4},
        "xp_cost": 1,
    },
    {
        "key": "wet_ammo_storage", "name": "Wet Ammo Storage", "category": "tank_special_module",
        "add_stats": {"reliability": 0.15, "build_cost_ic": 1},
        "xp_cost": 1,
    },
    {
        "key": "squeezebore_adaptor", "name": "Squeezebore Adaptor", "category": "tank_special_module",
        "add_stats": {},
        "xp_cost": 1,
        "multiply_stats": {"ap_attack": 0.1},
        "build_cost_resources": {"tungsten": 1},
    },
    {
        "key": "armor_skirts", "name": "Armor Skirts", "category": "tank_special_module",
        "add_stats": {"armor_value": 3, "breakthrough": 3, "build_cost_ic": 0.5},
        "xp_cost": 1,
    },
    {
        "key": "dozer_blade", "name": "Dozer Blade", "category": "tank_special_module",
        "add_stats": {"entrenchment": 1, "build_cost_ic": 1},
        "xp_cost": 1,
    },
    {
        "key": "auto_loader", "name": "Auto-Loader", "category": "tank_special_module",
        "add_stats": {"build_cost_ic": 1.5, "breakthrough": 4, "defense": 4},
        "xp_cost": 1,
        "multiply_stats": {"soft_attack": 0.02, "air_attack": 0.02},  # (1.19.4) new +2%/+2%
    },
    {
        "key": "easy_maintenance", "name": "Easy Maintenance", "category": "tank_special_module",
        # (1.19.4) reliability bonus 0.1->0.075, XP cost 30->20, IC reduction -0.075->-0.05
        "add_stats": {"reliability": 0.075},
        "dismantle_cost_ic": 1, "xp_cost": 20,
        "multiply_stats": {"build_cost_ic": -0.05},
    },
    {
        "key": "additional_machine_guns", "name": "Additional Machine Guns", "category": "tank_special_module",
        "add_stats": {"soft_attack": 1, "defense": 2, "build_cost_ic": 0.5},
        "xp_cost": 1,
    },
    {
        "key": "expanded_fuel_tank", "name": "Expanded Fuel Tank", "category": "tank_special_module",
        "add_stats": {"fuel_capacity": 100, "build_cost_ic": 1, "maximum_speed": -0.25},
        "xp_cost": 3,
    },

    # ============================================================
    # Land Cruiser - main armament (category: lc_main_armament)
    # ============================================================
    {
        "key": "lc_heavy_naval_guns", "name": "Heavy Naval Guns", "category": "lc_main_armament",
        "add_stats": {
            "breakthrough": 40, "soft_attack": 60, "hard_attack": 55, "ap_attack": 240,
            "build_cost_ic": 20, "maximum_speed": -0.6, "reliability": -0.2,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "lc_main_armament", "convert_cost_ic": 16},
        "build_cost_resources": {"tungsten": 7, "chromium": 4},
    },
    {
        "key": "lc_super_heavy_railway_gun", "name": "Super Heavy Railway Gun", "category": "lc_main_armament",
        "add_stats": {
            "breakthrough": 30, "soft_attack": 80, "hard_attack": 8, "ap_attack": 80,
            "build_cost_ic": 16, "maximum_speed": -0.5, "reliability": -0.15,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "lc_main_armament", "convert_cost_ic": 16},
        "build_cost_resources": {"tungsten": 5, "chromium": 3, "steel": 5},
    },
    {
        "key": "lc_high_impact_obliterator_cannon", "name": "High Impact Obliterator Cannon", "category": "lc_main_armament",
        "add_stats": {
            "breakthrough": 25, "soft_attack": 35, "hard_attack": 75, "ap_attack": 280,
            "build_cost_ic": 15, "maximum_speed": -0.4, "reliability": -0.1,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "lc_main_armament", "convert_cost_ic": 16},
        "build_cost_resources": {"tungsten": 7, "chromium": 3, "steel": 4},
    },
    {
        "key": "lc_heavy_anti_air_platform", "name": "Heavy Anti-Air Platform", "category": "lc_main_armament",
        "add_stats": {
            "breakthrough": 20, "soft_attack": 20, "hard_attack": 10, "ap_attack": 50,
            "air_attack": 80, "build_cost_ic": 10, "reliability": -0.05,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "lc_main_armament", "convert_cost_ic": 16},
        "build_cost_resources": {"tungsten": 3, "steel": 5},
    },

    # ============================================================
    # Land Cruiser - secondary armament (category: lc_secondary_armament)
    # ============================================================
    {
        "key": "lc_medium_naval_guns", "name": "Medium Naval Guns", "category": "lc_secondary_armament",
        "add_stats": {
            "breakthrough": 25, "soft_attack": 42, "hard_attack": 52, "ap_attack": 230,
            "build_cost_ic": 16, "maximum_speed": -0.4, "reliability": -0.1,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "lc_secondary_armament", "convert_cost_ic": 12},
        "build_cost_resources": {"tungsten": 6, "chromium": 3},
    },
    {
        "key": "lc_hull_mounted_railway_gun", "name": "Hull-Mounted Railway Gun", "category": "lc_secondary_armament",
        "add_stats": {
            "breakthrough": 15, "soft_attack": 70, "hard_attack": 5, "ap_attack": 70,
            "build_cost_ic": 14, "maximum_speed": -0.4, "reliability": -0.1,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "lc_secondary_armament", "convert_cost_ic": 12},
        "build_cost_resources": {"tungsten": 3, "chromium": 2, "steel": 4},
    },
    {
        "key": "lc_super_heavy_howitzer", "name": "Super Heavy Howitzer", "category": "lc_secondary_armament",
        "add_stats": {
            "breakthrough": 20, "soft_attack": 65, "hard_attack": 4, "ap_attack": 65,
            "build_cost_ic": 12, "maximum_speed": -0.4, "reliability": -0.1,
            "additional_collateral_damage": 500,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "lc_secondary_armament", "convert_cost_ic": 10},
        "build_cost_resources": {"tungsten": 3, "chromium": 2, "steel": 4},
    },
    {
        "key": "lc_heavy_high_velocity_cannons", "name": "Heavy High-Velocity Cannons", "category": "lc_secondary_armament",
        "add_stats": {
            "breakthrough": 15, "soft_attack": 30, "hard_attack": 55, "ap_attack": 250,
            "build_cost_ic": 12, "maximum_speed": -0.3, "reliability": -0.05,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "lc_secondary_armament", "convert_cost_ic": 12},
        "build_cost_resources": {"tungsten": 4, "chromium": 2, "steel": 4},
    },
    {
        "key": "lc_heavy_anti_air_battery", "name": "Heavy Anti-Air Battery", "category": "lc_secondary_armament",
        "add_stats": {
            "breakthrough": 10, "soft_attack": 14, "hard_attack": 7, "ap_attack": 40,
            "air_attack": 60, "build_cost_ic": 7,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "lc_secondary_armament", "convert_cost_ic": 12},
        "build_cost_resources": {"tungsten": 2, "steel": 4},
    },

    # ============================================================
    # Land Cruiser - additional armament (category: lc_additional_armament)
    # ============================================================
    {
        "key": "lc_medium_cannon_turret", "name": "Medium Cannon Turret", "category": "lc_additional_armament",
        "add_stats": {
            "breakthrough": 8, "soft_attack": 32, "hard_attack": 20, "ap_attack": 90,
            "build_cost_ic": 4, "maximum_speed": -0.2, "reliability": -0.05,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "lc_additional_armament", "convert_cost_ic": 4},
        "build_cost_resources": {"tungsten": 1, "chromium": 1, "steel": 2},
    },
    {
        "key": "lc_assault_gun", "name": "Assault Gun", "category": "lc_additional_armament",
        "add_stats": {
            "breakthrough": 16, "soft_attack": 55, "hard_attack": 2, "ap_attack": 40,
            "build_cost_ic": 8, "maximum_speed": -0.35, "reliability": -0.1,
            "additional_collateral_damage": 250,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "lc_additional_armament", "convert_cost_ic": 8},
        "build_cost_resources": {"tungsten": 1, "chromium": 1, "steel": 3},
    },
    {
        "key": "lc_high_velocity_cannon_turret", "name": "High-Velocity Cannon Turret", "category": "lc_additional_armament",
        "add_stats": {
            "breakthrough": 4, "soft_attack": 25, "hard_attack": 45, "ap_attack": 200,
            "build_cost_ic": 7, "maximum_speed": -0.3, "reliability": -0.05,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "lc_additional_armament", "convert_cost_ic": 8},
        "build_cost_resources": {"tungsten": 2, "chromium": 1, "steel": 3},
    },
    {
        "key": "lc_light_anti_air_battery", "name": "Light Anti-Air Battery", "category": "lc_additional_armament",
        "add_stats": {
            "soft_attack": 10, "hard_attack": 5, "ap_attack": 30, "air_attack": 46,
            "build_cost_ic": 4,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "lc_additional_armament", "convert_cost_ic": 8},
        "build_cost_resources": {"tungsten": 1, "steel": 3},
    },
    {
        "key": "lc_flamethrower_turret", "name": "Flamethrower Turret", "category": "lc_additional_armament",
        "add_stats": {"breakthrough": 8, "soft_attack": 8, "build_cost_ic": 1, "reliability": -0.05},
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "lc_additional_armament", "convert_cost_ic": 1},
        "build_cost_resources": {"steel": 1},
    },
    {
        "key": "lc_rocket_launcher", "name": "Rocket Launcher", "category": "lc_additional_armament",
        "add_stats": {
            "breakthrough": 4, "soft_attack": 35, "hard_attack": 1, "ap_attack": 2,
            "build_cost_ic": 5, "maximum_speed": -0.2, "reliability": -0.05,
        },
        "dismantle_cost_ic": 1, "xp_cost": 1,
        "can_convert_from": {"module_category": "lc_additional_armament", "convert_cost_ic": 5},
        "build_cost_resources": {"steel": 1, "tungsten": 2},
    },

    # ============================================================
    # Land Cruiser - special features
    # (categories: lc_radio_module / lc_aerial_deployment /
    # lc_external_features / lc_structural_features)
    # ============================================================
    {
        "key": "lc_radio_1", "name": "Radio I", "category": "lc_radio_module",
        "add_stats": {"build_cost_ic": 2},
        "xp_cost": 1,
        "multiply_stats": {"defense": 0.20, "breakthrough": 0.15},
    },
    {
        "key": "lc_radio_2", "name": "Radio II", "category": "lc_radio_module",
        "parent": "lc_radio_1",
        "add_stats": {"build_cost_ic": 4},
        "xp_cost": 1,
        "multiply_stats": {"defense": 0.40, "breakthrough": 0.25},
    },
    {
        "key": "lc_radio_3", "name": "Radio III", "category": "lc_radio_module",
        "parent": "lc_radio_2",
        "add_stats": {"build_cost_ic": 6},
        "xp_cost": 1,
        "multiply_stats": {"defense": 0.60, "breakthrough": 0.40},
    },
    {
        "key": "lc_command_center", "name": "Command Center", "category": "lc_radio_module",
        "add_stats": {"build_cost_ic": 8},
        "xp_cost": 1,
        "multiply_stats": {"defense": 0.75, "breakthrough": 0.5},
    },
    {
        "key": "lc_aircraft_catapult", "name": "Aircraft Catapult", "category": "lc_aerial_deployment",
        "add_stats": {"recon": 5, "defense": 1, "air_attack": 2, "build_cost_ic": 6, "fuel_consumption": 2},
        "xp_cost": 1,
    },
    {
        "key": "lc_helipad", "name": "Helipad", "category": "lc_aerial_deployment",
        "add_stats": {"recon": 8, "defense": 1, "air_attack": 2, "build_cost_ic": 4, "fuel_consumption": 1},
        "xp_cost": 1,
    },
    {
        "key": "lc_armored_skirts", "name": "Armored Skirts", "category": "lc_external_features",
        "add_stats": {"armor_value": 6, "breakthrough": 6, "build_cost_ic": 8},
        "xp_cost": 1,
    },
    {
        "key": "lc_smoke_generators", "name": "Smoke Generators", "category": "lc_external_features",
        "add_stats": {"defense": 2, "breakthrough": 3, "build_cost_ic": 2},
        "xp_cost": 1,
    },
    {
        "key": "lc_obstacle_clearance_gear", "name": "Obstacle Clearance Gear", "category": "lc_external_features",
        "add_stats": {"entrenchment": 4, "build_cost_ic": 2, "fuel_consumption": 1},
        "xp_cost": 1,
    },
    {
        "key": "lc_radar", "name": "Radar", "category": "lc_external_features",
        "add_stats": {"build_cost_ic": 10},
        "xp_cost": 1,
        "multiply_stats": {"defense": 0.1, "air_attack": 0.5},
    },
    {
        "key": "lc_internal_fuel_tanks", "name": "Internal Fuel Tanks", "category": "lc_structural_features",
        "add_stats": {"fuel_capacity": 150, "build_cost_ic": 2, "maximum_speed": -0.15},
        "xp_cost": 3,
    },
    {
        "key": "lc_internal_ammunition_compartments", "name": "Internal Ammunition Compartments", "category": "lc_structural_features",
        "add_stats": {"reliability": -0.05, "breakthrough": 2, "defense": 4},
        "xp_cost": 1,
    },
    {
        "key": "lc_wet_ammunition_storage", "name": "Wet Ammunition Storage", "category": "lc_structural_features",
        "add_stats": {"reliability": 0.15, "build_cost_ic": 2},
        "xp_cost": 1,
    },
    {
        "key": "lc_bunker_emplacement", "name": "Bunker Emplacement", "category": "lc_structural_features",
        "add_stats": {
            "defense": 10, "armor_value": 8, "breakthrough": 10, "soft_attack": 10,
            "build_cost_ic": 8, "fuel_consumption": 1,
        },
        "xp_cost": 1,
    },
    {
        "key": "lc_stabilizers", "name": "Stabilizers", "category": "lc_structural_features",
        "add_stats": {"build_cost_ic": 3, "breakthrough": 6},
        "xp_cost": 1,
    },
]
