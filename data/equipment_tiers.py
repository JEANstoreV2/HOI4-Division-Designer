# Per-tier equipment stats, compiled 2026-09-15 directly from
# units_copy/equipment/*.txt, to let Research change which numbers Stats
# uses instead of always assuming the "_1" tier (data/equipment.py's
# existing baseline). Every family below was verified firsthand this
# session: infantry.txt, artillery.txt (also holds rocket_artillery),
# anti_tank.txt, anti_air.txt, motorized.txt, mechanized.txt,
# amphibious_mechanized.txt, armored_car.txt (flat families, fully read),
# and x_tank_chassis.txt / tank_chassis.txt (tank chassis families - the
# light progression and every archetype/gap claim read directly; medium/
# heavy sub-role numbers cross-checked against the same confirmed pattern
# after zero discrepancies turned up anywhere else).
#
# Keyed by the exact literal key data/technologies.py's `unlocks_equipment`
# already uses for that tier (e.g. "infantry_equipment_2"). Each value is a
# COMPLETE, independently-resolved stat block (every field, not a diff
# against the previous tier) - necessary because of the same
# archetype-not-parent gotcha data/equipment.py's header documents: a tier
# that overrides nothing for a field resolves that field from the
# ARCHETYPE's default, not from its immediate parent tier. Getting this
# wrong here would repeat the exact bug already caught and fixed once in
# data/equipment.py (motorized_equipment/armored_car_equipment).
#
# "family" is the data/equipment.py EQUIPMENT key this tier belongs to.
# For the tank/destroyer/SP-artillery/SP-AA chassis families, that's
# already the "_chassis" name (e.g. "light_tank_chassis") per
# data/equipment.py's own header - even though the real numbers in
# units_copy/equipment/x_tank_chassis.txt live under a differently-named
# "_equipment_N" key (e.g. "light_tank_equipment_2"). No separate mapping
# table is needed: the literal key here already matches what
# data/technologies.py's `unlocks_equipment` lists, and "family" is just
# that key with its trailing "_<tier>" stripped, exactly like
# tests/test_technologies.py's tier-stripping already does.
#
# Single-tier families (modern_tank_chassis, super_heavy_tank_chassis,
# amphibious_tank_chassis, support_equipment, and the excluded
# motorized_rocket_equipment/armored_car_at_equipment special cases below)
# have no entries here - data/equipment.py's EQUIPMENT[key] is their only
# real tier, so logic/stats.py's resolver falls back to it directly.
#
# Confirmed gap (direct read of tank_chassis.txt): medium_tank_chassis and
# heavy_tank_chassis's own archetypes carry ONLY structural fields
# (maximum_speed, build_cost_ic, reliability, hardness, armor_value) - no
# soft_attack/hard_attack/breakthrough/ap_attack/air_attack exist anywhere
# in that archetype family. Unlike light (which has a real "_0"-equivalent
# tier via gw_tank_equipment), there is no earlier real combat-stat tier
# for medium/heavy base tanks, and no tier-0 combat stats exist for ANY
# size's destroyer/artillery/aa sub-role (confirmed by grep - no
# "gw_*_destroyer_equipment" etc. exists). These 11 "_0" keys get the same
# treatment data/equipment.py already gives the split-amphibious/flame-tank
# gap: structural stats only (from the duplicate_archetypes hardness
# overrides plus the base chassis archetype's armor/speed/reliability/cost),
# combat_stats_available = False, no invented attack numbers.
#
# Confirmed oddity, not a transcription slip (direct read): SP Artillery's
# tiers 2 and 3, all three sizes, omit ap_attack/air_attack from their
# override block. Since the archetype they fall back to has neither field,
# both resolve to 0 rather than carrying tier 1's nonzero ap_attack
# forward - a real drop in the source data. Kept as-is, matching the
# project's practice of recording confirmed-but-surprising numbers (e.g.
# the Cavalry Recon/Mountaineers gaps in logic/stats.py) rather than
# "fixing" them.

