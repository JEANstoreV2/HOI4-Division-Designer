import re

from data.battalions import BATTALIONS
from data.equipment import EQUIPMENT
from data.regimental_support import REGIMENTAL_SUPPORT
from data.support_companies import SUPPORT_COMPANIES
from data.tank_modules import TANK_MODULES
from data.special_projects import SPECIAL_PROJECTS
from data.technologies import BRANCH_LABELS, BRANCHES, EXTERNAL_DEPENDENCIES, TECHNOLOGIES
from data.unit_categories import UNIT_CATEGORIES

SPECIAL_PROJECT_KEYS = {p["key"] for p in SPECIAL_PROJECTS}

TECH_KEYS = {t["key"] for t in TECHNOLOGIES}
MODULE_KEYS = {m["key"] for m in TANK_MODULES}

SUBUNIT_KEYS = (
    {b["key"] for b in BATTALIONS}
    | {c["key"] for c in SUPPORT_COMPANIES}
    | {r["key"] for r in REGIMENTAL_SUPPORT}
)

ALL_CATEGORY_KEYS = {category for categories in UNIT_CATEGORIES.values() for category in categories}

# unit_bonuses' target keys that are neither a real category tag nor a real
# SUBUNIT_KEYS item - both confirmed, not gaps:
# - "motorized_rocket_brigade" (artillery.txt's rocket_artillery4): the same
#   disabled (active = no) unit already documented by
#   KNOWN_UNRESOLVED_SUBUNIT_KEYS above.
KNOWN_UNRESOLVED_UNIT_BONUS_TARGETS = {"motorized_rocket_brigade"}

# technologies_copy/infantry.txt's motorized_rocket_unit tech enables
# "motorized_rocket_brigade", which will never resolve against
# data/battalions.py - by design, not a gap. units_copy/artillery_brigade.txt
# defines it with active = no (disabled in-game), unlike its active
# counterpart "mot_rocket_artillery_brigade" which data/battalions.py
# correctly includes instead. See data/technologies.py's header.
KNOWN_UNRESOLVED_SUBUNIT_KEYS = {"motorized_rocket_brigade"}

# Two equipment keys enabled by armored-car techs that predate/extend the
# "_1" tier data/equipment.py models (see that file's own header on
# gw_armored_car_equipment/armored_car_equipment_1) - not modeled as
# distinct EQUIPMENT entries yet. "motorized_rocket_equipment_1" is the
# equipment for the same disabled (active = no) "motorized_rocket_brigade"
# unit as KNOWN_UNRESOLVED_SUBUNIT_KEYS above - since that battalion was
# correctly never compiled into data/battalions.py, its equipment was never
# compiled into data/equipment.py either.
KNOWN_UNRESOLVED_EQUIPMENT_KEYS = {
    "gw_armored_car_equipment", "armored_car_at_equipment", "motorized_rocket_equipment_1",
}

# `unlocks_equipment_modules` is copied verbatim from each source file's own
# `enable_equipment_modules` block (see this file's own header) - some of
# those blocks also enable non-Tank-Designer equipment that happens to live
# in the same tech (naval AA equipment on artillery.txt's land AA techs;
# towed AT/artillery gun variants alongside their tank-gun counterparts).
# Real source content, correctly never compiled into data/tank_modules.py.
KNOWN_NON_TANK_DESIGNER_MODULE_KEYS = {
    "ship_anti_air_1", "ship_anti_air_2", "ship_anti_air_3", "ship_anti_air_4",
    "rocket_rails", "tank_buster_1", "tank_buster_2",
}

_TIER_SUFFIX = re.compile(r"_\d+$")


def _equipment_base_key(equipment_key):
    return _TIER_SUFFIX.sub("", equipment_key)


def test_no_duplicate_keys():
    keys = [t["key"] for t in TECHNOLOGIES]
    assert len(keys) == len(set(keys))


def test_all_branches_are_declared():
    assert {t["branch"] for t in TECHNOLOGIES} <= set(BRANCHES)


def test_every_branch_has_a_label():
    assert set(BRANCH_LABELS) == set(BRANCHES)


def test_unlocked_by_references_real_technologies():
    for t in TECHNOLOGIES:
        for prereq in t["unlocked_by"]:
            assert prereq in TECH_KEYS, (t["key"], prereq)


def test_requires_references_real_technologies_or_documented_external_keys():
    for t in TECHNOLOGIES:
        for dep in t["requires"]:
            assert dep in TECH_KEYS or dep in EXTERNAL_DEPENDENCIES, (t["key"], dep)


