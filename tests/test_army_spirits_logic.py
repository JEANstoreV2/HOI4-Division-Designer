import pytest

from logic.army_spirits import (
    active_army_speed_factor,
    active_army_strength_factor,
    active_breakthrough_factor,
    active_equipment_bonuses,
    active_spirit_in_category,
    active_supply_consumption_factor,
    is_army_spirit_selectable,
)

# Fixtures below use the 9 entries that survived the 2026-11-02 rescope
# (see data/army_spirits.py's own header) - none of them has an empty
# `available` list any more (every surviving entry bears on a tracked
# stat via a real doctrine/subdoctrine gate), so there's no real-data case
# left to exercise is_army_spirit_selectable's "always selectable" branch
# the way the pre-rescope suite did with bold_attack_spirit.


def test_spirit_gated_by_a_grand_doctrine_is_blocked_without_it():
    assert not is_army_spirit_selectable(
        "maneuver_warfare_spirit", active_spirits=set(),
        active_grand_doctrines=set(), track_subdoctrines={},
    )


def test_spirit_gated_by_a_grand_doctrine_is_selectable_once_active():
    assert is_army_spirit_selectable(
        "maneuver_warfare_spirit", active_spirits=set(),
        active_grand_doctrines={"new_mobile_warfare"}, track_subdoctrines={},
    )


def test_spirit_gated_by_a_subdoctrine_is_selectable_once_assigned_to_a_track():
    # direct_fire_support_army_spirit's own available list includes
    # "self_propelled_support", a real Subdoctrine key (not a Grand
    # Doctrine) - has_doctrine matches either in real HOI4, confirmed
    # against data/doctrines.py.
    assert is_army_spirit_selectable(
        "direct_fire_support_army_spirit", active_spirits=set(),
        active_grand_doctrines=set(), track_subdoctrines={"combat_support": "self_propelled_support"},
    )


def test_spirit_gated_by_an_or_list_needs_only_one_match():
    # all_arms_at_defense_army_spirit's available is
    # [superior_firepower, tank_destroyer_force] - only one needs to be
    # active, and here only the Subdoctrine (not the Grand Doctrine) is.
    assert is_army_spirit_selectable(
        "all_arms_at_defense_army_spirit", active_spirits=set(),
        active_grand_doctrines=set(), track_subdoctrines={"armor": "tank_destroyer_force"},
    )


def test_already_active_spirit_is_still_reported_selectable():
    # Mirrors is_grand_doctrine_selectable's own "already active" case being
    # a caller-handled no-op, not a reason to say no - selectArmySpirit's
    # own category-replace logic handles re-picking the same key.
    assert is_army_spirit_selectable(
        "maneuver_warfare_spirit", active_spirits={"maneuver_warfare_spirit"},
        active_grand_doctrines={"new_mobile_warfare"}, track_subdoctrines={},
    )


def test_active_spirit_in_category_finds_the_right_one():
    active = {"subsidized_contracts_army_spirit", "maneuver_warfare_spirit"}
    assert active_spirit_in_category("army_spirit", active) == "subsidized_contracts_army_spirit"
    assert active_spirit_in_category("division_command_spirit", active) == "maneuver_warfare_spirit"


def test_active_spirit_in_category_returns_none_when_nothing_is_active_there():
    assert active_spirit_in_category("army_spirit", {"maneuver_warfare_spirit"}) is None


def test_active_army_strength_factor_sums_operational_reserves():
    assert active_army_strength_factor(["operational_reserve_spirit"]) == pytest.approx(0.1)


def test_active_army_strength_factor_is_zero_with_no_matching_spirit():
    assert active_army_strength_factor([]) == 0
    assert active_army_strength_factor(["subsidized_contracts_army_spirit"]) == 0


def test_active_army_strength_factor_tolerates_a_key_removed_by_the_rescope():
    # A real case (found 2026-11-02): a session persisted before the
    # same-day rescope from 40 to 9 entries can still reference a removed
    # key (bold_attack_spirit, an academy_spirit entry cut entirely) -
    # this must be skipped, not raise KeyError, since this function runs
    # on every /api/stats and /api/design-search request.
    assert active_army_strength_factor(["bold_attack_spirit"]) == 0
    assert active_army_strength_factor(["bold_attack_spirit", "operational_reserve_spirit"]) == pytest.approx(0.1)


# --- The remaining 7 of Officer Corps' 8 compiled-but-unapplied formula
# items, confirmed via real in-game tooltips 2026-11-03 (Ollie's own
# screenshots) and applied the same day. All 4 country-wide fields and all
# 4 equipment_bonus entries turned out to be percentages, matching
# Operational Reserves' own precedent exactly - no flat-vs-percentage
# surprises this time.

def test_active_breakthrough_factor_sums_smoke_and_fire():
    # Real tooltip: "Breakthrough: +6.00%".
    assert active_breakthrough_factor(["smoke_and_fire_spirit"]) == pytest.approx(0.06)
    assert active_breakthrough_factor([]) == 0


def test_active_supply_consumption_factor_sums_logistical_focus():
    # Real tooltip: "Supply Consumption: -10.0%".
    assert active_supply_consumption_factor(["logistical_focus_spirit"]) == pytest.approx(-0.10)
    assert active_supply_consumption_factor([]) == 0


def test_active_army_speed_factor_sums_either_mutually_exclusive_spirit():
    # Real tooltips: both Flexible Organization and Maneuver Warfare read
    # "Divisions speed: +5.00%" for the identically-named field - they're
    # the same category (division_command_spirit), so at most one is ever
    # active in practice, but the function itself doesn't assume that.
    assert active_army_speed_factor(["flexible_organization_spirit"]) == pytest.approx(0.05)
    assert active_army_speed_factor(["maneuver_warfare_spirit"]) == pytest.approx(0.05)
    assert active_army_speed_factor([]) == 0


def test_active_equipment_bonuses_flattens_every_active_spirits_own_entries():
    pairs = active_equipment_bonuses(["all_arms_at_defense_army_spirit"])
    assert pairs == [("infantry_equipment", {"hard_attack": 0.25})]


def test_active_equipment_bonuses_combines_several_active_spirits():
    pairs = active_equipment_bonuses(["all_arms_at_defense_army_spirit", "subsidized_contracts_army_spirit"])
    targets = {key for key, _ in pairs}
    assert "infantry_equipment" in targets
    assert "armored_car_equipment" in targets


def test_active_equipment_bonuses_empty_with_no_matching_spirit():
    assert active_equipment_bonuses([]) == []
    assert active_equipment_bonuses(["smoke_and_fire_spirit"]) == []


def test_active_equipment_bonuses_tolerates_a_stale_key():
    assert active_equipment_bonuses(["bold_attack_spirit"]) == []
