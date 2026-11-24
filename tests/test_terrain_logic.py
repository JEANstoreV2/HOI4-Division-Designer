import pytest

from data.battalion_stats import BATTALION_STATS
from logic.terrain import apply_terrain_modifier, division_terrain_percentage, terrain_percentage


# --- terrain_percentage ---
# Every value here is confirmed directly against data/terrain.py's own
# GENERIC_TERRAIN_MODIFIERS/UNIT_TERRAIN_MODIFIERS, which are themselves
# confirmed against real screenshots - see CLAUDE.md's Terrain section.

def test_mountaineers_attacking_into_mountain_matches_the_real_screenshot():
    # generic mountain attack -0.5 + mountaineers' own mountain attack 0.35
    # = -0.15, matching the real in-game tooltip ("Terrain: -15.00%")
    # exactly - this is the reconciliation that confirmed the whole
    # two-layer formula in the first place.
    assert terrain_percentage("mountaineers", "mountain", is_attacking=True) == pytest.approx(-0.15)


def test_mountaineers_defending_within_mountain_matches_the_real_screenshot():
    # No generic defence layer exists at all (confirmed - every terrain
    # type in terrain_copy/00_terrain.txt only ever sets `attack`) + own
    # mountain defence 0.1 = 0.1, matching the real in-game tooltip
    # ("Terrain: +10.00%") exactly.
    assert terrain_percentage("mountaineers", "mountain", is_attacking=False) == pytest.approx(0.1)


def test_plain_infantry_has_no_terrain_effect_anywhere():
    # infantry has no UNIT_TERRAIN_MODIFIERS entry at all, but the generic
    # layer still applies to every unit regardless of type - so a plain
    # Infantry attacking into Mountain still takes the generic -50%, even
    # though it has no per-unit terrain bonus of its own to offset it.
    assert terrain_percentage("infantry", "mountain", is_attacking=True) == pytest.approx(-0.5)
    assert terrain_percentage("infantry", "mountain", is_attacking=False) == pytest.approx(0)


def test_generic_layer_never_applies_when_defending():
    # Confirmed no terrain type in terrain_copy/00_terrain.txt sets a
    # generic `defence` value - heavy_armor's own mountain block has no
    # "defence" key either, so defending in mountain is a real, confirmed 0.
    assert terrain_percentage("heavy_armor", "mountain", is_attacking=False) == pytest.approx(0)


def test_terrain_with_no_generic_layer_still_uses_the_per_unit_value():
    # fort has no generic layer at all (confirmed absent from
    # terrain_copy/00_terrain.txt's categories block), but heavy_armor's
    # own fort attack bonus (0.1) still applies.
    assert terrain_percentage("heavy_armor", "fort", is_attacking=True) == pytest.approx(0.1)


def test_terrain_and_item_combination_with_no_data_at_all_is_zero():
    assert terrain_percentage("infantry", "fort", is_attacking=True) == pytest.approx(0)


# --- apply_terrain_modifier ---

def test_apply_terrain_modifier_is_a_no_op_when_percentage_is_zero():
    stats = {"soft_attack": 10, "hard_attack": 5, "breakthrough": 3, "defense": 20}
    result = apply_terrain_modifier(stats, "infantry", "fort", is_attacking=True)
    assert result is stats


def test_apply_terrain_modifier_scales_only_the_attack_side_fields():
    stats = {"soft_attack": 10, "hard_attack": 5, "breakthrough": 3, "defense": 20}
    result = apply_terrain_modifier(stats, "mountaineers", "mountain", is_attacking=True)
    assert result["soft_attack"] == pytest.approx(10 * 0.85)
    assert result["hard_attack"] == pytest.approx(5 * 0.85)
    assert result["breakthrough"] == pytest.approx(3 * 0.85)
    # defense is a defence-side-only field - untouched while attacking.
    assert result["defense"] == 20


