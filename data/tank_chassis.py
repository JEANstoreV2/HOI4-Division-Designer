# Hand-curated from units_copy/equipment/{tank_chassis,x_tank_chassis}.txt
# (HOI4 game files, No Step Back module system - see CLAUDE.md's DLC-content
# stance), compiled 2026-09-16 for the Tank Designer's Phase 1 (chassis +
# role data). Verified via an Explore agent's full-file survey of both
# files, then spot-checked directly (light_tank_chassis's full archetype +
# tiers, land_cruiser_chassis's full block, and the gw_tank_equipment naming
# note below) before being trusted - see Activity_Log.md, 2026-09-16, for
# the Tank Designer plan of attack this is Phase 1 of.
#
# Field names are kept exactly as HOI4's own files spell them
# (`maximum_speed`, not this project's own `max_speed`) - aligning to
# logic/stats.py's STRUCTURAL_STAT_FIELDS/COMBAT_STAT_FIELDS naming is a
# later logic-layer concern, matching how data/doctrines.py also keeps
# doctrine's raw `maximum_speed` field name rather than renaming it here.
#
# Schema, per TANK_CHASSIS entry:
# - "module_slots": {slot_name: {"required": bool, "allowed_module_categories": [...]}}
#   - the module framework's real slot layout. Order matches the source
#     file (turret/main armament first, then suspension/armor/engine, then
#     optional special/radio/secondary-turret slots) - real templates and
#     the AI rely on this order per the source file's own comment.
# - "module_count_limits": [{"module": key, "max_count": N} |
#   {"category": key, "max_count": N}, ...] - transcribed from the source's
#   `count < N+1` condition (every instance in both files uses a strict
#   "<", never "<="; stored as the actual max allowed count, N, not the
#   raw N+1 threshold, to avoid an off-by-one at every call site).
# - "default_modules": {slot_name: module_key} - what an undesigned/default
#   tank ships with. land_cruiser_chassis's are commented out in the source
#   (no real default) - kept as an empty dict here, not invented.
# - "base_stats": every structural field on the archetype itself.
# - "tiers": [{"key", "tier" (int), "stat_overrides" (dict, only fields the
#   tier actually overrides - NOT a complete stat block; resolving a tier's
#   full stats means base_stats merged with stat_overrides, following the
#   same "archetype is the fallback, not the immediate parent" rule
#   data/equipment_tiers.py's header already documents for this exact
#   family), "upgrades" (tick types available at that tier - only ever
#   populated on a chassis's lowest tier per the source data, confirmed by
#   direct read, not assumed), "default_equipment_key" (the real
#   data/equipment_tiers.py-style key this tier's un-designed stats already
#   live under - see EQUIPMENT_TIERS_NOTE below)}]
#
# EQUIPMENT_TIERS_NOTE: data/equipment_tiers.py already compiles the real
# combat-stat numbers for each numbered tier's DEFAULT module loadout (e.g.
# "light_tank_equipment_2") - that's what a nation fields before any player
# customizes a design via the Tank Designer. This file's job is different:
# the module-slot FRAMEWORK a custom design is built from. A finished
# design should be able to fall back to the EQUIPMENT_TIERS default when
# nothing's been customized, per the Tank Designer plan's Phase 6.
# "default_equipment_key" is what makes that fallback possible - but note
# one confirmed naming mismatch: light_tank_chassis_0's real HOI4
# `derived_variant_name` is "light_tank_equipment_0", which ISN'T a real
# equipment entry anywhere - the actual tier-0-equivalent equipment is
# named "gw_tank_equipment" instead (confirmed by direct read of
# x_tank_chassis.txt's equipments block). Recorded as "gw_tank_equipment"
# here, not the nonexistent derived name.
#
# Confirmed gaps, not oversights: no numbered "_amphibious"/"_flame"
# equipment tier exists in x_tank_chassis.txt for ANY size (light/medium/
# heavy) despite their role archetypes existing - matches
# data/equipment.py's/data/equipment_tiers.py's own already-documented
# Flame Tank / split Amphibious Tank gaps (structural-only,
# combat_stats_available: False). super_heavy_tank_chassis and
# modern_tank_chassis get only 3 roles each (anti_air, artillery,
# anti_tank) - no amphibious, no flame role exists for either size in the
# source data, matching the absence of e.g. "amphibious_modern_armor" or
# "modern_flame_tank" anywhere in data/battalions.py/data/support_companies.py.
# amphibious_tank_chassis is its own independent archetype (feeds the
# standalone "amphibious_armor" battalion) - NOT a role duplicate of
# light/medium/heavy (those have their own separate "amphibious" role
# variants, feeding amphibious_light/medium/heavy_armor instead). Two
# genuinely different sources of "amphibious tank" stats, not a duplicate
# entry to collapse.
#
# "module_additive_multiplier" (added 1.19.4, float, only present on
# Light/Medium/Heavy/Modern tank chassis tiers): a flat percentage scaling
# ONLY the sum of chosen modules' own `add_stats` contributions to
# soft_attack/hard_attack/air_attack - not the chassis's own base stat, not
# tick levels, and not the existing multiply_stats percentage stage. Per the
# 1.19.4 patch notes: Interwar -5%, Improved +5%, Advanced +10%, Modern +15%.
# ASSUMPTION, not independently screenshot-confirmed: this project's own
# tier indices (0-3) are mapped to Interwar/Improved/Advanced in that order;
# the patch text names no 4th tier for Light/Medium/Heavy, so tier 3 is
# assumed to share the standalone "Modern Tank Chassis" archetype's own
# +15% value (modern_tank_chassis's single tier also gets +15%) rather than
# being left at 0% by omission. Revisit if a screenshot shows otherwise.
#
# heavy_tank_chassis and super_heavy_tank_chassis's module_count_limits
# omit a tank_secondary_turret category limit even though that category is
# allowed in their special slots (light/medium both cap it) - a real
# inconsistency in the source data, kept as-is rather than "fixed", per
# this project's standing practice of recording confirmed-but-surprising
# numbers rather than smoothing them over.

