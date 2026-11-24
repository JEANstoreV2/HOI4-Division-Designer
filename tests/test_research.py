from data.technologies import TECHNOLOGIES
from logic.research import (
    ALWAYS_UNLOCKED_MODULES,
    ALWAYS_UNLOCKED_SUBUNITS,
    active_tech_unit_bonuses,
    can_unresearch,
    dependent_technologies,
    is_researchable,
    researchable_technologies,
    researched_keys_by_year,
    unlocked_module_keys,
    unlocked_subunit_keys,
)


def test_root_technology_is_always_researchable():
    assert is_researchable("infantry_weapons", researched=set())


def test_already_researched_technology_is_not_researchable_again():
    assert not is_researchable("infantry_weapons", researched={"infantry_weapons"})


def test_technology_with_unmet_prerequisite_is_not_researchable():
    assert not is_researchable("infantry_weapons1", researched=set())


def test_or_merge_either_prerequisite_is_enough():
    # main_battle_tank_chassis is unlocked_by BOTH advanced_medium_tank_chassis
    # and advanced_heavy_tank_chassis - either one alone should suffice.
    assert is_researchable("main_battle_tank_chassis", researched={"advanced_medium_tank_chassis"})
    assert is_researchable("main_battle_tank_chassis", researched={"advanced_heavy_tank_chassis"})
    assert not is_researchable("main_battle_tank_chassis", researched=set())


def test_and_requires_needs_every_dependency():
    # tech_field_hospital requires motorised_infantry in addition to its
    # unlocked_by prerequisite (tech_support).
    assert not is_researchable("tech_field_hospital", researched={"tech_support"})
    assert is_researchable(
        "tech_field_hospital", researched={"tech_support", "motorised_infantry"}
    )


def test_external_dependency_is_treated_as_always_satisfied():
    # tech_signal_company requires "radio" (an uncompiled, external
    # dependency - see data/technologies.py's EXTERNAL_DEPENDENCIES) in
    # addition to motorised_infantry.
    assert is_researchable(
        "tech_signal_company", researched={"tech_support", "motorised_infantry"}
    )


def test_mutually_exclusive_pair_blocks_the_other_option(monkeypatch):
    # advanced_special_forces/improved_special_forces were this project's
    # only REAL mutually_exclusive_with pair, until both were removed
    # 2026-11-03 (see data/technologies.py's own removal note - the whole
    # branch they belonged to turned out to be unreachable in the real
    # game for any player owning Arms Against Tyranny, which Ollie does).
    # With no real pair left anywhere in the compile, this test now
    # exercises the same generic XOR logic against synthetic data instead,
    # via a monkeypatched _TECHNOLOGIES_BY_KEY - the mechanism itself is
    # still real, general-purpose code worth covering even though nothing
    # in this app's current real data happens to use it any more.
    import logic.research as research_module

    fake_a = {
        "key": "fake_a", "unlocked_by": [], "requires": [],
        "mutually_exclusive_with": ["fake_b"], "special_project_requires": None,
    }
    fake_b = {
        "key": "fake_b", "unlocked_by": [], "requires": [],
        "mutually_exclusive_with": ["fake_a"], "special_project_requires": None,
    }
    monkeypatch.setattr(research_module, "_TECHNOLOGIES_BY_KEY", {"fake_a": fake_a, "fake_b": fake_b})

    researched = {"fake_a"}
    assert not is_researchable("fake_b", researched)
    # fake_a itself is already researched, so also no.
    assert not is_researchable("fake_a", researched)


def test_researchable_technologies_excludes_already_researched_and_locked():
    researched = {"infantry_weapons"}
    available = {t["key"] for t in researchable_technologies(researched)}
    assert "infantry_weapons1" in available
    assert "infantry_weapons" not in available
    assert "improved_infantry_weapons" not in available


def test_always_unlocked_subunits_are_selectable_with_no_research_at_all():
    unlocked = unlocked_subunit_keys(researched=set())
    assert ALWAYS_UNLOCKED_SUBUNITS <= unlocked
    # A few known-ungated examples: nation-specific focus units (see
    # data/technologies.py's header for the full list of exclusion
    # categories). armored_engineer and its Special-Project siblings used
    # to be here too - now properly gated behind Special Projects
    # (2026-10-01), see test_special_project_gated_subunits_are_not_always_unlocked.
    for key in ("camelry", "elephantry", "militia"):
        assert key in unlocked