def test_apply_terrain_modifier_scales_only_the_defence_side_fields():
    stats = {"soft_attack": 10, "hard_attack": 5, "breakthrough": 3, "defense": 20}
    result = apply_terrain_modifier(stats, "mountaineers", "mountain", is_attacking=False)
    assert result["soft_attack"] == pytest.approx(10 * 1.1)
    assert result["hard_attack"] == pytest.approx(5 * 1.1)
    assert result["defense"] == pytest.approx(20 * 1.1)
    # breakthrough is an attack-side-only field - untouched while defending.
    assert result["breakthrough"] == 3


def test_apply_terrain_modifier_does_not_mutate_the_original_stats():
    stats = {"soft_attack": 10, "hard_attack": 5, "breakthrough": 3, "defense": 20}
    apply_terrain_modifier(stats, "mountaineers", "mountain", is_attacking=True)
    assert stats["soft_attack"] == 10


# --- division_terrain_percentage ---
# A single representative number for a division mixing several item types -
# see the function's own docstring for why this is an average, not the
# exact per-item value apply_terrain_modifier/calculate_item_stats use.

def test_division_terrain_percentage_of_a_uniform_division_matches_the_single_item_value():
    # Averaging 5 identical values returns that same value.
    expected = terrain_percentage("mountaineers", "mountain", is_attacking=True)
    assert division_terrain_percentage(
        ["mountaineers"] * 5, "mountain", is_attacking=True
    ) == pytest.approx(expected)


def test_division_terrain_percentage_of_a_mixed_division_is_the_average():
    mountaineers_pct = terrain_percentage("mountaineers", "mountain", is_attacking=True)
    infantry_pct = terrain_percentage("infantry", "mountain", is_attacking=True)
    result = division_terrain_percentage(
        ["mountaineers", "infantry"], "mountain", is_attacking=True
    )
    assert result == pytest.approx((mountaineers_pct + infantry_pct) / 2)


def test_division_terrain_percentage_of_an_empty_division_is_zero():
    assert division_terrain_percentage([], "mountain", is_attacking=True) == 0


# --- doctrine_bonuses (added 2026-10-07 - Doctrine's own terrain-nested
# unit_bonuses, e.g. marines_2's real Pioneer Support/Amphibious bonus,
# were compiled but never applied anywhere until Ollie reported this gap
# directly: claimed "Marines: Amphibious Expeditionary", picked Pioneer
# Support, selected Amphibious Assault, saw no bonus at all. These tests
# use a synthetic (target_key, stat_dict) pair list - the same raw shape
# logic/doctrines.py's active_unit_bonuses returns - to test the mechanism
# in isolation; tests/test_stats.py covers the real end-to-end wiring
# through the actual marines_2 data.)

def test_doctrine_terrain_bonus_contributes_to_the_matching_side_only():
    bonuses = [("pioneer_support", {"amphibious": {"attack": 0.15, "defence": 0.15}})]
    assert terrain_percentage(
        "pioneer_support", "amphibious", is_attacking=True, doctrine_bonuses=bonuses
    ) == pytest.approx(0.15)
    assert terrain_percentage(
        "pioneer_support", "amphibious", is_attacking=False, doctrine_bonuses=bonuses
    ) == pytest.approx(0.15)


def test_doctrine_terrain_bonus_only_applies_to_its_own_terrain_key():
    # "desert" has no generic layer (not one of the 6 terrain types that
    # do) and no per-unit entry for pioneer_support (data/terrain.py only
    # gives it marsh/fort/river) - a genuine, confirmed zero to isolate
    # against, unlike "marsh" which pioneer_support has real own data for.
    bonuses = [("pioneer_support", {"amphibious": {"attack": 0.15}})]
    assert terrain_percentage(
        "pioneer_support", "desert", is_attacking=True, doctrine_bonuses=bonuses
    ) == pytest.approx(0.0)


