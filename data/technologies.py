# Hand-curated from technologies_copy/{infantry,NSB_armor,artillery,support}.txt
# (HOI4 game files), verified 2026-09-15. These are the four tech-tree files
# that actually gate Composition/Stats content (battalions, support
# companies, regimental support, equipment tiers, Tank Designer modules) -
# see Specification.md for why the other technologies_copy/*.txt files
# (naval, air, industry, electronic_mechanical_engineering, MTG_naval*,
# bba_air_techs, special_projects_tech) aren't compiled here.
#
# "key" matches the game's own technology identifier. "branch" records which
# of the four source files a tech came from - all four use a single tech-tree
# folder each (infantry_folder, nsb_armour_folder, artillery_folder,
# support_folder), so branch and folder are 1:1 and only branch is kept.
#
# "unlocked_by" is the OR-merge prerequisite chain: this tech becomes
# available once ANY ONE of these techs is done (the game's own `path`
# field, stored here in reverse - "who leads to me" instead of "who I lead
# to" - since "what can I research next" is the more useful query). Empty
# list = available from the start of its branch.
#
# "requires" is an additional AND requirement layered on top of
# unlocked_by, taken from the game's own `dependencies` field - ALL of these
# must also be done, regardless of which unlocked_by path was taken.
# tech_signal_company's "radio" requirement is a genuine cross-file
# dependency into technologies_copy/electronic_mechanical_engineering.txt,
# which isn't compiled here - flagged as an EXTERNAL_DEPENDENCIES key
# instead of pretending it doesn't exist.
#
# "mutually_exclusive_with" is the game's own `xor` field - picking one
# locks out researching the other. Stored symmetrically on both entries.
#
# "unlocks_equipment", "unlocks_equipment_modules" (Tank Designer parts -
# not consumed by anything yet, but recorded for when the Tank Designer is
# built) and "unlocks_subunits" (battalions/support companies/regimental
# support - not distinguished here; which list a given key belongs to is
# already recorded in data/battalions.py, data/support_companies.py and
# data/regimental_support.py, so this file doesn't repeat that
# classification) are taken directly from the game's own enable_equipments /
# enable_equipment_modules / enable_subunits fields. DLC-gated
# `hq_*` regimental HQ entries (e.g. tech_engineers' hq_engineer) are
# excluded, matching data/support_companies.py's exclusion of
# units_copy/hq_support.txt as belonging to the deferred Army
# Leadership/Military Staff system, not Composition.
#
# Deliberately excluded, two ways (a third, Special-Project-gated techs, was
# resolved 2026-10-01 - see special_project_requires below, not excluded
# anymore):
# - Hidden techs (`allow = { always = no }`), granted only by a national
#   focus, event, or national spirit - not real player choices. Per the
#   project's standing rule (see Specification.md), anything they unlock is
#   assumed already available rather than modeled as a research
#   requirement.
# - support.txt's train sub-branch (basic_train, wartime_train,
#   armored_train, railway_gun) - trains aren't a division battalion,
#   support company, or regimental support item; nothing in Composition or
#   Stats depends on them, so they're out of scope entirely rather than a
#   gap.
# - infantry.txt's tech_special_forces branch (tech_special_forces,
#   advanced_special_forces, improved_special_forces,
#   extreme_environment_training, survival_training, elite_forces) -
#   removed 2026-11-03, compiled through 2026-11-02 - the real source's
#   own `allow_branch = { NOT = { has_dlc = "Arms Against Tyranny" } }`
#   makes this entire branch unreachable for any AAT-owning player
#   (confirmed against both the copied reference file and the real
#   installed game's current file), and Ollie owns every DLC - see the
#   full removal note further down this file, where the entries used to
#   sit, for the complete story.
#
# motorised_infantry's sub_technology motorized_rocket_unit calls
# `enable_subunits = { motorized_rocket_brigade }`, which isn't a key in
# data/battalions.py - resolved, not a data error: units_copy/
# artillery_brigade.txt defines BOTH "mot_rocket_artillery_brigade"
# (active = yes, the one data/battalions.py correctly includes) and
# "motorized_rocket_brigade" (active = no - disabled in-game, hence
# correctly excluded from data/battalions.py). The tech file's
# enable_subunits entry is a vestigial reference to that disabled unit, left
# in place by Paradox rather than a compile mistake here. Kept as-is
# (matching technologies_copy/infantry.txt exactly) since it's still what
# the source file says, with tests/test_technologies.py's
# KNOWN_UNRESOLVED_SUBUNIT_KEYS documenting why it can never resolve. The
# same disabled-unit key resurfaces as a `unit_bonuses` target on
# artillery.txt's rocket_artillery4 - kept for the identical reason.
#
# "unit_bonuses" (added 2026-09-29) is a technology's own direct stat
# bonus, granted immediately once researched - a real, separate HOI4
# mechanic from unlocks_equipment/unlocks_subunits, structurally identical
# to data/doctrines.py's own "unit_bonuses" field
# ({target_key: {stat_field: value, ...}}, target_key a `category_*` tag or
# a literal item key - including nested terrain-shaped sub-dicts and
# `battalion_mult` lists, using that exact same shape). Compiled faithfully
# from every source file that has any - as of 2026-09-29, that meant
# infantry.txt/artillery.txt/support.txt only (NSB_armor.txt's eligible
# technologies all had none); as of 2026-10-01's Special Projects compile
# (see below), NSB_armor.txt now contributes some too, via its Special
# Project entries - including fields this project doesn't apply anywhere
# yet (acclimatization_*_factor, reliability_factor,
# equipment_capture_factor, recovery, casualty_trickleback,
# experience_loss_factor, supply_consumption_factor, fuel_consumption_factor,
# hardness-as-a-bonus, combat_width-as-a-bonus, and the bare `reliability`/
# `supply_consumption`/`maximum_speed`/`entrenchment` fields several Special
# Project technologies use directly - a different, untracked field set from
# Doctrine's own `supply_consumption`/`maximum_speed` handling) - not
# silently dropped, matching data/doctrines.py's own "capture faithfully
# even where clearly outside current scope" precedent. Terrain-nested
# bonuses (e.g. mountain_gun's artillery_brigade attack bonus specifically
# in Mountain terrain) are deliberately NOT fed into logic/terrain.py this
# phase - Ollie's explicit call, matching how data/doctrines.py's own
# terrain-nested rewards are already compiled-but-unapplied. See
# logic/research.py's active_tech_unit_bonuses and Activity_Log.md,
# 2026-09-29, for the full scope/rationale and what's still deliberately
# unapplied in logic/stats.py.
#
# "special_project_requires" (added 2026-10-01) is the bare
# data/special_projects.py key this technology needs completed before it's
# researchable at all - None for every technology except the 18 real
# Special-Project-gated ones (is_special_project_tech = yes in the source;
# previously excluded entirely, see Activity_Log.md, 2026-10-01, for the
# full scope investigation). Unlike every other gate in this file,
# `unlocked_by` is deliberately left [] for all 18 of these even though
# most have a visual path-parent in the source - confirmed that path is
# cosmetic tree-arrow wiring only here, not a hard OR-gate; the ONLY real
# gate is special_project_requires, checked by logic/research.py's
# is_researchable against a caller-owned completed_special_projects set,
# the same pattern `researched` itself already uses. One entry
# (sp_artillery_rocket_assisted_projectiles_tech) has a genuine SECOND,
# ordinary `requires` entry on top ("experimental_rockets") - a real
# cross-file AND condition, same EXTERNAL_DEPENDENCIES treatment as
# tech_signal_company's "radio".

EXTERNAL_DEPENDENCIES = {
    # tech_signal_company's dependency living in the uncompiled
    # electronic_mechanical_engineering.txt.
    "radio",
    # sp_artillery_rocket_assisted_projectiles_tech's dependency living in
    # an uncompiled rocket-artillery tech outside this file's four scoped
    # source files - added 2026-10-01 alongside Special Projects.
    "experimental_rockets",
}

