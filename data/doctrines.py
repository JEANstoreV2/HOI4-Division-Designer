# Hand-curated from doctrines_copy/{grand_doctrines,tracks,subdoctrines}/
# (HOI4 game files), compiled 2026-09-15. Only the `land` and
# `special_forces` folders are compiled - `naval`/`air` are Navy/Air Wing
# systems, out of scope for a land Division Designer (see CLAUDE.md).
#
# Schema, per DOCTRINE_TRACKS/GRAND_DOCTRINES/SUBDOCTRINES entry:
# - "effects" (grand doctrines, subdoctrines) / each entry of "milestones"
#   (grand doctrines) / each reward's "effects" (subdoctrines) is a dict
#   with up to four optional keys:
#     - "modifiers": {flat_modifier_name: value} - country/army-wide flat
#       modifiers (e.g. planning_speed, land_reinforce_rate). Captured
#       faithfully even where clearly outside this tool's current scope
#       (e.g. naval invasion, political power) rather than filtered by
#       guesswork about future relevance.
#     - "enable_tactics": [tactic_name, ...]
#     - "unit_bonuses": {item_or_category_key: {stat_field: value, ...}} -
#       the main content. Terrain modifiers nest as
#       {"forest": {"attack": ...}, ...} exactly like data/technologies.py's
#       terrain blocks. A `battalion_mult` (one unit boosting a *different*
#       category elsewhere in the division) nests as a list under the
#       "battalion_mult" key: [{"category": ..., **stat_fields}, ...],
#       kept alongside the item's own plain bonus fields exactly as the
#       source nests it.
#     - "equipment_bonus": {equipment_key: {field: value}} - a named
#       equipment type's stats directly, distinct from unit_bonuses.
# - "unlocks_subunits" (subdoctrines only, list) - extracted from
#   `effect = { unlock_subunit = X }`, found on a handful of Special Forces
#   subdoctrines/rewards. Mirrors data/technologies.py's field of the same
#   name; nothing wires it into Composition yet (matches Research's own
#   unlocked_subunit_keys not being wired in on its first pass either).
#
# Deliberately excluded, matching how data/technologies.py already treats
# the equivalent things in tech files: `ai_will_do` (AI behavior weighting),
# `available`/`visible` triggers (DLC/nation/government gates - not
# modeled, see below), `add_tech_bonus` effects, `custom_effect_tooltip`,
# `add_ideas`, and xp_cost/xp_type (no cost/time simulation, matching
# Research's plain-checklist decision).
#
# No DLC/nation/government gating is modeled - every subdoctrine is always
# offered, extending the same "all battalions are treated as accessible"
# stance Composition already takes (see Specification.md's Decisions log)
# to Doctrine. The one exception: Special Forces subdoctrines'
# `requires_technology` IS modeled, since `has_tech = X` is a real,
# checkable Research dependency, not an unmodelable nation/DLC fact.
#
# DLC-variant duplicate pairs (same track/rewards, one has richer effects
# gated behind owning a specific DLC) were deduplicated to their richer
# version rather than compiled as two distinct choices - four found, all
# in land subdoctrines: armored_spearhead (dropped armored_spearhead_no_lar),
# armored_cavalry (dropped armored_cavalry_no_lar), mobile_recon_and_assault
# (dropped mobile_recon_and_assault_no_lar), deep_battle (dropped
# deep_battle_no_lar).
#
# The "5th battalion row" mechanic (Specification.md) is directly visible
# in the data, not asserted from the spec's prose: exactly one track's
# milestone per land grand doctrine sets additional_brigade_column_size = 1
# (armor for Mobile Warfare, combat_support for Superior Firepower,
# infantry for both Grand Battleplan and Mass Assault) - logic/doctrines.py
# derives the 5th-row unlock from this field rather than a hardcoded map.

DOCTRINE_TRACKS = [
    {"key": "infantry", "folder": "land"},
    {"key": "combat_support", "folder": "land"},
    {"key": "armor", "folder": "land"},
    {"key": "operations", "folder": "land"},
    {"key": "special_forces_first", "folder": "special_forces"},
    {"key": "special_forces_second", "folder": "special_forces"},
]

GRAND_DOCTRINES = [
    {
        "key": "new_mobile_warfare", "name": "Mobile Warfare", "folder": "land",
        "tracks": ["infantry", "combat_support", "armor", "operations"],
        "effects": {
            "modifiers": {"planning_speed": 0.20, "army_speed_factor": 0.10},
            "enable_tactics": ["tactic_unexpected_thrust"],
        },
        "milestones": [
            {"modifiers": {"org_loss_when_moving": -0.15, "land_reinforce_rate": 0.02},
             "enable_tactics": ["tactic_delay"]},
            {"modifiers": {"planning_speed": 0.1, "org_loss_at_low_org_factor": -0.1},
             "enable_tactics": ["tactic_overwhelming_fire"]},
            {"modifiers": {"additional_brigade_column_size": 1},
             "unit_bonuses": {"category_army": {"breakthrough": 0.15}},  # (1.19.4) new
             "enable_tactics": ["tactic_blitz"]},
            {"modifiers": {"planning_speed": 0.2},
             "unit_bonuses": {"category_regimental_support_battalions": {"max_organisation": 10, "breakthrough": 0.1}},
             "enable_tactics": ["tactic_backhand_blow"]},
        ],
    },
    {
        "key": "superior_firepower", "name": "Superior Firepower", "folder": "land",
        "tracks": ["infantry", "combat_support", "armor", "operations"],
        "effects": {
            "enable_tactics": ["tactic_overwhelming_fire"],
            "unit_bonuses": {
                "category_line_artillery": {"soft_attack": 0.1},
                "category_support_artillery": {"soft_attack": 0.05},
            },
        },
        "milestones": [
            {"enable_tactics": ["tactic_elastic_defense"], "modifiers": {"supply_consumption_factor": -0.1}},
            {"modifiers": {"additional_brigade_column_size": 1, "planning_decay_rate_factor": -0.1},
             "unit_bonuses": {"category_support_battalions": {"max_organisation": 10}},
             "enable_tactics": ["tactic_barrage"]},
            {"enable_tactics": ["tactic_delay"],
             "unit_bonuses": {
                 "category_army": {"default_morale": 0.1},
                 "category_regimental_support_battalions": {"soft_attack": 0.05, "hard_attack": 0.05},
             }},
            {"enable_tactics": ["tactic_tactical_withdrawal"],
             "unit_bonuses": {"category_army": {"default_morale": 0.2}},
             "modifiers": {"planning_decay_rate_factor": -0.1}},
        ],
    },
    {
        "key": "grand_battleplan", "name": "Grand Battleplan", "folder": "land",
        "tracks": ["infantry", "combat_support", "armor", "operations"],
        "effects": {
            "enable_tactics": ["tactic_planned_attack"],
            "modifiers": {"max_planning": 0.1, "command_power_gain": 0.25},
        },
        "milestones": [
            {"modifiers": {"additional_brigade_column_size": 1, "max_dig_in_factor": 0.05},
             "enable_tactics": ["tactic_elastic_defense"]},
            {"modifiers": {"coordination_bonus": 0.1},
             "unit_bonuses": {"category_regimental_support_battalions": {"defense": 0.1, "entrenchment": 0.2}},
             "enable_tactics": ["tactic_overwhelming_fire"]},
            {"modifiers": {"land_reinforce_rate": 0.02}, "enable_tactics": ["tactic_breakthrough"]},
            {"modifiers": {"coordination_bonus": 0.1, "max_command_power": 30}},
        ],
    },
    {
        "key": "mass_assault", "name": "Mass Assault", "folder": "land",
        "tracks": ["infantry", "combat_support", "armor", "operations"],
        "effects": {
            "modifiers": {"no_supply_grace": 48, "out_of_supply_factor": -0.15},  # (1.19.4) -0.10->-0.15
            "enable_tactics": ["tactic_relentless_assault"],
        },
        "milestones": [
            # (1.19.4) additional_brigade_column_size (5th-battalion-row unlock)
            # REMOVED from this Infantry milestone - moved to the Combat
            # Support milestone below instead. New -0.2 Combat Width
            # reduction added; target category is a judgment call (the patch
            # doesn't name an exact key) - using category_all_infantry per
            # this file's own existing convention for infantry-wide doctrine
            # bonuses (e.g. large_unit_tactics' grand effect above).
            {"enable_tactics": ["tactic_human_wave_tactics"],
             "unit_bonuses": {
                 "category_regimental_support_battalions": {"supply_consumption": -0.02, "default_morale": 0.1},
                 "category_all_infantry": {"combat_width": -0.2},
             }},
            # (1.19.4) out_of_supply_factor/minimum_training_level penalties
            # removed; additional_brigade_column_size (5th-row unlock, moved
            # from the Infantry milestone above) and land_reinforce_rate added.
            {"enable_tactics": ["tactic_elastic_defense"],
             "modifiers": {"additional_brigade_column_size": 1, "land_reinforce_rate": 0.02}},
            {"modifiers": {"land_reinforce_rate": 0.02}, "enable_tactics": ["tactic_overwhelming_fire"]},
            # (1.19.4) dig_in_speed_factor removed; minimum_training_level
            # -0.05->-0.10; new supply_consumption_factor -0.15.
            {"enable_tactics": ["tactic_backhand_blow"],
             "modifiers": {"weekly_casualties_war_support": 0.001, "minimum_training_level": -0.10, "supply_consumption_factor": -0.15}},
        ],
    },
    {
        "key": "special_forces_quantity", "name": "Expanded Special Forces", "folder": "special_forces",
        "tracks": ["special_forces_first", "special_forces_second"],
        "effects": {"modifiers": {"special_forces_cap": 0.04, "special_forces_training_time_factor": -0.2}},
        "milestones": [
            {"modifiers": {"special_forces_cap": 0.04}, "unit_bonuses": {"category_special_forces": {"soft_attack": 0.05}}},
            {"modifiers": {"special_forces_cap": 0.04}, "unit_bonuses": {"category_special_forces": {"max_organisation": 5}}},
        ],
    },
    {
        "key": "special_forces_quality", "name": "Elite Special Forces", "folder": "special_forces",
        "tracks": ["special_forces_first", "special_forces_second"],
        "effects": {
            "unit_bonuses": {"category_special_forces": {"max_organisation": 10}},
            "modifiers": {"special_forces_no_supply_grace": 24},
        },
        "milestones": [
            {"unit_bonuses": {"category_special_forces": {
                "acclimatization_hot_climate_gain_factor": 0.1, "acclimatization_cold_climate_gain_factor": 0.1,
                "soft_attack": 0.05, "breakthrough": 0.05}},
             "modifiers": {"special_forces_cap": 0.02}},
            {"unit_bonuses": {"category_special_forces": {
                "acclimatization_hot_climate_gain_factor": 0.1, "acclimatization_cold_climate_gain_factor": 0.1,
                "soft_attack": 0.05, "defense": 0.05}},
             "modifiers": {"special_forces_cap": 0.02}},
        ],
    },
]