def test_special_project_gated_subunits_are_not_always_unlocked():
    # Confirms the 2026-10-01 tightening: these 7 support companies were
    # previously in ALWAYS_UNLOCKED_SUBUNITS (no research gate at all) -
    # now that data/technologies.py compiles their real gating technology,
    # they require it like everything else.
    unlocked = unlocked_subunit_keys(researched=set())
    for key in (
        "armored_engineer", "armored_maintenance", "armored_signal",
        "helicopter_transport", "helicopter_recon", "helicopter_field_hospital",
        "motorized_military_police",
    ):
        assert key not in unlocked

    with_techs = unlocked_subunit_keys(researched={
        "sp_armored_engineer_tech", "sp_helicopter_transport_pods_tech",
    })
    assert "armored_engineer" in with_techs
    assert "helicopter_transport" in with_techs


def test_special_project_direct_subunit_unlocks_are_not_always_unlocked():
    # Confirms the 2026-10-02 tightening: these 8 subunits are unlocked
    # directly by their PROJECT's own completion (data/special_projects.py),
    # not by any technology - a real, separate layer found via Ollie's
    # in-game screenshots. Previously in ALWAYS_UNLOCKED_SUBUNITS.
    unlocked = unlocked_subunit_keys(researched=set())
    for key in (
        "light_flame_tank", "medium_flame_tank", "heavy_flame_tank", "assault_engineer",
        "land_cruiser", "super_heavy_artillery", "self_propelled_super_heavy_artillery",
        "helicopter_brigade",
    ):
        assert key not in unlocked

    with_project = unlocked_subunit_keys(
        researched=set(), completed_special_projects={"sp_land_flamethrower_tank"}
    )
    assert {"light_flame_tank", "medium_flame_tank", "heavy_flame_tank"} <= with_project
    assert "land_cruiser" not in with_project  # gated by a different project

    with_land_cruiser = unlocked_subunit_keys(
        researched=set(), completed_special_projects={"sp_land_land_cruiser"}
    )
    assert "land_cruiser" in with_land_cruiser


def test_researched_technology_unlocks_its_subunits():
    unlocked = unlocked_subunit_keys(researched={"infantry_weapons"})
    assert "infantry" in unlocked


def test_ungated_technology_grants_nothing_extra_beyond_the_always_unlocked_set():
    # A tech with no unlocks_subunits at all (e.g. a pure stat-boost tech)
    # shouldn't change the unlocked set beyond ALWAYS_UNLOCKED_SUBUNITS.
    unlocked_none = unlocked_subunit_keys(researched=set())
    unlocked_with_stat_tech = unlocked_subunit_keys(researched={"infantry_weapons2"})
    assert unlocked_with_stat_tech == unlocked_none


# --- Un-researching (undoing a misclick) ---

def test_a_technology_with_nothing_built_on_it_can_be_unresearched():
    researched = {"infantry_weapons"}
    assert dependent_technologies("infantry_weapons", researched) == []
    assert can_unresearch("infantry_weapons", researched)


def test_a_technology_something_depends_on_cannot_be_unresearched():
    researched = {"infantry_weapons", "infantry_weapons1"}
    assert dependent_technologies("infantry_weapons", researched) == ["infantry_weapons1"]
    assert not can_unresearch("infantry_weapons", researched)
    # The dependent itself has nothing built on IT, so it's still fine to undo.
    assert can_unresearch("infantry_weapons1", researched)


def test_or_merge_prerequisite_stays_satisfied_by_the_other_branch():
    # main_battle_tank_chassis is unlocked_by EITHER advanced_medium_tank_chassis
    # OR advanced_heavy_tank_chassis - removing one while the other remains
    # researched shouldn't count as breaking it. Uses the full valid chain
    # for both branches (not just the two end nodes) so this doesn't trip
    # over an already-invalid research state.
    researched = {
        "gwtank_chassis",
        "basic_medium_tank_chassis", "improved_medium_tank_chassis", "advanced_medium_tank_chassis",
        "basic_heavy_tank_chassis", "improved_heavy_tank_chassis", "advanced_heavy_tank_chassis",
        "main_battle_tank_chassis",
    }
    assert dependent_technologies("advanced_medium_tank_chassis", researched) == []
    assert can_unresearch("advanced_medium_tank_chassis", researched)