def test_mutually_exclusive_with_references_real_technologies():
    for t in TECHNOLOGIES:
        for other in t["mutually_exclusive_with"]:
            assert other in TECH_KEYS, (t["key"], other)


def test_mutually_exclusive_with_is_symmetric():
    by_key = {t["key"]: t for t in TECHNOLOGIES}
    for t in TECHNOLOGIES:
        for other in t["mutually_exclusive_with"]:
            assert t["key"] in by_key[other]["mutually_exclusive_with"], (t["key"], other)


def test_no_technology_lists_itself():
    for t in TECHNOLOGIES:
        assert t["key"] not in t["unlocked_by"]
        assert t["key"] not in t["requires"]
        assert t["key"] not in t["mutually_exclusive_with"]


def test_unlocks_equipment_references_real_equipment():
    for t in TECHNOLOGIES:
        for equipment_key in t["unlocks_equipment"]:
            if equipment_key in KNOWN_UNRESOLVED_EQUIPMENT_KEYS:
                continue
            assert _equipment_base_key(equipment_key) in EQUIPMENT, (t["key"], equipment_key)


def test_unlocks_subunits_references_real_battalions_or_companies():
    for t in TECHNOLOGIES:
        for subunit_key in t["unlocks_subunits"]:
            if subunit_key in KNOWN_UNRESOLVED_SUBUNIT_KEYS:
                continue
            assert subunit_key in SUBUNIT_KEYS, (t["key"], subunit_key)


def test_unlocks_equipment_modules_references_real_modules_or_known_non_tank_designer_items():
    for t in TECHNOLOGIES:
        for module_key in t["unlocks_equipment_modules"]:
            if module_key in KNOWN_NON_TANK_DESIGNER_MODULE_KEYS:
                continue
            assert module_key in MODULE_KEYS, (t["key"], module_key)


def test_expected_entry_count():
    # A regression tripwire: if this changes, it should be a deliberate
    # addition/removal, not an accidental one. 131 = 137 (119 + the 18
    # Special Project technologies compiled 2026-10-01) minus 6 - the
    # tech_special_forces branch, removed 2026-11-03 once Ollie reported
    # never seeing it in his own real tech tree (it's genuinely
    # unreachable for any player owning Arms Against Tyranny, which Ollie
    # does - see data/technologies.py's own removal note for the full
    # source-file confirmation).
    assert len(TECHNOLOGIES) == 131


# --- unit_bonuses (added 2026-09-29) ---

def test_every_technology_has_a_unit_bonuses_field():
    # Always present, even when empty - matches unlocks_subunits' own
    # "always a list, never missing" convention (see this file's own
    # setdefault normalization loop).
    for t in TECHNOLOGIES:
        assert "unit_bonuses" in t, t["key"]


def test_expected_unit_bonuses_count():
    # A regression tripwire mirroring test_expected_entry_count: 72 = 77
    # (the original 68 + 9 of the 18 Special Project technologies added
    # 2026-10-01) minus 5 - 5 of the 6 tech_special_forces-branch entries
    # removed 2026-11-03 had a non-empty unit_bonuses (improved_special_forces,
    # the 6th, had an empty one and was never counted in the original 77).
    assert sum(1 for t in TECHNOLOGIES if t["unit_bonuses"]) == 72


def test_unit_bonuses_target_keys_reference_real_categories_or_subunits():
    for t in TECHNOLOGIES:
        for target_key in t["unit_bonuses"]:
            if target_key in KNOWN_UNRESOLVED_UNIT_BONUS_TARGETS:
                continue
            assert target_key in ALL_CATEGORY_KEYS or target_key in SUBUNIT_KEYS, (t["key"], target_key)


def test_unit_bonuses_battalion_mult_categories_reference_real_categories():
    # battalion_mult entries nest their own "category" field one level
    # deeper than a plain unit_bonuses target key - checked separately.
    for t in TECHNOLOGIES:
        for target_key, stat_dict in t["unit_bonuses"].items():
            for mult in stat_dict.get("battalion_mult", []):
                assert mult["category"] in ALL_CATEGORY_KEYS, (t["key"], target_key, mult["category"])