TANK_CHASSIS = [
    {
        "key": "light_tank_chassis", "name": "Light Tank", "feeds": "light_armor",
        "module_slots": {
            "turret_type_slot": {"required": True, "allowed_module_categories": ["tank_light_turret_type"]},
            "main_armament_slot": {"required": True, "allowed_module_categories": ["tank_small_main_armament", "tank_flamethrower"]},
            "suspension_type_slot": {"required": True, "allowed_module_categories": ["tank_suspension_type", "tank_non_tracked_suspension_type"]},
            "armor_type_slot": {"required": True, "allowed_module_categories": ["tank_armor_type"]},
            "engine_type_slot": {"required": True, "allowed_module_categories": ["tank_engine_type"]},
            "special_type_slot_1": {"required": False, "allowed_module_categories": ["tank_special_module", "tank_radio_module", "tank_secondary_turret"]},
            "special_type_slot_2": {"required": False, "allowed_module_categories": ["tank_special_module", "tank_radio_module", "tank_secondary_turret"]},
            "special_type_slot_3": {"required": False, "allowed_module_categories": ["tank_special_module", "tank_radio_module", "tank_secondary_turret"]},
            "special_type_slot_4": {"required": False, "allowed_module_categories": ["tank_special_module", "tank_radio_module", "tank_secondary_turret"]},
        },
        "module_count_limits": [
            {"module": "sloped_armor", "max_count": 1},
            {"category": "tank_radio_module", "max_count": 1},
            {"category": "tank_secondary_turret", "max_count": 1},
            {"module": "amphibious_drive", "max_count": 1},
            {"module": "wet_ammo_storage", "max_count": 1},
            {"module": "squeezebore_adaptor", "max_count": 1},
            {"module": "armor_skirts", "max_count": 1},
            {"module": "dozer_blade", "max_count": 1},
            {"module": "easy_maintenance", "max_count": 1},
            {"module": "auto_loader", "max_count": 1},
            {"module": "stabilizer", "max_count": 1},
        ],
        "default_modules": {
            "main_armament_slot": None,
            "turret_type_slot": "tank_light_one_man_tank_turret",
            "suspension_type_slot": "tank_bogie_suspension",
            "armor_type_slot": "tank_riveted_armor",
            "engine_type_slot": "tank_gasoline_engine",
        },
        "base_stats": {"fuel_consumption": 0, "maximum_speed": 4, "build_cost_ic": 2, "reliability": 0.8, "hardness": 0.8, "armor_value": 10},
        "tiers": [
            {"key": "light_tank_chassis_0", "tier": 0, "stat_overrides": {}, "module_additive_multiplier": -0.05,
             "upgrades": ["tank_nsb_engine_upgrade", "tank_nsb_armor_upgrade"], "default_equipment_key": "gw_tank_equipment"},
            {"key": "light_tank_chassis_1", "tier": 1,
             "stat_overrides": {"maximum_speed": 5, "build_cost_ic": 2.35, "reliability": 0.95, "armor_value": 15},
             "module_additive_multiplier": 0.05,
             "upgrades": [], "default_equipment_key": "light_tank_equipment_1"},
            {"key": "light_tank_chassis_2", "tier": 2,
             "stat_overrides": {"maximum_speed": 6, "build_cost_ic": 2.7, "reliability": 1.1, "armor_value": 20},
             "module_additive_multiplier": 0.10,
             "upgrades": [], "default_equipment_key": "light_tank_equipment_2"},
            {"key": "light_tank_chassis_3", "tier": 3,
             "stat_overrides": {"maximum_speed": 7, "build_cost_ic": 3, "reliability": 1.3, "armor_value": 25},
             "module_additive_multiplier": 0.15,
             "upgrades": [], "default_equipment_key": "light_tank_equipment_3"},
        ],
    },
    {
        "key": "medium_tank_chassis", "name": "Medium Tank", "feeds": "medium_armor",
        "module_slots": {
            "turret_type_slot": {"required": True, "allowed_module_categories": ["tank_light_turret_type", "tank_medium_turret_type"]},
            "main_armament_slot": {"required": True, "allowed_module_categories": ["tank_small_main_armament", "tank_flamethrower"]},
            "suspension_type_slot": {"required": True, "allowed_module_categories": ["tank_suspension_type"]},
            "armor_type_slot": {"required": True, "allowed_module_categories": ["tank_armor_type"]},
            "engine_type_slot": {"required": True, "allowed_module_categories": ["tank_engine_type"]},
            "special_type_slot_1": {"required": False, "allowed_module_categories": ["tank_special_module", "tank_radio_module", "tank_secondary_turret"]},
            "special_type_slot_2": {"required": False, "allowed_module_categories": ["tank_special_module", "tank_radio_module", "tank_secondary_turret"]},
            "special_type_slot_3": {"required": False, "allowed_module_categories": ["tank_special_module", "tank_radio_module", "tank_secondary_turret"]},
            "special_type_slot_4": {"required": False, "allowed_module_categories": ["tank_special_module", "tank_radio_module", "tank_secondary_turret"]},
        },
        "module_count_limits": [
            {"module": "sloped_armor", "max_count": 1},
            {"category": "tank_radio_module", "max_count": 1},
            {"category": "tank_secondary_turret", "max_count": 2},
            {"module": "amphibious_drive", "max_count": 1},
            {"module": "wet_ammo_storage", "max_count": 1},
            {"module": "squeezebore_adaptor", "max_count": 1},
            {"module": "armor_skirts", "max_count": 1},
            {"module": "dozer_blade", "max_count": 1},
            {"module": "easy_maintenance", "max_count": 1},
            {"module": "auto_loader", "max_count": 1},
            {"module": "stabilizer", "max_count": 1},
        ],
        "default_modules": {
            "main_armament_slot": None,
            "turret_type_slot": "tank_medium_one_man_tank_turret",
            "suspension_type_slot": "tank_bogie_suspension",
            "armor_type_slot": "tank_riveted_armor",
            "engine_type_slot": "tank_gasoline_engine",
        },
        "base_stats": {"fuel_consumption": 0, "maximum_speed": 4, "build_cost_ic": 2, "reliability": 0.5, "armor_value": 20, "hardness": 0.85},
        "tiers": [
            {"key": "medium_tank_chassis_0", "tier": 0,
             "stat_overrides": {"maximum_speed": 4, "build_cost_ic": 3.5, "reliability": 0.75, "armor_value": 20},
             "module_additive_multiplier": -0.05,
             "upgrades": ["tank_nsb_engine_upgrade", "tank_nsb_armor_upgrade"], "default_equipment_key": "medium_tank_equipment_1"},
            {"key": "medium_tank_chassis_1", "tier": 1,
             "stat_overrides": {"armor_value": 30, "build_cost_ic": 3.75, "reliability": 0.8, "maximum_speed": 5},
             "module_additive_multiplier": 0.05,
             "upgrades": [], "default_equipment_key": "medium_tank_equipment_1"},
            {"key": "medium_tank_chassis_2", "tier": 2,
             "stat_overrides": {"maximum_speed": 6, "build_cost_ic": 4, "reliability": 1, "armor_value": 40},
             "module_additive_multiplier": 0.10,
             "upgrades": [], "default_equipment_key": "medium_tank_equipment_2"},
            {"key": "medium_tank_chassis_3", "tier": 3,
             "stat_overrides": {"maximum_speed": 6, "build_cost_ic": 4.25, "reliability": 1.2, "armor_value": 50},
             "module_additive_multiplier": 0.15,
             "upgrades": [], "default_equipment_key": "medium_tank_equipment_3"},
        ],
    },
    {
        "key": "heavy_tank_chassis", "name": "Heavy Tank", "feeds": "heavy_armor",
        "module_slots": {
            "turret_type_slot": {"required": True, "allowed_module_categories": ["tank_light_turret_type", "tank_medium_turret_type", "tank_heavy_turret_type"]},
            "main_armament_slot": {"required": True, "allowed_module_categories": ["tank_small_main_armament", "tank_flamethrower"]},
            "suspension_type_slot": {"required": True, "allowed_module_categories": ["tank_suspension_type"]},
            "armor_type_slot": {"required": True, "allowed_module_categories": ["tank_armor_type"]},
            "engine_type_slot": {"required": True, "allowed_module_categories": ["tank_engine_type"]},
            "special_type_slot_1": {"required": False, "allowed_module_categories": ["tank_special_module", "tank_radio_module", "tank_secondary_turret"]},
            "special_type_slot_2": {"required": False, "allowed_module_categories": ["tank_special_module", "tank_radio_module", "tank_secondary_turret"]},
            "special_type_slot_3": {"required": False, "allowed_module_categories": ["tank_special_module", "tank_radio_module", "tank_secondary_turret"]},
            "special_type_slot_4": {"required": False, "allowed_module_categories": ["tank_special_module", "tank_radio_module", "tank_secondary_turret"]},
        },
        # No tank_secondary_turret count limit here - a real source-data
        # inconsistency vs. light/medium (see module header note), not a
        # transcription slip.
        "module_count_limits": [
            {"module": "sloped_armor", "max_count": 1},
            {"category": "tank_radio_module", "max_count": 1},
            {"module": "amphibious_drive", "max_count": 1},
            {"module": "wet_ammo_storage", "max_count": 1},
            {"module": "squeezebore_adaptor", "max_count": 1},
            {"module": "armor_skirts", "max_count": 1},
            {"module": "dozer_blade", "max_count": 1},
            {"module": "easy_maintenance", "max_count": 1},
            {"module": "auto_loader", "max_count": 1},
            {"module": "stabilizer", "max_count": 1},
        ],
        "default_modules": {
            "main_armament_slot": None,
            "turret_type_slot": "tank_heavy_two_man_tank_turret",
            "suspension_type_slot": "tank_bogie_suspension",
            "armor_type_slot": "tank_riveted_armor",
            "engine_type_slot": "tank_gasoline_engine",
        },
        "base_stats": {"fuel_consumption": 0, "maximum_speed": 3, "build_cost_ic": 10, "reliability": 0.75, "armor_value": 30, "hardness": 0.95},
        "tiers": [
            {"key": "heavy_tank_chassis_0", "tier": 0,
             "stat_overrides": {"maximum_speed": 3, "build_cost_ic": 9, "reliability": 0.75, "armor_value": 35},
             "module_additive_multiplier": -0.05,
             "upgrades": ["tank_nsb_engine_upgrade", "tank_nsb_armor_upgrade"], "default_equipment_key": "heavy_tank_equipment_1"},
            {"key": "heavy_tank_chassis_1", "tier": 1,
             "stat_overrides": {"armor_value": 55, "maximum_speed": 5, "reliability": 0.8},
             "module_additive_multiplier": 0.05,
             "upgrades": [], "default_equipment_key": "heavy_tank_equipment_1"},
            {"key": "heavy_tank_chassis_2", "tier": 2,
             "stat_overrides": {"build_cost_ic": 11, "maximum_speed": 5, "reliability": 1.1, "armor_value": 60},
             "module_additive_multiplier": 0.10,
             "upgrades": [], "default_equipment_key": "heavy_tank_equipment_2"},
            {"key": "heavy_tank_chassis_3", "tier": 3,
             "stat_overrides": {"build_cost_ic": 12, "maximum_speed": 5, "reliability": 1.2, "armor_value": 75},
             "module_additive_multiplier": 0.15,
             "upgrades": [], "default_equipment_key": "heavy_tank_equipment_3"},
        ],
    },
    {
        "key": "modern_tank_chassis", "name": "Modern Tank", "feeds": "modern_armor",
        "module_slots": {
            "turret_type_slot": {"required": True, "allowed_module_categories": ["tank_light_turret_type", "tank_medium_turret_type", "tank_heavy_turret_type", "tank_modern_turret_type"]},
            "main_armament_slot": {"required": True, "allowed_module_categories": ["tank_small_main_armament"]},
            "suspension_type_slot": {"required": True, "allowed_module_categories": ["tank_suspension_type"]},
            "armor_type_slot": {"required": True, "allowed_module_categories": ["tank_armor_type"]},
            "engine_type_slot": {"required": True, "allowed_module_categories": ["tank_engine_type"]},
            "special_type_slot_1": {"required": False, "allowed_module_categories": ["tank_special_module", "tank_radio_module"]},
            "special_type_slot_2": {"required": False, "allowed_module_categories": ["tank_special_module", "tank_radio_module"]},
            "special_type_slot_3": {"required": False, "allowed_module_categories": ["tank_special_module", "tank_radio_module"]},
            "special_type_slot_4": {"required": False, "allowed_module_categories": ["tank_special_module", "tank_radio_module"]},
        },
        "module_count_limits": [
            {"module": "sloped_armor", "max_count": 1},
            {"category": "tank_radio_module", "max_count": 1},
            {"module": "amphibious_drive", "max_count": 0},
            {"module": "wet_ammo_storage", "max_count": 1},
            {"module": "squeezebore_adaptor", "max_count": 1},
            {"module": "armor_skirts", "max_count": 1},
            {"module": "dozer_blade", "max_count": 1},
            {"module": "easy_maintenance", "max_count": 1},
            {"module": "auto_loader", "max_count": 1},
            {"module": "stabilizer", "max_count": 1},
        ],
        "default_modules": {
            "main_armament_slot": None,
            "turret_type_slot": "tank_modern_tank_turret",
            "suspension_type_slot": "tank_bogie_suspension",
            "armor_type_slot": "tank_riveted_armor",
            "engine_type_slot": "tank_gasoline_engine",
        },
        "base_stats": {"fuel_consumption": 0, "maximum_speed": 7, "build_cost_ic": 6, "reliability": 1.2, "armor_value": 65, "hardness": 0.95},
        "tiers": [
            {"key": "modern_tank_chassis_1", "tier": 1, "stat_overrides": {}, "module_additive_multiplier": 0.15,
             "upgrades": ["tank_nsb_engine_upgrade", "tank_nsb_armor_upgrade"], "default_equipment_key": "modern_tank_equipment_1"},
        ],
    },
    {
        "key": "super_heavy_tank_chassis", "name": "Super Heavy Tank", "feeds": "super_heavy_armor",
        "module_slots": {
            "turret_type_slot": {"required": True, "allowed_module_categories": ["tank_super_heavy_turret_type"]},
            "main_armament_slot": {"required": True, "allowed_module_categories": ["tank_small_main_armament"]},
            "suspension_type_slot": {"required": True, "allowed_module_categories": ["tank_suspension_type"]},
            "armor_type_slot": {"required": True, "allowed_module_categories": ["tank_armor_type"]},
            "engine_type_slot": {"required": True, "allowed_module_categories": ["tank_engine_type"]},
            "special_type_slot_1": {"required": False, "allowed_module_categories": ["tank_special_module", "tank_radio_module", "tank_secondary_turret"]},
            "special_type_slot_2": {"required": False, "allowed_module_categories": ["tank_special_module", "tank_radio_module", "tank_secondary_turret"]},
            "special_type_slot_3": {"required": False, "allowed_module_categories": ["tank_special_module", "tank_radio_module", "tank_secondary_turret"]},
            "special_type_slot_4": {"required": False, "allowed_module_categories": ["tank_special_module", "tank_radio_module", "tank_secondary_turret"]},
        },
        # No tank_secondary_turret count limit here either - same
        # source-data inconsistency as heavy_tank_chassis.
        "module_count_limits": [
            {"module": "sloped_armor", "max_count": 1},
            {"category": "tank_radio_module", "max_count": 1},
            {"module": "amphibious_drive", "max_count": 0},
            {"module": "wet_ammo_storage", "max_count": 1},
            {"module": "squeezebore_adaptor", "max_count": 1},
            {"module": "armor_skirts", "max_count": 1},
            {"module": "dozer_blade", "max_count": 1},
            {"module": "easy_maintenance", "max_count": 1},
            {"module": "auto_loader", "max_count": 1},
            {"module": "stabilizer", "max_count": 1},
        ],
        "default_modules": {
            "main_armament_slot": None,
            "turret_type_slot": "tank_super_heavy_three_man_tank_turret",
            "suspension_type_slot": "tank_bogie_suspension",
            "armor_type_slot": "tank_riveted_armor",
            "engine_type_slot": "tank_gasoline_engine",
        },
        # hardness intentionally 0 in the source ("doesn't apply to support
        # companies, must change if this ever becomes a line battalion") -
        # matches this chassis feeding a support company (super_heavy_armor),
        # not a line battalion, today.
        "base_stats": {"fuel_consumption": 0, "maximum_speed": 4, "build_cost_ic": 28, "reliability": 1, "armor_value": 90, "hardness": 0},
        "tiers": [
            {"key": "super_heavy_tank_chassis_1", "tier": 1, "stat_overrides": {},
             "upgrades": ["tank_nsb_engine_upgrade", "tank_nsb_armor_upgrade"], "default_equipment_key": "super_heavy_tank_equipment_1"},
        ],
    },
    {
        "key": "amphibious_tank_chassis", "name": "Amphibious Tank", "feeds": "amphibious_armor",
        # An independent archetype, NOT a role duplicate of light/medium/
        # heavy (those have their own separate amphibious role variants in
        # TANK_ROLES, feeding amphibious_light/medium/heavy_armor instead) -
        # see module header note.
        "module_slots": {
            "turret_type_slot": {"required": True, "allowed_module_categories": ["tank_light_turret_type"]},
            "main_armament_slot": {"required": True, "allowed_module_categories": ["tank_small_main_armament"]},
            "suspension_type_slot": {"required": True, "allowed_module_categories": ["tank_suspension_type"]},
            "armor_type_slot": {"required": True, "allowed_module_categories": ["tank_armor_type"]},
            "engine_type_slot": {"required": True, "allowed_module_categories": ["tank_engine_type"]},
            "special_type_slot_1": {"required": False, "allowed_module_categories": ["tank_special_module", "tank_radio_module"]},
            "special_type_slot_2": {"required": False, "allowed_module_categories": ["tank_special_module", "tank_radio_module"]},
            "special_type_slot_3": {"required": False, "allowed_module_categories": ["tank_special_module", "tank_radio_module"]},
            "special_type_slot_4": {"required": False, "allowed_module_categories": ["tank_special_module", "tank_radio_module"]},
        },
        "module_count_limits": [
            {"module": "sloped_armor", "max_count": 1},
            {"category": "tank_radio_module", "max_count": 1},
            {"module": "amphibious_drive", "max_count": 0},
            {"module": "wet_ammo_storage", "max_count": 1},
            {"module": "squeezebore_adaptor", "max_count": 1},
            {"module": "armor_skirts", "max_count": 1},
            {"module": "dozer_blade", "max_count": 1},
            {"module": "easy_maintenance", "max_count": 1},
            {"module": "auto_loader", "max_count": 1},
            {"module": "stabilizer", "max_count": 1},
        ],
        "default_modules": {
            "main_armament_slot": None,
            "turret_type_slot": "tank_light_one_man_tank_turret",
            "suspension_type_slot": "tank_bogie_suspension",
            "armor_type_slot": "tank_riveted_armor",
            "engine_type_slot": "tank_gasoline_engine",
        },
        "base_stats": {"fuel_consumption": 0, "maximum_speed": 5, "build_cost_ic": 4.5, "reliability": 1.1, "armor_value": 15, "hardness": 0.85},
        "tiers": [
            {"key": "amphibious_tank_chassis_1", "tier": 1, "stat_overrides": {},
             "upgrades": ["tank_nsb_engine_upgrade", "tank_nsb_armor_upgrade"], "default_equipment_key": "amphibious_tank_equipment_1"},
        ],
    },
    {
        "key": "land_cruiser_chassis", "name": "Land Cruiser", "feeds": "land_cruiser",
        # Structurally unique - no turret/suspension/armor/engine slots at
        # all, and no role variants (see TANK_ROLES header). Still gets the
        # same engine/armor tick upgrades as every tank chassis despite
        # having no explicit engine/armor-type module slot to attach them
        # to - ticks are a mechanic layered on top of whichever chassis a
        # design uses, not dependent on a matching module slot existing.
        "module_slots": {
            "lc_main_armament_slot": {"required": True, "allowed_module_categories": ["lc_main_armament"]},
            "lc_secondary_armament_slot": {"required": False, "allowed_module_categories": ["lc_secondary_armament"]},
            "lc_special_features_slot_1": {"required": False, "allowed_module_categories": ["lc_radio_module", "lc_aerial_deployment", "lc_external_features", "lc_structural_features"]},
            "lc_special_features_slot_2": {"required": False, "allowed_module_categories": ["lc_radio_module", "lc_aerial_deployment", "lc_external_features", "lc_structural_features"]},
            "lc_special_features_slot_3": {"required": False, "allowed_module_categories": ["lc_radio_module", "lc_aerial_deployment", "lc_external_features", "lc_structural_features"]},
            "lc_additional_armament_slot_1": {"required": False, "allowed_module_categories": ["lc_additional_armament"]},
            "lc_additional_armament_slot_2": {"required": False, "allowed_module_categories": ["lc_additional_armament"]},
            "lc_additional_armament_slot_3": {"required": False, "allowed_module_categories": ["lc_additional_armament"]},
            "lc_additional_armament_slot_4": {"required": False, "allowed_module_categories": ["lc_additional_armament"]},
        },
        "module_count_limits": [
            {"module": "lc_assault_gun", "max_count": 1},
            {"module": "lc_high_velocity_cannon_turret", "max_count": 2},
            {"module": "lc_flamethrower_turret", "max_count": 2},
            {"module": "lc_rocket_launcher", "max_count": 2},
            {"category": "lc_radio_module", "max_count": 1},
            {"module": "lc_radar", "max_count": 1},
            {"category": "lc_aerial_deployment", "max_count": 1},
            {"module": "lc_armored_skirts", "max_count": 1},
            {"module": "lc_obstacle_clearance_gear", "max_count": 1},
            {"module": "lc_wet_ammunition_storage", "max_count": 1},
            {"module": "lc_smoke_generators", "max_count": 1},
            {"module": "lc_stabilizers", "max_count": 1},
        ],
        # Both entries are commented out in the source (no real default
        # loadout) - kept empty, not invented.
        "default_modules": {},
        # defense=12 and max_military_factories=5 appear only on this
        # archetype, nowhere else in either file - transcribed as-is.
        "base_stats": {
            "fuel_consumption": 12, "maximum_speed": 5, "build_cost_ic": 330, "reliability": 1,
            "armor_value": 150, "defense": 12, "hardness": 0, "max_military_factories": 5,
        },
        "tiers": [
            {"key": "land_cruiser_chassis_1", "tier": 1, "stat_overrides": {},
             "upgrades": ["tank_nsb_engine_upgrade", "tank_nsb_armor_upgrade"], "default_equipment_key": "land_cruiser_equipment_1"},
        ],
    },
]