def test_removing_the_only_satisfied_or_branch_is_blocked():
    researched = {"advanced_medium_tank_chassis", "main_battle_tank_chassis"}
    assert dependent_technologies("advanced_medium_tank_chassis", researched) == ["main_battle_tank_chassis"]
    assert not can_unresearch("advanced_medium_tank_chassis", researched)


def test_removing_a_cross_branch_requires_dependency_is_blocked():
    researched = {"tech_support", "motorised_infantry", "tech_field_hospital"}
    assert not can_unresearch("motorised_infantry", researched)
    # tech_support itself has nothing depending on ITS specific presence
    # via requires (tech_field_hospital's unlocked_by is tech_support, so
    # removing tech_support WOULD break it too - only motorised_infantry is
    # asserted here to keep this test focused on the `requires` rule).


def test_a_technology_not_researched_cannot_be_unresearched():
    assert not can_unresearch("infantry_weapons", researched=set())


# --- Tank Designer module unlocks ---

def test_always_unlocked_modules_are_selectable_with_no_research_at_all():
    unlocked = unlocked_module_keys(researched=set())
    assert ALWAYS_UNLOCKED_MODULES <= unlocked
    # A basic structural module (needs gwtank_chassis) is NOT in this set.
    assert "tank_gasoline_engine" not in unlocked
    # A couple of known-ungated examples: never gated by any real tech
    # (stabilizer) or gated only by a tech living in an uncompiled file
    # (tank_radio_1, in electronic_mechanical_engineering.txt) - see
    # logic/research.py's header. flamethrower/advanced_flamethrower used to
    # be here too - now properly gated behind Special Projects (2026-10-01/
    # 02), see test_special_project_gated_modules_are_not_always_unlocked.
    for key in ("stabilizer", "tank_radio_1"):
        assert key in unlocked


def test_special_project_gated_modules_are_not_always_unlocked():
    unlocked = unlocked_module_keys(researched=set())
    for key in (
        "advanced_flamethrower", "lc_high_impact_obliterator_cannon", "lc_command_center",
        "flamethrower", "lc_flamethrower_turret", "lc_heavy_naval_guns", "lc_helipad",
    ):
        assert key not in unlocked

    with_tech = unlocked_module_keys(researched={"sp_armored_advanced_flamethrower_tech"})
    assert "advanced_flamethrower" in with_tech

    with_project = unlocked_module_keys(researched=set(), completed_special_projects={"sp_land_flamethrower_tank"})
    assert "flamethrower" in with_project
    assert "lc_flamethrower_turret" in with_project
    assert "lc_heavy_naval_guns" not in with_project  # gated by a different project (Land Cruiser)

    with_land_cruiser = unlocked_module_keys(researched=set(), completed_special_projects={"sp_land_land_cruiser"})
    assert "lc_heavy_naval_guns" in with_land_cruiser


def test_researched_technology_unlocks_its_modules():
    unlocked = unlocked_module_keys(researched={"gwtank_chassis"})
    assert "tank_gasoline_engine" in unlocked
    assert "tank_light_one_man_tank_turret" in unlocked
    # A module gated by a DIFFERENT technology stays locked.
    assert "tank_welded_armor" not in unlocked


def test_a_module_gated_by_multiple_technologies_unlocks_via_either():
    # tank_medium_cannon is unlocked by BOTH artillery1 and antitank1.
    assert "tank_medium_cannon" in unlocked_module_keys(researched={"artillery1"})
    assert "tank_medium_cannon" in unlocked_module_keys(researched={"antitank1"})
    assert "tank_medium_cannon" not in unlocked_module_keys(researched=set())


# --- active_tech_unit_bonuses (added 2026-09-29) ---

def test_no_research_gives_no_tech_bonuses():
    assert active_tech_unit_bonuses(researched=set()) == []