def test_infantry_at_bonus_matches_the_1_19_3_patch_notes_exactly():
    # infantry_at/infantry_at2 are the two technologies that originally
    # surfaced this whole feature (1.19.3 patch cleanup's "Anti-Tank
    # technology stat bonuses" item) - spot-checked directly against
    # technologies_copy/infantry.txt.
    by_key = {t["key"]: t for t in TECHNOLOGIES}
    expected = {
        "category_all_infantry": {"hard_attack": 0.25, "ap_attack": 1},
        "category_cavalry": {"hard_attack": 0.1, "ap_attack": 0.4},
        "fire_support": {"hard_attack": 0.15, "ap_attack": 0.5},
        "mot_fire_support": {"hard_attack": 0.15, "ap_attack": 0.5},
    }
    assert by_key["infantry_at"]["unit_bonuses"] == expected
    assert by_key["infantry_at2"]["unit_bonuses"] == expected


def test_mountain_gun_terrain_nested_bonus_compiled_but_not_a_flat_field():
    # Confirms terrain-nested bonuses ARE compiled (not silently dropped)
    # even though nothing reads them yet - see this file's own header on
    # the deliberate deferral.
    by_key = {t["key"]: t for t in TECHNOLOGIES}
    # mountain_gun itself is a hidden/national-focus tech (artillery.txt),
    # not compiled here at all - use tech_engineers2's fort-nested bonus
    # instead, which IS a real, compiled technology.
    assert by_key["tech_engineers2"]["unit_bonuses"]["engineer"]["fort"] == {"defence": 0.10, "attack": 0.10}


def test_a_technology_with_no_bonus_has_an_empty_dict_not_a_missing_key():
    by_key = {t["key"]: t for t in TECHNOLOGIES}
    assert by_key["infantry_weapons"]["unit_bonuses"] == {}


# --- Special Projects (added 2026-10-01) ---

def test_every_technology_has_a_special_project_requires_field():
    for t in TECHNOLOGIES:
        assert "special_project_requires" in t, t["key"]


def test_special_project_requires_is_none_or_a_real_project_key():
    for t in TECHNOLOGIES:
        req = t["special_project_requires"]
        assert req is None or req in SPECIAL_PROJECT_KEYS, (t["key"], req)


def test_expected_special_project_gated_technology_count():
    # A regression tripwire mirroring test_expected_entry_count: all 18 of
    # the technologies added 2026-10-01 (6 NSB_armor.txt, 5 artillery.txt,
    # 7 support.txt) set special_project_requires; nothing else does.
    assert sum(1 for t in TECHNOLOGIES if t["special_project_requires"] is not None) == 18


def test_special_project_gated_technologies_have_no_unlocked_by():
    # Confirmed against the source (Activity_Log.md, 2026-10-01): the only
    # real gate for these 18 is special_project_requires. Each has a visual
    # path-parent in technologies_copy/ that is NOT a hard OR-gate - kept
    # out of unlocked_by entirely rather than misrepresented as one.
    for t in TECHNOLOGIES:
        if t["special_project_requires"] is not None:
            assert t["unlocked_by"] == [], t["key"]


def test_sp_artillery_rocket_assisted_projectiles_has_the_one_genuine_extra_requires():
    by_key = {t["key"]: t for t in TECHNOLOGIES}
    assert by_key["sp_artillery_rocket_assisted_projectiles_tech"]["requires"] == ["experimental_rockets"]
    assert "experimental_rockets" in EXTERNAL_DEPENDENCIES
    # No other Special Project technology has a requires entry.
    for t in TECHNOLOGIES:
        if t["special_project_requires"] is not None and t["key"] != "sp_artillery_rocket_assisted_projectiles_tech":
            assert t["requires"] == [], t["key"]


def test_sp_advance_sabot_shells_bonus_matches_the_source_exactly():
    by_key = {t["key"]: t for t in TECHNOLOGIES}
    expected = {
        "anti_tank": {"ap_attack": 0.15},
        "anti_tank_brigade": {"ap_attack": 0.15},
        "mot_anti_tank_brigade": {"ap_attack": 0.15},
        "anti_tank_battery": {"ap_attack": 0.15},
        "category_tank_destroyers": {"ap_attack": 0.05},
    }
    assert by_key["sp_advance_sabot_shells"]["unit_bonuses"] == expected


def test_sp_armored_motorized_military_police_aliases_to_existing_motorbike_equipment():
    # The source's own "motorbike_equipment_1" doesn't exist as a tier -
    # aliased to the existing untiered key per Ollie's own call rather than
    # inventing a new tier (Activity_Log.md, 2026-10-01).
    by_key = {t["key"]: t for t in TECHNOLOGIES}
    assert by_key["sp_armored_motorized_military_police_tech"]["unlocks_equipment"] == ["motorbike_equipment"]


