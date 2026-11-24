# Hand-curated from units_copy/*.txt (HOI4 game files), verified 2026-09-23
# via three parallel full-file reads (not grep-sampled) covering every key
# in data/battalions.py/data/support_companies.py/data/regimental_support.py
# (101 total, matching those three files' own combined count exactly - a
# real cross-check, not a coincidence).
#
# TERRAIN_TYPES is the canonical list of the 11 terrain-ish keys found on
# sub_units - 8 real map terrain types (forest/jungle/hills/mountain/marsh/
# plains/urban/desert) plus 3 combat-situation modifiers that share the
# identical block syntax in the source files but aren't "where is this
# division deployed" terrain at all: fort (attacking a fortification),
# river (a river crossing), amphibious (an amphibious landing).
# `is_map_terrain` is exactly this split - Ollie's explicit call was to
# compile all 11 but keep the UI visually distinguishing the 3 situational
# ones from true terrain, not to drop them.
#
# A 12th key, `snow`, appears on a couple of units (winter_logistics_support,
# long_range_patrol_support) but is explicitly weather, not terrain - the
# source's own comment on recon.txt's snow block says it "can end up
# stacking with terrain benefits," i.e. its own author treats it as a
# separate mechanic. Weather is already out of scope
# (Expanded_real_stats.md) - excluded here on purpose, not missed.
TERRAIN_TYPES = [
    {"key": "forest", "name": "Forest", "is_map_terrain": True},
    {"key": "jungle", "name": "Jungle", "is_map_terrain": True},
    {"key": "hills", "name": "Hills", "is_map_terrain": True},
    {"key": "mountain", "name": "Mountain", "is_map_terrain": True},
    {"key": "marsh", "name": "Marsh", "is_map_terrain": True},
    {"key": "plains", "name": "Plains", "is_map_terrain": True},
    {"key": "urban", "name": "Urban", "is_map_terrain": True},
    {"key": "desert", "name": "Desert", "is_map_terrain": True},
    {"key": "fort", "name": "Fort", "is_map_terrain": False},
    {"key": "river", "name": "River Crossing", "is_map_terrain": False},
    {"key": "amphibious", "name": "Amphibious Assault", "is_map_terrain": False},
]