def test_researching_a_technology_surfaces_its_exact_bonus_dict():
    bonuses = active_tech_unit_bonuses(researched={"infantry_at"})
    assert ("category_all_infantry", {"hard_attack": 0.25, "ap_attack": 1}) in bonuses
    assert ("fire_support", {"hard_attack": 0.15, "ap_attack": 0.5}) in bonuses
    assert len(bonuses) == 4  # infantry_at has exactly 4 target keys


def test_a_technology_with_no_bonus_contributes_nothing():
    assert active_tech_unit_bonuses(researched={"infantry_weapons"}) == []


def test_two_technologies_targeting_the_same_category_both_appear():
    # infantry_at and infantry_at2 both target category_all_infantry -
    # aggregation across the two entries happens downstream
    # (logic/stats.py), same as doctrine bonuses; this function just
    # returns every pair unmerged.
    bonuses = active_tech_unit_bonuses(researched={"infantry_at", "infantry_at2"})
    matches = [pair for pair in bonuses if pair[0] == "category_all_infantry"]
    assert len(matches) == 2
    assert all(stat_dict == {"hard_attack": 0.25, "ap_attack": 1} for _, stat_dict in matches)


# --- Special Projects gating (added 2026-10-01) ---

def test_special_project_gated_technology_is_unresearchable_without_it():
    assert not is_researchable("sp_armored_engineer_tech", researched=set())
    assert not is_researchable(
        "sp_armored_engineer_tech", researched=set(), completed_special_projects=set()
    )


def test_special_project_gated_technology_becomes_researchable_once_completed():
    assert is_researchable(
        "sp_armored_engineer_tech", researched=set(),
        completed_special_projects={"sp_land_military_engineering_vehicles"},
    )


def test_wrong_special_project_does_not_unlock_a_different_one():
    assert not is_researchable(
        "sp_armored_engineer_tech", researched=set(),
        completed_special_projects={"sp_land_land_cruiser"},
    )


def test_ordinary_technology_researchability_is_unaffected_by_the_new_parameter():
    # infantry_weapons has special_project_requires: None - omitting the
    # parameter entirely must be byte-identical to passing an empty set.
    assert is_researchable("infantry_weapons", researched=set()) == is_researchable(
        "infantry_weapons", researched=set(), completed_special_projects=set()
    )


def test_researchable_technologies_respects_completed_special_projects():
    available_without = {t["key"] for t in researchable_technologies(researched=set())}
    assert "sp_armored_engineer_tech" not in available_without

    available_with = {
        t["key"] for t in researchable_technologies(
            researched=set(), completed_special_projects={"sp_land_military_engineering_vehicles"}
        )
    }
    assert "sp_armored_engineer_tech" in available_with


def test_sp_artillery_rocket_assisted_projectiles_still_gated_by_its_special_project():
    # Its extra "experimental_rockets" requires entry is an
    # EXTERNAL_DEPENDENCIES key (same treatment as tech_signal_company's
    # "radio") - always treated as satisfied since it isn't tracked, so
    # special_project_requires is the only gate that actually blocks this
    # in practice today.
    key = "sp_artillery_rocket_assisted_projectiles_tech"
    assert not is_researchable(key, researched=set(), completed_special_projects=set())
    assert is_researchable(
        key, researched=set(), completed_special_projects={"sp_land_super_heavy_howitzer"}
    )


# --- researched_keys_by_year (added 2026-11-02, AI Design Comparison's
# Research Year constraint)

def test_researched_keys_by_year_always_includes_the_one_yearless_technology():
    assert "gw_artillery" in researched_keys_by_year(1914)
    assert "gw_artillery" in researched_keys_by_year(1946)


def test_researched_keys_by_year_excludes_technology_strictly_after_the_cutoff():
    result = researched_keys_by_year(1940)
    for tech in TECHNOLOGIES:
        if tech["year"] is not None and tech["year"] > 1940:
            assert tech["key"] not in result
        elif tech["year"] is not None and tech["year"] <= 1940:
            assert tech["key"] in result


def test_researched_keys_by_year_is_monotonic_with_a_later_cutoff():
    early = researched_keys_by_year(1920)
    late = researched_keys_by_year(1945)
    assert early <= late