def test_doctrine_terrain_bonus_only_applies_to_its_own_item_or_category():
    bonuses = [("pioneer_support", {"amphibious": {"attack": 0.15}})]
    assert terrain_percentage(
        "jungle_pioneers_support", "amphibious", is_attacking=True, doctrine_bonuses=bonuses
    ) == pytest.approx(0.0)


def test_doctrine_terrain_bonus_matches_a_category_target():
    bonuses = [("category_all_infantry", {"amphibious": {"attack": 0.1}})]
    assert terrain_percentage(
        "infantry", "amphibious", is_attacking=True, doctrine_bonuses=bonuses
    ) == pytest.approx(0.1)


def test_doctrine_terrain_bonus_stacks_additively_with_the_per_unit_layer():
    # mountaineers' own mountain attack is 0.35 (see the screenshot test
    # above) - a doctrine bonus on top should sum, not replace.
    bonuses = [("mountaineers", {"mountain": {"attack": 0.1}})]
    without_doctrine = terrain_percentage("mountaineers", "mountain", is_attacking=True)
    with_doctrine = terrain_percentage(
        "mountaineers", "mountain", is_attacking=True, doctrine_bonuses=bonuses
    )
    assert with_doctrine == pytest.approx(without_doctrine + 0.1)


def test_doctrine_terrain_bonus_movement_field_is_never_applied():
    # Compiled but unused, same as every per-unit UNIT_TERRAIN_MODIFIERS
    # movement field already is - only attack/defence are ever read.
    bonuses = [("pioneer_support", {"amphibious": {"movement": 0.15}})]
    assert terrain_percentage(
        "pioneer_support", "amphibious", is_attacking=True, doctrine_bonuses=bonuses
    ) == pytest.approx(0.0)


def test_omitting_doctrine_bonuses_matches_passing_none_explicitly():
    assert terrain_percentage("pioneer_support", "amphibious", is_attacking=True) == terrain_percentage(
        "pioneer_support", "amphibious", is_attacking=True, doctrine_bonuses=None
    )


def test_apply_terrain_modifier_applies_a_doctrine_only_bonus():
    # Pioneer Support has no own amphibious entry at all (0 without
    # doctrine) - this is the exact "I see nothing" case Ollie reported,
    # confirming apply_terrain_modifier's early-return-on-zero path no
    # longer fires once a doctrine_bonuses entry is supplied.
    stats = {"soft_attack": 10.0, "hard_attack": 5.0, "breakthrough": 2.0, "defense": 3.0}
    bonuses = [("pioneer_support", {"amphibious": {"attack": 0.15}})]
    assert terrain_percentage("pioneer_support", "amphibious", is_attacking=True) == 0
    result = apply_terrain_modifier(
        stats, "pioneer_support", "amphibious", is_attacking=True, doctrine_bonuses=bonuses
    )
    assert result["soft_attack"] == pytest.approx(11.5)
    assert result["breakthrough"] == pytest.approx(2.3)
    assert result["defense"] == 3.0  # not an attack-side field - untouched


def test_division_terrain_percentage_includes_doctrine_bonuses():
    bonuses = [("pioneer_support", {"amphibious": {"attack": 0.15}})]
    assert division_terrain_percentage(
        ["pioneer_support"], "amphibious", is_attacking=True, doctrine_bonuses=bonuses
    ) == pytest.approx(0.15)


# --- division_terrain_percentage's real formula (corrected 2026-10-08 - see
# the function's own docstring for the full reverse-engineering trail
# against Template Examples/ingame_7_marines_1_mountaineer_pioneerSupport.png,
# a real in-game screenshot Ollie supplied after reporting Pioneer Support's
# terrain bonus looked wrong) ---