# {item_key: {terrain_key: {"attack": x, "defence": y, "movement": z}}},
# keyed by the same battalion/support-company/regimental-support keys
# data/battalions.py/data/support_companies.py/data/regimental_support.py
# already use. Only the fields a given terrain block actually sets are
# included - no invented zeros, matching every other data file's "don't
# guess missing data" rule (e.g. data/equipment.py's gap-flagging).
#
# An item with NO terrain block anywhere in units_copy/ is simply ABSENT
# from this dict entirely (not present with an empty {}) - confirmed, not
# a gap: every one of data/regimental_support.py's 14 items, and 18 of
# data/support_companies.py's 43 (the divisional support-artillery/AT/AA
# companies, signal/logistics/maintenance/field-hospital/military-police
# variants, and a few others - see tests/test_terrain.py for the exact
# list), have no terrain data in the source at all.
#
# What "attack"/"defence"/"movement" actually modify, and whether they're
# percentages or flat additions, is NOT yet confirmed - see Activity_Log.md,
# 2026-09-23, and CLAUDE.md's Terrain section. logic/terrain.py (applying
# this data to Stats) is deliberately not built yet, pending a real
# screenshot to verify the formula the same way Doctrine's was verified.
UNIT_TERRAIN_MODIFIERS = {
    # --- Infantry (units_copy/infantry.txt) ---
    "bicycle_battalion": {
        "forest": {"movement": 0.00},
        "jungle": {"movement": 0.00},
        "hills": {"movement": 0.1},
        "mountain": {"movement": 0.05},
        "marsh": {"movement": 0.05},
        "plains": {"movement": 0.2},
        "urban": {"movement": 0.2},
        "desert": {"movement": 0.05},
        "river": {"movement": -0.05},
        "amphibious": {"movement": -0.05},
    },
    "marine": {
        "marsh": {"attack": 0.3},
        "river": {"attack": 0.3},
        "amphibious": {"attack": 0.5},
    },
    "marine_commando": {
        "marsh": {"attack": 0.3},
        "river": {"attack": 0.3},
        "amphibious": {"attack": 0.5},
    },
    "mountaineers": {
        "hills": {"attack": 0.2, "defence": 0.05, "movement": 0.1},
        "mountain": {"attack": 0.35, "defence": 0.1, "movement": 0.2},
    },
    "ranger_battalion": {
        "forest": {"attack": 0.1, "defence": 0.1, "movement": 0.15},
        "jungle": {"attack": 0.2, "defence": 0.1, "movement": 0.15},
    },
    "irregular_infantry": {
        "hills": {"attack": 0.15, "defence": 0.05},
        "forest": {"attack": 0.15, "defence": 0.05},
        "mountain": {"attack": 0.15, "defence": 0.05},
        "desert": {"attack": 0.25, "defence": 0.10},
    },
    # infantry/paratrooper/penal_battalion/militia confirmed to have no
    # terrain block at all in units_copy/infantry.txt - not omitted by
    # accident.

    # --- Mobile (units_copy/infantry.txt, cavalry.txt, amphibious_mech.txt,
    # armored_car_battalion.txt) ---
    "motorized": {
        "forest": {"attack": -0.1, "movement": -0.5},
        "mountain": {"attack": -0.05},
        "jungle": {"attack": -0.2, "movement": -0.5},
        "marsh": {"attack": -0.1, "movement": -0.3},
        "urban": {"attack": -0.1},
        "river": {"attack": -0.1, "movement": -0.1},
        "amphibious": {"attack": -0.2},
    },
    "mechanized": {
        "forest": {"attack": -0.2},
        "mountain": {"attack": -0.05},
        "jungle": {"attack": -0.3},
        "marsh": {"attack": -0.1},
        "urban": {"attack": -0.2, "defence": -0.05},
        "river": {"attack": -0.2, "movement": -0.2},
        "amphibious": {"attack": -0.4},
    },
    "cavalry": {
        "forest": {"attack": -0.05},
        "hills": {"attack": -0.05},
        "mountain": {"attack": -0.1, "movement": -0.05},
        "jungle": {"attack": -0.1},
        "urban": {"attack": -0.05},
        "amphibious": {"attack": -0.4},
    },
    "camelry": {
        "forest": {"attack": -0.05},
        "hills": {"attack": -0.05, "movement": -0.05},
        "mountain": {"attack": -0.1, "movement": -0.05},
        "jungle": {"attack": -0.1},
        "marsh": {"movement": 0.05},
        "plains": {"movement": 0.15},
        "urban": {"attack": -0.05, "movement": -0.05},
        "desert": {"attack": 0.05, "defence": 0.05, "movement": 0.1},
        "amphibious": {"attack": -0.4},
    },
    "amphibious_mechanized": {
        "forest": {"attack": -0.2},
        "mountain": {"attack": -0.05},
        "jungle": {"attack": -0.3},
        "urban": {"attack": -0.2, "defence": -0.05},
        "marsh": {"attack": 0.2},
        "river": {"attack": 0.3},
        "amphibious": {"attack": 0.5},
    },
    "armored_car": {
        "forest": {"attack": -0.2, "movement": -0.4},
        "mountain": {"attack": -0.1, "movement": -0.1},
        "jungle": {"attack": -0.3, "movement": -0.5},
        "marsh": {"attack": -0.1, "movement": -0.2},
        "desert": {"movement": 0.15},
        "urban": {"attack": -0.3},
        "river": {"attack": -0.2, "movement": -0.2},
        "amphibious": {"attack": -0.4},
    },

    # --- Combat Support / Mobile Combat Support (units_copy/artillery_brigade.txt,
    # anti_tank_brigade.txt, anti-air_brigade.txt - the towed/motorized-speed
    # pairs share identical values except movement, confirmed not a
    # transcription slip) ---
    "artillery_brigade": {
        "forest": {"attack": -0.2, "movement": -0.2},
        "hills": {"movement": -0.05},
        "mountain": {"movement": -0.2},
        "jungle": {"attack": -0.25, "movement": -0.2},
        "marsh": {"attack": -0.2, "movement": -0.3},
        "fort": {"attack": 0.1},
        "river": {"attack": -0.2, "movement": -0.2},
        "amphibious": {"attack": -0.4},
    },
    "rocket_artillery_brigade": {
        "forest": {"attack": -0.2, "movement": -0.2},
        "hills": {"movement": -0.05},
        "mountain": {"movement": -0.2},
        "jungle": {"attack": -0.25, "movement": -0.2},
        "marsh": {"attack": -0.2, "movement": -0.3},
        "fort": {"attack": 0.1},
        "river": {"attack": -0.2, "movement": -0.2},
        "amphibious": {"attack": -0.4},
    },
    "anti_tank_brigade": {
        "forest": {"attack": -0.2, "movement": -0.2},
        "hills": {"movement": -0.05},
        "mountain": {"movement": -0.2},
        "jungle": {"attack": -0.25, "movement": -0.2},
        "marsh": {"attack": -0.2, "movement": -0.3},
        "fort": {"attack": 0.1},
        "river": {"attack": -0.2, "movement": -0.2},
        "amphibious": {"attack": -0.4},
    },
    "anti_air_brigade": {
        "forest": {"attack": -0.1, "movement": -0.1},
        "jungle": {"attack": -0.2, "movement": -0.2},
        "marsh": {"attack": -0.2, "movement": -0.2},
        "river": {"attack": -0.2, "movement": -0.2},
        "amphibious": {"attack": -0.4},
    },
    "mot_artillery_brigade": {
        "forest": {"attack": -0.2, "movement": -0.5},
        "hills": {"movement": -0.05},
        "mountain": {"movement": -0.2},
        "jungle": {"attack": -0.25, "movement": -0.5},
        "marsh": {"attack": -0.2, "movement": -0.3},
        "fort": {"attack": 0.1},
        "river": {"attack": -0.2, "movement": -0.2},
        "amphibious": {"attack": -0.4},
    },
    "mot_rocket_artillery_brigade": {
        "forest": {"attack": -0.2, "movement": -0.5},
        "hills": {"movement": -0.05},
        "mountain": {"movement": -0.2},
        "jungle": {"attack": -0.25, "movement": -0.5},
        "marsh": {"attack": -0.2, "movement": -0.3},
        "fort": {"attack": 0.1},
        "river": {"attack": -0.2, "movement": -0.2},
        "amphibious": {"attack": -0.4},
    },
    "mot_anti_tank_brigade": {
        "forest": {"attack": -0.2, "movement": -0.5},
        "hills": {"movement": -0.05},
        "mountain": {"movement": -0.2},
        "jungle": {"attack": -0.25, "movement": -0.5},
        "marsh": {"attack": -0.2, "movement": -0.3},
        "fort": {"attack": 0.1},
        "river": {"attack": -0.2, "movement": -0.2},
        "amphibious": {"attack": -0.4},
    },
    "mot_anti_air_brigade": {
        "forest": {"attack": -0.1, "movement": -0.5},
        "jungle": {"attack": -0.2, "movement": -0.5},
        "marsh": {"attack": -0.2, "movement": -0.2},
        "river": {"attack": -0.2, "movement": -0.2},
        "amphibious": {"attack": -0.4},
    },

    # --- Armor (units_copy/light_armor.txt, medium_armor.txt, heavy_armor.txt,
    # modern_armor.txt, amphibious_armor.txt) ---
    "light_armor": {
        "forest": {"attack": -0.2, "movement": -0.4},
        "mountain": {"attack": -0.1},
        "jungle": {"attack": -0.3, "movement": -0.4},
        "marsh": {"attack": -0.1, "movement": -0.1},
        "urban": {"attack": -0.4, "defence": -0.1},
        "river": {"attack": -0.2, "movement": -0.2},
        "amphibious": {"attack": -0.4},
    },
    "medium_armor": {
        "forest": {"attack": -0.3, "movement": -0.4},
        "hills": {"attack": -0.1},
        "mountain": {"attack": -0.2},
        "jungle": {"attack": -0.4, "movement": -0.4},
        "marsh": {"attack": -0.1, "movement": -0.1},
        "urban": {"attack": -0.4, "defence": -0.1},
        "river": {"attack": -0.2, "movement": -0.2},
        "amphibious": {"attack": -0.8},
    },
    "heavy_armor": {
        "forest": {"attack": -0.40, "movement": -0.40},
        "hills": {"attack": -0.20},
        "mountain": {"attack": -0.3},
        "jungle": {"attack": -0.6, "movement": -0.4},
        "marsh": {"attack": -0.4, "movement": -0.2},
        "urban": {"attack": -0.5, "defence": -0.2},
        "river": {"attack": -0.4, "movement": -0.4},
        "amphibious": {"attack": -0.9},
        "fort": {"attack": 0.1},
    },
    "modern_armor": {
        "forest": {"attack": -0.3, "movement": -0.4},
        "hills": {"attack": -0.1},
        "mountain": {"attack": -0.2},
        "jungle": {"attack": -0.4, "movement": -0.4},
        "marsh": {"attack": -0.1, "movement": -0.1},
        "urban": {"attack": -0.4, "defence": -0.1},
        "river": {"attack": -0.2, "movement": -0.2},
        "amphibious": {"attack": -0.7},
    },
    # All 4 amphibious-armor variants share byte-identical terrain blocks in
    # the source (units_copy/amphibious_armor.txt) - confirmed genuine, not
    # a transcription shortcut.
    "amphibious_armor": {
        "forest": {"attack": -0.2, "movement": -0.4},
        "mountain": {"attack": -0.1},
        "plains": {"attack": -0.1, "movement": -0.1},
        "jungle": {"attack": -0.3, "movement": -0.4},
        "urban": {"attack": -0.4, "defence": -0.1},
        "marsh": {"attack": 0.3},
        "river": {"attack": 0.4},
        "amphibious": {"attack": 0.6},
    },
    "amphibious_light_armor": {
        "forest": {"attack": -0.2, "movement": -0.4},
        "mountain": {"attack": -0.1},
        "plains": {"attack": -0.1, "movement": -0.1},
        "jungle": {"attack": -0.3, "movement": -0.4},
        "urban": {"attack": -0.4, "defence": -0.1},
        "marsh": {"attack": 0.3},
        "river": {"attack": 0.4},
        "amphibious": {"attack": 0.6},
    },
    "amphibious_medium_armor": {
        "forest": {"attack": -0.2, "movement": -0.4},
        "mountain": {"attack": -0.1},
        "plains": {"attack": -0.1, "movement": -0.1},
        "jungle": {"attack": -0.3, "movement": -0.4},
        "urban": {"attack": -0.4, "defence": -0.1},
        "marsh": {"attack": 0.3},
        "river": {"attack": 0.4},
        "amphibious": {"attack": 0.6},
    },
    "amphibious_heavy_armor": {
        "forest": {"attack": -0.2, "movement": -0.4},
        "mountain": {"attack": -0.1},
        "plains": {"attack": -0.1, "movement": -0.1},
        "jungle": {"attack": -0.3, "movement": -0.4},
        "urban": {"attack": -0.4, "defence": -0.1},
        "marsh": {"attack": 0.3},
        "river": {"attack": 0.4},
        "amphibious": {"attack": 0.6},
    },

    # --- Armored Combat Support (units_copy/tank_destroyer_brigade.txt,
    # sp_artillery_brigade.txt, sp_anti-air_brigade.txt) ---
    "light_tank_destroyer_brigade": {
        "forest": {"attack": -0.2, "movement": -0.4},
        "mountain": {"attack": -0.1},
        "jungle": {"attack": -0.3, "movement": -0.4},
        "marsh": {"attack": -0.1, "movement": -0.1},
        "urban": {"attack": -0.4, "defence": -0.1},
        "river": {"attack": -0.2, "movement": -0.2},
        "amphibious": {"attack": -0.6},
    },
    "medium_tank_destroyer_brigade": {
        "forest": {"attack": -0.3, "movement": -0.4},
        "hills": {"attack": -0.1},
        "mountain": {"attack": -0.2},
        "jungle": {"attack": -0.4, "movement": -0.4},
        "marsh": {"attack": -0.1, "movement": -0.1},
        "urban": {"attack": -0.4, "defence": -0.1},
        "river": {"attack": -0.2, "movement": -0.2},
        "amphibious": {"attack": -0.7},
    },
    "heavy_tank_destroyer_brigade": {
        "forest": {"attack": -0.40, "movement": -0.40},
        "hills": {"attack": -0.20},
        "mountain": {"attack": -0.3},
        "jungle": {"attack": -0.6, "movement": -0.4},
        "marsh": {"attack": -0.4, "movement": -0.2},
        "urban": {"attack": -0.5, "defence": -0.2},
        "river": {"attack": -0.4, "movement": -0.4},
        "amphibious": {"attack": -0.8},
        "fort": {"attack": 0.05},
    },
    "modern_tank_destroyer_brigade": {
        "forest": {"attack": -0.3, "movement": -0.4},
        "hills": {"attack": -0.1},
        "mountain": {"attack": -0.2},
        "jungle": {"attack": -0.4, "movement": -0.4},
        "marsh": {"attack": -0.1, "movement": -0.1},
        "urban": {"attack": -0.4, "defence": -0.1},
        "river": {"attack": -0.2, "movement": -0.2},
        "amphibious": {"attack": -0.7},
    },
    "light_sp_artillery_brigade": {
        "forest": {"attack": -0.2, "movement": -0.4},
        "mountain": {"attack": -0.1},
        "jungle": {"attack": -0.3, "movement": -0.4},
        "marsh": {"attack": -0.1, "movement": -0.1},
        "urban": {"attack": -0.4, "defence": -0.1},
        "river": {"attack": -0.2, "movement": -0.2},
        "amphibious": {"attack": -0.6},
    },
    "medium_sp_artillery_brigade": {
        "forest": {"attack": -0.3, "movement": -0.4},
        "hills": {"attack": -0.1},
        "mountain": {"attack": -0.2},
        "jungle": {"attack": -0.4, "movement": -0.4},
        "marsh": {"attack": -0.1, "movement": -0.1},
        "urban": {"attack": -0.4, "defence": -0.1},
        "river": {"attack": -0.2, "movement": -0.2},
        "amphibious": {"attack": -0.7},
    },
    "heavy_sp_artillery_brigade": {
        "forest": {"attack": -0.40, "movement": -0.40},
        "hills": {"attack": -0.20},
        "mountain": {"attack": -0.3},
        "jungle": {"attack": -0.6, "movement": -0.4},
        "marsh": {"attack": -0.4, "movement": -0.2},
        "urban": {"attack": -0.5, "defence": -0.2},
        "river": {"attack": -0.4, "movement": -0.4},
        "amphibious": {"attack": -0.8},
    },
    "modern_sp_artillery_brigade": {
        "forest": {"attack": -0.3, "movement": -0.4},
        "hills": {"attack": -0.1},
        "mountain": {"attack": -0.2},
        "jungle": {"attack": -0.4, "movement": -0.4},
        "marsh": {"attack": -0.1, "movement": -0.1},
        "urban": {"attack": -0.4, "defence": -0.1},
        "river": {"attack": -0.2, "movement": -0.2},
        "amphibious": {"attack": -0.7},
    },
    "light_sp_anti_air_brigade": {
        "forest": {"attack": -0.2, "movement": -0.4},
        "mountain": {"attack": -0.1},
        "jungle": {"attack": -0.3, "movement": -0.4},
        "marsh": {"attack": -0.1, "movement": -0.1},
        "urban": {"attack": -0.4, "defence": -0.1},
        "river": {"attack": -0.2, "movement": -0.2},
        "amphibious": {"attack": -0.6},
    },
    "medium_sp_anti_air_brigade": {
        "forest": {"attack": -0.3, "movement": -0.4},
        "hills": {"attack": -0.1},
        "mountain": {"attack": -0.2},
        "jungle": {"attack": -0.4, "movement": -0.4},
        "marsh": {"attack": -0.1, "movement": -0.1},
        "urban": {"attack": -0.4, "defence": -0.1},
        "river": {"attack": -0.2, "movement": -0.2},
        "amphibious": {"attack": -0.7},
    },
    "heavy_sp_anti_air_brigade": {
        "forest": {"attack": -0.40, "movement": -0.40},
        "hills": {"attack": -0.20},
        "mountain": {"attack": -0.3},
        "jungle": {"attack": -0.6, "movement": -0.4},
        "marsh": {"attack": -0.4, "movement": -0.2},
        "urban": {"attack": -0.5, "defence": -0.2},
        "river": {"attack": -0.4, "movement": -0.4},
        "amphibious": {"attack": -0.8},
    },
    "modern_sp_anti_air_brigade": {
        "forest": {"attack": -0.3, "movement": -0.4},
        "hills": {"attack": -0.1},
        "mountain": {"attack": -0.2},
        "jungle": {"attack": -0.4, "movement": -0.4},
        "marsh": {"attack": -0.1, "movement": -0.1},
        "urban": {"attack": -0.4, "defence": -0.1},
        "river": {"attack": -0.2, "movement": -0.2},
        "amphibious": {"attack": -0.7},
    },

    # --- Support companies: Reconnaissance (units_copy/recon.txt) ---
    "recon": {
        "forest": {"movement": 0.05},
        "hills": {"movement": 0.10},
        "mountain": {"movement": 0.10},
        "jungle": {"movement": 0.10},
        "marsh": {"movement": 0.10},
        "plains": {"movement": 0.05},
        "desert": {"movement": 0.05},
        "river": {"movement": 0.1},
    },
    "mot_recon": {
        "forest": {"movement": 0.05},
        "hills": {"movement": 0.1},
        "mountain": {"movement": 0.1},
        "jungle": {"movement": 0.05},
        "marsh": {"movement": 0.1},
        "plains": {"movement": 0.15},
        "desert": {"movement": 0.20},
        "river": {"movement": 0.1},
    },
    # A commented-out marsh block also exists in the source
    # (`#marsh = { #  movement = 0.1 #}`) - deliberately inactive in HOI4
    # itself, so deliberately excluded here too, not a missed field.
    "armored_car_recon": {
        "forest": {"movement": 0.05},
        "hills": {"movement": 0.1},
        "mountain": {"movement": 0.05},
        "jungle": {"movement": 0.05},
        "plains": {"movement": 0.15},
        "desert": {"movement": 0.15},
        "river": {"movement": 0.1},
    },
    "light_tank_recon": {
        "forest": {"movement": 0.1},
        "hills": {"movement": 0.1},
        "mountain": {"movement": 0.1},
        "jungle": {"movement": 0.1},
        "marsh": {"movement": 0.1},
        "plains": {"movement": 0.1},
        "desert": {"movement": 0.1},
        "river": {"movement": 0.1},
    },
    "airborne_light_armor": {
        "forest": {"movement": 0.1},
        "hills": {"movement": 0.1},
        "mountain": {"movement": 0.1},
        "jungle": {"movement": 0.1},
        "marsh": {"movement": 0.1},
        "plains": {"movement": 0.1},
        "desert": {"movement": 0.1},
        "river": {"movement": 0.1},
    },
    "rangers_support": {
        "forest": {"movement": 0.15, "attack": 0.05},
        "hills": {"movement": 0.15, "attack": 0.05},
        "mountain": {"movement": 0.10, "defence": 0.05},
        "jungle": {"movement": 0.10},
        "plains": {"movement": 0.1, "attack": 0.05},
    },
    "northern_territory_recon_support": {
        "forest": {"movement": 0.20, "attack": 0.075},
        "hills": {"movement": 0.20, "attack": 0.075},
        "mountain": {"movement": 0.10, "defence": 0.05},
        "jungle": {"movement": 0.10},
        "plains": {"movement": 0.1, "attack": 0.05},
    },
    "long_range_patrol_support": {
        "forest": {"movement": 0.15, "attack": 0.05},
        "hills": {"movement": 0.15, "attack": 0.05},
        "marsh": {"movement": 0.10, "attack": 0.05},
        "plains": {"movement": 0.1, "attack": 0.05},
        "mountain": {"movement": 0.15},
        "jungle": {"movement": 0.10},
        "desert": {"movement": 0.1},
        "river": {"movement": 0.1},
    },
    "helicopter_recon": {
        "forest": {"movement": 0.15},
        "hills": {"movement": 0.1},
        "mountain": {"movement": 0.1},
        "jungle": {"movement": 0.15},
        "marsh": {"movement": 0.15},
        "plains": {"movement": 0.15},
        "desert": {"movement": 0.15},
        "river": {"movement": 0.15},
    },

    # --- Support companies: Engineers (units_copy/engineer.txt) ---
    "engineer": {
        "forest": {"defence": 0.25, "movement": 0.05},
        "hills": {"defence": 0.1},
        "jungle": {"defence": 0.25},
        "marsh": {"defence": 0.25, "movement": 0.2},
        "fort": {"attack": 0.1, "defence": 0.25},
        "river": {"defence": 0.25, "movement": 0.25},
        "amphibious": {"attack": 0.15},
    },
    "pioneer_support": {
        "marsh": {"attack": 0.10, "defence": 0.20, "movement": 0.2},
        "fort": {"attack": 0.15, "defence": 0.20},
        "river": {"attack": 0.10, "defence": 0.20, "movement": 0.25},
    },
    "jungle_pioneers_support": {
        "forest": {"attack": 0.1, "defence": 0.05, "movement": 0.3},
        "jungle": {"attack": 0.1, "defence": 0.2, "movement": 0.3},
        "river": {"attack": 0.1, "defence": 0.25, "movement": 0.25},
    },
    "assault_engineer": {
        "forest": {"attack": 0.05, "defence": 0.1},
        "hills": {"attack": 0.05, "defence": 0.1},
        "jungle": {"attack": 0.05, "defence": 0.1},
        "marsh": {"attack": 0.05, "defence": 0.1, "movement": 0.1},
        "fort": {"attack": 0.25, "defence": 0.1},
        "river": {"attack": 0.05, "defence": 0.1, "movement": 0.25},
        "amphibious": {"attack": 0.15},
        "urban": {"attack": 0.2, "movement": 0.05},
    },
    "armored_engineer": {
        "forest": {"defence": 0.25, "movement": 0.1},
        "plains": {"movement": 0.1},
        "desert": {"movement": 0.1},
        "hills": {"defence": 0.1, "movement": 0.05},
        "jungle": {"defence": 0.15, "movement": 0.05},
        "marsh": {"defence": 0.15, "movement": 0.2},
        "fort": {"attack": 0.15, "defence": 0.25},
        "river": {"attack": 0.1, "defence": 0.15, "movement": 0.4},
        "amphibious": {"attack": 0.2},
        "urban": {"attack": 0.2, "defence": 0.1, "movement": 0.1},
    },

    # --- Support companies: misc (units_copy/logistics.txt, cavalry.txt,
    # flame_tank.txt, super_heavy_armor.txt, land_cruiser.txt,
    # tank_destroyer_brigade.txt, sp_artillery_brigade.txt,
    # sp_anti-air_brigade.txt, sturmtruppe_battalion.txt) ---
    "helicopter_transport": {
        "forest": {"movement": 0.05},
        "hills": {"movement": 0.05},
        "mountain": {"movement": 0.05},
        "jungle": {"movement": 0.05},
        "marsh": {"movement": 0.05},
        "plains": {"movement": 0.05},
        "desert": {"movement": 0.05},
        "river": {"movement": 0.05},
    },
    "elephantry": {
        "forest": {"attack": 0.05, "movement": 0.05},
        "hills": {"movement": 0.15, "attack": 0.05},
        "mountain": {"attack": 0.05, "movement": 0.15},
        "jungle": {"attack": 0.1, "movement": 0.15},
        "marsh": {"movement": -0.1, "attack": -0.1},
        "urban": {"attack": -0.15, "movement": -0.25},
        "amphibious": {"attack": -0.7},
    },
    "light_flame_tank": {
        "forest": {"attack": 0.05},
        "mountain": {"attack": 0.05},
        "hills": {"attack": 0.05},
        "jungle": {"attack": 0.1},
        "marsh": {"attack": 0.05},
        "urban": {"attack": 0.1},
        "fort": {"attack": 0.1, "movement": 0.1},
        "river": {"attack": 0.1},
        "amphibious": {"attack": 0.1},
    },
    "medium_flame_tank": {
        "forest": {"attack": 0.1},
        "mountain": {"attack": 0.05},
        "hills": {"attack": 0.05},
        "jungle": {"attack": 0.15},
        "marsh": {"attack": 0.05},
        "urban": {"attack": 0.15},
        "fort": {"attack": 0.2, "movement": 0.1},
        "river": {"attack": 0.1},
        "amphibious": {"attack": 0.1},
    },
    "heavy_flame_tank": {
        "forest": {"attack": 0.1},
        "hills": {"attack": 0.05},
        "jungle": {"attack": 0.1},
        "marsh": {"attack": 0.05},
        "urban": {"attack": 0.1},
        "fort": {"attack": 0.25, "movement": 0.1},
        "river": {"attack": 0.05},
        "amphibious": {"attack": 0.05},
    },
    "super_heavy_armor": {
        "forest": {"attack": -0.25, "movement": -0.3},
        "hills": {"attack": -0.15, "defence": -0.15},
        "mountain": {"attack": -0.2, "defence": -0.2},
        "urban": {"attack": -0.3, "defence": -0.3},
        "jungle": {"attack": -0.35, "defence": -0.35, "movement": -0.3},
        "marsh": {"attack": -0.3, "defence": -0.3, "movement": -0.3},
        "fort": {"attack": 0.1, "defence": 0.05},
        "river": {"attack": -0.25, "defence": -0.25, "movement": -0.3},
        "amphibious": {"attack": -0.6},
    },
    "land_cruiser": {
        "forest": {"attack": -0.3, "defence": -0.3, "movement": -0.2},
        "hills": {"attack": -0.2, "defence": -0.2, "movement": -0.25},
        "mountain": {"attack": -0.3, "defence": -0.3, "movement": -0.3},
        "jungle": {"attack": -0.4, "defence": -0.4, "movement": -0.35},
        "marsh": {"attack": -0.4, "defence": -0.4, "movement": -0.5},
        "urban": {"attack": -0.3, "defence": -0.3},
        "river": {"attack": -0.35, "defence": -0.35, "movement": -0.5},
        "amphibious": {"attack": -0.7},
        "fort": {"attack": 0.2, "defence": 0.1},
    },
    "super_heavy_tank_destroyer_brigade": {
        "forest": {"attack": -0.5, "movement": -0.4},
        "hills": {"attack": -0.3},
        "mountain": {"attack": -0.4},
        "jungle": {"attack": -0.7, "movement": -0.4},
        "marsh": {"attack": -0.5, "movement": -0.2},
        "urban": {"attack": -0.6, "defence": -0.2},
        "river": {"attack": -0.5, "movement": -0.5},
        "amphibious": {"attack": -1.0},
        "fort": {"attack": 0.3},
    },
    # Unlike its tank-destroyer/super_heavy_armor/land_cruiser siblings
    # above, neither super-heavy SP Artillery nor SP Anti-Air gets a fort
    # bonus - confirmed by direct read, a real asymmetry, not a gap.
    "super_heavy_sp_artillery_brigade": {
        "forest": {"attack": -0.5, "movement": -0.4},
        "hills": {"attack": -0.3},
        "mountain": {"attack": -0.4},
        "jungle": {"attack": -0.7, "movement": -0.4},
        "marsh": {"attack": -0.5, "movement": -0.2},
        "urban": {"attack": -0.6, "defence": -0.2},
        "river": {"attack": -0.5, "movement": -0.5},
        "amphibious": {"attack": -1.0},
    },
    "super_heavy_sp_anti_air_brigade": {
        "forest": {"attack": -0.5, "movement": -0.4},
        "hills": {"attack": -0.3},
        "mountain": {"attack": -0.4},
        "jungle": {"attack": -0.7, "movement": -0.4},
        "marsh": {"attack": -0.5, "movement": -0.2},
        "urban": {"attack": -0.6, "defence": -0.2},
        "river": {"attack": -0.5, "movement": -0.4},
        "amphibious": {"attack": -1.0},
    },
    "sturmtruppe_battalion": {
        "fort": {"attack": 0.1},
        "urban": {"attack": 0.1},
    },

    # winter_logistics_support/signal_company/armored_signal/field_hospital/
    # helicopter_field_hospital/logistics_company/military_police/
    # motorized_military_police/maintenance_company/armored_maintenance/
    # anti_tank/anti_air/artillery/rocket_artillery/super_heavy_artillery/
    # self_propelled_super_heavy_artillery/helicopter_brigade/
    # blackshirt_assault_battalion (support companies), and all 14
    # data/regimental_support.py items, confirmed to have NO terrain block
    # at all in units_copy/ - not omitted by accident, and not present here
    # with an empty {} (see this file's own header comment on why).
}

