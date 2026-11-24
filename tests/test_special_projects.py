from data.battalions import BATTALIONS
from data.equipment import EQUIPMENT
from data.regimental_support import REGIMENTAL_SUPPORT
from data.special_projects import SPECIAL_PROJECTS
from data.support_companies import SUPPORT_COMPANIES
from data.tank_modules import TANK_MODULES
from data.technologies import TECHNOLOGIES
from data.unit_categories import UNIT_CATEGORIES

SUBUNIT_KEYS = (
    {b["key"] for b in BATTALIONS}
    | {c["key"] for c in SUPPORT_COMPANIES}
    | {r["key"] for r in REGIMENTAL_SUPPORT}
)
MODULE_KEYS = {m["key"] for m in TANK_MODULES}
ALL_CATEGORY_KEYS = {category for categories in UNIT_CATEGORIES.values() for category in categories}


def test_expected_entry_count():
    # A regression tripwire: if this changes, it should be a deliberate
    # addition/removal, not an accidental one.
    assert len(SPECIAL_PROJECTS) == 8


def test_no_duplicate_keys():
    keys = [p["key"] for p in SPECIAL_PROJECTS]
    assert len(keys) == len(set(keys))


def test_every_project_has_a_key():
    for p in SPECIAL_PROJECTS:
        assert p["key"]


def test_names_match_the_real_game_localisation_file():
    # Pulled 2026-10-02 directly from the actual HOI4 install's own
    # localisation/english/special_projects_l_english.yml on Ollie's
    # machine - not a guess (data/special_projects.py's header has the full
    # story on why that file, not a screenshot, is the authoritative
    # source). Generic (non-country-specific) names only - this app doesn't
    # model country selection.
    by_key = {p["key"]: p["name"] for p in SPECIAL_PROJECTS}
    assert by_key == {
        "sp_land_land_cruiser": "Land Cruiser",
        "sp_land_military_engineering_vehicles": "Military Engineering Vehicles",
        "sp_air_helicopter": "Helicopter",
        "sp_naval_proximity_fuze": "Proximity Fuze",
        "sp_land_flamethrower_tank": "Flamethrower Tank",
        "sp_land_large_caliber_kinetic_energy_sabot": "Large Caliber Kinetic Energy Sabot",
        "sp_land_self_propelled_super_heavy_howitzer": "Self-Propelled Super-Heavy Howitzer",
        "sp_land_super_heavy_howitzer": "Super-Heavy Howitzer",
    }


def test_every_project_has_the_three_unlock_fields():
    for p in SPECIAL_PROJECTS:
        assert "unlocks_subunits" in p, p["key"]
        assert "unlocks_equipment" in p, p["key"]
        assert "unlocks_equipment_modules" in p, p["key"]


def test_requires_references_real_projects_and_never_self():
    project_keys = {p["key"] for p in SPECIAL_PROJECTS}
    for p in SPECIAL_PROJECTS:
        for parent in p["requires"]:
            assert parent in project_keys, (p["key"], parent)
            assert parent != p["key"], p["key"]


def test_only_self_propelled_super_heavy_howitzer_has_requires():
    by_key = {p["key"]: p["requires"] for p in SPECIAL_PROJECTS}
    assert by_key["sp_land_self_propelled_super_heavy_howitzer"] == [
        "sp_land_military_engineering_vehicles", "sp_land_super_heavy_howitzer",
    ]
    for key, requires in by_key.items():
        if key != "sp_land_self_propelled_super_heavy_howitzer":
            assert requires == [], key


def test_every_special_project_requires_value_in_technologies_matches_a_real_project():
    project_keys = {p["key"] for p in SPECIAL_PROJECTS}
    referenced = {t["special_project_requires"] for t in TECHNOLOGIES if t["special_project_requires"] is not None}
    assert referenced <= project_keys


def test_every_special_project_gates_at_least_one_technology():
    # Confirms none of the 8 keys are typos/orphans - every one was found
    # by reading an actual is_special_project_completed condition.
    project_keys = {p["key"] for p in SPECIAL_PROJECTS}
    referenced = {t["special_project_requires"] for t in TECHNOLOGIES if t["special_project_requires"] is not None}
    assert referenced == project_keys


# --- Direct project-level unlocks (added 2026-10-02) ---
# A real, separate unlock layer found via Ollie's own in-game screenshots of
# the "M3 Satan" (sp_land_flamethrower_tank) project showing a direct
# "Sub units(s): Light Flame Tank Company" grant with no technology
# involved - confirmed by reading all 8 projects' own project_output
# blocks directly (Copies/special_projects_copy/projects/).

def test_unlocks_subunits_reference_real_items():
    for p in SPECIAL_PROJECTS:
        for key in p["unlocks_subunits"]:
            assert key in SUBUNIT_KEYS, (p["key"], key)