SUBDOCTRINES = [
    # --- Infantry track (9) ---
    {"key": "mobile_infantry", "name": "Mobile Infantry", "tracks": ["infantry"], "xor": [], "requires_technology": None,
     "effects": {"enable_tactics": ["tactic_overwhelming_fire"], "unit_bonuses": {"category_all_infantry": {"breakthrough": 0.1}}},
     "rewards": [
        {"key": "cavalry_charge", "name": "Modernized Cavalry", "effects": {"unit_bonuses": {"recon": {"defense": 0.10, "breakthrough": 0.10}}}},  # (1.19.3) retargeted from category_cavalry
        {"key": "combined_arms_planning", "name": "Infiltration", "effects": {"unit_bonuses": {"category_all_infantry": {"max_organisation": 10, "maximum_speed": 0.05}}}},
        {"key": "decisive_operations", "name": "First Strike Operations", "effects": {"unit_bonuses": {
            "category_vehicle_infantry": {"max_organisation": 20},
            "category_regimental_support_artillery": {"soft_attack": 0.10, "defense": 0.05, "breakthrough": 0.05}}}},  # (1.19.3) soft_attack 0.15->0.10, +defense/breakthrough
        {"key": "delegated_authority", "name": "Delegated Authority", "effects": {"unit_bonuses": {"category_vehicle_infantry": {"default_morale": 0.1, "soft_attack": 0.1}}}},
        {"key": "maneuver_warfare", "name": "Maneuver Warfare", "effects": {"unit_bonuses": {
            "category_all_infantry": {"max_organisation": 10, "maximum_speed": 0.2},
            "mot_fire_support": {"max_organisation": 10, "soft_attack": 0.1}}}},  # (1.19.3) max_organisation 5->10
     ]},
    {"key": "defensive_postures", "name": "Defensive Postures", "tracks": ["infantry"], "xor": [], "requires_technology": None,
     "effects": {"unit_bonuses": {"category_cavalry": {"supply_consumption": -0.01}, "category_all_infantry": {"entrenchment": 0.2}}},
     "rewards": [
        {"key": "improvised_fighting_position", "name": "Improvised Fighting Positions", "effects": {"modifiers": {"dig_in_speed_factor": 0.05},
            "unit_bonuses": {"fire_support": {"supply_consumption": -0.01, "soft_attack": 0.2, "entrenchment": 0.2}}}},  # (1.19.3) +entrenchment
        {"key": "elastic_operations", "name": "Outpost Line", "effects": {"unit_bonuses": {"category_all_infantry": {"max_organisation": 10, "defense": 0.10}}}},
        {"key": "developed_trench_networking", "name": "Strongpoint Network", "effects": {"unit_bonuses": {"category_all_infantry": {"entrenchment": 0.2}}}},
        {"key": "field_emplacements", "name": "Interlocking Fields of Fire", "effects": {"unit_bonuses": {
            "category_all_infantry": {"soft_attack": 0.1},
            "category_regimental_support_artillery": {"soft_attack": 0.1}}}},  # (1.19.3) soft_attack 0.2->0.1
        {"key": "field_construction_training", "name": "Infantry Engineer Training", "effects": {"modifiers": {"dig_in_speed_factor": 0.15}}},
     ]},
    {"key": "large_unit_tactics", "name": "Large Unit Tactics", "tracks": ["infantry"], "xor": [], "requires_technology": None,
     "effects": {"unit_bonuses": {"category_all_infantry": {"supply_consumption": -0.01}}},
     "rewards": [
        {"key": "wide_trench_networks", "name": "Overnight Entrenchment", "effects": {"modifiers": {"dig_in_speed_factor": 0.15}}},  # (1.19.4) 0.10->0.15
        {"key": "flexible_division_structures", "name": "Flexible Division Structures", "effects": {"modifiers": {"unit_infantry_design_cost_factor": -1},
            "unit_bonuses": {"infantry": {"combat_width": -0.2}}}},  # (1.19.4) -0.3->-0.2
        {"key": "unit_knowledge_sharing", "name": "Unit Knowledge Sharing", "effects": {"unit_bonuses": {"category_all_infantry": {"experience_loss_factor": -0.01}}}},
        {"key": "large_front_offensive", "name": "Large Front Offensive", "effects": {"unit_bonuses": {
            "category_all_infantry": {"max_organisation": 10, "soft_attack": 0.1},
            "fire_support": {"breakthrough": 0.1},
            "category_regimental_support_artillery": {"soft_attack": 0.1}},
            "modifiers": {"army_morale": 0.1}}},
        {"key": "motorization_initiative", "name": "Motorization Initiative", "effects": {"unit_bonuses": {
            "category_all_infantry": {"breakthrough": 0.1, "soft_attack": 0.1},
            "category_vehicle_infantry": {"supply_consumption": -0.02, "reliability": 0.1}}}},
     ]},
    {"key": "assault_infantry", "name": "Assault Infantry", "tracks": ["infantry"], "xor": [], "requires_technology": None,
     "effects": {"unit_bonuses": {"artillery": {"soft_attack": 0.2}}},  # (1.19.3) Support Artillery soft_attack 0.1->0.2
     "rewards": [
        {"key": "low_echelon_fire_support", "name": "Low Echelon Fire Support", "effects": {"unit_bonuses": {
            "artillery": {"battalion_mult": [{"category": "category_light_infantry", "soft_attack": 0.2}]}}}},  # (1.19.3) field_guns bonus removed
        {"key": "organic_battalion_fire_support", "name": "Organic Battalion Fire Support", "effects": {"unit_bonuses": {
            "category_regimental_support_artillery": {"soft_attack": 0.1},
            "anti_tank_battery": {"ap_attack": 0.05, "hard_attack": 0.05},
            "anti_air_battery": {"air_attack": 0.05}}}},  # (1.19.3) anti_tank_battery/anti_air_battery 0.1->0.05
        {"key": "integrated_support_batteries", "name": "Infantry Forward Observer Training", "effects": {"unit_bonuses": {
            "category_support_artillery": {"max_organisation": 20, "soft_attack": 0.05},
            "anti_tank": {"max_organisation": 20, "ap_attack": 0.05, "hard_attack": 0.05},
            "anti_air": {"max_organisation": 20, "air_attack": 0.05}}}},
        {"key": "breakthrough_fireteams", "name": "Recon Pull", "effects": {"unit_bonuses": {
            "light_tank_recon": {"max_organisation": 20, "battalion_mult": [
                {"category": "category_all_infantry", "breakthrough": 0.2},
                {"category": "category_all_infantry", "max_organisation": 5, "add": True}]},
            "mot_recon": {"max_organisation": 20, "battalion_mult": [
                {"category": "category_all_infantry", "breakthrough": 0.1},
                {"category": "category_all_infantry", "max_organisation": 5, "add": True}]}}}},
        {"key": "assault_detachments", "name": "Assault Detachments", "effects": {"unit_bonuses": {
            "category_support_artillery": {"supply_consumption": -0.02},
            "category_regimental_support_artillery": {"supply_consumption": -0.01},
            "light_flame_tank": {"battalion_mult": [{"category": "category_all_infantry", "breakthrough": 0.1, "soft_attack": 0.1}]},
            "medium_flame_tank": {"battalion_mult": [{"category": "category_all_infantry", "breakthrough": 0.1, "soft_attack": 0.1}]},
            "heavy_flame_tank": {"battalion_mult": [{"category": "category_all_infantry", "breakthrough": 0.1, "soft_attack": 0.1}]}}}},
     ]},
    {"key": "mounted_infantry", "name": "Mounted Infantry", "tracks": ["infantry"], "xor": [], "requires_technology": None,
     "effects": {"unit_bonuses": {"category_cavalry": {"soft_attack": 0.1, "breakthrough": 0.1}},
                 "modifiers": {"unit_cavalry_design_cost_factor": -1}},
     "rewards": [
        {"key": "dragoon_traditions", "name": "Dragoon Traditions", "effects": {"unit_bonuses": {"category_cavalry": {"breakthrough": 0.20, "defense": 0.1}}}},
        {"key": "mounted_skirmish_groups", "name": "Regimental Scout Troop", "effects": {"unit_bonuses": {
            "recon": {"max_organisation": 10, "soft_attack": 0.2, "battalion_mult": [
                {"category": "category_light_infantry", "soft_attack": 0.1, "defense": 0.1},
                {"category": "category_light_infantry", "max_organisation": 5, "add": True}]},
            "category_cavalry": {"max_organisation": 5}}}},
        {"key": "anti_mechanized_cavalry_groups", "name": "Anti-Mechanized Cavalry Groups", "effects": {"unit_bonuses": {"category_cavalry": {"hard_attack": 0.2, "ap_attack": 0.2}}}},
        {"key": "beasts_of_war", "name": "Beasts of War", "effects": {"unit_bonuses": {
            "category_cavalry": {"maximum_speed": 0.4},
            "recon": {"maximum_speed": 0.4, "battalion_mult": [{"category": "category_cavalry", "max_strength": 5, "add": True}]}}}},  # (1.19.3) speed 0.5->0.4; flat +0.05 max_strength replaced by +5 flat HP via recon battalion_mult
        {"key": "limbered_combat_support", "name": "Limbered Combat Support", "effects": {"unit_bonuses": {
            "artillery_brigade": {"maximum_speed": 1.0}, "anti_tank_brigade": {"maximum_speed": 1.0},
            "anti_air_brigade": {"maximum_speed": 1.0}, "rocket_artillery_brigade": {"maximum_speed": 1.0}}}},  # (1.19.3) speed 0.5->1.0
     ]},
    {"key": "commandos", "name": "Individual Excellence", "tracks": ["infantry"], "xor": [], "requires_technology": None,
     "effects": {"unit_bonuses": {"logistics_company": {"battalion_mult": [{"category": "category_light_infantry", "max_strength": 5, "add": True}]}}},
     "rewards": [
        {"key": "isolated_combat_elements", "name": "Isolated Combat Elements", "effects": {"unit_bonuses": {
            "category_light_infantry": {"supply_consumption": -0.01, "reliability": 0.05},
            "field_hospital": {"casualty_trickleback": 0.05},
            "helicopter_brigade": {"casualty_trickleback": 0.05},
            "helicopter_field_hospital": {"casualty_trickleback": 0.05},
            "category_regimental_support_artillery": {"supply_consumption": -0.01, "soft_attack": 0.05}}}},
        {"key": "security_zone_operations", "name": "Dispersed Element Coordination", "effects": {"unit_bonuses": {
            "signal_company": {"battalion_mult": [{"category": "category_all_infantry", "defense": 0.1}]},
            "logistics_company": {"battalion_mult": [{"category": "category_vehicle_infantry", "max_strength": 2.5, "add": True}]},  # (1.19.4) 5->2.5
            "category_vehicle_infantry": {"reliability": 0.05, "breakthrough": 0.1}}}},
        {"key": "rigorous_training_regimen", "name": "Rigorous Training Regime", "effects": {"unit_bonuses": {
            "recon": {"battalion_mult": [{"category": "category_all_infantry", "soft_attack": 0.1}]},
            "mot_recon": {"battalion_mult": [{"category": "category_all_infantry", "soft_attack": 0.1}]},
            "light_tank_recon": {"battalion_mult": [{"category": "category_all_infantry", "soft_attack": 0.1}]},
            "anti_tank_battery": {"battalion_mult": [{"category": "category_light_infantry", "hard_attack": 0.1}]},
            "infantry": {"desert": {"attack": 0.05, "movement": 0.1}, "jungle": {"attack": 0.05, "movement": 0.1}, "hills": {"attack": 0.05, "movement": 0.1}}}}},
        {"key": "field_intel_retrieval", "name": "Field Intelligence Gathering", "effects": {"modifiers": {"intel_from_combat_factor": 0.15}}},
        {"key": "integrated_assaults", "name": "Integrated Assaults", "effects": {"unit_bonuses": {
            "category_all_infantry": {"soft_attack": 0.1, "breakthrough": 0.1},
            "category_regimental_support_artillery": {"breakthrough": 0.15},
            "fire_support": {"breakthrough": 0.15}, "mot_fire_support": {"breakthrough": 0.15}}}},
     ]},
    {"key": "irregulars", "name": "Irregulars", "tracks": ["infantry"], "xor": [], "requires_technology": None,
     "effects": {"unit_bonuses": {
         "irregular_infantry": {"defense": 0.1, "supply_consumption": -0.05},
         "militia": {"defense": 0.1, "supply_consumption": -0.01}}},
     "rewards": [
        {"key": "service_by_lot", "name": "Service By Lot", "effects": {"modifiers": {"mobilization_speed": 0.05}}},
        {"key": "partisan_regiments", "name": "Partisan Regiments", "effects": {"unit_bonuses": {
            "irregular_infantry": {"combat_width": -0.4}, "militia": {"combat_width": -0.4},
            "category_light_infantry": {"defense": 0.1}}}},
        {"key": "improvised_officer_groups", "name": "Improvised Officer Groups", "effects": {"unit_bonuses": {"category_light_infantry": {"max_organisation": 10, "soft_attack": 0.1, "breakthrough": 0.1}}}},
        {"key": "levee_en_masse", "name": "Levée En Masse", "effects": {"modifiers": {"conscription": 0.02, "mobilization_speed": 0.05}}},
        {"key": "standardization_efforts", "name": "Standardization Efforts", "effects": {"unit_bonuses": {"category_light_infantry": {"max_organisation": 10, "soft_attack": 0.1}}}},
     ]},
    {"key": "peoples_war", "name": "People's Militia", "tracks": ["infantry"], "xor": [], "requires_technology": None,
     "effects": {"enable_tactics": ["tactic_guerrilla_tactics"], "unit_bonuses": {"militia": {"soft_attack": 0.1, "defense": 0.2}}},
     "rewards": [
        {"key": "revolutionary_base_area", "name": "Revolutionary Base Area", "effects": {"unit_bonuses": {
            "militia": {"defense": 0.1, "supply_consumption": -0.02}, "category_light_infantry": {"max_organisation": 5}}}},
        {"key": "destruction_over_land_gains", "name": "Destruction over Land Gains", "effects": {"unit_bonuses": {
            "category_light_infantry": {"default_morale": 0.1}, "militia": {"equipment_capture_factor": 0.01},
            "field_guns": {"soft_attack": 0.10, "breakthrough": 0.10}}}},  # (1.19.3) soft_attack 0.15->0.10, +breakthrough
        {"key": "quick_decision_offensive_warfare", "name": "Quick Decision Offensive Warfare", "effects": {"unit_bonuses": {"militia": {"initiative": 0.015, "max_organisation": 10, "breakthrough": 0.2}}}},
        {"key": "people_not_things", "name": "People, not Things", "effects": {"unit_bonuses": {"category_light_infantry": {"soft_attack": 0.1, "max_strength": 0.15}}}},
     ]},
    {"key": "great_war_infantry", "name": "Great War Infantry", "tracks": ["infantry"], "xor": [], "requires_technology": None,
     "effects": {"unit_bonuses": {"category_cavalry": {"supply_consumption": -0.02}, "category_light_infantry": {"defense": 0.1}},
                 "modifiers": {"production_speed_bunker_factor": 0.25}},
     "rewards": [
        {"key": "traverse_digging", "name": "Zig-zag Trenches", "effects": {"modifiers": {"dig_in_speed_factor": 0.05}, "unit_bonuses": {
            "fire_support": {"soft_attack": 0.1, "defense": 0.1},
            "engineer": {"battalion_mult": [{"category": "category_light_infantry", "entrenchment": 0.05, "add": True}]}}}},
        {"key": "sapping_operations", "name": "Communication Trenches", "effects": {"unit_bonuses": {
            "category_light_infantry": {"defense": 0.1}, "field_hospital": {"casualty_trickleback": 0.1}}}},
        {"key": "centralized_artillery_control", "name": "Creeping Barrages", "effects": {"unit_bonuses": {
            "artillery": {"soft_attack": 0.1, "battalion_mult": [{"category": "category_light_infantry", "soft_attack": 0.1, "breakthrough": 0.10}]},  # (1.19.3) breakthrough 0.05->0.10
            "category_regimental_support_artillery": {"soft_attack": 0.1}}}},  # (1.19.3) soft_attack 0.2->0.1
        {"key": "field_fortification_emphasis", "name": "Overhead Cover", "effects": {"unit_bonuses": {"category_light_infantry": {"reliability": 0.05, "defense": 0.05, "max_organisation": 5}}}},
        {"key": "redoubt_networks", "name": "Redoubt Networks", "effects": {"modifiers": {"dig_in_speed_factor": 0.10}, "unit_bonuses": {"category_all_infantry": {"max_entrenchment": 5}}}},  # (1.19.3) +5 Max Entrenchment (new field, not applied in logic/stats.py - matches "entrenchment"'s own existing untracked treatment)
     ]},

    # --- Combat Support track (8 distinct; mobile_recon_and_assault_no_lar dropped, DLC version kept) ---
    {"key": "fire_concentration", "name": "Fire Concentration", "tracks": ["combat_support"], "xor": [], "requires_technology": None,
     "effects": {"enable_tactics": ["tactic_overwhelming_fire"], "unit_bonuses": {"category_line_artillery": {"breakthrough": 0.10, "max_organisation": 10}}},  # (1.19.3) defense 0.05->breakthrough 0.10; (1.19.4) max_organisation 5->10
     "rewards": [
        {"key": "predicted_fire", "name": "Predicted Fire", "effects": {"unit_bonuses": {"category_line_artillery": {"breakthrough": 0.10}}}},  # (1.19.3) defense 0.05->breakthrough 0.10
        {"key": "standing_barrage", "name": "Prepared Gun Pits", "effects": {"unit_bonuses": {"artillery_brigade": {"combat_width": -0.8}, "rocket_artillery_brigade": {"combat_width": -0.8}}}},
        {"key": "artillery_groups", "name": "Battery Local Security", "effects": {"unit_bonuses": {
            "category_support_artillery": {"soft_attack": 0.10, "defense": 0.1},
            "category_line_artillery": {"soft_attack": 0.10, "defense": 0.1}}}},  # (1.19.3) breakthrough->defense, soft_attack 0.05->0.10, Infantry Guns/Rocket Battery bonus removed
        {"key": "dedicated_air_support", "name": "Centralized Anti-Aircraft Support", "effects": {"unit_bonuses": {"category_anti_air": {"air_attack": 0.1}}}},
        {"key": "weakpoint_studies", "name": "Flanking Fire Emplacement", "effects": {"unit_bonuses": {
            "anti_tank_brigade": {"ap_attack": 0.1, "hard_attack": 0.1},
            "category_regimental_support_artillery": {"defense": 0.1, "breakthrough": 0.1}}}},  # (1.19.3) artillery_brigade/rocket_artillery_brigade bonus removed, Infantry Guns/Rocket Battery +10% Defense/Breakthrough added
     ]},
    {"key": "anti_tank_frontline", "name": "Anti-Tank Frontline", "tracks": ["combat_support"], "xor": [], "requires_technology": None,
     "effects": {"unit_bonuses": {"engineer": {"battalion_mult": [{"category": "category_line_artillery", "entrenchment": 0.2, "add": True}]}}},
     "rewards": [
        {"key": "pakfront", "name": "Pakfront", "effects": {"unit_bonuses": {
            "anti_tank_brigade": {"ap_attack": 0.1}, "anti_tank_battery": {"ap_attack": 0.1}, "anti_tank": {"ap_attack": 0.1}}}},  # (1.19.3) Anti-Tank Battery brought in line with Line Anti-Tank (ap_attack 0.1); Anti-Tank Support (divisional support company) now gets the same bonus
        {"key": "emplacement_rotation", "name": "Emplacement Rotation", "effects": {"unit_bonuses": {"anti_tank_brigade": {"defense": 0.2, "max_organisation": 10}}}},
        {"key": "weakpoint_studies", "name": "Weak-point Studies", "effects": {"unit_bonuses": {"anti_tank_brigade": {"ap_attack": 0.1, "hard_attack": 0.1, "soft_attack": 0.2}}}},
        {"key": "offensive_deployments", "name": "Offensive Deployment", "effects": {"unit_bonuses": {"mot_anti_tank_brigade": {"breakthrough": 0.2, "ap_attack": 0.2}}}},
        {"key": "assault_anti_tank", "name": "Direct Fire Bunker-Busting", "effects": {"unit_bonuses": {"mot_anti_tank_brigade": {"soft_attack": 0.2, "hard_attack": 0.2}}}},
     ]},
    {"key": "flying_batteries", "name": "Flying Batteries", "tracks": ["combat_support"], "xor": [], "requires_technology": None,
     "effects": {"unit_bonuses": {"category_line_artillery": {"soft_attack": 0.1}}},
     "rewards": [
        {"key": "deployment_drills", "name": "Deployment Drills", "effects": {"unit_bonuses": {
            "mot_rocket_artillery_brigade": {"max_organisation": 10, "soft_attack": 0.05, "breakthrough": 0.1},
            "motorized_rocket_brigade": {"max_organisation": 10, "soft_attack": 0.05, "breakthrough": 0.1},
            "mot_artillery_brigade": {"max_organisation": 10, "soft_attack": 0.05, "breakthrough": 0.1}}}},  # (1.19.3) Motorized Heavy Weapons Company bonus removed entirely; remaining units now also get +5% Soft Attack/+10% Breakthrough
        {"key": "counter_battery_tasks", "name": "Counter-battery Tasks", "effects": {"unit_bonuses": {
            "recon": {"battalion_mult": [{"category": "category_line_artillery", "soft_attack": 0.05, "defense": 0.1}], "recon": 0.25},
            "mot_recon": {"battalion_mult": [{"category": "category_line_artillery", "soft_attack": 0.05, "defense": 0.1}], "recon": 0.25}}}},
        {"key": "ballistics_corrections", "name": "Armored Forward Observer Vehicles", "effects": {"unit_bonuses": {
            "armored_signal": {"battalion_mult": [
                {"category": "category_line_artillery", "supply_consumption": -0.01, "add": True},
                {"category": "category_line_artillery", "initiative": 0.02},
                {"category": "category_line_artillery", "max_strength": 1.0, "add": True}]}}}},  # (1.19.3) +Strength to Line Artillery (final value 1.0 - the patch's stated "from 0.8" prior value wasn't present in our data at all, a likely original-compile gap, not something this patch itself changed)
        {"key": "mobile_barrages", "name": "Fast Unlimbering", "effects": {"unit_bonuses": {"category_line_artillery": {"default_morale": 0.05, "breakthrough": 0.05}}}},
        {"key": "wide_dispersal_positions", "name": "Widely Dispersed Batteries", "effects": {"unit_bonuses": {
            "mot_rocket_artillery_brigade": {"max_organisation": 10, "soft_attack": 0.05, "defense": 0.1},
            "motorized_rocket_brigade": {"max_organisation": 10, "soft_attack": 0.05, "defense": 0.1},
            "mot_artillery_brigade": {"max_organisation": 10, "soft_attack": 0.05, "defense": 0.1}}}},  # (1.19.3) now also gives +5% Soft Attack/+10% Defense
     ]},
    {"key": "air_cavalry", "name": "Air Cavalry", "tracks": ["combat_support"], "xor": [], "requires_technology": None,
     "effects": {},
     "rewards": [
        {"key": "airborne_observers", "name": "Heliborne Observers", "effects": {"unit_bonuses": {"helicopter_recon": {"battalion_mult": [{"category": "category_artillery", "soft_attack": 0.1}], "max_organisation": 10}}}},
        {"key": "service_and_support", "name": "Service & Support", "effects": {"unit_bonuses": {
            "maintenance_company": {"battalion_mult": [{"category": "category_helicopter_support_companies", "max_strength": 0.5, "add": True}]}}}},  # (1.19.3) flat 0.03 max_strength replaced by Maintenance Company battalion adjuster, +0.5 flat HP each
        {"key": "rescue_liasions", "name": "Rescue Liaisons", "effects": {"unit_bonuses": {"helicopter_field_hospital": {
            "battalion_mult": [{"category": "category_all_infantry", "max_strength": 0.05, "default_morale": 0.05}],
            "max_organisation": 5, "casualty_trickleback": 0.05}}}},
        {"key": "transport_assault", "name": "Transport-Assault", "effects": {"unit_bonuses": {"helicopter_transport": {
            "battalion_mult": [{"category": "category_light_infantry", "maximum_speed": 0.2, "breakthrough": 0.05}],
            "breakthrough": 0.05, "max_organisation": 10}}}},
        {"key": "intervention_units", "name": "Intervention Units", "effects": {"unit_bonuses": {"helicopter_brigade": {
            "battalion_mult": [{"category": "category_all_infantry", "soft_attack": 0.1}], "max_organisation": 10}}}},
     ]},
    {"key": "mobile_recon_and_assault", "name": "Mobile Recon & Assault", "tracks": ["combat_support"], "xor": [], "requires_technology": None,
     "effects": {"unit_bonuses": {"armored_car": {"max_organisation": 3}, "light_armor": {"max_organisation": 5}}},
     "rewards": [
        {"key": "motorization_support", "name": "Organic Motorized Supply", "effects": {"unit_bonuses": {
            "category_mobile_and_mobile_combat_sup": {"maximum_speed": 0.1, "default_morale": 0.1},
            "mot_fire_support": {"max_organisation": 10, "soft_attack": 0.1},
            "logistics_company": {"supply_consumption": -0.05}}}},  # (1.19.4) new
        {"key": "long_range_reconnaissance", "name": "Long Range Reconnaissance", "effects": {"unit_bonuses": {"category_recon": {"maximum_speed": 0.15}}}},
        {"key": "mobile_operational_deployments", "name": "Mobile Operational Deployment", "effects": {"unit_bonuses": {
            "light_tank_recon": {"battalion_mult": [{"category": "category_all_armor", "breakthrough": 0.1}]},
            "mot_artillery_brigade": {"soft_attack": 0.05}}}},
        {"key": "self_propelled_support_elements", "name": "Fire On The Move", "effects": {"unit_bonuses": {
            "category_self_propelled_artillery": {"soft_attack": 0.10},
            "category_self_propelled_anti_air": {"air_attack": 0.15, "soft_attack": 0.05},
            "category_tank_destroyers": {"hard_attack": 0.1, "ap_attack": 0.03},
            "armored_car": {"breakthrough": 0.2, "default_morale": 0.2}}}},
        {"key": "deep_reconnaissance_focus", "name": "Deep Reconnaissance Focus", "effects": {"unit_bonuses": {
            "category_recon": {"maximum_speed": 0.1}, "light_tank_recon": {"recon": 0.2, "breakthrough": 0.1},
            "category_tank_destroyer_regimental_support": {"hard_attack": 0.05},
            "category_self_propelled_anti_air_regimental_support": {"air_attack": 0.05}}}},  # (1.19.3) breakthrough 0.2 on both TD-RS/SPAA-RS changed to +5% Hard Attack / +5% Air Attack respectively
     ]},
    {"key": "self_propelled_support", "name": "Self-propelled Support", "tracks": ["combat_support"], "xor": [], "requires_technology": None,
     "effects": {"unit_bonuses": {
         "category_self_propelled_artillery": {"soft_attack": 0.05},
         "category_self_propelled_anti_air": {"air_attack": 0.05}, "category_tank_destroyers": {"hard_attack": 0.05}}},  # (1.19.3) self_propelled_artillery/anti_air soft/air attack 0.1->0.05
     "rewards": [
        {"key": "mobile_battery_management_platoons", "name": "Mobile Fire Direction Center", "effects": {"unit_bonuses": {
            "category_self_propelled_artillery": {"max_organisation": 10}, "category_self_propelled_anti_air": {"max_organisation": 10},
            "category_tank_destroyers": {"max_organisation": 10}}}},
        {"key": "screening_attacks", "name": "Time-On-Target Fire Missions", "effects": {"unit_bonuses": {
            "recon": {"battalion_mult": [{"category": "category_self_propelled_artillery", "soft_attack": 0.05, "default_morale": 0.1}]},
            "mot_recon": {"battalion_mult": [{"category": "category_self_propelled_artillery", "soft_attack": 0.05, "default_morale": 0.1}]},
            "light_tank_recon": {"battalion_mult": [{"category": "category_self_propelled_artillery", "soft_attack": 0.05, "default_morale": 0.1}]}}}},  # (1.19.3) soft_attack 0.1->0.05
        {"key": "all_terrain_mobility", "name": "All-terrain Mobility", "effects": {"unit_bonuses": {
            "category_self_propelled_artillery": {"maximum_speed": 0.1}, "category_self_propelled_anti_air": {"maximum_speed": 0.1},
            "category_tank_destroyers": {"maximum_speed": 0.1}}}},  # (1.19.3) speed 0.3->0.1
        {"key": "multirole_support_vehicles", "name": "Multi-role Support Vehicles", "effects": {"unit_bonuses": {
            "category_tank_destroyer_regimental_support": {"max_organisation": 5, "hard_attack": 0.05},
            "category_self_propelled_anti_air_regimental_support": {"max_organisation": 5, "air_attack": 0.05}}}},  # (1.19.3) org 10->5, hard/air_attack 0.1->0.05, breakthrough 0.2 removed
        {"key": "shoot_and_scoot", "name": "Shoot & Scoot", "effects": {"unit_bonuses": {
            "category_self_propelled_artillery": {"max_organisation": 5, "default_morale": 0.15, "soft_attack": 0.05},
            "category_self_propelled_anti_air": {"max_organisation": 5, "default_morale": 0.15, "air_attack": 0.05},
            "category_tank_destroyers": {"max_organisation": 5, "default_morale": 0.15, "hard_attack": 0.05}}}},
     ]},
    {"key": "siege_artillery", "name": "Siege Artillery", "tracks": ["combat_support"], "xor": [], "requires_technology": None,
     "effects": {"unit_bonuses": {"super_heavy_artillery": {"battalion_mult": [{"category": "category_army", "soft_attack": 0.1, "defense": 0.1}]}},
                 "equipment_bonus": {"railway_gun_equipment": {"railway_gun_attack": 0.25}, "super_heavy_railway_gun_equipment": {"railway_gun_attack": 0.25}}},
     "rewards": [
        {"key": "fortress_busters", "name": "Fortress Busters", "effects": {"unit_bonuses": {
            "super_heavy_artillery": {"fort": {"attack": 0.25}}, "self_propelled_super_heavy_artillery": {"fort": {"attack": 0.25}}}}},
        {"key": "improved_transport_preparation", "name": "Improved Transport Preparation", "effects": {
            "unit_bonuses": {
                "category_line_artillery": {"default_morale": 0.1},
                "super_heavy_artillery": {"recovery_rate": 0.1},
                "self_propelled_super_heavy_artillery": {"recovery_rate": 0.1}},  # (1.19.3) plains movement bonus replaced with 0.1 Recovery Rate
            "equipment_bonus": {
                "railway_gun_equipment": {"railway_gun_hours_between_redistribution": -0.5},
                "super_heavy_railway_gun_equipment": {"railway_gun_hours_between_redistribution": -0.5}}}},
        {"key": "precomputed_firing_data", "name": "Pre-computed Firing Data", "effects": {"unit_bonuses": {
            "super_heavy_artillery": {"max_organisation": 10, "defense": 0.2},
            "self_propelled_super_heavy_artillery": {"max_organisation": 10, "defense": 0.2}}}},
        {"key": "urban_strongpoint_sieges", "name": "Advanced Fire Correction", "effects": {"unit_bonuses": {
            "category_artillery": {"soft_attack": 0.05},
            "super_heavy_artillery": {"urban": {"attack": 0.1, "defence": 0.1}}, "self_propelled_super_heavy_artillery": {"urban": {"attack": 0.1, "defence": 0.1}},
            "fire_support": {"soft_attack": 0.1}, "category_regimental_support_artillery": {"soft_attack": 0.05}}}},  # (1.19.3) urban attack 0.2->0.1, +urban defence 0.1; Infantry Guns & Rocket Battery soft_attack 0.1->0.05
        {"key": "mobile_artillery_command", "name": "Mobile Artillery Command", "effects": {
            "unit_bonuses": {
                "category_support_artillery": {"max_organisation": 10},
                "self_propelled_super_heavy_artillery": {"max_organisation": 10, "maximum_speed": 0.5}},
            "equipment_bonus": {"railway_gun_equipment": {"maximum_speed": 1}, "super_heavy_railway_gun_equipment": {"maximum_speed": 1}}}},
     ]},
    {"key": "field_engineering", "name": "Field Engineering", "tracks": ["combat_support"], "xor": [], "requires_technology": None,
     "effects": {"unit_bonuses": {
         "engineer": {"river": {"movement": 0.2}, "forest": {"movement": 0.2}},
         "assault_engineer": {"river": {"movement": 0.2}, "forest": {"movement": 0.2}},
         "pioneer_support": {"river": {"movement": 0.2}, "forest": {"movement": 0.2}}}},
     "rewards": [
        {"key": "rapid_fire_lane_clearance", "name": "Rapid Fire Lane Clearance", "effects": {"unit_bonuses": {
            "engineer": {"max_organisation": 5, "battalion_mult": [{"category": "category_all_infantry", "entrenchment": 0.1, "add": True}]},
            "maintenance_company": {"max_organisation": 5}}}},
        {"key": "sapper_fieldcraft", "name": "Sapper Fieldcraft", "effects": {"unit_bonuses": {
            "engineer": {"max_strength": 0.25, "defense": 0.1}, "maintenance_company": {"max_strength": 0.25}}}},
        {"key": "engineerdug_gun_emplacements", "name": "Engineer-dug Gun Emplacements", "effects": {"unit_bonuses": {
            "engineer": {"battalion_mult": [
                {"category": "category_artillery", "soft_attack": 0.1, "defense": 0.1},
                {"category": "category_all_infantry", "soft_attack": 0.05}]},
            "field_guns": {"soft_attack": 0.1, "defense": 0.1}}}},
        {"key": "smoke_projector_training", "name": "Smoke Projector Training", "effects": {"unit_bonuses": {
            "engineer": {"breakthrough": 0.5},
            "maintenance_company": {"supply_consumption": -0.01, "battalion_mult": [{"category": "category_tanks", "reliability": 0.05, "strength": 0.05}]}}}},
        {"key": "charge_and_flame", "name": "Flames & Satchel Charges", "effects": {"unit_bonuses": {
            "engineer": {"max_organisation": 5, "soft_attack": 0.05, "hard_attack": 1},
            "maintenance_company": {"max_organisation": 5}, "fire_support": {"max_organisation": 5, "breakthrough": 0.1}}}},
     ]},

    # --- Armor track (6 distinct; armored_spearhead_no_lar and armored_cavalry_no_lar dropped, DLC versions kept) ---
    {"key": "armored_spearhead", "name": "Armored Spearhead", "tracks": ["armor"], "xor": [], "requires_technology": None,
     "effects": {"enable_tactics": ["tactic_breakthrough"]},
     "rewards": [
        {"key": "force_concentration", "name": "Point of Main Effort", "effects": {"unit_bonuses": {"category_tanks": {"max_organisation": 2, "default_morale": 0.05}}}},
        {"key": "armored_breakthrough_exploits", "name": "Breakthrough Exploitation", "effects": {"unit_bonuses": {"category_all_armor": {"breakthrough": 0.1}}}},
        {"key": "local_reserves", "name": "Local Reserves", "effects": {"unit_bonuses": {
            "armored_car": {"default_morale": 0.1, "max_organisation": 7}, "light_armor": {"default_morale": 0.1, "max_organisation": 3},
            "category_self_propelled_anti_air_regimental_support": {"max_organisation": 5, "air_attack": 0.05}}}},  # (1.19.3) SPAA-RS org bonus 10->5
        {"key": "tactical_reconnaissance", "name": "Strong Point Bypassing", "effects": {"unit_bonuses": {"category_all_armor": {"breakthrough": 0.1}}}},
        {"key": "assault_detachments", "name": "Flank Protection", "effects": {"unit_bonuses": {
            "armored_car": {"default_morale": 0.2, "max_organisation": 3, "breakthrough": 0.2},
            "category_tanks": {"max_organisation": 3, "breakthrough": 0.2}}}},
     ]},
    {"key": "armored_infantry_support", "name": "Armored Infantry Support", "tracks": ["armor"], "xor": [], "requires_technology": None,
     "effects": {"enable_tactics": ["tactic_blitz"]},
     "rewards": [
        {"key": "mobile_reserves", "name": "Assault Overrun", "effects": {"unit_bonuses": {
            "medium_armor": {"breakthrough": 0.05, "soft_attack": 0.1}, "heavy_armor": {"breakthrough": 0.05, "soft_attack": 0.1}}}},
        {"key": "armored_cohorts", "name": "Armored Cohorts", "effects": {"unit_bonuses": {
            "medium_armor": {"max_organisation": 5}, "heavy_armor": {"max_organisation": 5},
            "category_tank_destroyer_regimental_support": {"max_organisation": 5}}}},  # (1.19.3) Piercing (ap_attack) bonus removed for TD-Regimental Support
        {"key": "maintenance_routines", "name": "Maintenance Routines", "effects": {"unit_bonuses": {
            "armored_maintenance": {"battalion_mult": [{"category": "category_all_armor", "max_strength": 0.15, "add": True}]}}}},
        {"key": "fuel_rationing", "name": "Fuel Rationing", "effects": {"unit_bonuses": {"heavy_armor": {"supply_consumption": -0.08}}}},
        {"key": "mobile_armored_strongpoints", "name": "Mobile Armored Strongpoints", "effects": {"unit_bonuses": {
            "category_all_infantry": {"breakthrough": 0.05}, "heavy_armor": {"breakthrough": 0.1},
            "heavy_sp_anti_air_support": {"air_attack": 0.05}}}},  # (1.19.3) air_attack 0.1->0.05, +5 Organization bonus removed
     ]},
    {"key": "streamlined_deployment", "name": "Streamlined Deployment", "tracks": ["armor"], "xor": [], "requires_technology": None,
     "effects": {"unit_bonuses": {"category_all_armor": {"soft_attack": 0.1, "breakthrough": 0.1}}},
     "rewards": [
        {"key": "flexible_armored_battalions", "name": "Army Mechanization Drive", "effects": {
            "modifiers": {"unit_medium_armor_design_cost_factor": -0.5, "unit_light_armor_design_cost_factor": -0.5},
            "unit_bonuses": {"light_tank_recon": {"battalion_mult": [{"category": "category_all_armor", "max_organisation": 2, "add": True}]}}}},
        {"key": "mechanized_wave", "name": "Mechanized Wave", "effects": {"unit_bonuses": {
            "mechanized": {"max_organisation": 5, "default_morale": 0.1}, "category_all_armor": {"default_morale": 0.05}}}},
        {"key": "tank_desant", "name": "Tank Desant", "effects": {"unit_bonuses": {
            "armored_signal": {"battalion_mult": [{"category": "category_light_infantry", "maximum_speed": 0.05}]},
            "light_tank_recon": {"battalion_mult": [{"category": "category_light_infantry", "maximum_speed": 0.05}]}}}},
        {"key": "full_front_deployment", "name": "Austere Logistics", "effects": {"unit_bonuses": {"category_all_armor": {"reliability": 0.05, "supply_consumption": -0.02}}}},
        {"key": "continuous_offensives", "name": "Continuous Offensives", "effects": {"unit_bonuses": {"category_all_armor": {"default_morale": 0.05, "max_organisation": 3, "breakthrough": 0.1}}}},
     ]},
    {"key": "mobile_defense", "name": "Mobile Defense", "tracks": ["armor"], "xor": [], "requires_technology": None,
     "effects": {"unit_bonuses": {
         "armored_engineer": {"battalion_mult": [{"category": "category_all_armor", "entrenchment": 0.02, "add": True}]},
         "category_all_armor": {"defense": 0.1}}},
     "rewards": [
        {"key": "mechanized_offensive", "name": "Battle Taxis", "effects": {"unit_bonuses": {"mechanized": {"defense": 0.1, "soft_attack": 0.1}}}},
        {"key": "advance_under_fire", "name": "Advance Under Fire", "effects": {"unit_bonuses": {
            "light_armor": {"breakthrough": 0.1, "default_morale": 0.2}, "medium_armor": {"breakthrough": 0.1, "default_morale": 0.1}}}},
        {"key": "attached_support", "name": "Tracked Combat Support", "effects": {"unit_bonuses": {
            "assault_engineer": {"max_organisation": 10}, "armored_engineer": {"max_organisation": 10}, "armored_signal": {"max_organisation": 10},
            "category_self_propelled_anti_air_regimental_support": {"max_organisation": 10}}}},  # (1.19.3) +5% Air Attack for SPAA-RS removed
        {"key": "combined_anti_armor", "name": "Combined Anti-armor", "effects": {"unit_bonuses": {
            "anti_tank": {"battalion_mult": [{"category": "category_all_armor", "hard_attack": 0.05, "ap_attack": 0.05}]},
            "category_tank_destroyer_regimental_support": {"max_organisation": 10}}}},  # (1.19.3) TD-RS org bonus increased to +10, hard_attack/ap_attack bonuses removed
        {"key": "tank_on_tank_engagement", "name": "Tank-on-Tank Engagement", "effects": {"unit_bonuses": {"category_all_armor": {"hard_attack": 0.1, "soft_attack": 0.1, "ap_attack": 0.05}}}},
     ]},
    {"key": "armored_cavalry", "name": "Armored Cavalry", "tracks": ["armor"], "xor": [], "requires_technology": None,
     "effects": {"unit_bonuses": {"armored_car": {"max_organisation": 5, "defense": 0.1}, "mechanized": {"max_organisation": 5, "defense": 0.05}}},
     "rewards": [
        {"key": "cruiser_tanks", "name": "Cruiser Tanks", "effects": {"unit_bonuses": {"light_armor": {"maximum_speed": 0.1, "max_organisation": 5, "breakthrough": 0.05}}}},
        {"key": "quick_response_force", "name": "Motorized Security Forces", "effects": {"unit_bonuses": {
            "motorized_military_police": {"battalion_mult": [{"category": "category_vehicle_infantry", "suppression_factor": 0.05}]},
            "armored_car": {"suppression_factor": 0.2}}}},
        {"key": "speed_as_armour", "name": "Speed as Armour", "effects": {"unit_bonuses": {
            "light_armor": {"maximum_speed": 0.05, "breakthrough": 0.05},
            "armored_car": {"maximum_speed": 0.05, "breakthrough": 0.1, "soft_attack": 0.1},
            "mechanized": {"maximum_speed": 0.05, "breakthrough": 0.05}}}},
        {"key": "fighting_reconnaissance", "name": "Fighting Reconnaissance", "effects": {"unit_bonuses": {
            "armored_car_recon": {"max_organisation": 3, "soft_attack": 0.05}, "light_tank_recon": {"max_organisation": 2, "soft_attack": 0.05},
            "anti_tank_battery": {"ap_attack": 0.10}, "mot_fire_support": {"max_organisation": 5, "soft_attack": 0.05, "default_morale": 0.1}}}},
        {"key": "sustained_deployments", "name": "External Stowage", "effects": {"unit_bonuses": {
            "armored_car": {"max_organisation": 5, "soft_attack": 0.05, "default_morale": 0.2},
            "light_armor": {"max_organisation": 5, "soft_attack": 0.05, "hard_attack": 0.1, "default_morale": 0.15},
            "mechanized": {"max_organisation": 5, "soft_attack": 0.05, "default_morale": 0.1},
            "motorized": {"max_organisation": 5, "soft_attack": 0.05, "default_morale": 0.1}}}},
     ]},
    {"key": "tank_destroyer_force", "name": "Tank Destroyer Force", "tracks": ["armor"], "xor": [], "requires_technology": None,
     "effects": {"unit_bonuses": {"category_all_armor": {"defense": 0.1, "hard_attack": 0.1, "ap_attack": 0.1}}},
     "rewards": [
        {"key": "mobile_anti_tank", "name": "Mobile Anti-Tank Reserves", "effects": {"unit_bonuses": {"mot_anti_tank_brigade": {"max_organisation": 8, "hard_attack": 0.1, "ap_attack": 0.1}}}},
        {"key": "committed_operational_units", "name": "Organic Combat Engineer Platoons", "effects": {"unit_bonuses": {
            "assault_engineer": {"battalion_mult": [{"category": "category_tank_destroyers", "reliability": 0.02, "soft_attack": 0.05, "hard_attack": 0.1}]}}}},
        {"key": "redeployment_priority", "name": "Rapid Riposte", "effects": {"unit_bonuses": {"category_tank_destroyers": {"supply_consumption": -0.02, "default_morale": 0.1}}}},
        {"key": "independent_counterattacks", "name": "Independent Counterattacks", "effects": {"unit_bonuses": {"category_tank_destroyers": {"max_organisation": 6, "initiative": 0.01}}}},
        {"key": "selfsufficient_battalion", "name": "Radio-Directed Breakthrough Containment", "effects": {"unit_bonuses": {
            "armored_signal": {"battalion_mult": [{"category": "category_tank_destroyers", "hard_attack": 0.1, "ap_attack": 0.1}]},
            "category_tank_destroyer_regimental_support": {"max_organisation": 5}}}},  # (1.19.3) TD-RS +10% Hard Attack and Piercing removed
     ]},

    # --- Operations track (9 distinct; deep_battle_no_lar dropped, DLC version kept) ---
    {"key": "mission_type_tactics", "name": "Mission-Type Tactics", "tracks": ["operations"], "xor": [], "requires_technology": None,
     "effects": {"modifiers": {"command_power_gain": 0.2}, "unit_bonuses": {"category_all_infantry": {"max_organisation": 15}}},  # (1.19.3) command_power_gain 0.02->0.2
     "rewards": [
        {"key": "low_level_delegation", "name": "Low-level Delegation", "effects": {"unit_bonuses": {
            "category_all_infantry": {"default_morale": 0.1}, "category_regimental_support_artillery": {"max_organisation": 5, "soft_attack": 0.05}}}},
        {"key": "flexible_command", "name": "Flexible Command", "effects": {"modifiers": {"org_loss_when_moving": -0.15}}},
        {"key": "maneouver_drills", "name": "Combined Arms Battle Groups", "effects": {"modifiers": {"land_reinforce_rate": 0.02}, "unit_bonuses": {"category_all_armor": {"maximum_speed": 0.1}}}},
        {"key": "flexible_combat_formations", "name": "Offensive Posture", "effects": {"unit_bonuses": {"category_all_infantry": {"breakthrough": 0.1, "max_organisation": 10}}}},
        {"key": "control_zone_responsibilities", "name": "Control Zone Responsibilities", "effects": {"unit_bonuses": {
            "category_all_infantry": {"default_morale": 0.2}, "category_tanks": {"default_morale": 0.1}}}},
     ]},
    {"key": "last_stand", "name": "Desperate Defense", "tracks": ["operations"], "xor": [], "requires_technology": None,
     "effects": {"modifiers": {"conscription": 0.05}},
     "rewards": [
        {"key": "werwolf_groups", "name": "Sabotage Groups", "effects": {"modifiers": {"resistance_damage_to_garrison_on_our_occupied_states": 0.25}}},
        {"key": "pocket_consolidation", "name": "Pocket Consolidation", "effects": {"unit_bonuses": {"category_all_infantry": {"defense": 0.1}}}},
        {"key": "digging_in", "name": "Trench-Huddling", "effects": {"modifiers": {"out_of_supply_factor": -0.20}, "unit_bonuses": {"category_all_infantry": {"entrenchment": 0.1}}}},
        {"key": "stocking_up", "name": "Supply Cache Retrieval", "effects": {"modifiers": {"no_supply_grace": 72}}},
        {"key": "breaking_out", "name": "Final Offensive", "effects": {"unit_bonuses": {
            "category_army": {"soft_attack": 0.15}, "category_regimental_support_artillery": {"max_organisation": 5, "soft_attack": 0.1}}}},
     ]},
    {"key": "infiltration_tactics", "name": "Infiltration Tactics", "tracks": ["operations"], "xor": [], "requires_technology": None,
     "effects": {"enable_tactics": ["tactic_infantry_charge"], "modifiers": {"max_planning": 0.10}},  # (1.19.3) max_planning 0.05->0.10
     "rewards": [
        {"key": "infiltration_assault", "name": "Infiltration Assault", "effects": {"unit_bonuses": {
            "category_army": {"breakthrough": 0.10, "max_organisation": 5}, "fire_support": {"soft_attack": 0.1}}}},
        {"key": "nightly_assaults", "name": "Attacks At Night", "effects": {"modifiers": {"land_night_attack": 0.25}}},
        {"key": "self_sustaining_infiltration_units", "name": "Self-sustaining Infiltration Units", "effects": {
            "modifiers": {"supply_consumption_factor": -0.10, "command_power_gain": 0.1},  # (1.19.3) command_power_gain ~0.015->0.1
            "unit_bonuses": {"category_tanks": {"max_organisation": 2}, "category_all_armor": {"default_morale": 0.1}}}},
        {"key": "terrain_and_situation_assessment", "name": "Terrain and Situation Assessment", "effects": {"unit_bonuses": {
            "recon": {"battalion_mult": [{"category": "category_light_infantry", "soft_attack": 0.1}, {"category": "category_cavalry", "soft_attack": 0.1}]},
            "mot_recon": {"battalion_mult": [{"category": "category_light_infantry", "soft_attack": 0.1}, {"category": "category_cavalry", "soft_attack": 0.1}]},
            "light_tank_recon": {"battalion_mult": [{"category": "category_light_infantry", "soft_attack": 0.1}, {"category": "category_cavalry", "soft_attack": 0.1}]},
            "category_recon": {"recon": 1}}}},
        {"key": "infiltration_in_depth", "name": "Infiltration in Depth", "effects": {"modifiers": {"land_reinforce_rate": 0.02, "org_loss_when_moving": -0.20}}},
     ]},
    {"key": "grand_assault", "name": "Grand Assault", "tracks": ["operations"], "xor": [], "requires_technology": None,
     "effects": {"modifiers": {"max_planning": 0.1}, "unit_bonuses": {"category_army": {"breakthrough": 0.1, "soft_attack": 0.05}}},
     "rewards": [
        {"key": "central_planning", "name": "Central Planning", "effects": {"modifiers": {"max_command_power": 30},
            "unit_bonuses": {"logistics_company": {"battalion_mult": [{"category": "category_all_infantry", "defense": 0.05}]}}}},
        {"key": "multiple_attack_directions", "name": "Diversionary Attacks", "effects": {"unit_bonuses": {"category_army": {"breakthrough": 0.15}, "fire_support": {"soft_attack": 0.1}}}},
        {"key": "combined_arms_integration", "name": "Combined Arms Integration", "effects": {
            "modifiers": {"army_bonus_air_superiority_factor": 0.05, "coordination_bonus": 0.1},
            "unit_bonuses": {
                "category_tank_destroyer_regimental_support": {"max_organisation": 5},
                "anti_air_battery": {"max_organisation": 5, "air_attack": 0.1},
                "mot_fire_support": {"max_organisation": 5, "soft_attack": 0.1}}}},
        {"key": "forward_command_posts", "name": "Forward Command Posts", "effects": {"unit_bonuses": {
            "logistics_company": {"battalion_mult": [{"category": "category_all_infantry", "supply_consumption": -0.01, "add": True}]},
            "category_recon": {"recon": 0.1}}}},
        {"key": "c3i_theory", "name": "C3I", "effects": {"modifiers": {"max_planning": 0.1}, "unit_bonuses": {"category_all_infantry": {"max_organisation": 8}}}},
     ]},
    {"key": "deep_battle", "name": "Deep Battle", "tracks": ["operations"], "xor": [], "requires_technology": None,
     "effects": {"enable_tactics": ["tactic_backhand_blow"], "unit_bonuses": {"category_tanks": {"max_organisation": 4}}},
     "rewards": [
        {"key": "bounding_overwatch", "name": "Bounding Overwatch", "effects": {"unit_bonuses": {
            "recon": {"battalion_mult": [{"category": "category_light_infantry", "soft_attack": 0.05, "defense": 0.05}]},
            "mot_recon": {"battalion_mult": [{"category": "category_light_infantry", "soft_attack": 0.05, "defense": 0.05}]},
            "light_tank_recon": {"battalion_mult": [{"category": "category_light_infantry", "soft_attack": 0.05, "defense": 0.05}]},
            "armored_car_recon": {"battalion_mult": [{"category": "category_light_infantry", "soft_attack": 0.05, "defense": 0.05}]},  # (1.19.4) new
            "category_vehicle_infantry": {"max_organisation": 2}}}},
        {"key": "operational_concentration", "name": "Operational Reserves", "effects": {"modifiers": {"land_reinforce_rate": 0.05}, "unit_bonuses": {
            "category_tanks": {"max_organisation": 4}, "armored_car": {"max_organisation": 4}}}},
        {"key": "maskirovka", "name": "Strategic Deception", "effects": {"modifiers": {"army_intel_to_others": -10.0, "airforce_intel_to_others": -5.0, "army_intel_factor": 0.05}}},
        {"key": "breakthrough_priority", "name": "Breakthrough Priority", "effects": {"modifiers": {"org_loss_when_moving": -0.2}, "unit_bonuses": {
            "category_vehicle_infantry": {"max_organisation": 10, "default_morale": 0.1}, "category_tanks": {"max_organisation": 2},
            "category_all_armor": {"default_morale": 0.1}, "armored_car": {"max_organisation": 4},
            "mot_fire_support": {"max_organisation": 5, "soft_attack": 0.1}}}},
        {"key": "operational_depth_control", "name": "Operational Offensive Momentum", "effects": {"modifiers": {"org_loss_when_moving": -0.1, "land_reinforce_rate": 0.05}, "unit_bonuses": {
            "armored_car_recon": {"battalion_mult": [{"category": "category_light_infantry", "max_organisation": 10, "add": True}]},
            "light_tank_recon": {"battalion_mult": [{"category": "category_light_infantry", "max_organisation": 10, "add": True}]},
            "category_regimental_support_artillery": {"max_organisation": 5, "soft_attack": 0.1}}}},
     ]},
    {"key": "guerilla_war", "name": "Guerilla War", "tracks": ["operations"], "xor": [], "requires_technology": None,
     "effects": {"enable_tactics": ["tactic_guerrilla_tactics"], "unit_bonuses": {
         "irregular_infantry": {"soft_attack": 0.1, "defense": 0.2}, "militia": {"soft_attack": 0.1, "defense": 0.2}}},
     "rewards": [
        {"key": "catch_and_seize", "name": "The Enemy Will Supply Us", "effects": {"modifiers": {"pocket_penalty": -0.1}, "unit_bonuses": {
            "category_cavalry": {"equipment_capture_factor": 0.01, "plains": {"movement": 0.1}},
            "category_light_infantry": {"equipment_capture_factor": 0.01, "plains": {"movement": 0.1}}}}},
        {"key": "galvanize_support", "name": "Galvanize Support", "effects": {"modifiers": {
            "army_intel_to_others": -10.0, "army_intel_factor": 0.05, "war_support_factor": 0.1,
            "political_power_factor": 0.1, "mobilization_speed": 0.15}}},
        {"key": "scorched_earth", "name": "Scorched Earth", "effects": {"modifiers": {
            "resistance_damage_to_garrison_on_our_occupied_states": 0.1, "resistance_target_on_our_occupied_states": 0.1},
            "unit_bonuses": {"category_army": {"defense": 0.1}}}},
        {"key": "urban_assaults", "name": "Urban Combat Tactics", "effects": {"unit_bonuses": {
            "militia": {"urban": {"attack": 0.10, "defence": 0.10}}, "infantry": {"urban": {"attack": 0.10, "defence": 0.10}}}}},
        {"key": "defense_of_gained_power", "name": "Defense of Gained Power", "effects": {"modifiers": {"stability_factor": 0.1, "party_popularity_stability_factor": 0.05},
            "unit_bonuses": {"category_army": {"defense": 0.1}}}},
     ]},
    {"key": "rapid_domination", "name": "Rapid Domination", "tracks": ["operations"], "xor": [], "requires_technology": None,
     "effects": {"enable_tactics": ["tactic_breakthrough"], "modifiers": {"land_reinforce_rate": 0.02},
                 "unit_bonuses": {"category_all_infantry": {"soft_attack": 0.1}, "category_line_artillery": {"soft_attack": 0.1}}},
     "rewards": [
        {"key": "forward_observers", "name": "Scouts Out", "effects": {"modifiers": {"land_reinforce_rate": 0.02}, "unit_bonuses": {
            "category_recon": {"recon": 1}, "category_support_artillery": {"soft_attack": 0.05},
            "category_regimental_support_artillery": {"breakthrough": 0.1}}}},
        {"key": "advanced_firebases", "name": "Advanced Firebases", "effects": {"unit_bonuses": {
            "category_support_artillery": {"supply_consumption": -0.1, "battalion_mult": [{"category": "category_army", "default_morale": 0.1, "add": True}]},
            "category_regimental_support_artillery": {"soft_attack": 0.1}}}},
        {"key": "centralized_fire_control", "name": "Dynamic Fire Control", "effects": {"unit_bonuses": {"signal_company": {"battalion_mult": [{"category": "category_artillery", "soft_attack": 0.1}]}}}},
        {"key": "regimental_combat_teams", "name": "Regimental Combat Teams", "effects": {"unit_bonuses": {"category_support_battalions": {"max_organisation": 10, "soft_attack": 0.1}}}},
        {"key": "shock_and_awe", "name": "Shock & Awe", "effects": {"modifiers": {"army_bonus_air_superiority_factor": 0.1}, "unit_bonuses": {
            "category_army": {"soft_attack": 0.05}, "category_all_infantry": {"soft_attack": 0.1, "hard_attack": 0.1}}}},
     ]},
    {"key": "expeditionary_warfare", "name": "Expeditionary Warfare", "tracks": ["operations"], "xor": [], "requires_technology": None,
     "effects": {"modifiers": {"send_volunteer_divisions_required": -0.5, "send_volunteer_factor": 0.25, "send_volunteers_tension": -0.1}},
     "rewards": [
        {"key": "staging_area_security", "name": "Beachhead Security", "effects": {"modifiers": {"dig_in_speed_factor": 0.05, "out_of_supply_factor": -0.20},
            "unit_bonuses": {"category_army": {"defense": 0.1}}}},
        {"key": "landing_operations", "name": "Landing Operations", "effects": {"modifiers": {
            "naval_invasion_prep_speed": 0.2, "naval_invasion_penalty": -0.15, "naval_invasion_planning_bonus_speed": 0.2},
            "unit_bonuses": {"category_army": {"soft_attack": 0.1}}}},
        {"key": "shore_fire_control_parties", "name": "Shore Fire Control Parties", "effects": {"modifiers": {"shore_bombardment_bonus": 0.25}}},
        {"key": "breakout_emphasis", "name": "Resupply Emphasis", "effects": {"modifiers": {"no_supply_grace": 32}}},
        {"key": "withdrawal_protocols", "name": "Orderly Withdrawal Protocols", "effects": {"modifiers": {"org_loss_when_moving": -0.2}}},
     ]},
    {"key": "dispersed_operations", "name": "Dispersed Operations", "tracks": ["operations"], "xor": [], "requires_technology": None,
     "effects": {"modifiers": {"enemy_army_bonus_air_superiority_factor": -0.10, "land_reinforce_rate": 0.05}},
     "rewards": [
        {"key": "camouflage_discipline", "name": "Camouflage Discipline", "effects": {"modifiers": {"enemy_army_bonus_air_superiority_factor": -0.15}, "unit_bonuses": {
            "logistics_company": {"battalion_mult": [{"category": "category_all_infantry", "entrenchment": 0.1, "add": True}]}}}},
        {"key": "hardened_logistics", "name": "Hardened Logistics", "effects": {"modifiers": {"no_supply_grace": 24}, "unit_bonuses": {"logistics_company": {"max_organisation": 5}}}},
        {"key": "local_air_defense", "name": "Local Air Defense", "effects": {"unit_bonuses": {
            "anti_air_battery": {"air_attack": 0.20}, "anti_air": {"air_attack": 0.20},
            "category_self_propelled_anti_air_regimental_support": {"air_attack": 0.20}}}},
        {"key": "scattered_formations", "name": "Scattered Formations", "effects": {"modifiers": {"cas_damage_reduction": 0.05}}},
        {"key": "independent_operations", "name": "Independent Operations", "effects": {"modifiers": {"out_of_supply_factor": -0.15}, "unit_bonuses": {
            "category_all_infantry": {"initiative": 0.01, "breakthrough": 0.1, "max_organisation": 5},
            "category_all_armor": {"initiative": 0.01, "breakthrough": 0.1, "max_organisation": 2}}}},
     ]},

    # --- Special Forces (8; can be assigned to either special_forces_first or special_forces_second) ---
    {"key": "mountaineers_1", "name": "Mountaineers: Cold Weather Specialists", "tracks": ["special_forces_first", "special_forces_second"],
     "xor": ["mountaineers_2"], "requires_technology": "tech_mountaineers",
     "effects": {"modifiers": {"mountaineers_special_forces_contribution_factor": -0.25},
                 "unit_bonuses": {"rangers_support": {"acclimatization_cold_climate_gain_factor": 0.25, "snow": {"attack": 0.15, "defence": 0.15, "movement": 0.15}}},
                 "unlocks_subunits": ["rangers_support"]},
     "rewards": [
        {"key": "reward_1", "name": "Cold Weather Training", "effects": {"modifiers": {"special_forces_out_of_supply_factor": -0.1, "acclimatization_cold_climate_gain_factor": 0.1},
            "unit_bonuses": {"category_special_forces": {"max_organisation": 5, "soft_attack": 0.05}}}},
        {"key": "reward_2", "name": "Shared Instructors", "effects": {"modifiers": {"special_forces_training_time_factor": -0.1, "mountaineers_special_forces_contribution_factor": -0.25}}},
        {"key": "reward_3", "name": "Holding the Line", "effects": {"unit_bonuses": {"category_mountaineers": {"defense": 0.10}, "mountaineers": {"combat_width": -0.2}}}},
        {"key": "reward_4", "name": "Combined Arms Training", "effects": {"unit_bonuses": {"category_mountaineers": {"max_organisation": 10}}}},
        {"key": "reward_5", "name": "Backbone of the Armed Forces", "effects": {"unit_bonuses": {"category_mountaineers": {"soft_attack": 0.1}}}},
     ]},
    {"key": "mountaineers_2", "name": "Mountaineers: Elevate the Mountaineers", "tracks": ["special_forces_first", "special_forces_second"],
     "xor": ["mountaineers_1"], "requires_technology": "tech_mountaineers",
     "effects": {"modifiers": {"mountaineers_special_forces_contribution_factor": -0.25},
                 "unit_bonuses": {"rangers_support": {"mountain": {"attack": 0.10, "defence": 0.10, "movement": 0.10}}},
                 "unlocks_subunits": ["rangers_support"]},
     "rewards": [
        {"key": "reward_1", "name": "Rough Terrain Specialists", "effects": {"modifiers": {"acclimatization_hot_climate_gain_factor": 0.10, "acclimatization_cold_climate_gain_factor": 0.10},
            "unit_bonuses": {"mountaineers": {"forest": {"movement": 0.05}, "hills": {"movement": 0.05}, "mountain": {"movement": 0.05}, "desert": {"movement": 0.05}}}}},
        {"key": "reward_2", "name": "Battlefield Intelligence", "effects": {"modifiers": {"unit_mountaineers_design_cost_factor": -0.50, "unit_rangers_support_design_cost_factor": -0.50},
            "unit_bonuses": {"category_mountaineers": {"initiative": 0.01}}}},
        {"key": "reward_3", "name": "Mountain Artillery", "effects": {"unit_bonuses": {
            "artillery": {"battalion_mult": [{"category": "category_mountaineers", "breakthrough": 0.15}]},
            "rangers_support": {"battalion_mult": [{"category": "category_line_artillery", "soft_attack": 0.20}]}}}},
        {"key": "reward_4", "name": "Adaptation to Hardships", "effects": {"modifiers": {"mountaineers_special_forces_contribution_factor": -0.25},
            "unit_bonuses": {"category_mountaineers": {"supply_consumption": -0.02, "max_organisation": 10}}}},
        {"key": "reward_5", "name": "Mountain Warfare Lessons", "effects": {"modifiers": {"special_forces_attack_factor": 0.1}}},
     ]},
    {"key": "marines_1", "name": "Marines: Commandos", "tracks": ["special_forces_first", "special_forces_second"],
     "xor": ["marines_2"], "requires_technology": "marines",
     "effects": {"modifiers": {"marines_special_forces_contribution_factor": -0.25},
                 "unit_bonuses": {"pioneer_support": {"jungle": {"attack": 0.10, "defence": 0.10, "movement": 0.10}}},
                 "unlocks_subunits": ["pioneer_support"]},
     "rewards": [
        {"key": "reward_1", "name": "Organize Marine Commandos", "effects": {"unlocks_subunits": ["marine_commando"]}},
        {"key": "reward_2", "name": "Gruelling Training Regimen", "effects": {"modifiers": {"unit_marine_design_cost_factor": -0.50}, "unit_bonuses": {"marine": {"max_organisation": 5}}}},
        {"key": "reward_3", "name": "Demolition Experts", "effects": {"unit_bonuses": {"marine_commando": {"breakthrough": 0.15}}}},
        {"key": "reward_4", "name": "Marine Corps Expansion", "effects": {"modifiers": {"naval_invasion_plan_cap": 2, "marines_special_forces_contribution_factor": -0.25}}},
        {"key": "reward_5", "name": "Mechanized Marine Corps", "effects": {"unit_bonuses": {
            "amphibious_mechanized": {"soft_attack": 0.1, "breakthrough": 0.1, "max_organisation": 5},
            "pioneer_support": {"battalion_mult": [{"category": "category_amphibious_tanks", "armor": 0.15, "breakthrough": 0.15}]}}}},
     ]},
    {"key": "marines_2", "name": "Marines: Expeditionary Units", "tracks": ["special_forces_first", "special_forces_second"],
     "xor": ["marines_1"], "requires_technology": "marines",
     "effects": {"modifiers": {"marines_special_forces_contribution_factor": -0.25},
                 "unit_bonuses": {"pioneer_support": {"amphibious": {"attack": 0.15, "defence": 0.15, "movement": 0.15}}},
                 "unlocks_subunits": ["pioneer_support"]},
     "rewards": [
        {"key": "reward_1", "name": "Shore Parties", "effects": {"modifiers": {
            "naval_invasion_prep_days": -5, "naval_invasion_division_cap": 2, "naval_invasion_plan_cap": 1,
            "marines_special_forces_contribution_factor": -0.25}}},
        {"key": "reward_2", "name": "Increased Artillery Coordination", "effects": {"unit_bonuses": {
            "pioneer_support": {"battalion_mult": [{"category": "category_line_artillery", "max_organisation": 2, "add": True}]},
            "artillery": {"battalion_mult": [{"category": "category_marines", "defense": 0.05}]},
            "anti_air": {"battalion_mult": [{"category": "category_marines", "defense": 0.05}]},
            "anti_tank": {"battalion_mult": [{"category": "category_marines", "defense": 0.05}]}}}},
        {"key": "reward_3", "name": "Defending Beachhead", "effects": {"modifiers": {"extra_marine_supply_grace": 36}, "unit_bonuses": {"marine": {"max_organisation": 5, "soft_attack": 0.05}}}},
        {"key": "reward_4", "name": "Blowtorch and Corkscrew", "effects": {"modifiers": {
            "naval_invasion_planning_bonus_speed": 0.2, "shore_bombardment_bonus": 0.15, "army_bonus_air_superiority_factor": 0.10}}},
        {"key": "reward_5", "name": "Expeditionary Task Forces", "effects": {"modifiers": {"special_forces_attack_factor": 0.10}}},
     ]},
    {"key": "paratroopers_1", "name": "Paratroopers: Sabotage Parties", "tracks": ["special_forces_first", "special_forces_second"],
     "xor": ["paratroopers_2"], "requires_technology": "paratroopers",
     "effects": {"modifiers": {"paratroopers_special_forces_contribution_factor": -0.25, "extra_paratrooper_supply_grace": 48},
                 "unit_bonuses": {"signal_company": {"battalion_mult": [{"category": "category_paratroopers", "defense": 0.15}]}},
                 "unlocks_subunits": ["airborne_light_armor"]},
     "rewards": [
        {"key": "reward_1", "name": "Sabotage Missions", "effects": {"unit_bonuses": {"transport_plane": {"air_defence": 0.20}}}},
        {"key": "reward_2", "name": "Survival Training", "effects": {"modifiers": {"acclimatization_hot_climate_gain_factor": 0.10, "acclimatization_cold_climate_gain_factor": 0.10},
            "unit_bonuses": {"category_paratroopers": {"supply_consumption": -0.02}}}},
        {"key": "reward_3", "name": "Branch Knowledge Sharing", "effects": {"unit_bonuses": {"category_special_forces": {"max_organisation": 10, "soft_attack": 0.05}}}},
        {"key": "reward_4", "name": "Enhanced Navigational Training", "effects": {"unit_bonuses": {
            "category_paratroopers": {"default_morale": 0.15},
            "signal_company": {"battalion_mult": [{"category": "category_paratroopers", "max_strength": 0.1}]}}}},
        {"key": "reward_5", "name": "Best of the Best", "effects": {"modifiers": {"paratroopers_special_forces_contribution_factor": -0.25},
            "unit_bonuses": {"category_paratroopers": {"soft_attack": 0.15, "breakthrough": 0.15}}}},
     ]},
    {"key": "paratroopers_2", "name": "Paratroopers: Concentrated Drops", "tracks": ["special_forces_first", "special_forces_second"],
     "xor": ["paratroopers_1"], "requires_technology": "paratroopers",
     "effects": {"modifiers": {"paratroopers_special_forces_contribution_factor": -0.25, "paradrop_organization_factor": 0.5},
                 "unit_bonuses": {"field_hospital": {"battalion_mult": [{"category": "category_paratroopers", "default_morale": 0.15}]}},
                 "unlocks_subunits": ["airborne_light_armor"]},
     "rewards": [
        {"key": "reward_1", "name": "Combat Insertion", "effects": {"modifiers": {"paratroopers_special_forces_contribution_factor": -0.25}}},
        {"key": "reward_2", "name": "Expedited Training Process", "effects": {"modifiers": {"special_forces_training_time_factor": -0.1}}},
        {"key": "reward_3", "name": "Airborne Medical Detail", "effects": {"unit_bonuses": {"field_hospital": {"battalion_mult": [{"category": "category_paratroopers", "max_organisation": 5, "add": True}]}}}},
        {"key": "reward_4", "name": "Strategic Air Lift Corps", "effects": {"modifiers": {"paratrooper_weight_factor": -0.5, "paratrooper_aa_defense": 0.1}}},
        {"key": "reward_5", "name": "Backbone of the Armed Forces", "effects": {"modifiers": {"special_forces_attack_factor": 0.10}}},
     ]},
    {"key": "rangers_1", "name": "Rangers: Jaeger Traditions", "tracks": ["special_forces_first", "special_forces_second"],
     "xor": ["rangers_2"], "requires_technology": "rangers_tech",
     "effects": {"modifiers": {"rangers_special_forces_contribution_factor": -0.25},
                 "unit_bonuses": {"ranger_battalion": {"acclimatization_cold_climate_gain_factor": 0.25, "forest": {"attack": 0.1, "defence": 0.1, "movement": 0.05}}},
                 "unlocks_subunits": ["rangers_support"]},
     "rewards": [
        {"key": "reward_1", "name": "Forest Guerillas", "effects": {"unit_bonuses": {"category_rangers": {"defense": 0.1, "initiative": 0.01, "maximum_speed": 0.1}}}},
        {"key": "reward_2", "name": "Light Infantry Specialization", "effects": {"modifiers": {"rangers_special_forces_contribution_factor": -0.25},
            "unit_bonuses": {"category_special_forces": {"soft_attack": 0.05, "max_organisation": 5}}}},
        {"key": "reward_3", "name": "Fire Support Integration", "effects": {"unit_bonuses": {
            "artillery": {"battalion_mult": [{"category": "category_rangers", "defense": 0.05, "breakthrough": 0.05}]},
            "rangers_support": {"battalion_mult": [{"category": "category_line_artillery", "defense": 0.15, "breakthrough": 0.15}]}}}},
        {"key": "reward_4", "name": "Rangers Urban Combat Expertise", "effects": {"unit_bonuses": {
            "category_rangers": {"default_morale": 0.1, "supply_consumption": -0.02},
            "ranger_battalion": {"urban": {"attack": 0.1, "defence": 0.1, "movement": 0.05}}}}},
        {"key": "reward_5", "name": "Elite Rangers", "effects": {"unit_bonuses": {"ranger_battalion": {"max_organisation": 10, "soft_attack": 0.1, "breakthrough": 0.1}}}},
     ]},
    {"key": "rangers_2", "name": "Rangers: Jungle Training", "tracks": ["special_forces_first", "special_forces_second"],
     "xor": ["rangers_1"], "requires_technology": "rangers_tech",
     "effects": {"modifiers": {"rangers_special_forces_contribution_factor": -0.25},
                 "unit_bonuses": {"ranger_battalion": {"acclimatization_hot_climate_gain_factor": 0.25, "jungle": {"attack": 0.1, "defence": 0.1, "movement": 0.05}}},
                 "unlocks_subunits": ["rangers_support"]},
     "rewards": [
        {"key": "reward_1", "name": "Recon Rangers Terrain Mastery", "effects": {"unit_bonuses": {
            "rangers_support": {"jungle": {"attack": 0.05, "defence": 0.05, "movement": 0.05}, "forest": {"attack": 0.05, "defence": 0.05, "movement": 0.05}}}}},
        {"key": "reward_2", "name": "Elevate the Rangers", "effects": {"unit_bonuses": {"category_rangers": {"soft_attack": 0.1, "defense": 0.1, "max_organisation": 5}}}},
        {"key": "reward_3", "name": "Jungle Guerillas", "effects": {"modifiers": {"special_forces_no_supply_grace": 36}, "unit_bonuses": {"ranger_battalion": {"supply_consumption": -0.03}}}},
        {"key": "reward_4", "name": "Ranger Training Brigade", "effects": {"modifiers": {"special_forces_training_time_factor": -0.1, "rangers_special_forces_contribution_factor": -0.25}}},
        {"key": "reward_5", "name": "Establish Ranger School", "effects": {"modifiers": {"special_forces_attack_factor": 0.1}}},
     ]},
]
