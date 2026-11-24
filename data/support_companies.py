# Hand-curated from units_copy/*.txt (HOI4 game files), verified 2026-09-13.
# "key" matches the game's own sub_unit identifier.
# "same_support_type" lists the mutual-exclusion group(s) this company
# belongs to, taken directly from the game's own `same_support_type` field:
# entries sharing a group name are alternate flavors of the same slot and
# can't both be picked in one division. Not yet enforced by any picker UI -
# see Specification.md.
#
# Excluded on purpose (both looked like support companies by name, weren't):
# - units_copy/hq_support.txt: the Army HQ staff-officer system (gated by a
#   `required_dlc` flag), not a division support company. Belongs with
#   Expanded_real_stats.md's deferred Army Leadership/Military Staff content.
# - units_copy/fire_support.txt: every entry is tagged
#   category_regimental_support_battalions with divisional = no - that's
#   Regimental Support data, not Support Company data.

SUPPORT_COMPANIES = [
    # Reconnaissance (mutually exclusive with each other via "recon")
    {"key": "recon", "name": "Reconnaissance (Cavalry)", "same_support_type": ["recon"]},
    {"key": "mot_recon", "name": "Reconnaissance (Motorized)", "same_support_type": ["recon"]},
    {"key": "armored_car_recon", "name": "Reconnaissance (Armored Car)", "same_support_type": ["recon"]},
    {"key": "light_tank_recon", "name": "Reconnaissance (Light Tank)", "same_support_type": ["recon"]},
    {"key": "airborne_light_armor", "name": "Reconnaissance (Airborne Light Tank)", "same_support_type": ["recon"]},
    {"key": "rangers_support", "name": "Rangers Support", "same_support_type": ["recon"]},
    {"key": "northern_territory_recon_support", "name": "Northern Territory Recon Support", "same_support_type": ["recon"]},
    {"key": "long_range_patrol_support", "name": "Long-Range Patrol Support", "same_support_type": ["recon"]},
    {"key": "helicopter_recon", "name": "Helicopter Recon", "same_support_type": ["recon", "helicopter_recon"]},
    {"key": "winter_logistics_support", "name": "Winter Logistics Support (Ski Troops)", "same_support_type": []},

    # Engineers (mutually exclusive via "engineer")
    {"key": "engineer", "name": "Engineer Company", "same_support_type": ["engineer"]},
    {"key": "pioneer_support", "name": "Pioneer Support", "same_support_type": ["engineer"]},
    {"key": "jungle_pioneers_support", "name": "Jungle Pioneers Support", "same_support_type": []},
    {"key": "assault_engineer", "name": "Assault Engineer Company", "same_support_type": ["engineer"]},
    {"key": "armored_engineer", "name": "Armored Engineer Company", "same_support_type": ["engineer"]},

    # Signal
    {"key": "signal_company", "name": "Signal Company", "same_support_type": ["signal_company"]},
    {"key": "armored_signal", "name": "Armored Signal Company", "same_support_type": ["signal_company"]},

    # Field hospital
    {"key": "field_hospital", "name": "Field Hospital", "same_support_type": ["field_hospital"]},
    {"key": "helicopter_field_hospital", "name": "Helicopter Field Hospital", "same_support_type": ["field_hospital", "helicopter_field_hospital"]},

    # Logistics
    {"key": "logistics_company", "name": "Logistics Company", "same_support_type": ["logistics_company"]},
    {"key": "helicopter_transport", "name": "Helicopter Transport", "same_support_type": ["logistics_company", "helicopter_transport"]},

    # Military Police
    {"key": "military_police", "name": "Military Police", "same_support_type": ["military_police"]},
    {"key": "motorized_military_police", "name": "Motorized Military Police", "same_support_type": ["military_police"]},

    # Maintenance
    {"key": "maintenance_company", "name": "Maintenance Company", "same_support_type": ["maintenance_company"]},
    {"key": "armored_maintenance", "name": "Armored Maintenance Company", "same_support_type": ["maintenance_company"]},

    # Support-weapon companies
    {"key": "anti_tank", "name": "Anti-Tank", "same_support_type": []},
    {"key": "anti_air", "name": "Anti-Air", "same_support_type": []},
    {"key": "artillery", "name": "Artillery", "same_support_type": []},
    {"key": "rocket_artillery", "name": "Rocket Artillery", "same_support_type": []},
    {"key": "super_heavy_artillery", "name": "Super Heavy Artillery", "same_support_type": ["super_heavy_artillery"]},
    {"key": "self_propelled_super_heavy_artillery", "name": "Self-Propelled Super Heavy Artillery", "same_support_type": ["super_heavy_artillery"]},
    # Elephantry - reclassified from a battalion to a support company in
    # HOI4 1.19.3 (see Activity_Log.md, 2026-09-22); previously in
    # data/battalions.py's "mobile" category.
    {"key": "elephantry", "name": "Elephantry", "same_support_type": []},

    # Flame tanks (mutually exclusive tiers via "flame")
    {"key": "light_flame_tank", "name": "Light Flame Tank", "same_support_type": ["flame"]},
    {"key": "medium_flame_tank", "name": "Medium Flame Tank", "same_support_type": ["flame"]},
    {"key": "heavy_flame_tank", "name": "Heavy Flame Tank", "same_support_type": ["flame"]},

    # Heavy armor / tank-chassis support (too specialized for a full grid column)
    {"key": "super_heavy_armor", "name": "Super Heavy Tank", "same_support_type": []},
    {"key": "land_cruiser", "name": "Land Cruiser", "same_support_type": []},
    {"key": "super_heavy_tank_destroyer_brigade", "name": "Super Heavy Tank Destroyer", "same_support_type": []},
    {"key": "super_heavy_sp_artillery_brigade", "name": "Super Heavy SP Artillery", "same_support_type": []},
    {"key": "super_heavy_sp_anti_air_brigade", "name": "Super Heavy SP Anti-Air", "same_support_type": []},

    # All-purpose helicopter company (overlaps with the helicopter recon/
    # transport/field-hospital variants above - see module comment)
    {"key": "helicopter_brigade", "name": "Helicopter Support Company", "same_support_type": ["helicopter_recon", "helicopter_transport", "helicopter_field_hospital"]},

    # Nation-flavor infantry support (Germany, Italy)
    {"key": "sturmtruppe_battalion", "name": "Sturmtruppen", "same_support_type": []},
    {"key": "blackshirt_assault_battalion", "name": "Blackshirt Assault Battalion", "same_support_type": []},
]
