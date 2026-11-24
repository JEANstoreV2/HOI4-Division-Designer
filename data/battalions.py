# Hand-curated from units_copy/*.txt (HOI4 game files), verified 2026-09-13.
# "key" matches the game's own sub_unit identifier, for easy cross-referencing
# against patch notes or the source files if this ever needs updating.
# "category" matches the game's own column-grouping rule: a battalion column
# (brigade) may only contain battalions from the same category.

BATTALIONS = [
    # Infantry
    {"key": "infantry", "name": "Infantry", "category": "infantry"},
    {"key": "bicycle_battalion", "name": "Bicycle", "category": "infantry"},
    {"key": "marine", "name": "Marines", "category": "infantry"},
    {"key": "marine_commando", "name": "Marine Commandos", "category": "infantry"},
    {"key": "mountaineers", "name": "Mountaineers", "category": "infantry"},
    {"key": "ranger_battalion", "name": "Rangers", "category": "infantry"},
    {"key": "paratrooper", "name": "Paratroopers", "category": "infantry"},
    {"key": "penal_battalion", "name": "Penal Battalion", "category": "infantry"},
    {"key": "irregular_infantry", "name": "Irregulars", "category": "infantry"},
    {"key": "militia", "name": "Militia", "category": "infantry"},

    # Mobile
    {"key": "cavalry", "name": "Cavalry", "category": "mobile"},
    {"key": "camelry", "name": "Camelry", "category": "mobile"},
    {"key": "motorized", "name": "Motorized Infantry", "category": "mobile"},
    {"key": "mechanized", "name": "Mechanized Infantry", "category": "mobile"},
    {"key": "amphibious_mechanized", "name": "Amphibious Mechanized", "category": "mobile"},
    {"key": "armored_car", "name": "Armored Car", "category": "mobile"},

    # Combat Support (infantry-speed towed support weapons)
    {"key": "artillery_brigade", "name": "Artillery", "category": "combat_support"},
    {"key": "rocket_artillery_brigade", "name": "Rocket Artillery", "category": "combat_support"},
    {"key": "anti_tank_brigade", "name": "Anti-Tank", "category": "combat_support"},
    {"key": "anti_air_brigade", "name": "Anti-Air", "category": "combat_support"},

    # Mobile Combat Support (motorized-speed equivalents of the above)
    {"key": "mot_artillery_brigade", "name": "Motorized Artillery", "category": "mobile_combat_support"},
    {"key": "mot_rocket_artillery_brigade", "name": "Motorized Rocket Artillery", "category": "mobile_combat_support"},
    {"key": "mot_anti_tank_brigade", "name": "Motorized Anti-Tank", "category": "mobile_combat_support"},
    {"key": "mot_anti_air_brigade", "name": "Motorized Anti-Air", "category": "mobile_combat_support"},

    # Armor
    {"key": "light_armor", "name": "Light Tank", "category": "armor"},
    {"key": "medium_armor", "name": "Medium Tank", "category": "armor"},
    {"key": "heavy_armor", "name": "Heavy Tank", "category": "armor"},
    {"key": "modern_armor", "name": "Modern Tank", "category": "armor"},
    {"key": "amphibious_armor", "name": "Amphibious Tank", "category": "armor"},
    {"key": "amphibious_light_armor", "name": "Amphibious Light Tank", "category": "armor"},
    {"key": "amphibious_medium_armor", "name": "Amphibious Medium Tank", "category": "armor"},
    {"key": "amphibious_heavy_armor", "name": "Amphibious Heavy Tank", "category": "armor"},

    # Armored Combat Support (tank-chassis support: tank destroyers, SP artillery, SP AA)
    {"key": "light_tank_destroyer_brigade", "name": "Light Tank Destroyer", "category": "armor_combat_support"},
    {"key": "medium_tank_destroyer_brigade", "name": "Medium Tank Destroyer", "category": "armor_combat_support"},
    {"key": "heavy_tank_destroyer_brigade", "name": "Heavy Tank Destroyer", "category": "armor_combat_support"},
    {"key": "modern_tank_destroyer_brigade", "name": "Modern Tank Destroyer", "category": "armor_combat_support"},
    {"key": "light_sp_artillery_brigade", "name": "Light SP Artillery", "category": "armor_combat_support"},
    {"key": "medium_sp_artillery_brigade", "name": "Medium SP Artillery", "category": "armor_combat_support"},
    {"key": "heavy_sp_artillery_brigade", "name": "Heavy SP Artillery", "category": "armor_combat_support"},
    {"key": "modern_sp_artillery_brigade", "name": "Modern SP Artillery", "category": "armor_combat_support"},
    {"key": "light_sp_anti_air_brigade", "name": "Light SP Anti-Air", "category": "armor_combat_support"},
    {"key": "medium_sp_anti_air_brigade", "name": "Medium SP Anti-Air", "category": "armor_combat_support"},
    {"key": "heavy_sp_anti_air_brigade", "name": "Heavy SP Anti-Air", "category": "armor_combat_support"},
    {"key": "modern_sp_anti_air_brigade", "name": "Modern SP Anti-Air", "category": "armor_combat_support"},
]

# Column order the composition grid should offer, matching the game's own
# category grouping (a column may only hold battalions of one category).
CATEGORIES = [
    "infantry",
    "mobile",
    "combat_support",
    "mobile_combat_support",
    "armor",
    "armor_combat_support",
]

CATEGORY_LABELS = {
    "infantry": "Infantry",
    "mobile": "Mobile",
    "combat_support": "Combat Support",
    "mobile_combat_support": "Mobile Combat Support",
    "armor": "Armor",
    "armor_combat_support": "Armored Combat Support",
}
