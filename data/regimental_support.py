# Hand-curated from units_copy/*.txt (HOI4 game files), verified 2026-09-13.
# "key" matches the game's own sub_unit identifier.
# "allowed_battalion_groups" is the game's own `allowed_battalion_groups`
# field, listing which battalion categories (see data/battalions.py's
# CATEGORIES - the two use identical strings) a battalion column must be
# using before this regimental support option is offered for it. The
# doc-level rule (a column also needs >=3 battalions placed before its
# regimental support slot unlocks at all) is a UI/logic concern, not
# per-item data - not encoded here.
#
# Sources, both verified via the same rule used throughout data/: presence
# of category_regimental_support_battalions + divisional = no, not the
# file/key name:
# - units_copy/fire_support.txt: despite its name, every entry here is
#   regimental support, not a support company (see data/support_companies.py
#   for that earlier mix-up in the other direction).
# - the "##TD reg support" section inside units_copy/tank_destroyer_brigade.txt
#   and the "##SUPPORT" section inside units_copy/sp_anti-air_brigade.txt -
#   both files also define full grid battalions (already in
#   data/battalions.py) alongside these "_support"-suffixed regimental
#   variants.
#
# No regimental-support variant exists for SP Artillery in the source files
# (units_copy/sp_artillery_brigade.txt has no such section) - not an
# oversight here.

REGIMENTAL_SUPPORT = [
    {"key": "fire_support", "name": "Fire Support", "allowed_battalion_groups": ["infantry", "mobile", "combat_support"]},
    {"key": "mot_fire_support", "name": "Motorized Fire Support", "allowed_battalion_groups": ["infantry", "mobile", "combat_support", "mobile_combat_support", "armor", "armor_combat_support"]},
    {"key": "field_guns", "name": "Field Guns", "allowed_battalion_groups": ["infantry", "mobile", "combat_support"]},
    {"key": "rocket_battery", "name": "Rocket Battery", "allowed_battalion_groups": ["infantry", "mobile", "combat_support"]},
    {"key": "anti_air_battery", "name": "Anti-Air Battery", "allowed_battalion_groups": ["infantry", "mobile", "combat_support"]},
    {"key": "anti_tank_battery", "name": "Anti-Tank Battery", "allowed_battalion_groups": ["infantry", "mobile", "combat_support"]},

    {"key": "light_tank_destroyer_support", "name": "Light Tank Destroyer Support", "allowed_battalion_groups": ["armor", "mobile_combat_support", "armor_combat_support"]},
    {"key": "medium_tank_destroyer_support", "name": "Medium Tank Destroyer Support", "allowed_battalion_groups": ["armor", "mobile_combat_support", "armor_combat_support"]},
    {"key": "heavy_tank_destroyer_support", "name": "Heavy Tank Destroyer Support", "allowed_battalion_groups": ["armor", "mobile_combat_support", "armor_combat_support"]},
    {"key": "modern_tank_destroyer_support", "name": "Modern Tank Destroyer Support", "allowed_battalion_groups": ["armor", "mobile_combat_support", "armor_combat_support"]},

    {"key": "light_sp_anti_air_support", "name": "Light SP Anti-Air Support", "allowed_battalion_groups": ["armor", "mobile_combat_support", "armor_combat_support"]},
    {"key": "medium_sp_anti_air_support", "name": "Medium SP Anti-Air Support", "allowed_battalion_groups": ["armor", "mobile_combat_support", "armor_combat_support"]},
    {"key": "heavy_sp_anti_air_support", "name": "Heavy SP Anti-Air Support", "allowed_battalion_groups": ["armor", "mobile_combat_support", "armor_combat_support"]},
    {"key": "modern_sp_anti_air_support", "name": "Modern SP Anti-Air Support", "allowed_battalion_groups": ["armor", "mobile_combat_support", "armor_combat_support"]},
]
