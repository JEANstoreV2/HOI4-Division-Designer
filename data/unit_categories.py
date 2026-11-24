# Hand-curated from units_copy/*.txt (HOI4 game files), compiled 2026-09-15.
# Every sub_unit definition in units_copy carries the game's own
# `categories = { category_x category_y ... }` block - this file transcribes
# that block for every key already in data/battalions.py, data/support_companies.py,
# and data/regimental_support.py (~91 keys total), so logic/stats.py can match
# a doctrine unit_bonus targeting a category (e.g. "category_all_infantry")
# against the actual items it applies to.
#
# NOT the same thing as data/battalions.py's own "category" field (that's this
# project's own composition-column grouping - a different, smaller vocabulary
# invented for the Composition UI, not the game's own tag set used here).
#
# Extracted mechanically from every units_copy/*.txt file (script discarded
# after use, not checked in - same as every other data/*.py compile pass) and
# spot-checked directly against source: e.g. units_copy/infantry.txt's `marine`
# block carries category_special_forces/category_marines/category_all_infantry/
# category_army, all reproduced below.

UNIT_CATEGORIES = {
    # --- Battalions (data/battalions.py) ---
    "infantry": {"category_front_line", "category_light_infantry", "category_all_infantry", "category_army", "category_infantry_and_bicycle"},
    "bicycle_battalion": {"category_front_line", "category_light_infantry", "category_all_infantry", "category_army", "category_infantry_and_bicycle"},
    "marine": {"category_front_line", "category_light_infantry", "category_all_infantry", "category_army", "category_special_forces", "category_marines", "category_marines_and_amphibious", "category_special_forces_leg_infantry"},
    "marine_commando": {"category_front_line", "category_light_infantry", "category_all_infantry", "category_army", "category_special_forces", "category_marines", "category_marines_and_amphibious", "category_special_forces_leg_infantry"},
    "mountaineers": {"category_front_line", "category_light_infantry", "category_all_infantry", "category_army", "category_special_forces", "category_mountaineers", "category_special_forces_leg_infantry"},
    "ranger_battalion": {"category_front_line", "category_light_infantry", "category_all_infantry", "category_army", "category_special_forces", "category_rangers", "category_special_forces_leg_infantry"},
    "paratrooper": {"category_front_line", "category_light_infantry", "category_all_infantry", "category_army", "category_special_forces", "category_paratroopers", "category_special_forces_leg_infantry"},
    "penal_battalion": {"category_front_line", "category_light_infantry", "category_all_infantry", "category_army"},
    "irregular_infantry": {"category_front_line", "category_light_infantry", "category_all_infantry", "category_army"},
    "militia": {"category_front_line", "category_light_infantry", "category_all_infantry", "category_army", "category_militia"},

    "cavalry": {"category_army", "category_cavalry", "category_front_line"},
    "camelry": {"category_army", "category_cavalry", "category_front_line"},
    "elephantry": {"category_army", "category_cavalry", "category_front_line"},
    "motorized": {"category_all_infantry", "category_army", "category_front_line", "category_mobile_and_mobile_combat_sup", "category_vehicle_infantry"},
    "mechanized": {"category_all_infantry", "category_army", "category_front_line", "category_mobile_and_mobile_combat_sup", "category_vehicle_infantry"},
    "amphibious_mechanized": {"category_all_infantry", "category_army", "category_front_line", "category_marines_and_amphibious", "category_mobile_and_mobile_combat_sup", "category_special_forces", "category_vehicle_infantry"},
    "armored_car": {"category_army", "category_front_line", "category_mobile_and_mobile_combat_sup"},

    "artillery_brigade": {"category_army", "category_artillery", "category_line_artillery"},
    "rocket_artillery_brigade": {"category_army", "category_artillery", "category_line_artillery", "category_rocket_artillery"},
    "anti_tank_brigade": {"category_anti_tank", "category_army", "category_front_line", "category_line_artillery"},
    "anti_air_brigade": {"category_anti_air", "category_army", "category_line_artillery"},

    "mot_artillery_brigade": {"category_army", "category_artillery", "category_line_artillery", "category_mobile_and_mobile_combat_sup"},
    "mot_rocket_artillery_brigade": {"category_army", "category_artillery", "category_line_artillery", "category_mobile_and_mobile_combat_sup", "category_rocket_artillery"},
    "mot_anti_tank_brigade": {"category_anti_tank", "category_army", "category_front_line", "category_line_artillery", "category_mobile_and_mobile_combat_sup", "category_mobile_anti_tank"},
    "mot_anti_air_brigade": {"category_anti_air", "category_army", "category_line_artillery", "category_mobile_and_mobile_combat_sup"},

    "light_armor": {"category_all_armor", "category_army", "category_front_line", "category_tanks"},
    "medium_armor": {"category_all_armor", "category_army", "category_front_line", "category_tanks"},
    "heavy_armor": {"category_all_armor", "category_army", "category_front_line", "category_tanks"},
    "modern_armor": {"category_all_armor", "category_army", "category_front_line", "category_tanks"},
    "amphibious_armor": {"category_all_armor", "category_amphibious_tanks", "category_army", "category_front_line", "category_marines_and_amphibious", "category_tanks"},
    "amphibious_light_armor": {"category_all_armor", "category_amphibious_tanks", "category_army", "category_front_line", "category_tanks"},
    "amphibious_medium_armor": {"category_all_armor", "category_amphibious_tanks", "category_army", "category_front_line", "category_tanks"},
    "amphibious_heavy_armor": {"category_all_armor", "category_amphibious_tanks", "category_army", "category_front_line", "category_tanks"},

    "light_tank_destroyer_brigade": {"category_all_armor", "category_army", "category_front_line", "category_tank_destroyers"},
    "medium_tank_destroyer_brigade": {"category_all_armor", "category_army", "category_front_line", "category_tank_destroyers"},
    "heavy_tank_destroyer_brigade": {"category_all_armor", "category_army", "category_front_line", "category_tank_destroyers"},
    "modern_tank_destroyer_brigade": {"category_all_armor", "category_army", "category_front_line", "category_tank_destroyers"},
    "light_sp_artillery_brigade": {"category_all_armor", "category_army", "category_self_propelled_artillery"},
    "medium_sp_artillery_brigade": {"category_all_armor", "category_army", "category_self_propelled_artillery"},
    "heavy_sp_artillery_brigade": {"category_all_armor", "category_army", "category_self_propelled_artillery"},
    "modern_sp_artillery_brigade": {"category_all_armor", "category_army", "category_self_propelled_artillery"},
    "light_sp_anti_air_brigade": {"category_all_armor", "category_army", "category_self_propelled_anti_air"},
    "medium_sp_anti_air_brigade": {"category_all_armor", "category_army", "category_self_propelled_anti_air"},
    "heavy_sp_anti_air_brigade": {"category_all_armor", "category_army", "category_self_propelled_anti_air"},
    "modern_sp_anti_air_brigade": {"category_all_armor", "category_army", "category_self_propelled_anti_air"},

    # --- Support companies (data/support_companies.py) ---
    "recon": {"category_army", "category_divisional_support_battalions", "category_front_line", "category_recon", "category_support_battalions"},
    "mot_recon": {"category_army", "category_divisional_support_battalions", "category_front_line", "category_recon", "category_support_battalions"},
    "armored_car_recon": {"category_army", "category_divisional_support_battalions", "category_front_line", "category_recon", "category_support_battalions"},
    "light_tank_recon": {"category_all_armor", "category_army", "category_divisional_support_battalions", "category_front_line", "category_recon", "category_support_battalions"},
    "airborne_light_armor": {"category_all_armor", "category_army", "category_divisional_support_battalions", "category_front_line", "category_paratroopers", "category_support_battalions"},
    "rangers_support": {"category_army", "category_divisional_support_battalions", "category_front_line", "category_mountaineers", "category_rangers", "category_recon", "category_support_battalions"},
    "northern_territory_recon_support": {"category_army", "category_divisional_support_battalions", "category_front_line", "category_mountaineers", "category_rangers", "category_recon", "category_support_battalions"},
    "long_range_patrol_support": {"category_army", "category_divisional_support_battalions", "category_front_line", "category_recon", "category_support_battalions"},
    "helicopter_recon": {"category_army", "category_divisional_support_battalions", "category_helicopter_support_companies", "category_recon", "category_support_battalions"},
    "winter_logistics_support": {"category_army", "category_divisional_support_battalions", "category_front_line", "category_support_battalions"},

    "engineer": {"category_army", "category_divisional_support_battalions", "category_front_line", "category_support_battalions"},
    "pioneer_support": {"category_army", "category_divisional_support_battalions", "category_front_line", "category_marines", "category_marines_and_amphibious", "category_support_battalions"},
    "jungle_pioneers_support": {"category_army", "category_divisional_support_battalions", "category_support_battalions"},
    "assault_engineer": {"category_all_armor", "category_army", "category_divisional_support_battalions", "category_front_line", "category_support_battalions", "category_tanks"},
    "armored_engineer": {"category_all_armor", "category_army", "category_divisional_support_battalions", "category_front_line", "category_support_battalions", "category_tanks"},

    "signal_company": {"category_army", "category_divisional_support_battalions", "category_support_battalions"},
    "armored_signal": {"category_all_armor", "category_army", "category_divisional_support_battalions", "category_support_battalions", "category_tanks"},

    "field_hospital": {"category_army", "category_divisional_support_battalions", "category_support_battalions"},
    "helicopter_field_hospital": {"category_army", "category_divisional_support_battalions", "category_helicopter_support_companies", "category_support_battalions"},

    "logistics_company": {"category_army", "category_divisional_support_battalions", "category_support_battalions"},
    "helicopter_transport": {"category_army", "category_divisional_support_battalions", "category_helicopter_support_companies", "category_support_battalions"},

    "military_police": {"category_army", "category_divisional_support_battalions", "category_support_battalions"},
    "motorized_military_police": {"category_army", "category_divisional_support_battalions", "category_support_battalions"},

    "maintenance_company": {"category_army", "category_divisional_support_battalions", "category_support_battalions"},
    "armored_maintenance": {"category_all_armor", "category_army", "category_divisional_support_battalions", "category_support_battalions", "category_tanks"},

    "anti_tank": {"category_anti_tank", "category_army", "category_divisional_support_battalions", "category_front_line", "category_mobile_anti_tank", "category_support_battalions"},
    "anti_air": {"category_anti_air", "category_army", "category_divisional_support_battalions", "category_support_battalions"},
    "artillery": {"category_army", "category_artillery", "category_divisional_support_battalions", "category_support_artillery", "category_support_battalions"},
    "rocket_artillery": {"category_army", "category_artillery", "category_divisional_support_battalions", "category_rocket_artillery", "category_support_artillery", "category_support_battalions"},
    "super_heavy_artillery": {"category_army", "category_artillery", "category_divisional_support_battalions", "category_support_artillery", "category_support_battalions"},
    "self_propelled_super_heavy_artillery": {"category_army", "category_artillery", "category_divisional_support_battalions", "category_support_artillery", "category_support_battalions"},

    "light_flame_tank": {"category_all_armor", "category_army", "category_divisional_support_battalions", "category_front_line", "category_support_battalions", "category_tanks"},
    "medium_flame_tank": {"category_all_armor", "category_army", "category_divisional_support_battalions", "category_front_line", "category_support_battalions", "category_tanks"},
    "heavy_flame_tank": {"category_all_armor", "category_army", "category_divisional_support_battalions", "category_front_line", "category_support_battalions", "category_tanks"},

    "super_heavy_armor": {"category_all_armor", "category_army", "category_divisional_support_battalions", "category_front_line", "category_support_battalions", "category_tanks"},
    "land_cruiser": {"category_all_armor", "category_army", "category_divisional_support_battalions", "category_front_line", "category_support_battalions", "category_tanks"},
    "super_heavy_tank_destroyer_brigade": {"category_all_armor", "category_army", "category_divisional_support_battalions", "category_front_line", "category_support_battalions", "category_tank_destroyers"},
    "super_heavy_sp_artillery_brigade": {"category_all_armor", "category_army", "category_divisional_support_battalions", "category_self_propelled_artillery", "category_support_battalions"},
    "super_heavy_sp_anti_air_brigade": {"category_all_armor", "category_army", "category_divisional_support_battalions", "category_self_propelled_anti_air", "category_support_battalions"},

    "helicopter_brigade": {"category_army", "category_divisional_support_battalions", "category_helicopter_support_companies", "category_support_battalions"},

    "sturmtruppe_battalion": {"category_army", "category_divisional_support_battalions", "category_support_battalions"},
    "blackshirt_assault_battalion": {"category_army", "category_divisional_support_battalions", "category_support_battalions"},

    # --- Regimental support (data/regimental_support.py) ---
    "fire_support": {"category_army", "category_regimental_support_battalions", "category_support_battalions"},
    "mot_fire_support": {"category_army", "category_regimental_support_battalions", "category_support_battalions"},
    "field_guns": {"category_army", "category_regimental_support_artillery", "category_regimental_support_battalions", "category_support_battalions"},
    "rocket_battery": {"category_army", "category_regimental_support_artillery", "category_regimental_support_battalions", "category_support_battalions"},
    "anti_air_battery": {"category_anti_air", "category_army", "category_regimental_support_battalions", "category_support_battalions"},
    "anti_tank_battery": {"category_anti_tank", "category_army", "category_front_line", "category_mobile_anti_tank", "category_regimental_support_battalions", "category_support_battalions"},

    "light_tank_destroyer_support": {"category_all_armor", "category_army", "category_front_line", "category_regimental_support_battalions", "category_support_battalions", "category_tank_destroyer_regimental_support"},
    "medium_tank_destroyer_support": {"category_all_armor", "category_army", "category_front_line", "category_regimental_support_battalions", "category_support_battalions", "category_tank_destroyer_regimental_support"},
    "heavy_tank_destroyer_support": {"category_all_armor", "category_army", "category_front_line", "category_regimental_support_battalions", "category_support_battalions", "category_tank_destroyer_regimental_support"},
    "modern_tank_destroyer_support": {"category_all_armor", "category_army", "category_front_line", "category_regimental_support_battalions", "category_support_battalions", "category_tank_destroyer_regimental_support"},

    "light_sp_anti_air_support": {"category_all_armor", "category_army", "category_regimental_support_battalions", "category_self_propelled_anti_air_regimental_support", "category_support_battalions"},
    "medium_sp_anti_air_support": {"category_all_armor", "category_army", "category_regimental_support_battalions", "category_self_propelled_anti_air_regimental_support", "category_support_battalions"},
    "heavy_sp_anti_air_support": {"category_all_armor", "category_army", "category_regimental_support_battalions", "category_self_propelled_anti_air_regimental_support", "category_support_battalions"},
    "modern_sp_anti_air_support": {"category_all_armor", "category_army", "category_regimental_support_battalions", "category_self_propelled_anti_air_regimental_support", "category_support_battalions"},
}