def test_corrected_infantry_branch_technology_names():
    # Added 2026-11-01 - Ollie couldn't find "Infantry Weapons III" (etc.)
    # anywhere in his real tech tree, which led to discovering Technology
    # names had never been audited against the real game's own
    # localisation at all, unlike Doctrine/Subdoctrine/Special Project
    # names (2026-10-08/2026-10-02). A focused pass over the Infantry
    # branch (where Ollie's report pointed) found these real mismatches -
    # some of these technologies have no distinct name of their own at all
    # in the real localisation (e.g. infantry_weapons1, mechanised_infantry)
    # and are left as this project's own "append a roman numeral" naming
    # convention, which isn't a confirmed bug, just an approximation of a
    # real in-engine auto-numbering convention - only entries with a real,
    # confirmed, DIFFERENT override name are pinned here. The other 3
    # branches (armor, artillery, support) were audited the same way
    # 2026-11-03 - see test_corrected_armor_artillery_and_support_branch_technology_names
    # below, a much bigger finding (62 real mismatches).
    expected_names = {
        "infantry_weapons2": "Improved Infantry Equipment I",
        "improved_infantry_weapons_2": "Improved Infantry Equipment II",
        "advanced_infantry_weapons2": "Improved Infantry Equipment III",
        "tech_mountaineers": "Mountain Infantry I",
        "tech_mountaineers2": "Mountain Infantry II",
        "tech_mountaineers3": "Mountain Infantry III",
        # tech_special_forces/improved_special_forces were both corrected
        # here (2026-11-01) but removed from the compile entirely
        # 2026-11-03 - see data/technologies.py's own removal note - so
        # they're no longer pinned in this dict.
        "amphibious_mechanized_infantry": "Amphibious Tractors",
        "amphibious_mechanized_infantry_2": "Improved Amphibious Tractors",
        "armored_car1": "Inter-War Armored Car",
        "armored_car2": "Basic Armored Car",
        "armored_car3": "Improved Armored Car",
    }
    by_key = {t["key"]: t["name"] for t in TECHNOLOGIES}
    for key, expected_name in expected_names.items():
        assert by_key[key] == expected_name, key