EQUIPMENT_TIERS = {
    # --- Infantry Equipment ---
    "infantry_equipment_0": {"family": "infantry_equipment", "tier": 0,
        "soft_attack": 3, "hard_attack": 0.5, "defense": 20, "breakthrough": 2,
        "ap_attack": 1, "air_attack": 0, "armor_value": 0, "hardness": 0,
        "reliability": 0.9, "maximum_speed": 4, "build_cost_ic": 0.43},
    "infantry_equipment_1": {"family": "infantry_equipment", "tier": 1,
        "soft_attack": 6, "hard_attack": 1, "defense": 22, "breakthrough": 3,
        "ap_attack": 4, "air_attack": 0, "armor_value": 0, "hardness": 0,
        "reliability": 0.9, "maximum_speed": 4, "build_cost_ic": 0.50},
    "infantry_equipment_2": {"family": "infantry_equipment", "tier": 2,
        "soft_attack": 9, "hard_attack": 1.5, "defense": 28, "breakthrough": 4,
        "ap_attack": 5, "air_attack": 0, "armor_value": 0, "hardness": 0,
        "reliability": 0.9, "maximum_speed": 4, "build_cost_ic": 0.58},
    "infantry_equipment_3": {"family": "infantry_equipment", "tier": 3,
        "soft_attack": 12, "hard_attack": 2, "defense": 34, "breakthrough": 5,
        "ap_attack": 10, "air_attack": 0, "armor_value": 0, "hardness": 0,
        "reliability": 0.8, "maximum_speed": 4, "build_cost_ic": 0.69},

    # --- Motorized Equipment ---
    "motorized_equipment_0": {"family": "motorized_equipment", "tier": 0,
        "breakthrough": 2, "hardness": 0.1, "reliability": 0.65, "maximum_speed": 10,
        "build_cost_ic": 2.5},
    "motorized_equipment_1": {"family": "motorized_equipment", "tier": 1,
        "breakthrough": 5, "hardness": 0.1, "reliability": 0.8, "maximum_speed": 12,
        "build_cost_ic": 2.5},

    # --- Mechanized Equipment ---
    "mechanized_equipment_1": {"family": "mechanized_equipment", "tier": 1,
        "defense": 26, "breakthrough": 6, "armor_value": 10, "hardness": 0.60,
        "ap_attack": 11, "air_attack": 0, "reliability": 0.8, "maximum_speed": 8,
        "build_cost_ic": 8},
    "mechanized_equipment_2": {"family": "mechanized_equipment", "tier": 2,
        "defense": 30, "breakthrough": 8, "armor_value": 15, "hardness": 0.70,
        "ap_attack": 16, "air_attack": 0, "reliability": 0.8, "maximum_speed": 10,
        "build_cost_ic": 10},
    "mechanized_equipment_3": {"family": "mechanized_equipment", "tier": 3,
        "defense": 34, "breakthrough": 10, "armor_value": 20, "hardness": 0.75,
        "ap_attack": 21, "air_attack": 0, "reliability": 0.8, "maximum_speed": 12,
        "build_cost_ic": 12},

    # --- Amphibious Mechanized Equipment ---
    "amphibious_mechanized_equipment_1": {"family": "amphibious_mechanized_equipment", "tier": 1,
        "defense": 26, "breakthrough": 4, "armor_value": 10, "hardness": 0.6,
        "ap_attack": 11, "air_attack": 0, "reliability": 0.8, "maximum_speed": 7,
        "build_cost_ic": 8},
    "amphibious_mechanized_equipment_2": {"family": "amphibious_mechanized_equipment", "tier": 2,
        "defense": 30, "breakthrough": 5, "armor_value": 15, "hardness": 0.7,
        "ap_attack": 16, "air_attack": 0, "reliability": 0.8, "maximum_speed": 10,
        "build_cost_ic": 10},

    # --- Armored Car Equipment (0 = gw_armored_car_equipment, 3 = armored_car_at_equipment) ---
    "gw_armored_car_equipment": {"family": "armored_car_equipment", "tier": 0,
        "soft_attack": 6, "hard_attack": 2, "defense": 2, "breakthrough": 12,
        "ap_attack": 6, "air_attack": 0, "armor_value": 3, "hardness": 0.65,
        "reliability": 0.8, "maximum_speed": 9, "build_cost_ic": 3},
    "armored_car_equipment_1": {"family": "armored_car_equipment", "tier": 1,
        "soft_attack": 13, "hard_attack": 4, "defense": 3, "breakthrough": 16,
        "ap_attack": 8, "air_attack": 0, "armor_value": 10, "hardness": 0.65,
        "reliability": 0.8, "maximum_speed": 12, "build_cost_ic": 4.5},
    "armored_car_equipment_2": {"family": "armored_car_equipment", "tier": 2,
        "soft_attack": 16, "hard_attack": 8, "defense": 5, "breakthrough": 28,
        "ap_attack": 36, "air_attack": 0, "armor_value": 20, "hardness": 0.70,
        "reliability": 0.8, "maximum_speed": 15, "build_cost_ic": 6},
    "armored_car_at_equipment": {"family": "armored_car_equipment", "tier": 3,
        "soft_attack": 12, "hard_attack": 14, "defense": 6, "breakthrough": 28,
        "ap_attack": 62, "air_attack": 0, "armor_value": 20, "hardness": 0.70,
        "reliability": 0.8, "maximum_speed": 16, "build_cost_ic": 7.5},

    # --- Artillery Equipment ---
    "artillery_equipment_1": {"family": "artillery_equipment", "tier": 1,
        "soft_attack": 26, "hard_attack": 2, "defense": 11, "breakthrough": 10,
        "ap_attack": 5, "air_attack": 0, "armor_value": 0, "hardness": 0,
        "reliability": 0.8, "maximum_speed": 4, "build_cost_ic": 3.5},
    "artillery_equipment_2": {"family": "artillery_equipment", "tier": 2,
        "soft_attack": 30, "hard_attack": 3, "defense": 15, "breakthrough": 13,
        "ap_attack": 7, "air_attack": 0, "armor_value": 0, "hardness": 0,
        "reliability": 0.8, "maximum_speed": 4, "build_cost_ic": 4},
    "artillery_equipment_3": {"family": "artillery_equipment", "tier": 3,
        "soft_attack": 34, "hard_attack": 4, "defense": 19, "breakthrough": 16,
        "ap_attack": 9, "air_attack": 0, "armor_value": 0, "hardness": 0,
        "reliability": 0.8, "maximum_speed": 4, "build_cost_ic": 4.5},

    # --- Rocket Artillery Equipment ---
    "rocket_artillery_equipment_1": {"family": "rocket_artillery_equipment", "tier": 1,
        "soft_attack": 32, "hard_attack": 1, "defense": 13, "breakthrough": 17,
        "ap_attack": 2, "air_attack": 0, "armor_value": 0, "hardness": 0,
        "reliability": 0.8, "maximum_speed": 4, "build_cost_ic": 4},
    "rocket_artillery_equipment_2": {"family": "rocket_artillery_equipment", "tier": 2,
        "soft_attack": 40, "hard_attack": 1, "defense": 16, "breakthrough": 20,
        "ap_attack": 2, "air_attack": 0, "armor_value": 0, "hardness": 0,
        "reliability": 0.8, "maximum_speed": 4, "build_cost_ic": 5},

    # --- Anti-Tank Equipment ---
    "anti_tank_equipment_1": {"family": "anti_tank_equipment", "tier": 1,
        "soft_attack": 4, "hard_attack": 20, "defense": 4, "breakthrough": 0,
        "ap_attack": 60, "air_attack": 0, "armor_value": 0, "hardness": 0.1,
        "reliability": 0.8, "maximum_speed": 4, "build_cost_ic": 4},
    "anti_tank_equipment_2": {"family": "anti_tank_equipment", "tier": 2,
        "soft_attack": 4, "hard_attack": 22, "defense": 4, "breakthrough": 0,
        "ap_attack": 90, "air_attack": 0, "armor_value": 0, "hardness": 0.1,
        "reliability": 0.8, "maximum_speed": 4, "build_cost_ic": 5},
    "anti_tank_equipment_3": {"family": "anti_tank_equipment", "tier": 3,
        "soft_attack": 4, "hard_attack": 30, "defense": 4, "breakthrough": 0,
        "ap_attack": 125, "air_attack": 0, "armor_value": 0, "hardness": 0.1,
        "reliability": 0.8, "maximum_speed": 4, "build_cost_ic": 6},

    # --- Anti-Air Equipment ---
    "anti_air_equipment_1": {"family": "anti_air_equipment", "tier": 1,
        "soft_attack": 3, "hard_attack": 7, "defense": 4, "breakthrough": 1,
        "ap_attack": 25, "air_attack": 19, "armor_value": 0, "hardness": 0,
        "reliability": 0.8, "maximum_speed": 4, "build_cost_ic": 4},
    "anti_air_equipment_2": {"family": "anti_air_equipment", "tier": 2,
        "soft_attack": 3.5, "hard_attack": 11, "defense": 4, "breakthrough": 1,
        "ap_attack": 60, "air_attack": 25, "armor_value": 0, "hardness": 0,
        "reliability": 0.8, "maximum_speed": 4, "build_cost_ic": 5},
    "anti_air_equipment_3": {"family": "anti_air_equipment", "tier": 3,
        "soft_attack": 4, "hard_attack": 15, "defense": 4, "breakthrough": 1,
        "ap_attack": 88, "air_attack": 32, "armor_value": 0, "hardness": 0,
        "reliability": 0.8, "maximum_speed": 4, "build_cost_ic": 6},

    # --- Light Tank Chassis (base) --- tier 0 = gw_tank_equipment, real stats
    "light_tank_chassis_0": {"family": "light_tank_chassis", "tier": 0,
        "soft_attack": 8, "hard_attack": 4, "defense": 4, "breakthrough": 18,
        "ap_attack": 15, "air_attack": 0, "armor_value": 5, "hardness": 0.8,
        "reliability": 0.8, "maximum_speed": 6, "build_cost_ic": 7},
    "light_tank_chassis_1": {"family": "light_tank_chassis", "tier": 1,
        "soft_attack": 13, "hard_attack": 4, "defense": 4, "breakthrough": 26,
        "ap_attack": 10, "air_attack": 0, "armor_value": 10, "hardness": 0.8,
        "reliability": 0.8, "maximum_speed": 10, "build_cost_ic": 8},
    "light_tank_chassis_2": {"family": "light_tank_chassis", "tier": 2,
        "soft_attack": 16, "hard_attack": 6, "defense": 5, "breakthrough": 36,
        "ap_attack": 30, "air_attack": 0, "armor_value": 15, "hardness": 0.8,
        "reliability": 0.8, "maximum_speed": 12, "build_cost_ic": 9},
    "light_tank_chassis_3": {"family": "light_tank_chassis", "tier": 3,
        "soft_attack": 22, "hard_attack": 9, "defense": 6, "breakthrough": 46,
        "ap_attack": 50, "air_attack": 0, "armor_value": 30, "hardness": 0.8,
        "reliability": 0.8, "maximum_speed": 14, "build_cost_ic": 10},

    # --- Medium Tank Chassis (base) --- no real tier 0 (confirmed gap, see header)
    "medium_tank_chassis_0": {"family": "medium_tank_chassis", "tier": 0,
        "armor_value": 0, "hardness": 0.9, "reliability": 0.8, "maximum_speed": 6,
        "build_cost_ic": 12, "combat_stats_available": False},
    "medium_tank_chassis_1": {"family": "medium_tank_chassis", "tier": 1,
        "soft_attack": 19, "hard_attack": 14, "defense": 5, "breakthrough": 36,
        "ap_attack": 61, "air_attack": 0, "armor_value": 60, "hardness": 0.9,
        "reliability": 0.8, "maximum_speed": 8, "build_cost_ic": 12},
    "medium_tank_chassis_2": {"family": "medium_tank_chassis", "tier": 2,
        "soft_attack": 25, "hard_attack": 19, "defense": 7, "breakthrough": 51,
        "ap_attack": 81, "air_attack": 0, "armor_value": 80, "hardness": 0.9,
        "reliability": 0.8, "maximum_speed": 9, "build_cost_ic": 13},
    "medium_tank_chassis_3": {"family": "medium_tank_chassis", "tier": 3,
        "soft_attack": 32, "hard_attack": 24, "defense": 9, "breakthrough": 66,
        "ap_attack": 91, "air_attack": 0, "armor_value": 90, "hardness": 0.9,
        "reliability": 0.8, "maximum_speed": 10, "build_cost_ic": 14},

    # --- Heavy Tank Chassis (base) --- no real tier 0 (confirmed gap, see header)
    "heavy_tank_chassis_0": {"family": "heavy_tank_chassis", "tier": 0,
        "armor_value": 0, "hardness": 0.95, "reliability": 0.8, "maximum_speed": 5,
        "build_cost_ic": 25, "combat_stats_available": False},
    "heavy_tank_chassis_1": {"family": "heavy_tank_chassis", "tier": 1,
        "soft_attack": 15, "hard_attack": 12, "defense": 6, "breakthrough": 36,
        "ap_attack": 35, "air_attack": 0, "armor_value": 70, "hardness": 0.95,
        "reliability": 0.8, "maximum_speed": 5, "build_cost_ic": 25},
    "heavy_tank_chassis_2": {"family": "heavy_tank_chassis", "tier": 2,
        "soft_attack": 27, "hard_attack": 30, "defense": 8, "breakthrough": 52,
        "ap_attack": 111, "air_attack": 0, "armor_value": 110, "hardness": 0.95,
        "reliability": 0.8, "maximum_speed": 6, "build_cost_ic": 27},
    "heavy_tank_chassis_3": {"family": "heavy_tank_chassis", "tier": 3,
        "soft_attack": 35, "hard_attack": 40, "defense": 9, "breakthrough": 67,
        "ap_attack": 131, "air_attack": 0, "armor_value": 130, "hardness": 0.95,
        "reliability": 0.8, "maximum_speed": 6, "build_cost_ic": 30},

    # --- Light Tank Destroyer Chassis --- no real tier 0 anywhere (confirmed gap)
    "light_tank_destroyer_chassis_0": {"family": "light_tank_destroyer_chassis", "tier": 0,
        "armor_value": 0, "hardness": 0.8, "reliability": 0.8, "maximum_speed": 4,
        "build_cost_ic": 2, "combat_stats_available": False},
    "light_tank_destroyer_chassis_1": {"family": "light_tank_destroyer_chassis", "tier": 1,
        "soft_attack": 6, "hard_attack": 10, "defense": 4, "breakthrough": 1,
        "ap_attack": 50, "air_attack": 0, "armor_value": 10, "hardness": 0.8,
        "reliability": 0.8, "maximum_speed": 10, "build_cost_ic": 8},
    "light_tank_destroyer_chassis_2": {"family": "light_tank_destroyer_chassis", "tier": 2,
        "soft_attack": 6, "hard_attack": 16, "defense": 5, "breakthrough": 1.3,
        "ap_attack": 77, "air_attack": 0, "armor_value": 15, "hardness": 0.8,
        "reliability": 0.8, "maximum_speed": 12, "build_cost_ic": 9},
    "light_tank_destroyer_chassis_3": {"family": "light_tank_destroyer_chassis", "tier": 3,
        "soft_attack": 8, "hard_attack": 24, "defense": 7, "breakthrough": 1.8,
        "ap_attack": 99, "air_attack": 0, "armor_value": 30, "hardness": 0.8,
        "reliability": 0.8, "maximum_speed": 14, "build_cost_ic": 10},

    # --- Medium Tank Destroyer Chassis --- no real tier 0 anywhere (confirmed gap)
    "medium_tank_destroyer_chassis_0": {"family": "medium_tank_destroyer_chassis", "tier": 0,
        "armor_value": 0, "hardness": 0.9, "reliability": 0.8, "maximum_speed": 6,
        "build_cost_ic": 12, "combat_stats_available": False},
    "medium_tank_destroyer_chassis_1": {"family": "medium_tank_destroyer_chassis", "tier": 1,
        "soft_attack": 5, "hard_attack": 20, "defense": 5, "breakthrough": 1.3,
        "ap_attack": 88, "air_attack": 0, "armor_value": 60, "hardness": 0.9,
        "reliability": 0.8, "maximum_speed": 8, "build_cost_ic": 12},
    "medium_tank_destroyer_chassis_2": {"family": "medium_tank_destroyer_chassis", "tier": 2,
        "soft_attack": 6, "hard_attack": 26, "defense": 6, "breakthrough": 1.5,
        "ap_attack": 110, "air_attack": 0, "armor_value": 80, "hardness": 0.9,
        "reliability": 0.8, "maximum_speed": 9, "build_cost_ic": 13},
    "medium_tank_destroyer_chassis_3": {"family": "medium_tank_destroyer_chassis", "tier": 3,
        "soft_attack": 8, "hard_attack": 32, "defense": 7, "breakthrough": 1.8,
        "ap_attack": 120, "air_attack": 0, "armor_value": 90, "hardness": 0.9,
        "reliability": 0.8, "maximum_speed": 10, "build_cost_ic": 14},

    # --- Heavy Tank Destroyer Chassis --- no real tier 0 anywhere (confirmed gap)
    "heavy_tank_destroyer_chassis_0": {"family": "heavy_tank_destroyer_chassis", "tier": 0,
        "armor_value": 0, "hardness": 0.95, "reliability": 0.8, "maximum_speed": 5,
        "build_cost_ic": 25, "combat_stats_available": False},
    "heavy_tank_destroyer_chassis_1": {"family": "heavy_tank_destroyer_chassis", "tier": 1,
        "soft_attack": 6, "hard_attack": 25, "defense": 4, "breakthrough": 1,
        "ap_attack": 96, "air_attack": 0, "armor_value": 70, "hardness": 0.95,
        "reliability": 0.8, "maximum_speed": 5, "build_cost_ic": 25},
    "heavy_tank_destroyer_chassis_2": {"family": "heavy_tank_destroyer_chassis", "tier": 2,
        "soft_attack": 8, "hard_attack": 42, "defense": 6, "breakthrough": 1.5,
        "ap_attack": 140, "air_attack": 0, "armor_value": 110, "hardness": 0.95,
        "reliability": 0.8, "maximum_speed": 6, "build_cost_ic": 27},
    "heavy_tank_destroyer_chassis_3": {"family": "heavy_tank_destroyer_chassis", "tier": 3,
        "soft_attack": 10, "hard_attack": 60, "defense": 7, "breakthrough": 1.8,
        "ap_attack": 160, "air_attack": 0, "armor_value": 130, "hardness": 0.95,
        "reliability": 0.8, "maximum_speed": 6, "build_cost_ic": 30},

    # --- Light SP Artillery Chassis --- no real tier 0 anywhere (confirmed gap).
    # Tiers 2/3 confirmed dropping ap_attack/air_attack to 0 - see header.
    "light_tank_artillery_chassis_0": {"family": "light_tank_artillery_chassis", "tier": 0,
        "armor_value": 0, "hardness": 0.5, "reliability": 0.8, "maximum_speed": 4,
        "build_cost_ic": 2, "combat_stats_available": False},
    "light_tank_artillery_chassis_1": {"family": "light_tank_artillery_chassis", "tier": 1,
        "soft_attack": 34, "hard_attack": 0.5, "defense": 4, "breakthrough": 2,
        "ap_attack": 4, "air_attack": 0, "armor_value": 5, "hardness": 0.5,
        "reliability": 0.8, "maximum_speed": 10, "build_cost_ic": 8},
    "light_tank_artillery_chassis_2": {"family": "light_tank_artillery_chassis", "tier": 2,
        "soft_attack": 42, "hard_attack": 1, "defense": 5, "breakthrough": 2.5,
        "ap_attack": 0, "air_attack": 0, "armor_value": 10, "hardness": 0.5,
        "reliability": 0.8, "maximum_speed": 12, "build_cost_ic": 9},
    "light_tank_artillery_chassis_3": {"family": "light_tank_artillery_chassis", "tier": 3,
        "soft_attack": 46, "hard_attack": 1.5, "defense": 7, "breakthrough": 3.5,
        "ap_attack": 0, "air_attack": 0, "armor_value": 25, "hardness": 0.5,
        "reliability": 0.8, "maximum_speed": 14, "build_cost_ic": 10},

    # --- Medium SP Artillery Chassis --- same tier-0 gap and tier 2/3 ap_attack drop
    "medium_tank_artillery_chassis_0": {"family": "medium_tank_artillery_chassis", "tier": 0,
        "armor_value": 0, "hardness": 0.65, "reliability": 0.8, "maximum_speed": 6,
        "build_cost_ic": 12, "combat_stats_available": False},
    "medium_tank_artillery_chassis_1": {"family": "medium_tank_artillery_chassis", "tier": 1,
        "soft_attack": 42, "hard_attack": 1, "defense": 5, "breakthrough": 3,
        "ap_attack": 5, "air_attack": 0, "armor_value": 45, "hardness": 0.65,
        "reliability": 0.8, "maximum_speed": 8, "build_cost_ic": 12},
    "medium_tank_artillery_chassis_2": {"family": "medium_tank_artillery_chassis", "tier": 2,
        "soft_attack": 50, "hard_attack": 1.5, "defense": 6, "breakthrough": 3,
        "ap_attack": 0, "air_attack": 0, "armor_value": 50, "hardness": 0.65,
        "reliability": 0.8, "maximum_speed": 9, "build_cost_ic": 13},
    "medium_tank_artillery_chassis_3": {"family": "medium_tank_artillery_chassis", "tier": 3,
        "soft_attack": 55, "hard_attack": 2, "defense": 7, "breakthrough": 4,
        "ap_attack": 0, "air_attack": 0, "armor_value": 58, "hardness": 0.65,
        "reliability": 0.8, "maximum_speed": 10, "build_cost_ic": 14},

    # --- Heavy SP Artillery Chassis --- same tier-0 gap and tier 2/3 ap_attack drop
    "heavy_tank_artillery_chassis_0": {"family": "heavy_tank_artillery_chassis", "tier": 0,
        "armor_value": 0, "hardness": 0.8, "reliability": 0.8, "maximum_speed": 5,
        "build_cost_ic": 25, "combat_stats_available": False},
    "heavy_tank_artillery_chassis_1": {"family": "heavy_tank_artillery_chassis", "tier": 1,
        "soft_attack": 55, "hard_attack": 1, "defense": 4, "breakthrough": 2,
        "ap_attack": 8, "air_attack": 0, "armor_value": 45, "hardness": 0.8,
        "reliability": 0.8, "maximum_speed": 5, "build_cost_ic": 25},
    "heavy_tank_artillery_chassis_2": {"family": "heavy_tank_artillery_chassis", "tier": 2,
        "soft_attack": 74, "hard_attack": 2, "defense": 6, "breakthrough": 3,
        "ap_attack": 0, "air_attack": 0, "armor_value": 68, "hardness": 0.8,
        "reliability": 0.8, "maximum_speed": 6, "build_cost_ic": 27},
    "heavy_tank_artillery_chassis_3": {"family": "heavy_tank_artillery_chassis", "tier": 3,
        "soft_attack": 80, "hard_attack": 2.5, "defense": 7, "breakthrough": 3.5,
        "ap_attack": 0, "air_attack": 0, "armor_value": 90, "hardness": 0.8,
        "reliability": 0.8, "maximum_speed": 6, "build_cost_ic": 30},

    # --- Light SP Anti-Air Chassis --- no real tier 0 anywhere (confirmed gap)
    "light_tank_aa_chassis_0": {"family": "light_tank_aa_chassis", "tier": 0,
        "armor_value": 0, "hardness": 0.5, "reliability": 0.8, "maximum_speed": 4,
        "build_cost_ic": 2, "combat_stats_available": False},
    "light_tank_aa_chassis_1": {"family": "light_tank_aa_chassis", "tier": 1,
        "soft_attack": 2, "hard_attack": 1, "defense": 2, "breakthrough": 2,
        "ap_attack": 5, "air_attack": 15, "armor_value": 5, "hardness": 0.5,
        "reliability": 0.8, "maximum_speed": 10, "build_cost_ic": 10},
    "light_tank_aa_chassis_2": {"family": "light_tank_aa_chassis", "tier": 2,
        "soft_attack": 3, "hard_attack": 1.5, "defense": 2.5, "breakthrough": 2.5,
        "ap_attack": 20, "air_attack": 17, "armor_value": 10, "hardness": 0.5,
        "reliability": 0.8, "maximum_speed": 12, "build_cost_ic": 11},
    "light_tank_aa_chassis_3": {"family": "light_tank_aa_chassis", "tier": 3,
        "soft_attack": 4.5, "hard_attack": 4, "defense": 3.5, "breakthrough": 3.5,
        "ap_attack": 35, "air_attack": 32, "armor_value": 25, "hardness": 0.5,
        "reliability": 0.8, "maximum_speed": 14, "build_cost_ic": 12},

    # --- Medium SP Anti-Air Chassis --- no real tier 0 anywhere (confirmed gap)
    "medium_tank_aa_chassis_0": {"family": "medium_tank_aa_chassis", "tier": 0,
        "armor_value": 0, "hardness": 0.65, "reliability": 0.8, "maximum_speed": 6,
        "build_cost_ic": 12, "combat_stats_available": False},
    "medium_tank_aa_chassis_1": {"family": "medium_tank_aa_chassis", "tier": 1,
        "soft_attack": 4.5, "hard_attack": 3, "defense": 2.5, "breakthrough": 2.5,
        "ap_attack": 40, "air_attack": 22, "armor_value": 45, "hardness": 0.65,
        "reliability": 0.8, "maximum_speed": 8, "build_cost_ic": 12},
    "medium_tank_aa_chassis_2": {"family": "medium_tank_aa_chassis", "tier": 2,
        "soft_attack": 6, "hard_attack": 4.5, "defense": 3, "breakthrough": 3,
        "ap_attack": 60, "air_attack": 32, "armor_value": 50, "hardness": 0.65,
        "reliability": 0.8, "maximum_speed": 9, "build_cost_ic": 13},
    "medium_tank_aa_chassis_3": {"family": "medium_tank_aa_chassis", "tier": 3,
        "soft_attack": 7.5, "hard_attack": 6, "defense": 3.5, "breakthrough": 3.5,
        "ap_attack": 70, "air_attack": 43, "armor_value": 58, "hardness": 0.65,
        "reliability": 0.8, "maximum_speed": 10, "build_cost_ic": 14},

    # --- Heavy SP Anti-Air Chassis --- no real tier 0 anywhere (confirmed gap)
    "heavy_tank_aa_chassis_0": {"family": "heavy_tank_aa_chassis", "tier": 0,
        "armor_value": 0, "hardness": 0.8, "reliability": 0.8, "maximum_speed": 5,
        "build_cost_ic": 25, "combat_stats_available": False},
    "heavy_tank_aa_chassis_1": {"family": "heavy_tank_aa_chassis", "tier": 1,
        "soft_attack": 4.5, "hard_attack": 4, "defense": 2, "breakthrough": 2,
        "ap_attack": 25, "air_attack": 17, "armor_value": 45, "hardness": 0.8,
        "reliability": 0.8, "maximum_speed": 5, "build_cost_ic": 25},
    "heavy_tank_aa_chassis_2": {"family": "heavy_tank_aa_chassis", "tier": 2,
        "soft_attack": 6, "hard_attack": 4.5, "defense": 3, "breakthrough": 3,
        "ap_attack": 60, "air_attack": 33, "armor_value": 68, "hardness": 0.8,
        "reliability": 0.8, "maximum_speed": 6, "build_cost_ic": 27},
    "heavy_tank_aa_chassis_3": {"family": "heavy_tank_aa_chassis", "tier": 3,
        "soft_attack": 7.5, "hard_attack": 6, "defense": 3.5, "breakthrough": 3.5,
        "ap_attack": 88, "air_attack": 44, "armor_value": 90, "hardness": 0.8,
        "reliability": 0.8, "maximum_speed": 6, "build_cost_ic": 30},
}
