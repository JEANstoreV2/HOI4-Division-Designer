# Hand-curated from units_copy/equipment/*.txt (HOI4 game files), verified
# 2026-09-14. Every entry is the "_1" tier (or, where a "_1" entry adds no
# stat overrides of its own, the equivalent effective values after resolving
# its archetype/parent chain by hand) - see Specification.md's "Equipment
# data" section for why _1 = "no research done yet".
#
# Keys match exactly what battalions/support companies/regimental support
# already ask for in their `need` field, including the tank "chassis" keys
# (e.g. "light_tank_destroyer_chassis") even though the real numbers live
# under a differently-named "_equipment_1" entry in
# units_copy/equipment/x_tank_chassis.txt - see that file's comment for why.
#
# Only fields the source actually defines are included - e.g. motorized
# and mechanized equipment have no soft_attack/hard_attack of their own
# (that comes from the infantry_equipment a Motorized/Mechanized battalion
# also carries), so those keys are simply absent here rather than set to 0.
#
# "combat_stats_available" is only set to False on the two confirmed-gap
# families (split Amphibious tanks, Flame tanks), where no numbered
# equipment tier exists anywhere in units_copy/ - those entries carry only
# structural stats (armor_value, hardness, reliability, maximum_speed,
# build_cost_ic) inherited from their base chassis archetype.
#
# Correction (2026-09-14): found by cross-checking real division-designer
# screenshots against calculate_division_stats output. "motorized_equipment"
# and "armored_car_equipment" originally held their intermediate tier's
# values (motorized_equipment_0 / gw_armored_car_equipment) instead of the
# tier actually used at "no research done" (motorized_equipment_1 /
# armored_car_equipment_1). Both of those tiers only set a "parent" pointing
# at the intermediate tier and override nothing else, and it turns out
# unlisted fields resolve from the ARCHETYPE, not the "parent" (parent is
# tech-tree ordering metadata, not a stat-inheritance chain) - confirmed by
# Motorised's real max_speed (12.0, the archetype's value) and 7 Motorised +
# 2 Motorised Artillery's real breakthrough (78.0, only reachable with the
# archetype's breakthrough=5, not motorized_equipment_0's 2).

