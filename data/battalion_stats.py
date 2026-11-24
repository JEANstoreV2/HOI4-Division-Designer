# Hand-curated from units_copy/*.txt (HOI4 game files), reconstructed
# 2026-09-14 from the same reads already done to build data/battalions.py,
# data/support_companies.py, and data/regimental_support.py (not fresh
# file reads) - treat as a first pass worth spot-checking against
# units_copy/ if a specific number ever looks wrong.
#
# combat_width and max_speed (added 2026-09-14, after cross-checking real
# division-designer screenshots against fresh units_copy/ reads) are the
# exception - fully verified against a real division for every non-armor
# battalion except one:
# - combat_width is a direct per-unit field for every entry that has one.
# - max_speed for infantry/mounted-type units (no "transport" field) is
#   4.0 km/h (HOI4's base leg-infantry speed) times (1 + the unit's own
#   "maximum_speed" field, if it has one) - confirmed exactly against
#   Infantry, Cavalry, Mountaineers, and Paratrooper screenshots.
# - max_speed for vehicle-transported units (motorized/mechanized/
#   amphibious_mechanized/mot_* brigades) equals their transport
#   equipment's own max_speed at tier 1 - confirmed exactly against
#   Motorised and Mechanised screenshots.
# - armored_car's max_speed (12.0) follows the same equipment-tier pattern
#   as the above but has no "transport" field in its own sub_unit entry to
#   confirm it derives from armored_car_equipment the same way - predicted,
#   not screenshot-confirmed.
# - Armor/Armored Combat Support (tank-chassis categories) got their
#   combat_width filled in on 2026-09-16 (see below) after Ollie found the
#   real bug this caused: it's a direct per-battalion field, same as every
#   other battalion, and never actually depended on the Tank Designer being
#   done - the original 2026-09-14 deferral lumped it in with max_speed,
#   which genuinely does need Tank Designer's chassis data (a tank's
#   max_speed comes from its equipped chassis, unlike combat_width). Only
#   max_speed for these categories remains an open gap.
#
# Keyed the same way as data/equipment_needs.py: one flat dict, keyed by
# each item's own "key" from battalions/support_companies/regimental_support.
#
# Each entry holds:
# - structural stats: max_strength, max_organisation, default_morale,
#   manpower, training_time, weight, supply_consumption, suppression,
#   combat_width, max_speed
# - suppression_factor: a percentage bonus to division Suppression (not a
#   flat stat like suppression above) - confirmed against the Military
#   Police screenshot exactly (10.5 base suppression x 0.20 = the +2.1
#   jump seen once Military Police was added). Rare: only Military Police
#   variants and the deferred HQ Support system use it anywhere in
#   units_copy/.
# - combat stats defined directly on the sub_unit itself (as opposed to
#   coming from its equipment, which lives in data/equipment.py): soft_attack,
#   hard_attack, defense, breakthrough, ap_attack, air_attack, armor_value
# - battalion_mult (added 2026-10-08): a unit's own innate aura, granting a
#   bonus to every OTHER item in the division belonging to a given category
#   (e.g. Pioneer Support's own `{category_marines: {breakthrough: 0.15}}` -
#   the real source of the Breakthrough gap found and confirmed this
#   session, see Activity_Log.md). `[]` on every entry without one via the
#   setdefault loop at the end of this file; the 21 real entries (23 blocks
#   - armored_engineer and motorized_military_police each have two) are
#   compiled directly from every `battalion_mult = { ... }` block found
#   across units_copy/*.txt, cross-checked against the owning item's own
#   compiled key. An `"add": True` key (present only when the source has an
#   active, uncommented `add = yes`) means the field is a flat add; absent
#   means percentage - see logic/stats.py's battalion_mult application for
#   the full rule, the same `add`-flag convention Doctrine's and
#   Technology's own already-compiled battalion_mult entries
#   (data/doctrines.py, data/technologies.py) already use.
#
# Deliberately excluded (only a field actually present in the source is
# included at all - nothing is padded with a 0 to fill a gap):
# - Terrain modifiers - a separate Stats component, not started yet.
# - Niche mechanic-only fields not in Intial_problem.md's own stat list
#   (recon, entrenchment, initiative, casualty_trickleback,
#   experience_loss_factor, acclimatization_*, reliability_factor,
#   equipment_capture_factor, recovery, etc.). suppression_factor is the
#   one exception - included where present (see above) once we found it's
#   actually needed to reproduce Suppression correctly.
# - Values that were present in the file but commented out with `#`
#   (e.g. super_heavy_armor's nerf block is entirely commented out in
#   units_copy/super_heavy_armor.txt, so it has no combat stat overrides
#   here either).