def test_division_terrain_percentage_reproduces_the_real_marines_screenshot_exactly():
    # 9 Marine + 1 Mountaineer (both combat_width 2) + 1 Pioneer Support
    # (combat_width 0) with "Marines: Amphibious Expeditionary" active.
    # Real in-game tooltip: Attack 160% (+60%), Defence 115% (+15%).
    battalions = ["marine"] * 9 + ["mountaineers"]
    support_companies = ["pioneer_support"]
    bonuses = [("pioneer_support", {"amphibious": {"attack": 0.15, "defence": 0.15}})]
    items = battalions + support_companies

    attack = division_terrain_percentage(items, "amphibious", is_attacking=True, doctrine_bonuses=bonuses)
    defence = division_terrain_percentage(items, "amphibious", is_attacking=False, doctrine_bonuses=bonuses)

    assert attack == pytest.approx(0.60)
    assert defence == pytest.approx(0.15)


def test_division_terrain_percentage_weights_by_combat_width_not_item_count():
    # 1 Marine (own amphibious attack 0.5, combat_width 2) + 9 Mountaineers
    # (no own amphibious entry, combat_width 2 each) - a plain per-item
    # average would give 0.05 (1/10 contribute 0.5); a combat-width-weighted
    # average gives the same 0.05 here too since every item shares the same
    # width (2) - confirming uniform-width divisions are unaffected by the
    # fix, exactly as the pre-existing "mixed division" test already showed
    # (infantry and mountaineers also share combat_width 2).
    items = ["marine"] + ["mountaineers"] * 9
    assert division_terrain_percentage(items, "amphibious", is_attacking=True) == pytest.approx(0.05)


def test_division_terrain_percentage_excludes_zero_width_items_from_the_weighted_part():
    # Pioneer Support's own combat_width is 0 (support companies are, by
    # design - units_copy/engineer.txt) - a width-weighted average would
    # silently zero out ANY of its own per-unit terrain data (not just a
    # doctrine bonus) if folded into the same weighted term as battalions,
    # so it must be added flat instead. Marsh is pioneer_support's own real
    # per-unit terrain (attack 0.10) - confirms this isn't specific to the
    # doctrine-bonus case.
    items = ["infantry"] * 5 + ["pioneer_support"]
    infantry_marsh = terrain_percentage("infantry", "marsh", is_attacking=True)  # 0, no own entry
    pioneer_marsh = terrain_percentage("pioneer_support", "marsh", is_attacking=True)  # own 0.10
    result = division_terrain_percentage(items, "marsh", is_attacking=True)
    # Weighted part (5 infantry, all contributing infantry_marsh) + flat part (pioneer_marsh).
    assert result == pytest.approx(infantry_marsh + pioneer_marsh)


# --- Real bug fixed 2026-11-02: the flat (zero-combat-width) group was a
# running SUM, not an average - Ollie reported an obviously-impossible
# terrain badge (over -300% attack in Mountain) mixing Mechanized with
# several Tank-Designer-fed support-company roles (Super Heavy Tank
# Destroyer, the 3 Flame Tank sizes, Super Heavy Tank itself) - all genuine
# combat_width=0 HOI4 units (confirmed directly against Copies/units_copy/),
# not a data gap. Every test above only ever exercised ONE flat
# contributor at a time, so "sum" and "average" were indistinguishable
# until now.

def test_division_terrain_percentage_averages_rather_than_sums_the_flat_group():
    # 5 zero-combat-width support-company roles, each with a real own
    # mountain penalty - a sum would make a single item's own penalty
    # dominate the badge 5x over; an average can never exceed the single
    # most extreme contributor, the same bound the weighted (battalion)
    # part already enforces.
    flat_items = [
        "super_heavy_tank_destroyer_brigade", "light_flame_tank",
        "medium_flame_tank", "heavy_flame_tank", "super_heavy_armor",
    ]
    for key in flat_items:
        assert BATTALION_STATS[key].get("combat_width", 0) == 0

    percentages = [terrain_percentage(key, "mountain", is_attacking=True) for key in flat_items]
    expected_flat_average = sum(percentages) / len(percentages)

    result = division_terrain_percentage(flat_items, "mountain", is_attacking=True)
    assert result == pytest.approx(expected_flat_average)
    # Physically sane bound: an average can't exceed its most extreme input.
    assert result >= min(percentages) - 1e-9
    assert result <= max(percentages) + 1e-9