def test_unlocks_equipment_references_real_equipment():
    for p in SPECIAL_PROJECTS:
        for key in p["unlocks_equipment"]:
            assert key in EQUIPMENT, (p["key"], key)


def test_unlocks_equipment_modules_reference_real_modules():
    for p in SPECIAL_PROJECTS:
        for key in p["unlocks_equipment_modules"]:
            assert key in MODULE_KEYS, (p["key"], key)


def test_sp_land_flamethrower_tank_unlocks_match_the_screenshot_exactly():
    # Template Examples/ equivalent for Special Projects - Ollie's own
    # "M3 Satan" screenshots (2026-10-02) showed "Sub units(s): Light Flame
    # Tank Company" directly, confirmed against the raw source to also
    # include medium/heavy and the base "flamethrower" module (distinct
    # from the technology-gated "advanced_flamethrower").
    by_key = {p["key"]: p for p in SPECIAL_PROJECTS}
    project = by_key["sp_land_flamethrower_tank"]
    assert set(project["unlocks_subunits"]) == {"light_flame_tank", "medium_flame_tank", "heavy_flame_tank"}
    assert "flamethrower" in project["unlocks_equipment_modules"]


def test_sp_land_land_cruiser_unlocks_the_land_cruiser_subunit_directly():
    # Confirms the land_cruiser subunit is gated by the PROJECT itself, not
    # by any of the 5 sp_armored_lc_* technologies it also gates (none of
    # those list land_cruiser in their own unlocks_subunits).
    by_key = {p["key"]: p for p in SPECIAL_PROJECTS}
    assert by_key["sp_land_land_cruiser"]["unlocks_subunits"] == ["land_cruiser"]
    by_tech_key = {t["key"]: t for t in TECHNOLOGIES}
    for tech_key in (
        "sp_armored_lc_naval_engine_conversion_tech", "sp_armored_lc_transmission_improvements_tech",
        "sp_armored_lc_specialized_field_manuals_tech", "sp_armored_lc_weapon_fire_control_tech",
        "sp_armored_lc_high_impact_obliterator_cannon_tech",
    ):
        assert "land_cruiser" not in by_tech_key[tech_key]["unlocks_subunits"]


# --- unit_bonuses (added 2026-10-07 - see data/special_projects.py's header) ---

def test_every_project_has_a_unit_bonuses_field():
    for p in SPECIAL_PROJECTS:
        assert "unit_bonuses" in p, p["key"]


def test_only_large_caliber_kinetic_energy_sabot_has_unit_bonuses():
    by_key = {p["key"]: p for p in SPECIAL_PROJECTS}
    for p in SPECIAL_PROJECTS:
        if p["key"] == "sp_land_large_caliber_kinetic_energy_sabot":
            assert by_key[p["key"]]["unit_bonuses"]
        else:
            assert by_key[p["key"]]["unit_bonuses"] == {}


def test_unit_bonuses_target_keys_reference_real_categories_or_subunits():
    for p in SPECIAL_PROJECTS:
        for target_key in p["unit_bonuses"]:
            assert target_key in ALL_CATEGORY_KEYS or target_key in SUBUNIT_KEYS, (p["key"], target_key)


def test_sp_land_large_caliber_kinetic_energy_sabot_unit_bonuses_match_the_screenshot_exactly():
    # Special_Projects_Screenshots/large_caliber_sabot_1.PNG/_2.PNG
    # (2026-10-07): the project's own Project Output screen shows Piercing
    # +15%/Fort Attack +15% on Artillery/Support Artillery/Motorized
    # Artillery/Self-Propelled Artillery/Super-Heavy Artillery/Self-Propelled
    # Super-Heavy Artillery, and Piercing +10% on Field Guns - traced to a
    # hidden, unresearchable technology (technologies_copy/artillery.txt's
    # sp_land_large_caliber_kinetic_energy_sabot_gd_tech) the project
    # silently auto-grants on completion, never compiled before since
    # `allow = { always = no }` technologies are normally correctly excluded.
    by_key = {p["key"]: p for p in SPECIAL_PROJECTS}
    bonuses = by_key["sp_land_large_caliber_kinetic_energy_sabot"]["unit_bonuses"]
    fort_attack = {"fort": {"attack": 0.15}}
    assert bonuses["artillery_brigade"] == {"ap_attack": 0.15, **fort_attack}
    assert bonuses["artillery"] == {"ap_attack": 0.15, **fort_attack}
    assert bonuses["mot_artillery_brigade"] == {"ap_attack": 0.15, **fort_attack}
    assert bonuses["category_self_propelled_artillery"] == {"ap_attack": 0.15, **fort_attack}
    assert bonuses["super_heavy_artillery"] == {"ap_attack": 0.15, **fort_attack}
    assert bonuses["self_propelled_super_heavy_artillery"] == {"ap_attack": 0.15, **fort_attack}
    assert bonuses["field_guns"] == {"ap_attack": 0.1}