BATTALION_STATS = {
    # Battalions - Infantry
    "infantry": {
        "max_strength": 25, "max_organisation": 60, "default_morale": 0.3,
        "manpower": 1000, "training_time": 90, "suppression": 1.5,
        "weight": 0.5, "supply_consumption": 0.06,
        "combat_width": 2, "max_speed": 4.0,
    },
    "bicycle_battalion": {
        "max_strength": 25, "max_organisation": 60, "default_morale": 0.3,
        "manpower": 1000, "training_time": 90, "suppression": 2,
        "weight": 0.5, "supply_consumption": 0.06,
        "combat_width": 2, "max_speed": 6.4,
    },
    "marine": {
        "max_strength": 20, "max_organisation": 70, "default_morale": 0.4,
        "manpower": 1000, "training_time": 120, "suppression": 1,
        "weight": 0.5, "supply_consumption": 0.05, "breakthrough": 0.3,
        "combat_width": 2, "max_speed": 4.0,
    },
    "marine_commando": {
        "max_strength": 20, "max_organisation": 70, "default_morale": 0.4,
        "manpower": 1000, "training_time": 120, "suppression": 1,
        "weight": 0.5, "supply_consumption": 0.05, "breakthrough": 0.3,
        "combat_width": 2, "max_speed": 4.0,
    },
    "mountaineers": {
        "max_strength": 20, "max_organisation": 70, "default_morale": 0.4,
        "manpower": 1000, "training_time": 120, "suppression": 1,
        "weight": 0.5, "supply_consumption": 0.05, "breakthrough": 0.3,
        "combat_width": 2, "max_speed": 4.0,
    },
    "ranger_battalion": {
        "max_strength": 20, "max_organisation": 70, "default_morale": 0.4,
        "manpower": 1000, "training_time": 120, "suppression": 1,
        "weight": 0.5, "supply_consumption": 0.05, "breakthrough": 0.3,
        "combat_width": 2, "max_speed": 4.0,
    },
    "paratrooper": {
        "max_strength": 22, "max_organisation": 70, "default_morale": 0.4,
        "manpower": 1000, "training_time": 150, "suppression": 1,
        "weight": 0.5, "supply_consumption": 0.05,
        "combat_width": 2, "max_speed": 4.0,
    },
    "penal_battalion": {
        "max_strength": 15, "max_organisation": 70, "default_morale": 0.4,
        "manpower": 850, "training_time": 50, "suppression": 0.5,
        "weight": 0.5, "supply_consumption": 0.05,
        "combat_width": 2, "max_speed": 4.0,
    },
    "irregular_infantry": {
        "max_strength": 30, "max_organisation": 45, "default_morale": 0.2,
        "manpower": 1000, "training_time": 30, "suppression": 1.5,
        "weight": 0.5, "supply_consumption": 0.04,
        "soft_attack": -0.05, "defense": -0.15,
        "combat_width": 2, "max_speed": 4.0,
    },
    "militia": {
        "max_strength": 25, "max_organisation": 50, "default_morale": 0.3,
        "manpower": 1000, "training_time": 80, "suppression": 1.5,
        "weight": 0.5, "supply_consumption": 0.06,
        "combat_width": 2, "max_speed": 4.0,
    },

    # Battalions - Mobile
    "cavalry": {
        "max_strength": 25, "max_organisation": 70, "default_morale": 0.3,
        "manpower": 1000, "training_time": 120, "suppression": 2,
        "weight": 0.5, "supply_consumption": 0.06,
        "breakthrough": 0.2,  # (1.19.4) new - own field, % of equipment per the Mountaineers precedent
        "combat_width": 2, "max_speed": 6.4,
    },
    "camelry": {
        "max_strength": 30, "max_organisation": 70, "default_morale": 0.3,
        "manpower": 1000, "training_time": 160, "suppression": 2,
        "weight": 0.6, "supply_consumption": 0.1,
        "combat_width": 2, "max_speed": 5.6,
    },
    "motorized": {
        "max_strength": 27.5,  # (1.19.4) 25->27.5
        "max_organisation": 60, "default_morale": 0.30,
        "manpower": 1200, "training_time": 90, "suppression": 2.2,
        "weight": 0.75, "supply_consumption": 0.065,
        "combat_width": 2, "max_speed": 12.0,
    },
    "mechanized": {
        "max_strength": 30, "max_organisation": 60, "default_morale": 0.3,
        "manpower": 1200, "training_time": 120, "suppression": 2,
        "weight": 1, "supply_consumption": 0.14,
        "hard_attack": 4.0,  # (1.19.4) own +10% soft_attack bonus removed
        "combat_width": 2, "max_speed": 8.0,
    },
    "amphibious_mechanized": {
        "max_strength": 30, "max_organisation": 60, "default_morale": 0.3,
        "manpower": 1200, "training_time": 120, "suppression": 1,
        "weight": 1, "supply_consumption": 0.18,
        "hard_attack": 0.5,  # (1.19.4) own +10% soft_attack bonus removed
        "combat_width": 2, "max_speed": 7.0,
    },
    "armored_car": {
        "max_strength": 5, "max_organisation": 20, "default_morale": 0.3,
        "manpower": 500, "training_time": 180, "suppression": 2.5,
        "weight": 0.8, "supply_consumption": 0.14,
        "combat_width": 2, "max_speed": 12.0,  # predicted from armored_car_equipment's tier-1 value; not yet confirmed by a real screenshot
    },

    # Battalions - Combat Support
    "artillery_brigade": {
        "max_strength": 0.6, "max_organisation": 0, "default_morale": 0.1,
        "manpower": 500, "training_time": 120,
        "weight": 0.5, "supply_consumption": 0.21,
        "combat_width": 3, "max_speed": 4.0,
    },
    "rocket_artillery_brigade": {
        "max_strength": 0.6, "max_organisation": 0, "default_morale": 0.1,
        "manpower": 500, "training_time": 120,
        "weight": 0.5, "supply_consumption": 0.22,
        "combat_width": 3, "max_speed": 4.0,
    },
    "anti_tank_brigade": {
        "max_strength": 0.6, "max_organisation": 0, "default_morale": 0,
        "manpower": 500, "training_time": 120,
        "weight": 0.5, "supply_consumption": 0.1,
        "combat_width": 1, "max_speed": 4.0,
    },
    "anti_air_brigade": {
        "max_strength": 0.6, "max_organisation": 0, "default_morale": 0.1,
        "manpower": 500, "training_time": 120,
        "weight": 0.5, "supply_consumption": 0.1,
        "combat_width": 1, "max_speed": 4.0,
    },

    # Battalions - Mobile Combat Support
    "mot_artillery_brigade": {
        "max_strength": 0.6, "max_organisation": 0, "default_morale": 0.1,
        "manpower": 500, "training_time": 120,
        "weight": 0.5, "supply_consumption": 0.25,
        "combat_width": 3, "max_speed": 12.0,
    },
    "mot_rocket_artillery_brigade": {
        "max_strength": 0.6, "max_organisation": 0, "default_morale": 0.1,
        "manpower": 500, "training_time": 120,
        "weight": 0.5, "supply_consumption": 0.25,
        "combat_width": 3, "max_speed": 12.0,
    },
    "mot_anti_tank_brigade": {
        "max_strength": 0.6, "max_organisation": 0, "default_morale": 0,
        "manpower": 500, "training_time": 120,
        "weight": 0.5, "supply_consumption": 0.15,
        "combat_width": 1, "max_speed": 12.0,
    },
    "mot_anti_air_brigade": {
        "max_strength": 0.6, "max_organisation": 0, "default_morale": 0.1,
        "manpower": 500, "training_time": 120,
        "weight": 0.5, "supply_consumption": 0.15,
        "combat_width": 1, "max_speed": 12.0,
    },

    # Battalions - Armor. combat_width added 2026-09-16, direct from
    # units_copy/{light,medium,heavy,modern,amphibious}_armor.txt - all 8
    # entries are combat_width = 2 in the source, no exceptions.
    "light_armor": {
        "max_strength": 2, "max_organisation": 10, "default_morale": 0.3,
        "manpower": 500, "training_time": 180, "suppression": 2.5,
        "weight": 1, "supply_consumption": 0.22, "breakthrough": 0.15,
        "combat_width": 2,
    },
    "medium_armor": {
        "max_strength": 2, "max_organisation": 10, "default_morale": 0.3,
        "manpower": 500, "training_time": 180, "suppression": 2.5,
        "weight": 1.25, "supply_consumption": 0.25, "breakthrough": 0.15,
        "combat_width": 2,
    },
    "heavy_armor": {
        "max_strength": 2, "max_organisation": 10, "default_morale": 0.3,
        "manpower": 500, "training_time": 180, "suppression": 2.5,
        "weight": 1.5, "supply_consumption": 0.32, "breakthrough": 0.15,
        "combat_width": 2,
    },
    "modern_armor": {
        "max_strength": 2, "max_organisation": 10, "default_morale": 0.3,
        "manpower": 500, "training_time": 180, "suppression": 2.5,
        "weight": 1.5, "supply_consumption": 0.25, "breakthrough": 0.15,
        "combat_width": 2,
    },
    "amphibious_armor": {
        "max_strength": 2, "max_organisation": 10, "default_morale": 0.3,
        "manpower": 500, "training_time": 180,
        "weight": 1, "supply_consumption": 0.2,
        "combat_width": 2,
    },
    "amphibious_light_armor": {
        "max_strength": 2, "max_organisation": 10, "default_morale": 0.3,
        "manpower": 500, "training_time": 180,
        "weight": 1, "supply_consumption": 0.2,
        "combat_width": 2,
    },
    "amphibious_medium_armor": {
        "max_strength": 2, "max_organisation": 10, "default_morale": 0.3,
        "manpower": 500, "training_time": 180,
        "weight": 1, "supply_consumption": 0.2,
        "combat_width": 2,
    },
    "amphibious_heavy_armor": {
        "max_strength": 2, "max_organisation": 10, "default_morale": 0.3,
        "manpower": 500, "training_time": 180,
        "weight": 1, "supply_consumption": 0.2,
        "combat_width": 2,
    },

    # Battalions - Armored Combat Support. combat_width added 2026-09-16,
    # direct from units_copy/{tank_destroyer,sp_artillery,sp_anti-air}_brigade.txt
    # - all 12 entries are combat_width = 2 in the source (their super_heavy
    # siblings are support companies, not battalions, and correctly have no
    # combat_width at all - see data/support_companies.py; same for every
    # "_support" regimental variant of these keys, also correctly absent).
    "light_tank_destroyer_brigade": {
        "max_strength": 0.5, "max_organisation": 0, "default_morale": 0.3,
        "manpower": 500, "training_time": 180, "suppression": 1.0,
        "weight": 1, "supply_consumption": 0.2,
        "breakthrough": -0.42, "ap_attack": 0.15,
        "combat_width": 2,
    },
    "medium_tank_destroyer_brigade": {
        "max_strength": 0.5, "max_organisation": 0, "default_morale": 0.3,
        "manpower": 500, "training_time": 180, "suppression": 1.25,
        "weight": 1.25, "supply_consumption": 0.22,
        "breakthrough": -0.25, "ap_attack": 0.15,
        "combat_width": 2,
    },
    "heavy_tank_destroyer_brigade": {
        "max_strength": 0.5, "max_organisation": 0, "default_morale": 0.3,
        "manpower": 500, "training_time": 180, "suppression": 1.25,
        "weight": 1.5, "supply_consumption": 0.3,
        "breakthrough": -0.25, "ap_attack": 0.15,
        "combat_width": 2,
    },
    "modern_tank_destroyer_brigade": {
        "max_strength": 0.5, "max_organisation": 0, "default_morale": 0.3,
        "manpower": 500, "training_time": 180, "suppression": 1.25,
        "weight": 1.5, "supply_consumption": 0.25,
        "breakthrough": -0.25, "ap_attack": 0.15,
        "combat_width": 2,
    },
    "light_sp_artillery_brigade": {
        "max_strength": 0.5, "max_organisation": 0, "default_morale": 0.1,
        "manpower": 500, "training_time": 180, "suppression": 1.25,
        "weight": 1, "supply_consumption": 0.42,
        "breakthrough": -0.42, "soft_attack": 0.15,
        "combat_width": 2,
    },
    "medium_sp_artillery_brigade": {
        "max_strength": 0.5, "max_organisation": 0, "default_morale": 0.1,
        "manpower": 500, "training_time": 180, "suppression": 1.5,
        "weight": 1.25, "supply_consumption": 0.46,
        "breakthrough": -0.25, "soft_attack": 0.15,
        "combat_width": 2,
    },
    "heavy_sp_artillery_brigade": {
        "max_strength": 0.5, "max_organisation": 0, "default_morale": 0.1,
        "manpower": 500, "training_time": 180, "suppression": 1.5,
        "weight": 1.5, "supply_consumption": 0.6,
        "breakthrough": -0.25, "soft_attack": 0.15,
        "combat_width": 2,
    },
    "modern_sp_artillery_brigade": {
        "max_strength": 0.5, "max_organisation": 0, "default_morale": 0.1,
        "manpower": 500, "training_time": 180, "suppression": 1.5,
        "weight": 1.5, "supply_consumption": 0.5,
        "breakthrough": -0.25, "soft_attack": 0.15,
        "combat_width": 2,
    },
    "light_sp_anti_air_brigade": {
        "max_strength": 0.5, "max_organisation": 0, "default_morale": 0.1,
        "manpower": 500, "training_time": 180, "suppression": 0.75,
        "weight": 1, "supply_consumption": 0.1,
        "breakthrough": -0.55, "air_attack": 0.15,
        "combat_width": 2,
    },
    "medium_sp_anti_air_brigade": {
        "max_strength": 0.5, "max_organisation": 0, "default_morale": 0.1,
        "manpower": 500, "training_time": 180, "suppression": 0.8,
        "weight": 1.25, "supply_consumption": 0.1,
        "breakthrough": -0.53, "air_attack": 0.15,
        "combat_width": 2,
    },
    "heavy_sp_anti_air_brigade": {
        "max_strength": 0.5, "max_organisation": 0, "default_morale": 0.1,
        "manpower": 500, "training_time": 180, "suppression": 0.75,
        "weight": 1.5, "supply_consumption": 0.1,
        "breakthrough": -0.35, "air_attack": 0.15,
        "combat_width": 2,
    },
    "modern_sp_anti_air_brigade": {
        "max_strength": 0.5, "max_organisation": 0, "default_morale": 0.1,
        "manpower": 500, "training_time": 180, "suppression": 2,
        "weight": 1.5, "supply_consumption": 0.1,
        "breakthrough": -0.53, "air_attack": 0.15,
        "combat_width": 2,
    },

    # Support companies - Reconnaissance
    "recon": {
        "max_strength": 2, "max_organisation": 20, "default_morale": 0.3,
        "manpower": 500, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.02,
        "defense": -0.5, "breakthrough": -0.5, "soft_attack": -0.9, "hard_attack": -0.9,
    },
    "mot_recon": {
        "max_strength": 2, "max_organisation": 20, "default_morale": 0.3,
        "manpower": 500, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.02,
        "defense": -0.09, "breakthrough": -0.5, "soft_attack": -0.9, "hard_attack": -0.9,
    },
    "armored_car_recon": {
        "max_strength": 2, "max_organisation": 20, "default_morale": 0.3,
        "manpower": 500, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.02,
        "defense": -0.5, "breakthrough": -0.2, "soft_attack": -0.5, "hard_attack": -0.5,
    },
    "light_tank_recon": {
        "max_strength": 2, "max_organisation": 20, "default_morale": 0.3,
        "manpower": 500, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.02,
        "defense": -0.6, "breakthrough": -0.6, "soft_attack": -0.6,
        "hard_attack": -0.6, "armor_value": -0.6,
    },
    "airborne_light_armor": {
        "max_strength": 2, "max_organisation": 20, "default_morale": 0.3,
        "manpower": 500, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.02,
        "defense": -0.5, "breakthrough": -0.25, "soft_attack": -0.25,
        "hard_attack": -0.25, "armor_value": -0.5,
    },
    "rangers_support": {
        "max_strength": 2, "max_organisation": 30, "default_morale": 0.3,
        "manpower": 500, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.06,
    },
    "northern_territory_recon_support": {
        "max_strength": 2, "max_organisation": 30, "default_morale": 0.3,
        "manpower": 500, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.04,
    },
    "winter_logistics_support": {
        "max_strength": 2, "max_organisation": 45, "default_morale": 0.3,
        "manpower": 500, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.05,
        "breakthrough": -0.5, "soft_attack": -0.5, "hard_attack": -0.5, "armor_value": -0.5,
    },
    "long_range_patrol_support": {
        "max_strength": 10, "max_organisation": 60, "default_morale": 0.3,
        "manpower": 500, "training_time": 120,
        "weight": 0.3, "supply_consumption": 0.04,
        "soft_attack": 0.1, "breakthrough": 0.3,
    },
    "helicopter_recon": {
        "max_strength": 2, "max_organisation": 20, "default_morale": 0.3,
        "manpower": 500, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.070,
    },

    # Support companies - Signal
    "signal_company": {
        "max_strength": 1, "max_organisation": 20, "default_morale": 0.3,
        "manpower": 500, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.02,
    },
    "armored_signal": {
        "max_strength": 1, "max_organisation": 20, "default_morale": 0.3,
        "manpower": 500, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.035,
    },

    # Support companies - Engineers
    "engineer": {
        "max_strength": 2, "max_organisation": 20, "default_morale": 0.3,
        "manpower": 300, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.02,
        "defense": 0.1, "breakthrough": 0.5, "soft_attack": -0.5,
    },
    "pioneer_support": {
        "max_strength": 2, "max_organisation": 20, "default_morale": 0.3,
        "manpower": 300, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.02,
        "defense": 0.1, "breakthrough": 0.5, "soft_attack": -0.5,
    },
    "jungle_pioneers_support": {
        "max_strength": 1, "max_organisation": 30, "default_morale": 0.3,
        "manpower": 500, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.1,
        "defense": 0.05, "breakthrough": 0.3,
    },
    "assault_engineer": {
        "max_strength": 2, "max_organisation": 20, "default_morale": 0.3,
        "manpower": 300, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.025,
        "defense": 0.1, "breakthrough": 1.5, "soft_attack": -0.5,
    },
    "armored_engineer": {
        "max_strength": 2, "max_organisation": 20, "default_morale": 0.3,
        "manpower": 300, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.035,
        "defense": 0.15, "breakthrough": 1, "soft_attack": -0.5,
    },

    # Support companies - Field hospital
    "field_hospital": {
        "max_strength": 2, "max_organisation": 20, "default_morale": 0.3,
        "manpower": 500, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.05,
    },
    "helicopter_field_hospital": {
        "max_strength": 2, "max_organisation": 20, "default_morale": 0.3,
        "manpower": 500, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.070,
    },

    # Support companies - Logistics
    "logistics_company": {
        "max_strength": 1, "max_organisation": 10, "default_morale": 0.3,
        "manpower": 500, "training_time": 120, "weight": 0.1,
        # Own innate reduction, confirmed via its tech tooltip
        # (Template Examples/LogisticsCompany1.png - "Supply Usage: -10.00%",
        # "Fuel Usage: -5.00%") - previously missing entirely since nothing
        # tracked "_factor"-suffixed fields until the 2026-09-30 Technology
        # stat bonuses investigation. supply_consumption_factor is applied
        # (see logic/stats.py); fuel_consumption_factor stays compiled here
        # for faithfulness but unapplied - no fuel_consumption division stat
        # exists to multiply, same as every other untracked field.
        "supply_consumption_factor": -0.10, "fuel_consumption_factor": -0.05,
    },
    "helicopter_transport": {
        "max_strength": 1, "max_organisation": 12, "default_morale": 0.3,
        "manpower": 500, "training_time": 120, "weight": 0.1,
    },

    # Support companies - Military Police
    "military_police": {
        "max_strength": 1, "max_organisation": 0, "default_morale": 0.3,
        "manpower": 500, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.02,
        "suppression_factor": 0.20,
    },
    "motorized_military_police": {
        "max_strength": 2, "max_organisation": 10, "default_morale": 0.3,
        "manpower": 500, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.03,
        "suppression_factor": 0.30,
    },

    # Support companies - Maintenance
    "maintenance_company": {
        "max_strength": 1, "max_organisation": 20, "default_morale": 0.3,
        "manpower": 500, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.03,
    },
    "armored_maintenance": {
        "max_strength": 1, "max_organisation": 20, "default_morale": 0.3,
        "manpower": 500, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.035,
    },

    # Support companies - Support-weapon companies
    "anti_tank": {
        "max_strength": 0.2, "max_organisation": 0, "default_morale": 0.1,
        "manpower": 300, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.08,
        "defense": -0.4, "breakthrough": -0.4, "soft_attack": -0.4,
        "hard_attack": -0.5, "ap_attack": -0.15,
    },
    "anti_air": {
        "max_strength": 0.2, "max_organisation": 0, "default_morale": 0.1,
        "manpower": 300, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.1,
        "defense": -0.4, "breakthrough": -0.4, "soft_attack": -0.4,
        "hard_attack": -0.4, "air_attack": -0.2,
    },
    "artillery": {
        "max_strength": 0.2, "max_organisation": 0, "default_morale": 0.1,
        "manpower": 300, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.16,
        "defense": -0.5, "breakthrough": -0.5, "soft_attack": -0.5, "hard_attack": -0.5,
    },
    "rocket_artillery": {
        "max_strength": 0.2, "max_organisation": 0, "default_morale": 0.1,
        "manpower": 300, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.16,
        "defense": -0.5, "breakthrough": -0.5, "soft_attack": -0.5, "hard_attack": -0.5,
    },
    # Reclassified from a battalion to a support company in HOI4 1.19.3
    # (see Activity_Log.md, 2026-09-22) - dropped combat_width/max_speed
    # accordingly, since support companies don't occupy combat width.
    "elephantry": {
        "max_strength": 30, "max_organisation": 55, "default_morale": 0.25,
        "manpower": 1100, "training_time": 210, "suppression": 2.3,
        "weight": 1.2, "supply_consumption": 0.12,
        "soft_attack": -0.25, "hard_attack": -0.15, "breakthrough": 0.3,
    },
    "super_heavy_artillery": {
        "max_strength": 0.2, "max_organisation": 0, "default_morale": 0.1,
        "manpower": 1000, "training_time": 180,
        "weight": 0.1, "supply_consumption": 0.25,
    },
    "self_propelled_super_heavy_artillery": {
        "max_strength": 0.2, "max_organisation": 0, "default_morale": 0.1,
        "manpower": 1000, "training_time": 180,
        "weight": 0.1, "supply_consumption": 0.35,
    },

    # Support companies - Flame tanks
    "light_flame_tank": {
        "max_strength": 2, "max_organisation": 20, "default_morale": 0.3,
        "manpower": 300, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.02,
        "soft_attack": -0.5, "breakthrough": -0.5, "hard_attack": -0.75,
        "defense": -0.75, "armor_value": -0.75,
    },
    "medium_flame_tank": {
        "max_strength": 2, "max_organisation": 20, "default_morale": 0.3,
        "manpower": 300, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.025,
        "soft_attack": -0.45, "breakthrough": -0.45, "hard_attack": -0.7,
        "defense": -0.7, "armor_value": -0.7,
    },
    "heavy_flame_tank": {
        "max_strength": 2, "max_organisation": 20, "default_morale": 0.3,
        "manpower": 300, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.03,
        "soft_attack": -0.4, "breakthrough": -0.4, "hard_attack": -0.625,
        "defense": -0.625, "armor_value": -0.625,
    },

    # Support companies - Heavy armor / tank-chassis support
    "super_heavy_armor": {
        "max_strength": 2, "max_organisation": 10, "default_morale": 0.3,
        "manpower": 500, "training_time": 180, "suppression": 2.5,
        "weight": 1.0, "supply_consumption": 0.4,
    },
    "land_cruiser": {
        "max_strength": 15, "max_organisation": 60, "default_morale": 0.3,
        "manpower": 1000, "training_time": 250, "suppression": 4,
        "weight": 2, "supply_consumption": 0.6,
    },
    "super_heavy_tank_destroyer_brigade": {
        "max_strength": 0.5, "max_organisation": 0, "default_morale": 0.3,
        "manpower": 500, "training_time": 180, "suppression": 1.25,
        "weight": 1.75, "supply_consumption": 0.4,
        "breakthrough": -0.25, "ap_attack": 0.15,
    },
    "super_heavy_sp_artillery_brigade": {
        "max_strength": 0.5, "max_organisation": 0, "default_morale": 0.1,
        "manpower": 500, "training_time": 180, "suppression": 1.25,
        "weight": 1.75, "supply_consumption": 0.8,
        "breakthrough": -0.25, "soft_attack": 0.15,
    },
    "super_heavy_sp_anti_air_brigade": {
        "max_strength": 0.5, "max_organisation": 0, "default_morale": 0.1,
        "manpower": 500, "training_time": 180, "suppression": 0.75,
        "weight": 1.75, "supply_consumption": 0.1,
        "breakthrough": -0.35, "air_attack": 0.15,
    },

    # Support companies - Helicopter / nation-flavor infantry
    "helicopter_brigade": {
        "max_strength": 2, "max_organisation": 20, "default_morale": 0.3,
        "manpower": 500, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.070,
    },
    "sturmtruppe_battalion": {
        "max_strength": 20, "max_organisation": 70, "default_morale": 0.4,
        "manpower": 1000, "training_time": 120, "suppression": 1,
        "weight": 0.5, "supply_consumption": 0.05, "soft_attack": 0.1,
    },
    "blackshirt_assault_battalion": {
        "max_strength": 40, "max_organisation": 10, "default_morale": 0.2,
        "manpower": 1000, "training_time": 120, "suppression": 1.5,
        "weight": 0.4, "supply_consumption": 0.06,
        "soft_attack": 0.1, "breakthrough": 0.3,
    },

    # Regimental support - Fire Support group
    "fire_support": {
        "max_strength": 0.4, "max_organisation": 20, "default_morale": 0.2,
        "manpower": 240, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.06,
        "defense": -0.25, "soft_attack": -0.5, "hard_attack": -0.5,
    },
    "mot_fire_support": {
        "max_strength": 0.4, "max_organisation": 20, "default_morale": 0.2,
        "manpower": 240, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.06,
        "defense": -0.25, "breakthrough": -0.25, "soft_attack": -0.5, "hard_attack": -0.5,
    },
    "field_guns": {
        "max_strength": 0.1, "max_organisation": 0, "default_morale": 0.1,
        "manpower": 180, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.1,
        "defense": -0.75, "breakthrough": -0.75, "soft_attack": -0.75, "hard_attack": -0.75,
    },
    "rocket_battery": {
        "max_strength": 0.1, "max_organisation": 0, "default_morale": 0.1,
        "manpower": 180, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.1,
        "defense": -0.75, "breakthrough": -0.75, "soft_attack": -0.75, "hard_attack": -0.75,
    },
    "anti_air_battery": {
        "max_strength": 0.1, "max_organisation": 0, "default_morale": 0.1,
        "manpower": 120, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.06,
        "defense": -0.6, "breakthrough": -0.6, "soft_attack": -0.6,
        "hard_attack": -0.6, "air_attack": -0.6,
    },
    "anti_tank_battery": {
        "max_strength": 0.1, "max_organisation": 0, "default_morale": 0.1,
        "manpower": 180, "training_time": 120,
        "weight": 0.1, "supply_consumption": 0.06,
        "defense": -0.6, "breakthrough": -0.8, "soft_attack": -0.6,
        "hard_attack": -0.65, "ap_attack": -0.2,
    },

    # Regimental support - Tank Destroyer Support
    "light_tank_destroyer_support": {
        "max_strength": 0.1,  # (1.19.4) 0.2->0.1
        "max_organisation": 0, "default_morale": 0.1,
        "manpower": 180, "training_time": 120, "suppression": 0.25,
        "weight": 0.3, "supply_consumption": 0.06, "fuel_consumption": 0.40,
        "breakthrough": -0.9, "defense": -0.33,  # (1.19.4) breakthrough/defense standardized
        "soft_attack": -0.66,
        "hard_attack": -0.50, "armor_value": -0.66,
    },
    "medium_tank_destroyer_support": {
        "max_strength": 0.1,  # (1.19.4) 0.2->0.1
        "max_organisation": 0, "default_morale": 0.1,
        "manpower": 180, "training_time": 180, "suppression": 0.25,
        "weight": 0.4, "supply_consumption": 0.07, "fuel_consumption": 0.40,
        "breakthrough": -0.9, "defense": -0.33,  # (1.19.4) breakthrough/defense standardized
        "soft_attack": -0.66,
        "hard_attack": -0.50, "armor_value": -0.66,
    },
    "heavy_tank_destroyer_support": {
        "max_strength": 0.1,  # (1.19.4) 0.2->0.1
        "max_organisation": 0, "default_morale": 0.1,
        "manpower": 180, "training_time": 120, "suppression": 0.25,
        "weight": 0.5, "supply_consumption": 0.09, "fuel_consumption": 0.40,
        "breakthrough": -0.9, "defense": -0.33,  # (1.19.4) breakthrough/defense standardized
        "soft_attack": -0.66,
        "hard_attack": -0.50, "armor_value": -0.66,
    },
    "modern_tank_destroyer_support": {
        "max_strength": 0.1,  # (1.19.4) 0.2->0.1
        "max_organisation": 0, "default_morale": 0.1,
        "manpower": 180, "training_time": 120, "suppression": 0.25,
        "weight": 0.5, "supply_consumption": 0.08, "fuel_consumption": 0.40,
        "breakthrough": -0.9, "defense": -0.33,  # (1.19.4) breakthrough/defense standardized
        "soft_attack": -0.66,
        "hard_attack": -0.50, "armor_value": -0.66,
    },

    # Regimental support - SP Anti-Air Support
    "light_sp_anti_air_support": {
        "max_strength": 0.1,  # (1.19.4) was 0.3 (not the patch's assumed 0.2) - forced to the patch's new 0.1 regardless
        "max_organisation": 0, "default_morale": 0.1,
        "manpower": 180, "training_time": 120, "suppression": 0.5,
        "weight": 0.3, "supply_consumption": 0.05, "fuel_consumption": 0.40,
        "breakthrough": -0.9,  # (1.19.4) standardized
        "defense": -0.50, "soft_attack": -0.66,
        "hard_attack": -0.66, "air_attack": -0.25, "armor_value": -0.66,
    },
    "medium_sp_anti_air_support": {
        "max_strength": 0.1,  # (1.19.4) was 0.3 (not the patch's assumed 0.2) - forced to the patch's new 0.1 regardless
        "max_organisation": 0, "default_morale": 0.1,
        "manpower": 180, "training_time": 120, "suppression": 0.6,
        "weight": 0.4, "supply_consumption": 0.06, "fuel_consumption": 0.40,
        "breakthrough": -0.9,  # (1.19.4) standardized
        "defense": -0.50, "soft_attack": -0.66,
        "hard_attack": -0.66, "air_attack": -0.25, "armor_value": -0.66,
    },
    "heavy_sp_anti_air_support": {
        "max_strength": 0.1,  # (1.19.4) 0.2->0.1
        "max_organisation": 0, "default_morale": 0.1,
        "manpower": 180, "training_time": 120, "suppression": 0.5,
        "weight": 0.5, "supply_consumption": 0.07, "fuel_consumption": 0.40,
        "breakthrough": -0.9,  # (1.19.4) standardized
        "defense": -0.50, "soft_attack": -0.66,
        "hard_attack": -0.66, "air_attack": -0.25, "armor_value": -0.66,
    },
    "modern_sp_anti_air_support": {
        "max_strength": 0.1,  # (1.19.4) 0.2->0.1
        "max_organisation": 0, "default_morale": 0.1,
        "manpower": 180, "training_time": 120, "suppression": 0.5,
        "weight": 0.5, "supply_consumption": 0.06, "fuel_consumption": 0.40,
        "breakthrough": -0.9,  # (1.19.4) standardized
        "defense": -0.50, "soft_attack": -0.66,
        "hard_attack": -0.66, "air_attack": -0.25, "armor_value": -0.66,
    },
}