# The SECOND, separately-sourced terrain layer - confirmed 2026-09-29 against
# two real screenshots (see CLAUDE.md's Terrain section for the full
# reconciliation). Unlike UNIT_TERRAIN_MODIFIERS (which comes from each
# sub_unit's own block in units_copy/*.txt), this comes from HOI4's generic
# per-terrain-TYPE file, terrain_copy/00_terrain.txt (gitignored, real
# common/terrain/00_terrain.txt), and applies to every unit regardless of
# type - a flat percentage penalty layered additively with the per-unit
# value above, not a replacement for it.
#
# terrain_copy/00_terrain.txt's categories.<key>.units block only ever sets
# `attack` (never `defence`) for 6 of the 8 real terrain types - plains and
# desert have no `units` block at all, and `movement` is commented out
# (inactive) for every terrain type that has one. fort/river/amphibious
# don't appear in this file's categories block at all, confirming those
# three really are purely per-unit modifiers with no generic layer - so
# this dict only ever has an "attack" key, and only for the 6 keys below.
GENERIC_TERRAIN_MODIFIERS = {
    "forest": {"attack": -0.15},
    "hills": {"attack": -0.25},
    "mountain": {"attack": -0.5},
    "urban": {"attack": -0.3},
    "jungle": {"attack": -0.3},
    "marsh": {"attack": -0.4},
}