EQUIPMENT = {
    # Core infantry-type equipment
    "infantry_equipment": {
        "name": "Infantry Equipment",
        "soft_attack": 6, "hard_attack": 1, "defense": 22, "breakthrough": 3,
        "ap_attack": 4, "air_attack": 0, "armor_value": 0, "hardness": 0,
        "reliability": 0.9, "maximum_speed": 4, "build_cost_ic": 0.50,
    },
    "motorized_equipment": {
        "name": "Motorized Equipment",
        "breakthrough": 5, "hardness": 0.1,
        "reliability": 0.8, "maximum_speed": 12, "build_cost_ic": 2.5,
    },
    "mechanized_equipment": {
        "name": "Mechanized Equipment",
        "defense": 26, "breakthrough": 6, "armor_value": 10, "hardness": 0.60,
        "ap_attack": 11, "air_attack": 0,
        "reliability": 0.8, "maximum_speed": 8, "build_cost_ic": 8,
    },
    "amphibious_mechanized_equipment": {
        "name": "Amphibious Mechanized Equipment",
        "defense": 26, "breakthrough": 4, "armor_value": 10, "hardness": 0.6,
        "ap_attack": 11, "air_attack": 0,
        "reliability": 0.8, "maximum_speed": 7, "build_cost_ic": 8,
    },
    "armored_car_equipment": {
        "name": "Armored Car",
        "soft_attack": 13, "hard_attack": 4, "defense": 3, "breakthrough": 16,
        "ap_attack": 8, "air_attack": 0, "armor_value": 10, "hardness": 0.65,
        "reliability": 0.8, "maximum_speed": 12, "build_cost_ic": 4.5,
    },
    "artillery_equipment": {
        "name": "Artillery",
        "soft_attack": 26, "hard_attack": 2, "defense": 11, "breakthrough": 10,
        "ap_attack": 5, "air_attack": 0, "armor_value": 0, "hardness": 0,
        "reliability": 0.8, "maximum_speed": 4, "build_cost_ic": 3.5,
    },
    "rocket_artillery_equipment": {
        "name": "Rocket Artillery",
        "soft_attack": 32, "hard_attack": 1, "defense": 13, "breakthrough": 17,
        "ap_attack": 2, "air_attack": 0, "armor_value": 0, "hardness": 0,
        "reliability": 0.8, "maximum_speed": 4, "build_cost_ic": 4,
    },
    "anti_tank_equipment": {
        "name": "Anti-Tank",
        "soft_attack": 4, "hard_attack": 20, "defense": 4, "breakthrough": 0,
        "ap_attack": 60, "air_attack": 0, "armor_value": 0, "hardness": 0.1,
        "reliability": 0.8, "maximum_speed": 4, "build_cost_ic": 4,
    },
    "anti_air_equipment": {
        "name": "Anti-Air",
        "soft_attack": 3, "hard_attack": 7, "defense": 4, "breakthrough": 1,
        "ap_attack": 25, "air_attack": 19, "armor_value": 0, "hardness": 0,
        "reliability": 0.8, "maximum_speed": 4, "build_cost_ic": 4,
    },

    # Support/regimental-only equipment, found by cross-checking those data files
    "helicopter_equipment": {
        "name": "Helicopter Equipment",
        "defense": 6, "breakthrough": 8, "armor_value": 4, "hardness": 0.40,
        "ap_attack": 11, "air_attack": 0,
        "reliability": 0.7, "maximum_speed": 10, "build_cost_ic": 9,
    },
    "armored_support_vehicle": {
        "name": "Armored Support Vehicle",
        "soft_attack": 6, "hard_attack": 2, "defense": 10, "breakthrough": 3,
        "ap_attack": 5, "air_attack": 0, "armor_value": 12, "hardness": 0.65,
        "reliability": 0.8, "maximum_speed": 8, "build_cost_ic": 12,
    },
    "super_heavy_artillery_equipment": {
        "name": "Super Heavy Artillery",
        "soft_attack": 35, "hard_attack": 4, "defense": 12, "breakthrough": 12,
        "ap_attack": 7, "air_attack": 0, "armor_value": 0, "hardness": 0,
        "reliability": 0.7, "build_cost_ic": 45,
    },
    "self_propelled_super_heavy_artillery_equipment": {
        "name": "Self-Propelled Super Heavy Artillery",
        "soft_attack": 44, "hard_attack": 6, "defense": 14, "breakthrough": 14,
        "ap_attack": 9, "air_attack": 0, "armor_value": 6, "hardness": 0.1,
        "reliability": 0.7, "build_cost_ic": 65,
    },
    "support_equipment": {
        # No combat stats at all - a quantity/manpower requirement only.
        "name": "Support Equipment",
        "reliability": 0.8, "build_cost_ic": 4,
    },
    "motorbike_equipment": {
        # No combat stats at all - same role as support_equipment above.
        "name": "Motorbike Equipment",
        "breakthrough": 1,
        "reliability": 0.9, "maximum_speed": 12, "build_cost_ic": 1.5,
    },

    # Tank/role chassis - real numbers sourced from x_tank_chassis.txt's
    # "_equipment_1" entries, keyed here by the "_chassis" name battalions
    # actually reference.
    "light_tank_chassis": {
        "name": "Light Tank",
        "soft_attack": 13, "hard_attack": 4, "defense": 4, "breakthrough": 26,
        "ap_attack": 10, "air_attack": 0, "armor_value": 10, "hardness": 0.8,
        "reliability": 0.8, "maximum_speed": 10, "build_cost_ic": 8,
    },
    "medium_tank_chassis": {
        "name": "Medium Tank",
        "soft_attack": 19, "hard_attack": 14, "defense": 5, "breakthrough": 36,
        "ap_attack": 61, "air_attack": 0, "armor_value": 60, "hardness": 0.9,
        "reliability": 0.8, "maximum_speed": 8, "build_cost_ic": 12,
    },
    "heavy_tank_chassis": {
        "name": "Heavy Tank",
        "soft_attack": 15, "hard_attack": 12, "defense": 6, "breakthrough": 36,
        "ap_attack": 35, "air_attack": 0, "armor_value": 70, "hardness": 0.95,
        "reliability": 0.8, "maximum_speed": 5, "build_cost_ic": 25,
    },
    "modern_tank_chassis": {
        "name": "Modern Tank",
        "soft_attack": 40, "hard_attack": 32, "defense": 10, "breakthrough": 84,
        "ap_attack": 131, "air_attack": 0, "armor_value": 130, "hardness": 0.98,
        "reliability": 0.8, "maximum_speed": 10, "build_cost_ic": 28,
    },
    "super_heavy_tank_chassis": {
        "name": "Super Heavy Tank",
        "soft_attack": 38, "hard_attack": 45, "defense": 10, "breakthrough": 74,
        "ap_attack": 146, "air_attack": 0, "armor_value": 145, "hardness": 0.99,
        "reliability": 0.8, "maximum_speed": 4, "build_cost_ic": 100,
    },
    "light_tank_destroyer_chassis": {
        "name": "Light Tank Destroyer",
        "soft_attack": 6, "hard_attack": 10, "defense": 4, "breakthrough": 1,
        "ap_attack": 50, "air_attack": 0, "armor_value": 10, "hardness": 0.8,
        "reliability": 0.8, "maximum_speed": 10, "build_cost_ic": 8,
    },
    "medium_tank_destroyer_chassis": {
        "name": "Medium Tank Destroyer",
        "soft_attack": 5, "hard_attack": 20, "defense": 5, "breakthrough": 1.3,
        "ap_attack": 88, "air_attack": 0, "armor_value": 60, "hardness": 0.9,
        "reliability": 0.8, "maximum_speed": 8, "build_cost_ic": 12,
    },
    "heavy_tank_destroyer_chassis": {
        "name": "Heavy Tank Destroyer",
        "soft_attack": 6, "hard_attack": 25, "defense": 4, "breakthrough": 1,
        "ap_attack": 96, "air_attack": 0, "armor_value": 70, "hardness": 0.95,
        "reliability": 0.8, "maximum_speed": 5, "build_cost_ic": 25,
    },
    "modern_tank_destroyer_chassis": {
        "name": "Modern Tank Destroyer",
        "soft_attack": 10, "hard_attack": 42, "defense": 8, "breakthrough": 2,
        "ap_attack": 165, "air_attack": 0, "armor_value": 130, "hardness": 0.98,
        "reliability": 0.8, "maximum_speed": 10, "build_cost_ic": 28,
    },
    "super_heavy_tank_destroyer_chassis": {
        "name": "Super Heavy Tank Destroyer",
        "soft_attack": 12, "hard_attack": 70, "defense": 7, "breakthrough": 1.8,
        "ap_attack": 170, "air_attack": 0, "armor_value": 145, "hardness": 0.99,
        "reliability": 0.8, "maximum_speed": 4, "build_cost_ic": 100,
    },
    "light_tank_artillery_chassis": {
        "name": "Light SP Artillery",
        "soft_attack": 34, "hard_attack": 0.5, "defense": 4, "breakthrough": 2,
        "ap_attack": 4, "air_attack": 0, "armor_value": 5, "hardness": 0.5,
        "reliability": 0.8, "maximum_speed": 10, "build_cost_ic": 8,
    },
    "medium_tank_artillery_chassis": {
        "name": "Medium SP Artillery",
        "soft_attack": 42, "hard_attack": 1, "defense": 5, "breakthrough": 3,
        "ap_attack": 5, "air_attack": 0, "armor_value": 45, "hardness": 0.65,
        "reliability": 0.8, "maximum_speed": 8, "build_cost_ic": 12,
    },
    "heavy_tank_artillery_chassis": {
        "name": "Heavy SP Artillery",
        "soft_attack": 55, "hard_attack": 1, "defense": 4, "breakthrough": 2,
        "ap_attack": 8, "air_attack": 0, "armor_value": 45, "hardness": 0.8,
        "reliability": 0.8, "maximum_speed": 5, "build_cost_ic": 25,
    },
    "modern_tank_artillery_chassis": {
        "name": "Modern SP Artillery",
        "soft_attack": 80, "hard_attack": 3, "defense": 8, "breakthrough": 4,
        "ap_attack": 10, "air_attack": 0, "armor_value": 90, "hardness": 0.85,
        "reliability": 0.8, "maximum_speed": 10, "build_cost_ic": 28,
    },
    "super_heavy_tank_artillery_chassis": {
        "name": "Super Heavy SP Artillery",
        "soft_attack": 85, "hard_attack": 3, "defense": 7, "breakthrough": 3.5,
        "ap_attack": 9, "air_attack": 0, "armor_value": 100, "hardness": 0.9,
        "reliability": 0.8, "maximum_speed": 4, "build_cost_ic": 100,
    },
    "light_tank_aa_chassis": {
        "name": "Light SP Anti-Air",
        "soft_attack": 2, "hard_attack": 1, "defense": 2, "breakthrough": 2,
        "ap_attack": 5, "air_attack": 15, "armor_value": 5, "hardness": 0.5,
        "reliability": 0.8, "maximum_speed": 10, "build_cost_ic": 10,
    },
    "medium_tank_aa_chassis": {
        "name": "Medium SP Anti-Air",
        "soft_attack": 4.5, "hard_attack": 3, "defense": 2.5, "breakthrough": 2.5,
        "ap_attack": 40, "air_attack": 22, "armor_value": 45, "hardness": 0.65,
        "reliability": 0.8, "maximum_speed": 8, "build_cost_ic": 12,
    },
    "heavy_tank_aa_chassis": {
        "name": "Heavy SP Anti-Air",
        "soft_attack": 4.5, "hard_attack": 4, "defense": 2, "breakthrough": 2,
        "ap_attack": 25, "air_attack": 17, "armor_value": 45, "hardness": 0.8,
        "reliability": 0.8, "maximum_speed": 5, "build_cost_ic": 25,
    },
    "modern_tank_aa_chassis": {
        "name": "Modern SP Anti-Air",
        "soft_attack": 9, "hard_attack": 7.5, "defense": 4, "breakthrough": 4,
        "ap_attack": 100, "air_attack": 50, "armor_value": 90, "hardness": 0.85,
        "reliability": 0.8, "maximum_speed": 10, "build_cost_ic": 28,
    },
    "super_heavy_tank_aa_chassis": {
        "name": "Super Heavy SP Anti-Air",
        "soft_attack": 11.5, "hard_attack": 9, "defense": 3.5, "breakthrough": 3.5,
        "ap_attack": 98, "air_attack": 50, "armor_value": 100, "hardness": 0.9,
        "reliability": 0.8, "maximum_speed": 4, "build_cost_ic": 100,
    },
    "amphibious_tank_chassis": {
        "name": "Amphibious Tank",
        "soft_attack": 13, "hard_attack": 4, "defense": 4, "breakthrough": 26,
        "ap_attack": 10, "air_attack": 0, "armor_value": 20, "hardness": 0.8,
        "reliability": 0.8, "maximum_speed": 7, "build_cost_ic": 10,
    },
    "land_cruiser_chassis": {
        "name": "Land Cruiser",
        "soft_attack": 75, "hard_attack": 62, "defense": 35, "breakthrough": 120,
        "ap_attack": 160, "air_attack": 30, "armor_value": 180, "hardness": 12,
        "reliability": 0.65, "maximum_speed": 5, "build_cost_ic": 330,
    },

    # Confirmed gaps: no numbered equipment tier exists anywhere in
    # units_copy/ for these. Structural stats only, inherited from the base
    # chassis archetype (tank_chassis.txt / x_tank_chassis.txt's
    # duplicate_archetypes block); no attack/defense numbers are invented.
    "light_tank_amphibious_chassis": {
        "name": "Amphibious Light Tank",
        "armor_value": 10, "hardness": 0.55,
        "reliability": 0.8, "maximum_speed": 4, "build_cost_ic": 2,
        "combat_stats_available": False,
    },
    "medium_tank_amphibious_chassis": {
        "name": "Amphibious Medium Tank",
        "armor_value": 20, "hardness": 0.7,
        "reliability": 0.5, "maximum_speed": 4, "build_cost_ic": 2,
        "combat_stats_available": False,
    },
    "heavy_tank_amphibious_chassis": {
        "name": "Amphibious Heavy Tank",
        "armor_value": 30, "hardness": 0.8,
        "reliability": 0.75, "maximum_speed": 3, "build_cost_ic": 10,
        "combat_stats_available": False,
    },
    "light_tank_flame_chassis": {
        "name": "Light Flame Tank",
        "armor_value": 10, "hardness": 0.8,
        "reliability": 0.8, "maximum_speed": 4, "build_cost_ic": 2,
        "combat_stats_available": False,
    },
    "medium_tank_flame_chassis": {
        "name": "Medium Flame Tank",
        "armor_value": 20, "hardness": 0.85,
        "reliability": 0.5, "maximum_speed": 4, "build_cost_ic": 2,
        "combat_stats_available": False,
    },
    "heavy_tank_flame_chassis": {
        "name": "Heavy Flame Tank",
        "armor_value": 30, "hardness": 0.95,
        "reliability": 0.75, "maximum_speed": 3, "build_cost_ic": 10,
        "combat_stats_available": False,
    },
}
