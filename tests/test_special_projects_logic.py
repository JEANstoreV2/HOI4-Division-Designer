from logic.special_projects import (
    active_special_project_unit_bonuses,
    can_uncomplete_special_project,
    completable_special_projects,
    dependent_special_projects,
    is_special_project_completable,
)

_PARENT_1 = "sp_land_military_engineering_vehicles"
_PARENT_2 = "sp_land_super_heavy_howitzer"
_CHILD = "sp_land_self_propelled_super_heavy_howitzer"


def test_a_project_with_no_requires_is_always_completable():
    assert is_special_project_completable("sp_naval_proximity_fuze", completed_special_projects=set())


def test_an_already_completed_project_is_not_completable_again():
    assert not is_special_project_completable(
        "sp_naval_proximity_fuze", completed_special_projects={"sp_naval_proximity_fuze"}
    )


def test_the_one_project_with_parents_is_blocked_until_both_are_done():
    assert not is_special_project_completable(_CHILD, completed_special_projects=set())
    assert not is_special_project_completable(_CHILD, completed_special_projects={_PARENT_1})
    assert not is_special_project_completable(_CHILD, completed_special_projects={_PARENT_2})
    assert is_special_project_completable(_CHILD, completed_special_projects={_PARENT_1, _PARENT_2})


def test_completable_special_projects_excludes_the_blocked_child():
    available = {p["key"] for p in completable_special_projects(completed_special_projects=set())}
    assert _CHILD not in available
    assert _PARENT_1 in available
    assert _PARENT_2 in available


def test_dependent_special_projects_reflects_the_one_real_dependency():
    completed = {_PARENT_1, _PARENT_2, _CHILD}
    assert dependent_special_projects(_PARENT_1, completed) == [_CHILD]
    assert dependent_special_projects(_PARENT_2, completed) == [_CHILD]
    assert dependent_special_projects(_CHILD, completed) == []


def test_can_uncomplete_blocks_a_parent_still_needed_by_its_child():
    completed = {_PARENT_1, _PARENT_2, _CHILD}
    assert not can_uncomplete_special_project(_PARENT_1, completed, researched=set())
    assert can_uncomplete_special_project(_CHILD, completed, researched=set())


def test_can_uncomplete_blocks_a_project_an_already_researched_technology_needs():
    completed = {"sp_land_flamethrower_tank"}
    assert can_uncomplete_special_project("sp_land_flamethrower_tank", completed, researched=set())
    assert not can_uncomplete_special_project(
        "sp_land_flamethrower_tank", completed, researched={"sp_armored_advanced_flamethrower_tech"}
    )


def test_cannot_uncomplete_a_project_that_was_never_completed():
    assert not can_uncomplete_special_project("sp_naval_proximity_fuze", completed_special_projects=set(), researched=set())


# --- active_special_project_unit_bonuses (added 2026-10-07) ---

def test_no_completed_projects_means_no_bonuses():
    assert active_special_project_unit_bonuses(set()) == []


def test_a_project_with_no_unit_bonuses_contributes_nothing():
    assert active_special_project_unit_bonuses({"sp_land_flamethrower_tank"}) == []


def test_large_caliber_kinetic_energy_sabot_contributes_its_unit_bonuses():
    pairs = active_special_project_unit_bonuses({"sp_land_large_caliber_kinetic_energy_sabot"})
    targets = {target_key for target_key, _ in pairs}
    assert "artillery_brigade" in targets
    assert "field_guns" in targets
    field_guns_bonus = next(stat_dict for target_key, stat_dict in pairs if target_key == "field_guns")
    assert field_guns_bonus == {"ap_attack": 0.1}
