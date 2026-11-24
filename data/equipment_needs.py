# Hand-curated from units_copy/*.txt (HOI4 game files), verified 2026-09-14.
# Each key here is a battalion/support-company/regimental-support "key" from
# data/battalions.py, data/support_companies.py, or data/regimental_support.py
# (those three key spaces don't overlap, so one flat dict is fine). The value
# is that item's own `need` block: which equipment (data/equipment.py keys)
# it requires, and how much of each.
#
# This is what was missing to actually compute stats: data/equipment.py has
# the per-unit stats, but Stats needs quantity too (e.g. Infantry uses 100
# Infantry Equipment, not 1) to scale them correctly.

EQUIPMENT_NEEDS = {
    # Battalions - Infantry category
    "infantry": {"infantry_equipment": 100},
    "bicycle_battalion": {"infantry_equipment": 100, "support_equipment": 5},  # (1.19.4) 10->5
    "marine": {"infantry_equipment": 150},
    "marine_commando": {"infantry_equipment": 150},
    "mountaineers": {"infantry_equipment": 140},
    "ranger_battalion": {"infantry_equipment": 140},
    "paratrooper": {"infantry_equipment": 130},
    "penal_battalion": {"infantry_equipment": 85},
    "irregular_infantry": {"infantry_equipment": 80},
    "militia": {"infantry_equipment": 100},

    # Battalions - Mobile category
    "cavalry": {"infantry_equipment": 120},
    "camelry": {"infantry_equipment": 150},
    "elephantry": {"infantry_equipment": 260, "artillery_equipment": 30},
    "motorized": {"infantry_equipment": 100, "motorized_equipment": 35},
    "mechanized": {"infantry_equipment": 100, "mechanized_equipment": 40},
    "amphibious_mechanized": {"infantry_equipment": 100, "amphibious_mechanized_equipment": 50},
    "armored_car": {"armored_car_equipment": 60},

    # Battalions - Combat Support category
    "artillery_brigade": {"artillery_equipment": 24},
    "rocket_artillery_brigade": {"rocket_artillery_equipment": 24},
    "anti_tank_brigade": {"anti_tank_equipment": 36},
    "anti_air_brigade": {"anti_air_equipment": 36},

    # Battalions - Mobile Combat Support category
    "mot_artillery_brigade": {"artillery_equipment": 24, "motorized_equipment": 36},
    "mot_rocket_artillery_brigade": {"rocket_artillery_equipment": 24, "motorized_equipment": 36},
    "mot_anti_tank_brigade": {"anti_tank_equipment": 36, "motorized_equipment": 36},
    "mot_anti_air_brigade": {"anti_air_equipment": 36, "motorized_equipment": 36},

    # Battalions - Armor category
    "light_armor": {"light_tank_chassis": 60},
    "medium_armor": {"medium_tank_chassis": 50},
    "heavy_armor": {"heavy_tank_chassis": 40},
    "modern_armor": {"modern_tank_chassis": 50},
    "amphibious_armor": {"amphibious_tank_chassis": 50},
    "amphibious_light_armor": {"light_tank_amphibious_chassis": 50},
    "amphibious_medium_armor": {"medium_tank_amphibious_chassis": 50},
    "amphibious_heavy_armor": {"heavy_tank_amphibious_chassis": 50},

    # Battalions - Armored Combat Support category
    "light_tank_destroyer_brigade": {"light_tank_destroyer_chassis": 40},
    "medium_tank_destroyer_brigade": {"medium_tank_destroyer_chassis": 40},
    "heavy_tank_destroyer_brigade": {"heavy_tank_destroyer_chassis": 40},
    "modern_tank_destroyer_brigade": {"modern_tank_destroyer_chassis": 40},
    "light_sp_artillery_brigade": {"light_tank_artillery_chassis": 40},
    "medium_sp_artillery_brigade": {"medium_tank_artillery_chassis": 40},
    "heavy_sp_artillery_brigade": {"heavy_tank_artillery_chassis": 40},
    "modern_sp_artillery_brigade": {"modern_tank_artillery_chassis": 40},
    "light_sp_anti_air_brigade": {"light_tank_aa_chassis": 40},
    "medium_sp_anti_air_brigade": {"medium_tank_aa_chassis": 40},
    "heavy_sp_anti_air_brigade": {"heavy_tank_aa_chassis": 40},
    "modern_sp_anti_air_brigade": {"modern_tank_aa_chassis": 40},

    # Support companies - Reconnaissance
    "recon": {"infantry_equipment": 40, "support_equipment": 10},
    "mot_recon": {"infantry_equipment": 40, "support_equipment": 10, "motorized_equipment": 20},
    "armored_car_recon": {"armored_car_equipment": 24},
    "light_tank_recon": {"light_tank_chassis": 24},
    "airborne_light_armor": {"light_tank_chassis": 24},
    "rangers_support": {"infantry_equipment": 40, "support_equipment": 15},
    "northern_territory_recon_support": {"infantry_equipment": 20, "support_equipment": 10},
    "winter_logistics_support": {"infantry_equipment": 40, "support_equipment": 10},
    "long_range_patrol_support": {"infantry_equipment": 40, "support_equipment": 10},
    "helicopter_recon": {"helicopter_equipment": 20, "support_equipment": 10},

    # Support companies - Signal
    "signal_company": {"support_equipment": 20, "motorized_equipment": 10},
    "armored_signal": {"support_equipment": 15, "armored_support_vehicle": 20},

    # Support companies - Engineers
    "engineer": {"infantry_equipment": 10, "support_equipment": 30},
    "pioneer_support": {"infantry_equipment": 10, "support_equipment": 40},
    "jungle_pioneers_support": {"infantry_equipment": 10, "support_equipment": 40},
    "assault_engineer": {"armored_support_vehicle": 20, "support_equipment": 20},
    "armored_engineer": {"armored_support_vehicle": 30, "support_equipment": 15},

    # Support companies - Field hospital
    "field_hospital": {"support_equipment": 30, "motorized_equipment": 20},
    "helicopter_field_hospital": {"support_equipment": 30, "helicopter_equipment": 15, "motorized_equipment": 15},

    # Support companies - Logistics
    "logistics_company": {"support_equipment": 20, "motorized_equipment": 10},
    "helicopter_transport": {"support_equipment": 20, "helicopter_equipment": 10, "motorized_equipment": 10},

    # Support companies - Military Police
    "military_police": {"support_equipment": 10, "infantry_equipment": 40},
    "motorized_military_police": {"support_equipment": 5, "infantry_equipment": 20, "motorbike_equipment": 20},

    # Support companies - Maintenance
    "maintenance_company": {"support_equipment": 25},
    "armored_maintenance": {"support_equipment": 15, "armored_support_vehicle": 20},

    # Support companies - Support-weapon companies
    "anti_tank": {"anti_tank_equipment": 24},
    "anti_air": {"anti_air_equipment": 24},
    "artillery": {"artillery_equipment": 12},
    "rocket_artillery": {"rocket_artillery_equipment": 12},
    "super_heavy_artillery": {"super_heavy_artillery_equipment": 3},
    "self_propelled_super_heavy_artillery": {"self_propelled_super_heavy_artillery_equipment": 3},

    # Support companies - Flame tanks
    "light_flame_tank": {"light_tank_flame_chassis": 15},
    "medium_flame_tank": {"medium_tank_flame_chassis": 15},
    "heavy_flame_tank": {"heavy_tank_flame_chassis": 15},

    # Support companies - Heavy armor / tank-chassis support
    "super_heavy_armor": {"super_heavy_tank_chassis": 20},
    "land_cruiser": {"land_cruiser_chassis": 1},
    "super_heavy_tank_destroyer_brigade": {"super_heavy_tank_destroyer_chassis": 20},
    "super_heavy_sp_artillery_brigade": {"super_heavy_tank_artillery_chassis": 20},
    "super_heavy_sp_anti_air_brigade": {"super_heavy_tank_aa_chassis": 20},

    # Support companies - Helicopter / nation-flavor infantry
    "helicopter_brigade": {"helicopter_equipment": 15, "support_equipment": 15},
    "sturmtruppe_battalion": {"infantry_equipment": 150, "support_equipment": 10},
    "blackshirt_assault_battalion": {"infantry_equipment": 100, "support_equipment": 10},

    # Regimental support - Fire Support group
    "fire_support": {"infantry_equipment": 30, "support_equipment": 5},
    "mot_fire_support": {"infantry_equipment": 30, "support_equipment": 5, "motorized_equipment": 5},
    "field_guns": {"artillery_equipment": 6},
    "rocket_battery": {"rocket_artillery_equipment": 6},
    "anti_air_battery": {"anti_air_equipment": 16},
    "anti_tank_battery": {"anti_tank_equipment": 16},

    # Regimental support - Tank Destroyer Support
    "light_tank_destroyer_support": {"light_tank_destroyer_chassis": 15},
    "medium_tank_destroyer_support": {"medium_tank_destroyer_chassis": 15},
    "heavy_tank_destroyer_support": {"heavy_tank_destroyer_chassis": 15},
    "modern_tank_destroyer_support": {"modern_tank_destroyer_chassis": 15},

    # Regimental support - SP Anti-Air Support
    "light_sp_anti_air_support": {"light_tank_aa_chassis": 15},
    "medium_sp_anti_air_support": {"medium_tank_aa_chassis": 15},
    "heavy_sp_anti_air_support": {"heavy_tank_aa_chassis": 15},
    "modern_sp_anti_air_support": {"modern_tank_aa_chassis": 15},
}