TECHNOLOGIES = [
    # ---------------------------------------------------------------
    # infantry.txt
    # ---------------------------------------------------------------

    # Infantry Weapons (main line, with an Anti-Tank sub-branch)
    {"key": "infantry_weapons", "name": "Infantry Weapons I", "branch": "infantry",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["infantry_equipment_0"],
     "unlocks_equipment_modules": ["tank_heavy_machine_gun", "secondary_turret_hmg", "additional_machine_guns"],
     "unlocks_subunits": ["infantry"]},
    {"key": "infantry_weapons1", "name": "Infantry Weapons II", "branch": "infantry",
     "unlocked_by": ["infantry_weapons"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["infantry_equipment_1"], "unlocks_equipment_modules": [],
     "unlocks_subunits": []},
    {"key": "infantry_weapons2", "name": "Improved Infantry Equipment I", "branch": "infantry",  # (2026-11-01) real name, not "Infantry Weapons III" - confirmed via the real game's own localisation
     "unlocked_by": ["infantry_weapons1"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"category_light_infantry": {"soft_attack": 0.05}, "category_cavalry": {"soft_attack": 0.05},
                       "category_vehicle_infantry": {"soft_attack": 0.05}}},
    {"key": "improved_infantry_weapons", "name": "Improved Infantry Weapons I", "branch": "infantry",
     "unlocked_by": ["infantry_weapons2"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["infantry_equipment_2"], "unlocks_equipment_modules": [],
     "unlocks_subunits": []},
    {"key": "improved_infantry_weapons_2", "name": "Improved Infantry Equipment II", "branch": "infantry",  # (2026-11-01) real name, not "Improved Infantry Weapons II"
     "unlocked_by": ["improved_infantry_weapons"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"category_light_infantry": {"soft_attack": 0.05}, "category_cavalry": {"soft_attack": 0.05},
                       "category_vehicle_infantry": {"soft_attack": 0.05}}},
    {"key": "infantry_at", "name": "Infantry Anti-Tank I", "branch": "infantry",
     "unlocked_by": ["improved_infantry_weapons"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"category_all_infantry": {"hard_attack": 0.25, "ap_attack": 1},
                       "category_cavalry": {"hard_attack": 0.1, "ap_attack": 0.4},
                       "fire_support": {"hard_attack": 0.15, "ap_attack": 0.5},
                       "mot_fire_support": {"hard_attack": 0.15, "ap_attack": 0.5}}},
    {"key": "infantry_at2", "name": "Infantry Anti-Tank II", "branch": "infantry",
     "unlocked_by": ["infantry_at"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"category_all_infantry": {"hard_attack": 0.25, "ap_attack": 1},
                       "category_cavalry": {"hard_attack": 0.1, "ap_attack": 0.4},
                       "fire_support": {"hard_attack": 0.15, "ap_attack": 0.5},
                       "mot_fire_support": {"hard_attack": 0.15, "ap_attack": 0.5}}},
    {"key": "advanced_infantry_weapons", "name": "Advanced Infantry Weapons I", "branch": "infantry",
     "unlocked_by": ["improved_infantry_weapons_2"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["infantry_equipment_3"], "unlocks_equipment_modules": [],
     "unlocks_subunits": []},
    {"key": "advanced_infantry_weapons2", "name": "Improved Infantry Equipment III", "branch": "infantry",  # (2026-11-01) real name, not "Advanced Infantry Weapons II"
     "unlocked_by": ["advanced_infantry_weapons"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"category_light_infantry": {"soft_attack": 0.05}, "category_cavalry": {"soft_attack": 0.05},
                       "category_vehicle_infantry": {"soft_attack": 0.1}}},

    # Special forces: Paratroopers / Marines / Mountaineers / Rangers (three
    # tiers each), converging into a shared Special Forces sub-branch.
    {"key": "paratroopers", "name": "Paratroopers I", "branch": "infantry",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": ["paratrooper"]},
    {"key": "paratroopers2", "name": "Paratroopers II", "branch": "infantry",
     "unlocked_by": ["paratroopers"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"paratrooper": {"max_organisation": 5, "soft_attack": 0.05}}},
    {"key": "paratroopers3", "name": "Paratroopers III", "branch": "infantry",
     "unlocked_by": ["paratroopers2"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"paratrooper": {"max_organisation": 5}}},

    {"key": "marines", "name": "Marines I", "branch": "infantry",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": ["marine"]},
    {"key": "marines2", "name": "Marines II", "branch": "infantry",
     "unlocked_by": ["marines"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"marine": {"max_organisation": 5, "soft_attack": 0.05}}},
    {"key": "marines3", "name": "Marines III", "branch": "infantry",
     "unlocked_by": ["marines2"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"marine": {"max_organisation": 5}}},

    {"key": "tech_mountaineers", "name": "Mountain Infantry I", "branch": "infantry",  # (2026-11-01) real name, not "Mountaineers I"
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": ["mountaineers"]},
    {"key": "tech_mountaineers2", "name": "Mountain Infantry II", "branch": "infantry",  # (2026-11-01) real name, not "Mountaineers II"
     "unlocked_by": ["tech_mountaineers"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"mountaineers": {"max_organisation": 5, "soft_attack": 0.05}}},
    {"key": "tech_mountaineers3", "name": "Mountain Infantry III", "branch": "infantry",  # (2026-11-01) real name, not "Mountaineers III"
     "unlocked_by": ["tech_mountaineers2"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"mountaineers": {"max_organisation": 5}}},

    {"key": "rangers_tech", "name": "Rangers I", "branch": "infantry",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": ["ranger_battalion"]},
    {"key": "rangers_tech2", "name": "Rangers II", "branch": "infantry",
     "unlocked_by": ["rangers_tech"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"ranger_battalion": {"max_organisation": 5, "soft_attack": 0.05}}},
    {"key": "rangers_tech3", "name": "Rangers III", "branch": "infantry",
     "unlocked_by": ["rangers_tech2"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"ranger_battalion": {"max_organisation": 5}}},

    # tech_special_forces / advanced_special_forces / improved_special_forces /
    # extreme_environment_training / survival_training / elite_forces were
    # compiled here through 2026-11-02, then REMOVED 2026-11-03: Ollie
    # reported never seeing this branch in his own real tech tree at all
    # (what he actually sees under "Special Forces" is the 4-row Marine/
    # Mountaineer/Paratrooper/Ranger grid - already correctly compiled
    # above as marines/marines2/marines3, tech_mountaineers/2/3,
    # paratroopers/2/3, rangers_tech/2/3). Checked directly against both
    # this project's own copied technologies_copy/infantry.txt AND the
    # real installed game's own current common/technologies/infantry.txt -
    # byte-identical, confirming tech_special_forces' own real source line:
    # `allow_branch = { NOT = { has_dlc = "Arms Against Tyranny" } }` -
    # this whole branch is a pre-AAT relic, hard-excluded from the real
    # game's own UI for anyone who owns that DLC. Ollie owns every DLC
    # (confirmed 2026-10-08), so these 6 technologies can never actually
    # appear in his own real research tree at all - the exact same
    # "genuinely inaccessible to this project's real scope" standard
    # already used to exclude Norway-only Tank Designer modules and
    # country-specific Officer Corps entries, just discovered later. A
    # 2026-10-08 investigation had already found and noted this exact
    # exclusion (see Activity_Log.md) but only applied it to one test
    # fixture's own "research everything" set, never to the real compile -
    # this is that correction. These were also this project's only real
    # `mutually_exclusive_with` (XOR) pair - tests/test_research.py's own
    # XOR test now uses synthetic data instead, so the mechanism itself
    # stays covered even with no real pair left in the compile.

    # Night Vision
    {"key": "night_vision", "name": "Night Vision I", "branch": "infantry",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": []},
    {"key": "night_vision2", "name": "Night Vision II", "branch": "infantry",
     "unlocked_by": ["night_vision"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": []},

    # Support Weapons (regimental support: Field Guns / Fire Support)
    {"key": "support_weapons", "name": "Support Weapons I", "branch": "infantry",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [],
     "unlocks_subunits": ["fire_support", "mot_fire_support"]},
    {"key": "support_weapons2", "name": "Support Weapons II", "branch": "infantry",
     "unlocked_by": ["support_weapons"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"field_guns": {"defense": 0.1, "soft_attack": 0.1},
                       "fire_support": {"defense": 0.15, "breakthrough": 0.15, "soft_attack": 0.1},
                       "mot_fire_support": {"defense": 0.15, "breakthrough": 0.05, "soft_attack": 0.1}}},
    {"key": "support_weapons3", "name": "Support Weapons III", "branch": "infantry",
     "unlocked_by": ["support_weapons2"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"field_guns": {"defense": 0.1, "soft_attack": 0.1},
                       "fire_support": {"defense": 0.15, "breakthrough": 0.15, "soft_attack": 0.1},
                       "mot_fire_support": {"defense": 0.15, "breakthrough": 0.05, "soft_attack": 0.1}}},
    {"key": "support_weapons4", "name": "Support Weapons IV", "branch": "infantry",
     "unlocked_by": ["support_weapons3"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"field_guns": {"defense": 0.1, "soft_attack": 0.1},
                       "fire_support": {"defense": 0.15, "breakthrough": 0.15, "soft_attack": 0.1},
                       "mot_fire_support": {"defense": 0.15, "breakthrough": 0.05, "soft_attack": 0.1}}},

    # Trucks -> Motorized/Mechanized Infantry, Armored Car
    {"key": "tech_trucks", "name": "Trucks", "branch": "infantry",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["motorized_equipment_0"],
     "unlocks_equipment_modules": ["tank_wheeled_suspension"],
     "unlocks_subunits": ["mot_anti_tank_brigade", "mot_artillery_brigade", "mot_anti_air_brigade"]},
    {"key": "motorised_infantry", "name": "Motorized Infantry", "branch": "infantry",
     "unlocked_by": ["tech_trucks"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["motorized_equipment_1"], "unlocks_equipment_modules": [],
     "unlocks_subunits": ["motorized"],
     "unit_bonuses": {"mot_fire_support": {"breakthrough": 0.1}}},
    {"key": "motorized_rocket_unit", "name": "Motorized Rocket Artillery", "branch": "infantry",
     "unlocked_by": ["motorised_infantry"], "requires": ["rocket_artillery"],
     "mutually_exclusive_with": [],
     "unlocks_equipment": ["motorized_rocket_equipment_1"], "unlocks_equipment_modules": [],
     "unlocks_subunits": ["motorized_rocket_brigade"]},
    {"key": "armored_car1", "name": "Inter-War Armored Car", "branch": "infantry",  # (2026-11-01) real name (via its own equipment's name) - not "Armored Car I"
     "unlocked_by": ["tech_trucks"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["gw_armored_car_equipment"], "unlocks_equipment_modules": [],
     "unlocks_subunits": ["armored_car"]},
    {"key": "armored_car2", "name": "Basic Armored Car", "branch": "infantry",  # (2026-11-01) real name - not "Armored Car II"
     "unlocked_by": ["armored_car1"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["armored_car_equipment_1"], "unlocks_equipment_modules": [],
     "unlocks_subunits": []},
    {"key": "armored_car3", "name": "Improved Armored Car", "branch": "infantry",  # (2026-11-01) real name - not "Armored Car III"
     "unlocked_by": ["armored_car2"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["armored_car_equipment_2"], "unlocks_equipment_modules": [],
     "unlocks_subunits": []},
    {"key": "armored_car_at_upgrade", "name": "Armored Car Anti-Tank Upgrade", "branch": "infantry",
     "unlocked_by": ["armored_car3"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["armored_car_at_equipment"], "unlocks_equipment_modules": [],
     "unlocks_subunits": []},

    {"key": "mechanised_infantry", "name": "Mechanized Infantry I", "branch": "infantry",
     "unlocked_by": ["motorised_infantry"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["mechanized_equipment_1"], "unlocks_equipment_modules": ["tank_half_track_suspension"],
     "unlocks_subunits": ["mechanized"],
     "unit_bonuses": {"mot_fire_support": {"breakthrough": 0.1, "soft_attack": 0.05},
                       "motorized": {"hardness": 1.0}, "mot_artillery_brigade": {"hardness": 1.0},
                       "mot_anti_tank_brigade": {"hardness": 1.0}, "mot_anti_air_brigade": {"hardness": 1.0},
                       "mot_rocket_artillery_brigade": {"hardness": 1.0}}},
    {"key": "amphibious_mechanized_infantry", "name": "Amphibious Tractors", "branch": "infantry",  # (2026-11-01) real name, not "Amphibious Mechanized Infantry I"
     "unlocked_by": ["mechanised_infantry"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["amphibious_mechanized_equipment_1"], "unlocks_equipment_modules": [],
     "unlocks_subunits": ["amphibious_mechanized"]},
    {"key": "amphibious_mechanized_infantry_2", "name": "Improved Amphibious Tractors", "branch": "infantry",  # (2026-11-01) real name, not "Amphibious Mechanized Infantry II"
     "unlocked_by": ["amphibious_mechanized_infantry"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["amphibious_mechanized_equipment_2"], "unlocks_equipment_modules": [],
     "unlocks_subunits": []},
    {"key": "mechanised_infantry2", "name": "Mechanized Infantry II", "branch": "infantry",
     "unlocked_by": ["mechanised_infantry"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["mechanized_equipment_2"], "unlocks_equipment_modules": [],
     "unlocks_subunits": [],
     "unit_bonuses": {"mot_fire_support": {"breakthrough": 0.1, "soft_attack": 0.05}}},
    {"key": "mechanised_infantry3", "name": "Mechanized Infantry III", "branch": "infantry",
     "unlocked_by": ["mechanised_infantry2"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["mechanized_equipment_3"], "unlocks_equipment_modules": [],
     "unlocks_subunits": [],
     "unit_bonuses": {"mechanized": {"soft_attack": 0.15, "hard_attack": 0.15},
                       "mot_fire_support": {"breakthrough": 0.1, "soft_attack": 0.05}}},

    # ---------------------------------------------------------------
    # NSB_armor.txt
    # ---------------------------------------------------------------

    {"key": "gwtank_chassis", "name": "Inter-War Tank Development", "branch": "armor",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [
         "light_tank_chassis_0", "medium_tank_chassis_0", "heavy_tank_chassis_0",
         "light_tank_destroyer_chassis_0", "medium_tank_destroyer_chassis_0", "heavy_tank_destroyer_chassis_0",
         "light_tank_artillery_chassis_0", "medium_tank_artillery_chassis_0", "heavy_tank_artillery_chassis_0",
         "light_tank_aa_chassis_0", "medium_tank_aa_chassis_0", "heavy_tank_aa_chassis_0",
     ],
     "unlocks_equipment_modules": [
         "tank_torsion_bar_suspension", "tank_riveted_armor", "tank_gasoline_engine", "tank_diesel_engine",
         "tank_petrol_electric_engine", "tank_cast_armor", "tank_christie_suspension", "tank_bogie_suspension",
         "tank_interleaved_suspension", "tank_light_one_man_tank_turret", "tank_light_two_man_tank_turret",
         "tank_light_three_man_tank_turret", "tank_light_fixed_superstructure_turret",
         "tank_medium_one_man_tank_turret", "tank_medium_two_man_tank_turret",
         "tank_medium_three_man_tank_turret", "tank_medium_fixed_superstructure_turret",
         "tank_heavy_two_man_tank_turret", "tank_heavy_three_man_tank_turret",
         "tank_heavy_fixed_superstructure_turret", "tank_super_heavy_four_man_tank_turret",
         "tank_super_heavy_three_man_tank_turret", "tank_modern_tank_turret", "sloped_armor",
         "extra_ammo_storage", "wet_ammo_storage", "smoke_launchers", "expanded_fuel_tank",
     ],
     "unlocks_subunits": ["light_armor", "medium_armor", "heavy_armor"]},

    {"key": "basic_light_tank_chassis", "name": "Basic Light Tank", "branch": "armor",
     "unlocked_by": ["gwtank_chassis"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [
         "light_tank_chassis_1", "light_tank_destroyer_chassis_1",
         "light_tank_artillery_chassis_1", "light_tank_aa_chassis_1",
     ],
     "unlocks_equipment_modules": [], "unlocks_subunits": ["light_armor"]},
    {"key": "improved_light_tank_chassis", "name": "Improved Light Tank", "branch": "armor",
     "unlocked_by": ["basic_light_tank_chassis"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [
         "light_tank_chassis_2", "light_tank_destroyer_chassis_2",
         "light_tank_artillery_chassis_2", "light_tank_aa_chassis_2",
     ],
     "unlocks_equipment_modules": [], "unlocks_subunits": []},
    {"key": "amphibious_tank_chassis", "name": "Amphibious Tank", "branch": "armor",
     "unlocked_by": ["improved_light_tank_chassis"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["amphibious_tank_chassis_1"], "unlocks_equipment_modules": [],
     "unlocks_subunits": ["amphibious_armor"]},
    {"key": "amphibious_drive", "name": "Amphibious Drive", "branch": "armor",
     "unlocked_by": ["amphibious_tank_chassis"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [
         "light_tank_amphibious_chassis_0", "medium_tank_amphibious_chassis_0", "heavy_tank_amphibious_chassis_0",
         "light_tank_amphibious_chassis_1", "medium_tank_amphibious_chassis_1", "heavy_tank_amphibious_chassis_1",
         "light_tank_amphibious_chassis_2", "medium_tank_amphibious_chassis_2", "heavy_tank_amphibious_chassis_2",
         "light_tank_amphibious_chassis_3", "medium_tank_amphibious_chassis_3", "heavy_tank_amphibious_chassis_3",
     ],
     "unlocks_equipment_modules": ["amphibious_drive"], "unlocks_subunits": []},
    {"key": "advanced_light_tank_chassis", "name": "Advanced Light Tank", "branch": "armor",
     "unlocked_by": ["improved_light_tank_chassis"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [
         "light_tank_chassis_3", "light_tank_destroyer_chassis_3",
         "light_tank_artillery_chassis_3", "light_tank_aa_chassis_3",
     ],
     "unlocks_equipment_modules": [], "unlocks_subunits": []},

    {"key": "basic_medium_tank_chassis", "name": "Basic Medium Tank", "branch": "armor",
     "unlocked_by": ["gwtank_chassis"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [
         "medium_tank_chassis_1", "medium_tank_destroyer_chassis_1",
         "medium_tank_artillery_chassis_1", "medium_tank_aa_chassis_1",
     ],
     "unlocks_equipment_modules": [], "unlocks_subunits": ["medium_armor"]},
    {"key": "improved_medium_tank_chassis", "name": "Improved Medium Tank", "branch": "armor",
     "unlocked_by": ["basic_medium_tank_chassis"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [
         "medium_tank_chassis_2", "medium_tank_destroyer_chassis_2",
         "medium_tank_artillery_chassis_2", "medium_tank_aa_chassis_2",
     ],
     "unlocks_equipment_modules": [], "unlocks_subunits": []},
    {"key": "advanced_medium_tank_chassis", "name": "Advanced Medium Tank", "branch": "armor",
     "unlocked_by": ["improved_medium_tank_chassis"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [
         "medium_tank_chassis_3", "medium_tank_destroyer_chassis_3",
         "medium_tank_artillery_chassis_3", "medium_tank_aa_chassis_3",
     ],
     "unlocks_equipment_modules": [], "unlocks_subunits": []},
    {"key": "main_battle_tank_chassis", "name": "Modern Tank", "branch": "armor",
     "unlocked_by": ["advanced_medium_tank_chassis", "advanced_heavy_tank_chassis"],
     "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [
         "modern_tank_chassis_1", "modern_tank_destroyer_chassis_1",
         "modern_tank_artillery_chassis_1", "modern_tank_aa_chassis_1",
     ],
     "unlocks_equipment_modules": [], "unlocks_subunits": ["modern_armor"]},

    {"key": "basic_heavy_tank_chassis", "name": "Basic Heavy Tank", "branch": "armor",
     "unlocked_by": ["gwtank_chassis"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [
         "heavy_tank_chassis_1", "heavy_tank_destroyer_chassis_1",
         "heavy_tank_artillery_chassis_1", "heavy_tank_aa_chassis_1",
     ],
     "unlocks_equipment_modules": [], "unlocks_subunits": ["heavy_armor"]},
    {"key": "improved_heavy_tank_chassis", "name": "Improved Heavy Tank", "branch": "armor",
     "unlocked_by": ["basic_heavy_tank_chassis"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [
         "heavy_tank_chassis_2", "heavy_tank_destroyer_chassis_2",
         "heavy_tank_artillery_chassis_2", "heavy_tank_aa_chassis_2",
     ],
     "unlocks_equipment_modules": [], "unlocks_subunits": []},
    {"key": "advanced_heavy_tank_chassis", "name": "Advanced Heavy Tank", "branch": "armor",
     "unlocked_by": ["improved_heavy_tank_chassis"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [
         "heavy_tank_chassis_3", "heavy_tank_destroyer_chassis_3",
         "heavy_tank_artillery_chassis_3", "heavy_tank_aa_chassis_3",
     ],
     "unlocks_equipment_modules": [], "unlocks_subunits": []},
    {"key": "super_heavy_tank_chassis", "name": "Super-Heavy Tank", "branch": "armor",
     "unlocked_by": ["improved_heavy_tank_chassis"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [
         "super_heavy_tank_chassis_1", "super_heavy_tank_destroyer_chassis_1",
         "super_heavy_tank_artillery_chassis_1", "super_heavy_tank_aa_chassis_1",
     ],
     "unlocks_equipment_modules": ["tank_super_heavy_cannon"], "unlocks_subunits": ["super_heavy_armor"]},

    # Tank Armor Upgrade / Tank Engine Upgrade - stat/module sub-branches,
    # not gated behind any chassis tech.
    {"key": "armor_tech_1", "name": "Basic Armor Protection", "branch": "armor",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": ["tank_welded_armor"], "unlocks_subunits": []},
    {"key": "armor_tech_2", "name": "Improved Armor Protection", "branch": "armor",
     "unlocked_by": ["armor_tech_1"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": ["armor_skirts"], "unlocks_subunits": []},
    {"key": "armor_tech_3", "name": "Advanced Armor Protection", "branch": "armor",
     "unlocked_by": ["armor_tech_2"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": ["lc_armored_skirts"], "unlocks_subunits": []},
    {"key": "armor_tech_4", "name": "Modern Armor Protection", "branch": "armor",
     "unlocked_by": ["armor_tech_3"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": []},

    {"key": "engine_tech_1", "name": "Basic Engine", "branch": "armor",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": []},
    {"key": "engine_tech_2", "name": "Improved Engine", "branch": "armor",
     "unlocked_by": ["engine_tech_1"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": []},
    {"key": "engine_tech_3", "name": "Advanced Engine", "branch": "armor",
     "unlocked_by": ["engine_tech_2"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": []},
    {"key": "engine_tech_4", "name": "Modern Engine", "branch": "armor",
     "unlocked_by": ["engine_tech_3"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": []},

    # --- Special Projects (added 2026-10-01 - see special_project_requires
    # below). unlocked_by is deliberately [] for all 18 entries in this
    # section, even though most have a visual path-parent in the source
    # (e.g. this group's own gwtank_chassis/super_heavy_tank_chassis) -
    # confirmed that path is cosmetic tree-arrow wiring only for these,
    # NOT a hard OR-gate the way it is for every other technology; the
    # only real gate is special_project_requires. ---
    {"key": "sp_armored_advanced_flamethrower_tech", "name": "Advanced Flamethrower (Special Project)", "branch": "armor",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": ["advanced_flamethrower"], "unlocks_subunits": [],
     "special_project_requires": "sp_land_flamethrower_tank",
     "unit_bonuses": {
         "light_flame_tank": {"forest": {"attack": 0.05}, "hills": {"attack": 0.05}, "jungle": {"attack": 0.05}},
         "medium_flame_tank": {"forest": {"attack": 0.05}, "hills": {"attack": 0.05}, "jungle": {"attack": 0.05}},
         "heavy_flame_tank": {"forest": {"attack": 0.05}, "hills": {"attack": 0.05}, "jungle": {"attack": 0.05}},
     }},
    {"key": "sp_armored_lc_naval_engine_conversion_tech", "name": "Naval Engine Conversion (Special Project)", "branch": "armor",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "special_project_requires": "sp_land_land_cruiser",
     "unit_bonuses": {
         "land_cruiser": {"maximum_speed": 0.05, "supply_consumption": -0.02},
         "super_heavy_armor": {"maximum_speed": 0.05, "supply_consumption": -0.02},
     }},
    {"key": "sp_armored_lc_transmission_improvements_tech", "name": "Transmission Improvements (Special Project)", "branch": "armor",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "special_project_requires": "sp_land_land_cruiser",
     "unit_bonuses": {
         "land_cruiser": {"reliability": 0.05, "supply_consumption": -0.02,
                           "forest": {"movement": 0.2}, "hills": {"movement": 0.2},
                           "mountain": {"movement": 0.2}, "jungle": {"movement": 0.2}},
         "super_heavy_armor": {"reliability": 0.05, "supply_consumption": -0.02,
                                "forest": {"movement": 0.2}, "jungle": {"movement": 0.2}},
     }},
    {"key": "sp_armored_lc_specialized_field_manuals_tech", "name": "Specialized Field Manuals (Special Project)", "branch": "armor",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "special_project_requires": "sp_land_land_cruiser",
     "unit_bonuses": {
         "land_cruiser": {"entrenchment": 0.05, "max_strength": 0.05, "max_organisation": 10},
     }},
    {"key": "sp_armored_lc_weapon_fire_control_tech", "name": "Weapon Fire Control (Special Project)", "branch": "armor",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "special_project_requires": "sp_land_land_cruiser",
     "unit_bonuses": {
         "land_cruiser": {"breakthrough": 0.1, "defense": 0.1},
     }},
    {"key": "sp_armored_lc_high_impact_obliterator_cannon_tech", "name": "High-Impact Obliterator Cannon (Special Project)", "branch": "armor",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": ["lc_high_impact_obliterator_cannon"], "unlocks_subunits": [],
     "special_project_requires": "sp_land_land_cruiser"},

    # ---------------------------------------------------------------
    # artillery.txt
    # ---------------------------------------------------------------

    {"key": "gw_artillery", "name": "Artillery I", "branch": "artillery",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["artillery_equipment_1"],
     "unlocks_equipment_modules": ["ship_anti_air_1", "tank_small_cannon", "secondary_turret_small_cannon"],
     "unlocks_subunits": ["field_guns"],
     "unit_bonuses": {"armored_car": {"soft_attack": 0.1}}},
    {"key": "interwar_artillery", "name": "Inter-War Artillery", "branch": "artillery",
     "unlocked_by": ["gw_artillery"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [],
     "unlocks_equipment_modules": ["tank_small_cannon_2", "tank_close_support_gun"],
     "unlocks_subunits": [],
     "unit_bonuses": {"artillery": {"soft_attack": 0.05}, "artillery_brigade": {"soft_attack": 0.1},
                       "mot_artillery_brigade": {"soft_attack": 0.1},
                       "category_self_propelled_artillery": {"soft_attack": 0.05}}},  # (1.19.4) 0.15->0.05, capped
    {"key": "artillery1", "name": "Artillery I", "branch": "artillery",
     "unlocked_by": ["interwar_artillery"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["artillery_equipment_2"],
     "unlocks_equipment_modules": ["tank_medium_howitzer", "tank_medium_cannon", "lc_medium_cannon_turret", "lc_assault_gun"],
     "unlocks_subunits": [],
     "unit_bonuses": {"armored_car": {"soft_attack": 0.1}}},
    {"key": "artillery2", "name": "Improved Artillery Upgrade I", "branch": "artillery",
     "unlocked_by": ["artillery1"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"artillery": {"soft_attack": 0.05}, "artillery_brigade": {"soft_attack": 0.1},
                       "mot_artillery_brigade": {"soft_attack": 0.1},
                       "category_self_propelled_artillery": {"soft_attack": 0.05}}},  # (1.19.4) 0.1->0.05, capped
    {"key": "artillery3", "name": "Improved Artillery Upgrade II", "branch": "artillery",
     "unlocked_by": ["artillery2"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": ["tank_medium_howitzer_2"], "unlocks_subunits": [],
     "unit_bonuses": {"artillery": {"soft_attack": 0.05}, "artillery_brigade": {"soft_attack": 0.1},
                       "mot_artillery_brigade": {"soft_attack": 0.1},
                       "category_self_propelled_artillery": {"soft_attack": 0.025}}},  # (1.19.4) 0.05->0.025
    {"key": "artillery4", "name": "Artillery IV", "branch": "artillery",
     "unlocked_by": ["artillery3"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["artillery_equipment_3"],
     "unlocks_equipment_modules": ["tank_medium_cannon_2"], "unlocks_subunits": [],
     "unit_bonuses": {"armored_car": {"soft_attack": 0.1}}},
    {"key": "artillery5", "name": "Advanced Artillery Upgrade", "branch": "artillery",
     "unlocked_by": ["artillery4"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": ["auto_loader", "tank_heavy_howitzer"],
     "unlocks_subunits": [],
     "unit_bonuses": {"artillery": {"soft_attack": 0.05}, "artillery_brigade": {"soft_attack": 0.1},
                       "mot_artillery_brigade": {"soft_attack": 0.1},
                       "category_self_propelled_artillery": {"soft_attack": 0.025}}},  # (1.19.4) 0.05->0.025

    {"key": "rocket_artillery", "name": "Support Rocket Artillery", "branch": "artillery",
     "unlocked_by": ["artillery2"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["rocket_artillery_equipment_1"],
     "unlocks_equipment_modules": ["tank_rocket_launcher", "rocket_rails", "lc_rocket_launcher"],
     "unlocks_subunits": []},
    {"key": "rocket_artillery2", "name": "Rocket Artillery Upgrade I", "branch": "artillery",
     "unlocked_by": ["rocket_artillery"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"category_rocket_artillery": {"soft_attack": 0.15}, "rocket_battery": {"soft_attack": 0.15}}},
    {"key": "rocket_artillery3", "name": "Rocket Artillery Upgrade II", "branch": "artillery",
     "unlocked_by": ["rocket_artillery2"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"category_rocket_artillery": {"soft_attack": 0.15}, "rocket_battery": {"soft_attack": 0.15}}},
    {"key": "rocket_artillery4", "name": "Rocket Artillery III", "branch": "artillery",
     "unlocked_by": ["rocket_artillery3"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["rocket_artillery_equipment_2"],
     "unlocks_equipment_modules": ["tank_rocket_launcher_2"], "unlocks_subunits": [],
     # motorized_rocket_brigade is a real units_copy/ reference to a disabled
     # (active = no) unit - matches KNOWN_UNRESOLVED_SUBUNIT_KEYS's existing
     # precedent (see this file's own header). Compiled faithfully.
     "unit_bonuses": {"motorized_rocket_brigade": {"soft_attack": 0.3}}},

    {"key": "interwar_antiair", "name": "Anti-Air", "branch": "artillery",
     "unlocked_by": ["gw_artillery"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["anti_air_equipment_1"],
     "unlocks_equipment_modules": ["ship_anti_air_2", "tank_auto_cannon", "tank_anti_air_cannon", "tank_heavy_cannon", "lc_light_anti_air_battery"],
     "unlocks_subunits": ["anti_air_battery"],
     "unit_bonuses": {"armored_car": {"hard_attack": 0.1}}},
    {"key": "antiair1", "name": "Anti-Air Upgrade", "branch": "artillery",
     "unlocked_by": ["interwar_antiair"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"anti_air": {"air_attack": 0.1}, "anti_air_brigade": {"air_attack": 0.1},
                       "anti_air_battery": {"air_attack": 0.1}, "mot_anti_air_brigade": {"air_attack": 0.1},
                       "category_self_propelled_anti_air": {"air_attack": 0.15}}},
    {"key": "antiair2", "name": "Anti-Air II", "branch": "artillery",
     "unlocked_by": ["antiair1"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["anti_air_equipment_2"],
     "unlocks_equipment_modules": ["ship_anti_air_3", "tank_auto_cannon_2", "tank_anti_air_cannon_2", "lc_heavy_anti_air_battery"],
     "unlocks_subunits": [],
     "unit_bonuses": {"armored_car": {"hard_attack": 0.1}}},
    {"key": "antiair3", "name": "Improved Anti-Air Upgrade I", "branch": "artillery",
     "unlocked_by": ["antiair2"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": ["tank_heavy_cannon_2"], "unlocks_subunits": [],
     "unit_bonuses": {"anti_air": {"air_attack": 0.1}, "anti_air_brigade": {"air_attack": 0.1},
                       "anti_air_battery": {"air_attack": 0.1}, "mot_anti_air_brigade": {"air_attack": 0.1},
                       "category_self_propelled_anti_air": {"air_attack": 0.1}}},
    {"key": "antiair4", "name": "Improved Anti-Air Upgrade II", "branch": "artillery",
     "unlocked_by": ["antiair3"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"anti_air": {"air_attack": 0.1}, "anti_air_brigade": {"air_attack": 0.1},
                       "anti_air_battery": {"air_attack": 0.1}, "mot_anti_air_brigade": {"air_attack": 0.1},
                       "category_self_propelled_anti_air": {"air_attack": 0.05}}},
    {"key": "antiair5", "name": "Anti-Air V", "branch": "artillery",
     "unlocked_by": ["antiair4"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["anti_air_equipment_3"],
     "unlocks_equipment_modules": ["ship_anti_air_4", "tank_heavy_cannon_3", "tank_anti_air_cannon_3", "auto_loader", "lc_heavy_anti_air_platform"],
     "unlocks_subunits": [],
     "unit_bonuses": {"armored_car": {"hard_attack": 0.1}}},

    {"key": "interwar_antitank", "name": "Anti-tank", "branch": "artillery",
     "unlocked_by": ["gw_artillery"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["anti_tank_equipment_1"],
     "unlocks_equipment_modules": ["tank_high_velocity_cannon", "tank_heavy_cannon", "tank_buster_1", "lc_high_velocity_cannon_turret"],
     "unlocks_subunits": ["anti_tank_battery"],
     "unit_bonuses": {"armored_car": {"ap_attack": 0.1}}},
    {"key": "antitank1", "name": "Anti-Tank Upgrade", "branch": "artillery",
     "unlocked_by": ["interwar_antitank"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": ["tank_medium_cannon", "squeezebore_adaptor"],
     "unlocks_subunits": [],
     "unit_bonuses": {"category_anti_tank": {"hard_attack": 0.1, "ap_attack": 0.2},
                       "category_tank_destroyers": {"hard_attack": 0.05, "ap_attack": 0.2}}},  # (1.19.4) hard_attack 0.15->0.05, capped
    {"key": "antitank2", "name": "Anti-Tank II", "branch": "artillery",
     "unlocked_by": ["antitank1"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["anti_tank_equipment_2"],
     "unlocks_equipment_modules": ["tank_heavy_cannon_2", "tank_buster_2"], "unlocks_subunits": [],
     "unit_bonuses": {"mot_anti_tank_brigade": {"hard_attack": 0.1, "ap_attack": 0.1},
                       "armored_car": {"ap_attack": 0.1}}},
    {"key": "antitank3", "name": "Improved Anti-Tank Upgrade I", "branch": "artillery",
     "unlocked_by": ["antitank2"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": ["tank_medium_cannon_2"], "unlocks_subunits": [],
     "unit_bonuses": {"category_anti_tank": {"hard_attack": 0.1, "ap_attack": 0.1},
                       "category_tank_destroyers": {"hard_attack": 0.05, "ap_attack": 0.05}}},  # (1.19.4) hard_attack 0.1->0.05, capped
    {"key": "antitank4", "name": "Improved Anti-Tank Upgrade II", "branch": "artillery",
     "unlocked_by": ["antitank3"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": ["tank_high_velocity_cannon_2"], "unlocks_subunits": [],
     "unit_bonuses": {"category_anti_tank": {"hard_attack": 0.1, "ap_attack": 0.1},
                       "category_tank_destroyers": {"hard_attack": 0.05, "ap_attack": 0.05}}},
    {"key": "antitank5", "name": "Anti-Tank V", "branch": "artillery",
     "unlocked_by": ["antitank4"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["anti_tank_equipment_3"],
     "unlocks_equipment_modules": ["tank_high_velocity_cannon_3", "tank_heavy_cannon_3", "auto_loader", "lc_heavy_high_velocity_cannons"],
     "unlocks_subunits": [],
     "unit_bonuses": {"armored_car": {"ap_attack": 0.1}}},

    # --- Special Projects (added 2026-10-01) - see the armor section's own
    # header note above on unlocked_by being deliberately []. sp_shock_hardening_techniques
    # has no unit_bonuses: its only real effect (static_anti_air_damage_factor/
    # static_anti_air_hit_chance_factor) is a global/country-wide field, not
    # item-keyed - same exclusion treatment as Doctrine's own country-wide
    # `modifiers` field. sp_artillery_rocket_assisted_projectiles_tech is the
    # ONE entry (of all 18) with a genuine extra AND requirement
    # (has_tech = experimental_rockets, added to EXTERNAL_DEPENDENCIES below -
    # not a compiled technology, same treatment as tech_signal_company's
    # "radio"). ---
    {"key": "sp_artillery_rocket_assisted_projectiles_tech", "name": "Rocket-Assisted Projectiles (Special Project)", "branch": "artillery",
     "unlocked_by": [], "requires": ["experimental_rockets"], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "special_project_requires": "sp_land_super_heavy_howitzer",
     "unit_bonuses": {
         "super_heavy_artillery": {"soft_attack": 0.1},
         "self_propelled_super_heavy_artillery": {"soft_attack": 0.1},
     }},
    {"key": "sp_artillery_purpose_built_gun_motor_carriages_tech", "name": "Purpose-Built Gun Motor Carriages (Special Project)", "branch": "artillery",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "special_project_requires": "sp_land_self_propelled_super_heavy_howitzer",
     "unit_bonuses": {
         "super_heavy_artillery": {"reliability": 0.07, "supply_consumption": -0.1},
         "self_propelled_super_heavy_artillery": {"reliability": 0.07, "supply_consumption": -0.1},
     }},
    {"key": "sp_shock_hardening_techniques", "name": "Shock-Hardening Techniques (Special Project)", "branch": "artillery",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "special_project_requires": "sp_naval_proximity_fuze"},
    {"key": "sp_variable_time_fuze_shells", "name": "Variable Time Fuze Shells (Special Project)", "branch": "artillery",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "special_project_requires": "sp_naval_proximity_fuze",
     "unit_bonuses": {
         "artillery": {"soft_attack": 0.1},
         "artillery_brigade": {"soft_attack": 0.2},
         "mot_artillery_brigade": {"soft_attack": 0.2},
         "category_self_propelled_artillery": {"soft_attack": 0.05},  # (1.19.4) 0.1->0.05, capped
     }},
    {"key": "sp_advance_sabot_shells", "name": "Advanced Sabot Rounds (Special Project)", "branch": "artillery",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "special_project_requires": "sp_land_large_caliber_kinetic_energy_sabot",
     "unit_bonuses": {
         "anti_tank": {"ap_attack": 0.15},
         "anti_tank_brigade": {"ap_attack": 0.15},
         "mot_anti_tank_brigade": {"ap_attack": 0.15},
         "anti_tank_battery": {"ap_attack": 0.15},
         "category_tank_destroyers": {"ap_attack": 0.05},
     }},

    # ---------------------------------------------------------------
    # support.txt
    # ---------------------------------------------------------------

    {"key": "tech_support", "name": "Support Equipment", "branch": "support",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["support_equipment_1"], "unlocks_equipment_modules": [], "unlocks_subunits": []},

    {"key": "tech_engineers", "name": "Engineer Company I", "branch": "support",
     "unlocked_by": ["tech_support"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": ["engineer"]},
    {"key": "tech_engineers2", "name": "Engineer Company II", "branch": "support",
     "unlocked_by": ["tech_engineers"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": ["dozer_blade"], "unlocks_subunits": [],
     # "fort" here is terrain-nested (same shape as data/terrain.py's own
     # UNIT_TERRAIN_MODIFIERS) - compiled faithfully, deliberately NOT fed
     # into logic/terrain.py this phase (Ollie's explicit call).
     "unit_bonuses": {"engineer": {"entrenchment": 0.50, "fort": {"defence": 0.10, "attack": 0.10}},
                       "assault_engineer": {"breakthrough": 0.1, "fort": {"attack": 0.15}},
                       "armored_engineer": {"entrenchment": 1, "fort": {"defence": 0.15}}}},
    {"key": "tech_engineers3", "name": "Engineer Company III", "branch": "support",
     "unlocked_by": ["tech_engineers2"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": ["lc_obstacle_clearance_gear"], "unlocks_subunits": [],
     "unit_bonuses": {"engineer": {"entrenchment": 0.50, "river": {"attack": 0.1, "defence": 0.10}},
                       "assault_engineer": {"breakthrough": 0.1, "river": {"attack": 0.1}},
                       "armored_engineer": {"entrenchment": 1,
                                             "river": {"attack": 0.05, "defence": 0.05, "movement": 0.15}},
                       "light_flame_tank": {"urban": {"attack": 0.1}, "fort": {"attack": 0.1}},
                       "medium_flame_tank": {"urban": {"attack": 0.1}, "fort": {"attack": 0.1}},
                       "heavy_flame_tank": {"urban": {"attack": 0.1}, "fort": {"attack": 0.1}}}},
    {"key": "tech_engineers4", "name": "Engineer Company IV", "branch": "support",
     "unlocked_by": ["tech_engineers3"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"engineer": {"entrenchment": 0.50, "urban": {"attack": 0.1, "defence": 0.1}},
                       "assault_engineer": {"breakthrough": 0.1, "urban": {"attack": 0.15}},
                       "armored_engineer": {"entrenchment": 1, "urban": {"defence": 0.15, "movement": 0.15}},
                       "light_flame_tank": {"urban": {"attack": 0.1}, "fort": {"attack": 0.1}},
                       "medium_flame_tank": {"urban": {"attack": 0.1}, "fort": {"attack": 0.1}},
                       "heavy_flame_tank": {"urban": {"attack": 0.1}, "fort": {"attack": 0.1}}}},

    {"key": "tech_recon", "name": "Recon Company I", "branch": "support",
     "unlocked_by": ["tech_support"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [],
     "unlocks_subunits": ["recon", "mot_recon", "armored_car_recon", "light_tank_recon"]},
    {"key": "tech_recon2", "name": "Recon Company II", "branch": "support",
     "unlocked_by": ["tech_recon"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"category_recon": {"recon": 2}, "helicopter_recon": {"recon": 1}}},
    {"key": "tech_recon3", "name": "Recon Company III", "branch": "support",
     "unlocked_by": ["tech_recon2"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"category_recon": {"recon": 2}, "helicopter_recon": {"recon": 1},
                       "helicopter_brigade": {"recon": 2}}},
    {"key": "tech_recon4", "name": "Recon Company IV", "branch": "support",
     "unlocked_by": ["tech_recon3"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"category_recon": {"recon": 2}, "helicopter_recon": {"recon": 2}}},

    {"key": "tech_field_hospital", "name": "Field Hospital I", "branch": "support",
     "unlocked_by": ["tech_support"], "requires": ["motorised_infantry"], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": ["field_hospital"]},
    {"key": "tech_field_hospital2", "name": "Field Hospital II", "branch": "support",
     "unlocked_by": ["tech_field_hospital"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"field_hospital": {"casualty_trickleback": 0.10, "experience_loss_factor": -0.10},
                       "helicopter_field_hospital": {"casualty_trickleback": 0.12, "experience_loss_factor": -0.08,
                           "battalion_mult": [{"category": "category_all_infantry", "default_morale": 0.05}]}}},
    {"key": "tech_field_hospital3", "name": "Field Hospital III", "branch": "support",
     "unlocked_by": ["tech_field_hospital2"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"field_hospital": {"casualty_trickleback": 0.1, "experience_loss_factor": -0.10},
                       "helicopter_field_hospital": {"casualty_trickleback": 0.12, "experience_loss_factor": -0.08,
                           "battalion_mult": [{"category": "category_all_infantry", "default_morale": 0.05}]},
                       "helicopter_brigade": {"casualty_trickleback": 0.15, "experience_loss_factor": -0.1,
                           "battalion_mult": [{"category": "category_all_infantry", "default_morale": 0.05}]}}},
    {"key": "tech_field_hospital4", "name": "Field Hospital IV", "branch": "support",
     "unlocked_by": ["tech_field_hospital3"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"field_hospital": {"casualty_trickleback": 0.1, "experience_loss_factor": -0.10},
                       "helicopter_field_hospital": {"casualty_trickleback": 0.12, "experience_loss_factor": -0.08,
                           "battalion_mult": [{"category": "category_all_infantry", "default_morale": 0.05}]}}},

    {"key": "tech_logistics_company", "name": "Logistics Company I", "branch": "support",
     "unlocked_by": ["tech_support"], "requires": ["motorised_infantry"], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": ["logistics_company"]},
    {"key": "tech_logistics_company2", "name": "Logistics Company II", "branch": "support",
     "unlocked_by": ["tech_logistics_company"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"logistics_company": {"supply_consumption_factor": -0.1, "fuel_consumption_factor": -0.05},
                       "helicopter_transport": {"supply_consumption_factor": -0.12}}},
    {"key": "tech_logistics_company3", "name": "Logistics Company III", "branch": "support",
     "unlocked_by": ["tech_logistics_company2"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"logistics_company": {"supply_consumption_factor": -0.1, "fuel_consumption_factor": -0.05},
                       "helicopter_transport": {"supply_consumption_factor": -0.12},
                       "helicopter_brigade": {"supply_consumption_factor": -0.12}}},
    {"key": "tech_logistics_company4", "name": "Logistics Company IV", "branch": "support",
     "unlocked_by": ["tech_logistics_company3"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"logistics_company": {"supply_consumption_factor": -0.1, "fuel_consumption_factor": -0.05},
                       "helicopter_transport": {"supply_consumption_factor": -0.15}}},

    {"key": "tech_military_police", "name": "Military Police I", "branch": "support",
     "unlocked_by": ["tech_support"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": ["military_police"]},
    {"key": "tech_military_police2", "name": "Military Police II", "branch": "support",
     "unlocked_by": ["tech_military_police"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"military_police": {"suppression_factor": 0.1},
                       "motorized_military_police": {"suppression_factor": 0.1,
                           "battalion_mult": [{"category": "category_vehicle_infantry", "default_morale": 0.05}]}}},
    {"key": "tech_military_police3", "name": "Military Police III", "branch": "support",
     "unlocked_by": ["tech_military_police2"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"military_police": {"suppression_factor": 0.1},
                       "motorized_military_police": {"suppression_factor": 0.1,
                           "battalion_mult": [{"category": "category_vehicle_infantry", "default_morale": 0.05}]}}},
    {"key": "tech_military_police4", "name": "Military Police IV", "branch": "support",
     "unlocked_by": ["tech_military_police3"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"military_police": {"suppression_factor": 0.1},
                       "motorized_military_police": {"suppression_factor": 0.1,
                           "battalion_mult": [{"category": "category_vehicle_infantry", "default_morale": 0.05}]}}},

    {"key": "tech_maintenance_company", "name": "Maintenance Company I", "branch": "support",
     "unlocked_by": ["tech_support"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": ["maintenance_company"]},
    {"key": "tech_maintenance_company2", "name": "Maintenance Company II", "branch": "support",
     "unlocked_by": ["tech_maintenance_company"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": ["easy_maintenance"], "unlocks_subunits": [],
     "unit_bonuses": {"maintenance_company": {"reliability_factor": 0.05, "equipment_capture_factor": 0.05},
                       "armored_maintenance": {"reliability_factor": 0.02, "recovery": 0.03,
                                                "equipment_capture_factor": 0.1}}},
    {"key": "tech_maintenance_company3", "name": "Maintenance Company III", "branch": "support",
     "unlocked_by": ["tech_maintenance_company2"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"maintenance_company": {"reliability_factor": 0.05,
                           "battalion_mult": [{"category": "category_all_armor", "equipment_capture_factor": 0.01,
                                                "add": True, "display_as_percentage": True}]},
                       "armored_maintenance": {"reliability_factor": 0.02, "recovery": 0.03,
                           "battalion_mult": [{"category": "category_all_armor", "equipment_capture_factor": 0.02,
                                                "add": True, "display_as_percentage": True}]}}},
    {"key": "tech_maintenance_company4", "name": "Maintenance Company IV", "branch": "support",
     "unlocked_by": ["tech_maintenance_company3"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"maintenance_company": {"reliability_factor": 0.05, "equipment_capture_factor": 0.05},
                       "armored_maintenance": {"reliability_factor": 0.02, "recovery": 0.03,
                                                "equipment_capture_factor": 0.1}}},

    {"key": "tech_signal_company", "name": "Signal Company I", "branch": "support",
     "unlocked_by": ["tech_support"], "requires": ["radio", "motorised_infantry"], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": ["signal_company"]},
    {"key": "tech_signal_company2", "name": "Signal Company II", "branch": "support",
     "unlocked_by": ["tech_signal_company"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"signal_company": {"initiative": 0.12},
                       "armored_signal": {"initiative": 0.08,
                           "battalion_mult": [{"category": "category_all_armor", "breakthrough": 0.01}]}}},
    {"key": "tech_signal_company3", "name": "Signal Company III", "branch": "support",
     "unlocked_by": ["tech_signal_company2"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"signal_company": {"initiative": 0.12},
                       "armored_signal": {"initiative": 0.08,
                           "battalion_mult": [{"category": "category_all_armor", "breakthrough": 0.01}]}}},
    {"key": "tech_signal_company4", "name": "Signal Company IV", "branch": "support",
     "unlocked_by": ["tech_signal_company3"], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": [],
     "unit_bonuses": {"signal_company": {"initiative": 0.12},
                       "armored_signal": {"initiative": 0.08,
                           "battalion_mult": [{"category": "category_all_armor", "breakthrough": 0.01}]}}},

    # --- Special Projects (added 2026-10-01) - see the armor section's own
    # header note above on unlocked_by being deliberately []. All 7 of these
    # unlock a support company that was previously in ALWAYS_UNLOCKED_SUBUNITS
    # (see logic/research.py) - a real, deliberate tightening, not a bug: see
    # Activity_Log.md, 2026-10-01. sp_armored_motorized_military_police_tech's
    # own source unlocks "motorbike_equipment_1", which doesn't exist as a
    # separate tier - aliased to the existing "motorbike_equipment" key per
    # Ollie's own call rather than inventing a new tier. ---
    {"key": "sp_armored_engineer_tech", "name": "Armored Engineer Company (Special Project)", "branch": "support",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": ["armored_engineer"],
     "special_project_requires": "sp_land_military_engineering_vehicles"},
    {"key": "sp_armored_maintenance_tech", "name": "Armored Maintenance Company (Special Project)", "branch": "support",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": ["armored_maintenance"],
     "special_project_requires": "sp_land_military_engineering_vehicles"},
    {"key": "sp_armored_signal_tech", "name": "Armored Signal Company (Special Project)", "branch": "support",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": ["lc_command_center"], "unlocks_subunits": ["armored_signal"],
     "special_project_requires": "sp_land_military_engineering_vehicles"},
    {"key": "sp_helicopter_transport_pods_tech", "name": "Helicopter Transport Company (Special Project)", "branch": "support",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": ["helicopter_transport"],
     "special_project_requires": "sp_air_helicopter"},
    {"key": "sp_helicopter_artillery_observers_tech", "name": "Helicopter Recon Company (Special Project)", "branch": "support",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": ["helicopter_recon"],
     "special_project_requires": "sp_air_helicopter"},
    {"key": "sp_helicopter_med_evac_tech", "name": "Helicopter Med-Evac Company (Special Project)", "branch": "support",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": [], "unlocks_equipment_modules": [], "unlocks_subunits": ["helicopter_field_hospital"],
     "special_project_requires": "sp_air_helicopter"},
    {"key": "sp_armored_motorized_military_police_tech", "name": "Motorized Military Police (Special Project)", "branch": "support",
     "unlocked_by": [], "requires": [], "mutually_exclusive_with": [],
     "unlocks_equipment": ["motorbike_equipment"], "unlocks_equipment_modules": [],
     "unlocks_subunits": ["motorized_military_police"],
     "special_project_requires": "sp_land_military_engineering_vehicles"},
]

# 68 of the first 119 technologies above define a real "unit_bonuses" field
# (compiled 2026-09-29 from technologies_copy/infantry.txt/artillery.txt/
# support.txt - NSB_armor.txt contributed none from its non-Special-Project
# entries; several of the 18 Special Project technologies added 2026-10-01
# below DO have unit_bonuses, including some from NSB_armor.txt - see that
# section). Every entry without one in the source has none here either;
# rather than write "unit_bonuses": {} on every one by hand, this loop
# guarantees the field is always present (matching every other field's
# "always present, even empty" convention - see unlocks_subunits etc.) so
# callers can index tech["unit_bonuses"] directly without a .get() fallback.
# Same treatment for "special_project_requires" (added 2026-10-01): None
# for every technology except the 18 Special Project entries, each of which
# sets it explicitly to the bare data/special_projects.py key it needs
# completed - see that file and logic/research.py's is_researchable.
#
# "year" (added 2026-11-02, Ollie's own request - show each technology's
# real historical unlock year, e.g. "Improved Infantry Equipment I
# (1938)", in the Research tab): taken directly from each technology's own
# `start_year` field in the real technologies_copy/*.txt source files, via
# a one-off block-scoped parser (not a blind file-wide regex, which would
# also match the unrelated `@1936 = 2`-style position-constant table at
# the top of each file). A lookup table rather than editing each of the
# 137 hand-formatted dict literals above directly - every value needed is
# distinct (unlike unit_bonuses/special_project_requires's shared `{}`/
# `None` defaults), and a flat key->year table is far safer to generate
# and verify than a line-insertion script touching 137 separately-
# formatted blocks. Every compiled technology has a real value here
# except gw_artillery - confirmed by direct inspection of its own source
# block, not a parsing gap: it's the root/always-available base artillery
# tech and genuinely carries no start_year in the game's own data.
_TECHNOLOGY_YEARS = {
    "infantry_weapons": 1918,
    "infantry_weapons1": 1936,
    "infantry_weapons2": 1938,
    "improved_infantry_weapons": 1939,
    "improved_infantry_weapons_2": 1940,
    "infantry_at": 1942,
    "infantry_at2": 1943,
    "advanced_infantry_weapons": 1942,
    "advanced_infantry_weapons2": 1944,
    "paratroopers": 1936,
    "paratroopers2": 1939,
    "paratroopers3": 1943,
    "marines": 1936,
    "marines2": 1939,
    "marines3": 1943,
    "tech_mountaineers": 1936,
    "tech_mountaineers2": 1939,
    "tech_mountaineers3": 1943,
    "rangers_tech": 1936,
    "rangers_tech2": 1939,
    "rangers_tech3": 1943,
    "tech_special_forces": 1938,
    "advanced_special_forces": 1940,
    "improved_special_forces": 1940,
    "extreme_environment_training": 1942,
    "survival_training": 1942,
    "elite_forces": 1944,
    "night_vision": 1943,
    "night_vision2": 1946,
    "support_weapons": 1918,
    "support_weapons2": 1938,
    "support_weapons3": 1940,
    "support_weapons4": 1942,
    "tech_trucks": 1936,
    "motorised_infantry": 1936,
    "motorized_rocket_unit": 1939,
    "armored_car1": 1914,
    "armored_car2": 1940,
    "armored_car3": 1942,
    "armored_car_at_upgrade": 1942,
    "mechanised_infantry": 1940,
    "amphibious_mechanized_infantry": 1941,
    "amphibious_mechanized_infantry_2": 1943,
    "mechanised_infantry2": 1942,
    "mechanised_infantry3": 1944,
    "gwtank_chassis": 1918,
    "basic_light_tank_chassis": 1934,
    "improved_light_tank_chassis": 1936,
    "amphibious_tank_chassis": 1938,
    "amphibious_drive": 1941,
    "advanced_light_tank_chassis": 1941,
    "basic_medium_tank_chassis": 1938,
    "improved_medium_tank_chassis": 1940,
    "advanced_medium_tank_chassis": 1943,
    "main_battle_tank_chassis": 1945,
    "basic_heavy_tank_chassis": 1934,
    "improved_heavy_tank_chassis": 1940,
    "advanced_heavy_tank_chassis": 1943,
    "super_heavy_tank_chassis": 1941,
    "armor_tech_1": 1936,
    "armor_tech_2": 1938,
    "armor_tech_3": 1941,
    "armor_tech_4": 1944,
    "engine_tech_1": 1934,
    "engine_tech_2": 1938,
    "engine_tech_3": 1941,
    "engine_tech_4": 1944,
    "sp_armored_advanced_flamethrower_tech": 1941,
    "sp_armored_lc_naval_engine_conversion_tech": 1943,
    "sp_armored_lc_transmission_improvements_tech": 1943,
    "sp_armored_lc_specialized_field_manuals_tech": 1943,
    "sp_armored_lc_weapon_fire_control_tech": 1945,
    "sp_armored_lc_high_impact_obliterator_cannon_tech": 1943,
    "gw_artillery": None,
    "interwar_artillery": 1936,
    "artillery1": 1939,
    "artillery2": 1940,
    "artillery3": 1941,
    "artillery4": 1942,
    "artillery5": 1943,
    "rocket_artillery": 1940,
    "rocket_artillery2": 1941,
    "rocket_artillery3": 1942,
    "rocket_artillery4": 1943,
    "interwar_antiair": 1936,
    "antiair1": 1939,
    "antiair2": 1940,
    "antiair3": 1941,
    "antiair4": 1942,
    "antiair5": 1943,
    "interwar_antitank": 1936,
    "antitank1": 1939,
    "antitank2": 1940,
    "antitank3": 1941,
    "antitank4": 1942,
    "antitank5": 1943,
    "sp_artillery_rocket_assisted_projectiles_tech": 1940,
    "sp_artillery_purpose_built_gun_motor_carriages_tech": 1940,
    "sp_shock_hardening_techniques": 1941,
    "sp_variable_time_fuze_shells": 1942,
    "sp_advance_sabot_shells": 1942,
    "tech_support": 1918,
    "tech_engineers": 1936,
    "tech_engineers2": 1939,
    "tech_engineers3": 1942,
    "tech_engineers4": 1945,
    "tech_recon": 1936,
    "tech_recon2": 1939,
    "tech_recon3": 1942,
    "tech_recon4": 1945,
    "tech_field_hospital": 1936,
    "tech_field_hospital2": 1939,
    "tech_field_hospital3": 1942,
    "tech_field_hospital4": 1945,
    "tech_logistics_company": 1936,
    "tech_logistics_company2": 1939,
    "tech_logistics_company3": 1942,
    "tech_logistics_company4": 1945,
    "tech_military_police": 1936,
    "tech_military_police2": 1939,
    "tech_military_police3": 1942,
    "tech_military_police4": 1945,
    "tech_maintenance_company": 1936,
    "tech_maintenance_company2": 1939,
    "tech_maintenance_company3": 1942,
    "tech_maintenance_company4": 1945,
    "tech_signal_company": 1936,
    "tech_signal_company2": 1939,
    "tech_signal_company3": 1942,
    "tech_signal_company4": 1945,
    "sp_armored_engineer_tech": 1938,
    "sp_armored_maintenance_tech": 1938,
    "sp_armored_signal_tech": 1938,
    "sp_helicopter_transport_pods_tech": 1938,
    "sp_helicopter_artillery_observers_tech": 1938,
    "sp_helicopter_med_evac_tech": 1938,
    "sp_armored_motorized_military_police_tech": 1938,
}

for _tech in TECHNOLOGIES:
    _tech.setdefault("unit_bonuses", {})
    _tech.setdefault("special_project_requires", None)
    _tech["year"] = _TECHNOLOGY_YEARS.get(_tech["key"])
del _tech

BRANCHES = ["infantry", "armor", "artillery", "support"]

BRANCH_LABELS = {
    "infantry": "Infantry",
    "armor": "Armor",
    "artillery": "Artillery",
    "support": "Support",
}