# Role conversions (units_copy/equipment/x_tank_chassis.txt's
# duplicate_archetypes block) - each entry inherits its base chassis's
# entire module_slots/module_count_limits/default_modules unchanged, adding
# only a `type` tag (which Composition role it feeds) and, for most roles,
# a hardness override. `stat_overrides` is empty wherever the source's
# `for_each` block has no override at all (confirmed: anti_tank and flame
# roles never get one; anti_air/artillery/amphibious always do).
#
# "feeds" is the existing data/battalions.py, data/support_companies.py, or
# data/regimental_support.py key (or keys, for anti_tank/anti_air which
# feed both a full battalion/support-company slot AND a regimental-support
# variant) this role produces stats for - cross-checked directly against
# all three files, not guessed from naming alone (e.g. SP Artillery has NO
# regimental-support variant anywhere, confirmed absent, so "artillery"
# roles only ever list one feed target).
#
# Confirmed absent, not omitted by mistake: super_heavy and modern get only
# 3 roles each (anti_air/artillery/anti_tank) - no amphibious or flame
# archetype exists for either size anywhere in x_tank_chassis.txt, matching
# the absence of e.g. "amphibious_modern_armor" in data/battalions.py.
# amphibious_tank_chassis (above) is not further role-duplicated at all.
# land_cruiser_chassis has zero role duplicates - confirmed absent from the
# entire duplicate_archetypes block.
TANK_ROLES = [
    # --- Light tank (5/5 roles) ---
    {"key": "light_tank_aa_chassis", "base_chassis": "light_tank_chassis", "role": "anti_air",
     "stat_overrides": {"hardness": 0.5}, "feeds": ["light_sp_anti_air_brigade", "light_sp_anti_air_support"]},
    {"key": "light_tank_artillery_chassis", "base_chassis": "light_tank_chassis", "role": "artillery",
     "stat_overrides": {"hardness": 0.5}, "feeds": ["light_sp_artillery_brigade"]},
    {"key": "light_tank_destroyer_chassis", "base_chassis": "light_tank_chassis", "role": "anti_tank",
     "stat_overrides": {}, "feeds": ["light_tank_destroyer_brigade", "light_tank_destroyer_support"]},
    {"key": "light_tank_amphibious_chassis", "base_chassis": "light_tank_chassis", "role": "amphibious",
     "stat_overrides": {"hardness": 0.55}, "feeds": ["amphibious_light_armor"]},
    {"key": "light_tank_flame_chassis", "base_chassis": "light_tank_chassis", "role": "flame",
     "stat_overrides": {}, "feeds": ["light_flame_tank"]},

    # --- Medium tank (5/5 roles) ---
    {"key": "medium_tank_aa_chassis", "base_chassis": "medium_tank_chassis", "role": "anti_air",
     "stat_overrides": {"hardness": 0.65}, "feeds": ["medium_sp_anti_air_brigade", "medium_sp_anti_air_support"]},
    {"key": "medium_tank_artillery_chassis", "base_chassis": "medium_tank_chassis", "role": "artillery",
     "stat_overrides": {"hardness": 0.65}, "feeds": ["medium_sp_artillery_brigade"]},
    {"key": "medium_tank_destroyer_chassis", "base_chassis": "medium_tank_chassis", "role": "anti_tank",
     "stat_overrides": {}, "feeds": ["medium_tank_destroyer_brigade", "medium_tank_destroyer_support"]},
    {"key": "medium_tank_amphibious_chassis", "base_chassis": "medium_tank_chassis", "role": "amphibious",
     "stat_overrides": {"hardness": 0.7}, "feeds": ["amphibious_medium_armor"]},
    {"key": "medium_tank_flame_chassis", "base_chassis": "medium_tank_chassis", "role": "flame",
     "stat_overrides": {}, "feeds": ["medium_flame_tank"]},

    # --- Heavy tank (5/5 roles) ---
    {"key": "heavy_tank_aa_chassis", "base_chassis": "heavy_tank_chassis", "role": "anti_air",
     "stat_overrides": {"hardness": 0.8}, "feeds": ["heavy_sp_anti_air_brigade", "heavy_sp_anti_air_support"]},
    {"key": "heavy_tank_artillery_chassis", "base_chassis": "heavy_tank_chassis", "role": "artillery",
     "stat_overrides": {"hardness": 0.8}, "feeds": ["heavy_sp_artillery_brigade"]},
    {"key": "heavy_tank_destroyer_chassis", "base_chassis": "heavy_tank_chassis", "role": "anti_tank",
     "stat_overrides": {}, "feeds": ["heavy_tank_destroyer_brigade", "heavy_tank_destroyer_support"]},
    {"key": "heavy_tank_amphibious_chassis", "base_chassis": "heavy_tank_chassis", "role": "amphibious",
     "stat_overrides": {"hardness": 0.8}, "feeds": ["amphibious_heavy_armor"]},
    {"key": "heavy_tank_flame_chassis", "base_chassis": "heavy_tank_chassis", "role": "flame",
     "stat_overrides": {}, "feeds": ["heavy_flame_tank"]},

    # --- Super heavy tank (3/5 roles only - confirmed, see module header) ---
    {"key": "super_heavy_tank_aa_chassis", "base_chassis": "super_heavy_tank_chassis", "role": "anti_air",
     "stat_overrides": {"hardness": 0.9}, "feeds": ["super_heavy_sp_anti_air_brigade"]},
    {"key": "super_heavy_tank_artillery_chassis", "base_chassis": "super_heavy_tank_chassis", "role": "artillery",
     "stat_overrides": {"hardness": 0.9}, "feeds": ["super_heavy_sp_artillery_brigade"]},
    {"key": "super_heavy_tank_destroyer_chassis", "base_chassis": "super_heavy_tank_chassis", "role": "anti_tank",
     "stat_overrides": {}, "feeds": ["super_heavy_tank_destroyer_brigade"]},

    # --- Modern tank (3/5 roles only - confirmed, see module header) ---
    {"key": "modern_tank_aa_chassis", "base_chassis": "modern_tank_chassis", "role": "anti_air",
     "stat_overrides": {"hardness": 0.85}, "feeds": ["modern_sp_anti_air_brigade", "modern_sp_anti_air_support"]},
    {"key": "modern_tank_artillery_chassis", "base_chassis": "modern_tank_chassis", "role": "artillery",
     "stat_overrides": {"hardness": 0.85}, "feeds": ["modern_sp_artillery_brigade"]},
    {"key": "modern_tank_destroyer_chassis", "base_chassis": "modern_tank_chassis", "role": "anti_tank",
     "stat_overrides": {}, "feeds": ["modern_tank_destroyer_brigade", "modern_tank_destroyer_support"]},
]