# battalion_mult (added 2026-10-08) - every unit's own innate aura, compiled
# directly from each owning item's own `battalion_mult = { ... }` block
# across units_copy/*.txt (21 owning items, 23 blocks - armored_engineer and
# motorized_military_police each have two). See this file's own header
# comment for the full shape/`add`-flag explanation.
_BATTALION_MULT = {
    "engineer": [{"category": "category_light_infantry", "entrenchment": 0.20, "add": True}],
    "pioneer_support": [{"category": "category_marines", "breakthrough": 0.15}],
    "assault_engineer": [{"category": "category_light_infantry", "breakthrough": 0.1}],
    "armored_engineer": [
        {"category": "category_all_infantry", "entrenchment": 0.2, "add": True},
        {"category": "category_all_armor", "breakthrough": 0.05, "add": True},
    ],
    "field_hospital": [{"category": "category_all_infantry", "max_strength": 0.10}],
    "helicopter_field_hospital": [
        {"category": "category_all_infantry", "max_strength": 0.05, "default_morale": 0.1}
    ],
    "light_flame_tank": [{"category": "category_all_infantry", "breakthrough": 0.05}],
    "medium_flame_tank": [{"category": "category_all_infantry", "breakthrough": 0.05}],
    "heavy_flame_tank": [{"category": "category_all_infantry", "breakthrough": 0.05}],
    "helicopter_brigade": [{"category": "category_all_infantry", "max_strength": 0.03}],
    "armored_maintenance": [{"category": "category_all_armor", "max_strength": 0.1, "add": True}],
    "military_police": [{"category": "category_all_infantry", "default_morale": 0.20}],
    "motorized_military_police": [
        {"category": "category_all_infantry", "default_morale": 0.20},
        {"category": "category_vehicle_infantry", "suppression_factor": 0.20},
    ],
    "recon": [{"category": "category_artillery", "soft_attack": 0.10}],
    "mot_recon": [{"category": "category_artillery", "soft_attack": 0.10}],
    "armored_car_recon": [{"category": "category_artillery", "soft_attack": 0.10}],
    "light_tank_recon": [{"category": "category_all_armor", "hard_attack": 0.10}],
    "long_range_patrol_support": [{"category": "category_light_infantry", "initiative": 0.02, "add": True}],
    "helicopter_recon": [{"category": "category_artillery", "soft_attack": 0.1}],
    "armored_signal": [{"category": "category_all_armor", "breakthrough": 0.05}],
    "sturmtruppe_battalion": [{"category": "category_all_infantry", "breakthrough": 0.1}],
}

for _key, _mult in _BATTALION_MULT.items():
    BATTALION_STATS[_key]["battalion_mult"] = _mult
for _key in BATTALION_STATS:
    BATTALION_STATS[_key].setdefault("battalion_mult", [])
del _key, _mult