def test_corrected_armor_artillery_and_support_branch_technology_names():
    # Added 2026-11-03 - the "other 3 branches not audited" gap flagged by
    # the test above was closed this session: a full pass over armor (28),
    # artillery (28), and support (36) against the real game's own
    # localisation (research_l_english.yml, falling back to
    # tank_modules_l_english.yml/unit_l_english.yml/equipment_l_english.yml
    # for technologies that display via their own equipment/unit name - the
    # same indirection pattern the infantry audit above already established)
    # found 62 real mismatches, far more than infantry's 13/45 - the armor
    # and artillery branches in particular had apparently never been
    # cross-checked at all during their original compile (every single
    # non-special-project entry in both was wrong), while support was
    # mostly already correct (9 wrong out of 29) - closer to infantry's own
    # ratio. A handful of the 18 Special-Project-gated technologies across
    # all 3 branches needed fixing too (beyond this project's own added
    # "(Special Project)" suffix) - real name differences, not just
    # punctuation (e.g. "Helicopter Transport Pods" is really "Helicopter
    # Transport Company"; "Advanced Sabot Shells" is really "Advanced Sabot
    # Rounds"). `gw_artillery` (the one technology confirmed to have no real
    # distinct name at all, same as it has no real `year`) is deliberately
    # left out of this dict, same "no override without a real name"
    # convention as infantry's own `infantry_weapons1`/`mechanised_infantry`.
    expected_names = {
        # armor
        "gwtank_chassis": "Inter-War Tank Development",
        "basic_light_tank_chassis": "Basic Light Tank",
        "improved_light_tank_chassis": "Improved Light Tank",
        "amphibious_tank_chassis": "Amphibious Tank",
        "advanced_light_tank_chassis": "Advanced Light Tank",
        "basic_medium_tank_chassis": "Basic Medium Tank",
        "improved_medium_tank_chassis": "Improved Medium Tank",
        "advanced_medium_tank_chassis": "Advanced Medium Tank",
        "main_battle_tank_chassis": "Modern Tank",
        "basic_heavy_tank_chassis": "Basic Heavy Tank",
        "improved_heavy_tank_chassis": "Improved Heavy Tank",
        "advanced_heavy_tank_chassis": "Advanced Heavy Tank",
        "super_heavy_tank_chassis": "Super-Heavy Tank",
        "armor_tech_1": "Basic Armor Protection",
        "armor_tech_2": "Improved Armor Protection",
        "armor_tech_3": "Advanced Armor Protection",
        "armor_tech_4": "Modern Armor Protection",
        "engine_tech_1": "Basic Engine",
        "engine_tech_2": "Improved Engine",
        "engine_tech_3": "Advanced Engine",
        "engine_tech_4": "Modern Engine",
        "sp_armored_lc_high_impact_obliterator_cannon_tech": "High-Impact Obliterator Cannon (Special Project)",
        # artillery
        "interwar_artillery": "Inter-War Artillery",
        "artillery1": "Artillery I",
        "artillery2": "Improved Artillery Upgrade I",
        "artillery3": "Improved Artillery Upgrade II",
        "artillery4": "Artillery IV",
        "artillery5": "Advanced Artillery Upgrade",
        "rocket_artillery": "Support Rocket Artillery",
        "rocket_artillery2": "Rocket Artillery Upgrade I",
        "rocket_artillery3": "Rocket Artillery Upgrade II",
        "rocket_artillery4": "Rocket Artillery III",
        "interwar_antiair": "Anti-Air",
        "antiair1": "Anti-Air Upgrade",
        "antiair2": "Anti-Air II",
        "antiair3": "Improved Anti-Air Upgrade I",
        "antiair4": "Improved Anti-Air Upgrade II",
        "antiair5": "Anti-Air V",
        "interwar_antitank": "Anti-tank",
        "antitank1": "Anti-Tank Upgrade",
        "antitank2": "Anti-Tank II",
        "antitank3": "Improved Anti-Tank Upgrade I",
        "antitank4": "Improved Anti-Tank Upgrade II",
        "antitank5": "Anti-Tank V",
        "sp_artillery_rocket_assisted_projectiles_tech": "Rocket-Assisted Projectiles (Special Project)",
        "sp_shock_hardening_techniques": "Shock-Hardening Techniques (Special Project)",
        "sp_advance_sabot_shells": "Advanced Sabot Rounds (Special Project)",
        # support
        "tech_support": "Support Equipment",
        "tech_engineers": "Engineer Company I",
        "tech_engineers2": "Engineer Company II",
        "tech_engineers3": "Engineer Company III",
        "tech_engineers4": "Engineer Company IV",
        "tech_recon": "Recon Company I",
        "tech_recon2": "Recon Company II",
        "tech_recon3": "Recon Company III",
        "tech_recon4": "Recon Company IV",
        "sp_armored_engineer_tech": "Armored Engineer Company (Special Project)",
        "sp_armored_maintenance_tech": "Armored Maintenance Company (Special Project)",
        "sp_armored_signal_tech": "Armored Signal Company (Special Project)",
        "sp_helicopter_transport_pods_tech": "Helicopter Transport Company (Special Project)",
        "sp_helicopter_artillery_observers_tech": "Helicopter Recon Company (Special Project)",
        "sp_helicopter_med_evac_tech": "Helicopter Med-Evac Company (Special Project)",
    }
    by_key = {t["key"]: t["name"] for t in TECHNOLOGIES}
    for key, expected_name in expected_names.items():
        assert by_key[key] == expected_name, key
    assert len(expected_names) == 62


# --- "year" field (added 2026-11-02) - each technology's real historical
# HOI4 unlock year, shown in the Research tab per Ollie's own request
# (e.g. "Improved Infantry Equipment I (1938)"). Sourced directly from
# each technology's own start_year field in the real
# technologies_copy/*.txt source files.

def test_every_technology_has_a_year_field_thats_none_or_a_sane_int():
    for tech in TECHNOLOGIES:
        year = tech["year"]
        assert year is None or (isinstance(year, int) and 1900 <= year <= 1946), tech["key"]


def test_only_gw_artillery_has_no_real_start_year():
    # Confirmed by direct inspection of its own source block (the root/
    # always-available base artillery tech) - every other compiled
    # technology has a real start_year in the source.
    missing = [t["key"] for t in TECHNOLOGIES if t["year"] is None]
    assert missing == ["gw_artillery"]


def test_known_years_match_the_real_game():
    by_key = {t["key"]: t["year"] for t in TECHNOLOGIES}
    expected_years = {
        "infantry_weapons": 1918,
        "infantry_weapons2": 1938,  # Ollie's own example
        "tech_mountaineers": 1936,
        "gw_artillery": None,
    }
    for key, expected_year in expected_years.items():
        assert by_key[key] == expected_year, key