def test_division_terrain_percentage_flat_group_matches_weighted_bound_when_mixed():
    # Mechanized (real combat width, weighted part) plus the same 5 flat
    # support-company roles - the old sum formula gave -3.55 (-355%) for
    # this exact mix; the fixed formula stays within a believable range
    # (bounded by weighted-average's own extreme, -0.55, plus flat-
    # average's own extreme, -0.9).
    items = ["mechanized"] * 5 + [
        "super_heavy_tank_destroyer_brigade", "light_flame_tank",
        "medium_flame_tank", "heavy_flame_tank", "super_heavy_armor",
    ]
    result = division_terrain_percentage(items, "mountain", is_attacking=True)
    assert result > -2.0  # nowhere near the old, physically-impossible -3.55
    assert result == pytest.approx(-1.15)


# --- Real bug fixed 2026-11-02 (same day, continued): the flat group's
# average was diluted by zero-combat-width items with NO terrain effect at
# all for the selected terrain (most support companies, most of the time -
# 36 of 101 compiled items have no UNIT_TERRAIN_MODIFIERS entry anywhere).
# A structural non-participant should not change the average's denominator
# any more than it should change a real HOI4 tooltip just by being present.

def test_division_terrain_percentage_is_unaffected_by_an_inert_flat_item():
    # Reproduces the real screenshot case (9 Marine + 1 Mountaineer + 1
    # Pioneer Support, "Marines: Amphibious Expeditionary" active, real
    # Attack 160%/+60%) then adds a Signal Company - a genuine combat_width=0
    # support company with NO amphibious entry anywhere (data/terrain.py has
    # no "signal_company" key at all) and no doctrine bonus targeting it.
    # The badge must stay exactly 0.60, not get diluted toward 0 just
    # because a second, irrelevant support slot was filled.
    battalions = ["marine"] * 9 + ["mountaineers"]
    bonuses = [("pioneer_support", {"amphibious": {"attack": 0.15, "defence": 0.15}})]

    with_one_support = division_terrain_percentage(
        battalions + ["pioneer_support"], "amphibious", is_attacking=True, doctrine_bonuses=bonuses
    )
    with_inert_support_added = division_terrain_percentage(
        battalions + ["pioneer_support", "signal_company"],
        "amphibious", is_attacking=True, doctrine_bonuses=bonuses,
    )
    assert with_one_support == pytest.approx(0.60)
    assert with_inert_support_added == pytest.approx(0.60)


def test_division_terrain_percentage_still_averages_multiple_real_flat_contributors():
    # Guards against overcorrecting into a pure sum: two flat items that
    # BOTH have a real, nonzero own value for this terrain must still be
    # averaged together, not summed (the 2026-11-02 fix earlier this file
    # covers) - adding a zero-effect item is what changed, not this.
    pioneer_marsh = terrain_percentage("pioneer_support", "marsh", is_attacking=True)  # own 0.10
    jungle_pioneer_marsh = terrain_percentage("jungle_pioneers_support", "marsh", is_attacking=True)
    assert pioneer_marsh != 0 and jungle_pioneer_marsh != 0

    result = division_terrain_percentage(
        ["infantry"] * 5 + ["pioneer_support", "jungle_pioneers_support"], "marsh", is_attacking=True
    )
    infantry_marsh = terrain_percentage("infantry", "marsh", is_attacking=True)  # 0
    expected_flat_average = (pioneer_marsh + jungle_pioneer_marsh) / 2
    assert result == pytest.approx(infantry_marsh + expected_flat_average)
