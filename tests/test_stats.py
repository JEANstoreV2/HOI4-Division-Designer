import pytest

from data.battalion_stats import BATTALION_STATS
from logic.stats import calculate_division_stats, calculate_item_stats
from logic.tank_designer import calculate_tank_design_stats


def test_infantry_combines_its_own_stats_with_its_equipment():
    stats = calculate_item_stats("infantry")

    # Structural stats pass through from data/battalion_stats.py unchanged.
    assert stats["max_strength"] == 25
    assert stats["max_organisation"] == 60
    assert stats["manpower"] == 1000

    # Combat stats: infantry has no direct combat bonus of its own, so
    # these come entirely from infantry_equipment_1.
    assert stats["soft_attack"] == 6
    assert stats["hard_attack"] == 1
    assert stats["defense"] == 22
    assert stats["breakthrough"] == 3
    assert stats["ap_attack"] == 4

    # Production cost: 100 Infantry Equipment at 0.50 IC each.
    assert stats["production_cost"] == pytest.approx(50)
    assert stats["combat_stats_available"] is True


def test_mechanized_adds_its_own_bonus_on_top_of_two_equipment_types():
    stats = calculate_item_stats("mechanized")

    # (1.19.4) Mechanized's own +0.1 soft attack bonus was removed by the
    # patch - soft_attack is now equipment-only (6, no own contribution).
    # +4.0 hard attack still stacks on top of infantry_equipment's
    # contribution (mechanized_equipment defines neither soft_attack nor
    # hard_attack, so it contributes 0 to both).
    assert stats["soft_attack"] == pytest.approx(6)
    assert stats["hard_attack"] == pytest.approx(4.0 + 1)

    # Defense/breakthrough/armor/hardness sum across both equipment types,
    # since mechanized itself has no direct values for these.
    assert stats["defense"] == pytest.approx(22 + 26)
    assert stats["breakthrough"] == pytest.approx(3 + 6)
    assert stats["armor_value"] == pytest.approx(0 + 10)
    assert stats["hardness"] == pytest.approx(0 + 0.60)

    # Production cost: 100 Infantry Equipment (0.50 ea) + 40 Mechanized
    # Equipment (8 ea).
    assert stats["production_cost"] == pytest.approx(100 * 0.50 + 40 * 8)
    assert stats["combat_stats_available"] is True


def test_confirmed_gap_item_is_flagged_but_still_returns_its_own_stats():
    stats = calculate_item_stats("light_flame_tank")

    # No combat stats from equipment (light_tank_flame_chassis has none),
    # so these are exactly the battalion's own direct values.
    assert stats["soft_attack"] == pytest.approx(-0.5)
    assert stats["hard_attack"] == pytest.approx(-0.75)
    assert stats["defense"] == pytest.approx(-0.75)

    # armor_value/hardness DO get a contribution, since the gap equipment
    # still defines those structural fields.
    assert stats["armor_value"] == pytest.approx(-0.75 + 10)
    assert stats["hardness"] == pytest.approx(0 + 0.8)

    assert stats["combat_stats_available"] is False


def test_every_item_can_be_calculated_without_error():
    for item_key in BATTALION_STATS:
        stats = calculate_item_stats(item_key)
        assert stats["production_cost"] >= 0


# --- Research-aware equipment tier resolution (data/equipment_tiers.py) ---
# These prove calculate_item_stats's optional `researched` parameter is
# purely additive: omitting it (every test above) is unaffected, and
# passing it resolves the right tier rather than assuming EQUIPMENT[key] is
# always either the floor or the ceiling.

def test_researched_none_matches_omitting_the_argument():
    assert calculate_item_stats("infantry", researched=None) == calculate_item_stats("infantry")


def test_higher_researched_tier_improves_stats():
    baseline = calculate_item_stats("light_armor")
    tier1 = calculate_item_stats(
        "light_armor", researched={"gwtank_chassis", "basic_light_tank_chassis"}
    )
    tier2 = calculate_item_stats(
        "light_armor",
        researched={"gwtank_chassis", "basic_light_tank_chassis", "improved_light_tank_chassis"},
    )

    # Tier 1 researched matches the no-researched-arg baseline exactly,
    # since data/equipment.py's fixed entry already represents tier 1.
    assert tier1 == baseline

    # Tier 2 is a real improvement over tier 1.
    assert tier2["soft_attack"] > tier1["soft_attack"]
    assert tier2["armor_value"] > tier1["armor_value"]


def test_researching_only_the_earliest_tech_gives_the_weaker_pre_tier_1_stats():
    # motorized_equipment has a real tier BELOW data/equipment.py's fixed
    # baseline (motorized_equipment_0, unlocked by tech_trucks alone,
    # before motorised_infantry unlocks tier 1) - proving the resolver
    # doesn't assume EQUIPMENT[key] is the floor.
    baseline = calculate_item_stats("mot_artillery_brigade")
    tier0 = calculate_item_stats("mot_artillery_brigade", researched={"tech_trucks"})

    assert tier0["breakthrough"] < baseline["breakthrough"]


def test_confirmed_tier_zero_gap_marks_combat_stats_unavailable():
    # Only the light base-tank line has real tier-0 combat stats
    # (gw_tank_equipment) - medium/heavy do not, per data/equipment_tiers.py's
    # header. With only the root armor tech done, Medium Tank is selectable
    # but has no real combat stats yet.
    gap = calculate_item_stats("medium_armor", researched={"gwtank_chassis"})
    assert gap["combat_stats_available"] is False


# --- Doctrine-aware unit bonuses (data/doctrines.py, logic/doctrines.py) ---
# These prove calculate_item_stats's optional `doctrine` parameter is purely
# additive (omitting it is unaffected) and that the three doctrine bonus
# conventions - flat add (max_organisation/suppression_factor/combat_width/
# max_strength), a flat km/h add scaled by the base speed constant
# (max_speed), and a single percentage multiplier for everything else - are
# applied correctly. See logic/stats.py's _DOCTRINE_FLAT_FIELDS/
# _DOCTRINE_SPEED_SCALED_FIELDS comments for the evidence behind that split.

def test_doctrine_none_matches_omitting_the_argument():
    assert calculate_item_stats("infantry", doctrine=None) == calculate_item_stats("infantry")


def test_category_targeted_bonus_applies_as_a_percentage():
    # mobile_infantry's immediate effect gives category_all_infantry (which
    # "infantry" belongs to) +10% breakthrough.
    baseline = calculate_item_stats("infantry")
    doctrine = {
        "active_grand_doctrines": {"new_mobile_warfare"},
        "track_subdoctrines": {"infantry": "mobile_infantry"},
        "claimed_rewards": {},
    }
    with_doctrine = calculate_item_stats("infantry", doctrine=doctrine)
    assert with_doctrine["breakthrough"] == pytest.approx(baseline["breakthrough"] * 1.1)


def test_item_key_targeted_bonus_applies_too():
    # assault_infantry's immediate effect targets the "artillery" item key
    # directly (a support company), not a category: +20% soft attack.
    # (1.19.3): raised from +10% to +20% ("Assault Infantry Adoption Bonus:
    # Bonus to Support Artillery attack has been increased from +10% to +20%").
    baseline = calculate_item_stats("artillery", is_support_type=True)
    doctrine = {
        "active_grand_doctrines": {"new_mobile_warfare"},
        "track_subdoctrines": {"infantry": "assault_infantry"},
        "claimed_rewards": {},
    }
    with_doctrine = calculate_item_stats("artillery", is_support_type=True, doctrine=doctrine)
    assert with_doctrine["soft_attack"] == pytest.approx(baseline["soft_attack"] * 1.2)


def test_max_organisation_bonus_is_a_flat_addition_not_a_percentage():
    # mobile_infantry's 2nd reward (combined_arms_planning) gives
    # category_all_infantry +10 max_organisation - a flat number in the
    # source data, not a fraction, unlike every other field it also sets.
    doctrine_before = {
        "active_grand_doctrines": {"new_mobile_warfare"},
        "track_subdoctrines": {"infantry": "mobile_infantry"},
        "claimed_rewards": {"mobile_infantry": 1},
    }
    doctrine_after = {
        "active_grand_doctrines": {"new_mobile_warfare"},
        "track_subdoctrines": {"infantry": "mobile_infantry"},
        "claimed_rewards": {"mobile_infantry": 2},
    }
    before = calculate_item_stats("infantry", doctrine=doctrine_before)
    after = calculate_item_stats("infantry", doctrine=doctrine_after)
    assert after["max_organisation"] == before["max_organisation"] + 10


def test_combat_width_bonus_is_a_flat_addition_not_a_percentage():
    # Large Unit Tactics' 2nd reward (flexible_division_structures) gives
    # "infantry" (targeted directly, not via a category) combat_width -0.3,
    # reduced to -0.2 by the 1.19.4 patch. Confirmed flat by real gameplay
    # (Ollie: 2 -> 1.7 in-game, pre-1.19.4), not a percentage (2 x 0.7 = 1.4,
    # this tool's wrong answer before the original fix) - see
    # logic/stats.py's _DOCTRINE_FLAT_FIELDS comment.
    doctrine = {
        "active_grand_doctrines": set(),
        "track_subdoctrines": {"infantry": "large_unit_tactics"},
        "claimed_rewards": {"large_unit_tactics": 2},
    }
    stats = calculate_item_stats("infantry", doctrine=doctrine)
    assert stats["combat_width"] == pytest.approx(1.8)  # (1.19.4) 1.7->1.8 (-0.3->-0.2)


def test_max_strength_bonus_is_a_flat_addition_not_a_percentage():
    # Grand Battleplan + Field Engineering's "Sapper Fieldcraft" reward
    # (index 1) gives "engineer" max_strength: 0.25 - confirmed flat by real
    # gameplay (a division containing this Engineer support company had its
    # TOTAL max_strength go 127.0 -> 127.2, i.e. +0.25 on the Engineer's own
    # 2.0 base, not the ~2.5 a percentage reading would give: 2 x 1.25) -
    # see logic/stats.py's _DOCTRINE_FLAT_FIELDS comment. (1.19.3 note: this
    # classification's own original evidence example, Mounted Infantry's
    # "Beasts of War" cavalry max_strength bonus, was removed by the patch -
    # replaced with a battalion_mult, a cross-unit synergy effect this
    # project doesn't apply, matching Cavalry Recon's own existing deferral
    # - so this test now uses the OTHER independent example this
    # classification was already cross-checked against, unaffected by the
    # patch.)
    doctrine = {
        "active_grand_doctrines": set(),
        "track_subdoctrines": {"combat_support": "field_engineering"},
        "claimed_rewards": {"field_engineering": 2},
    }
    stats = calculate_item_stats("engineer", is_support_type=True, doctrine=doctrine)
    assert stats["max_strength"] == pytest.approx(2.25)


def test_maximum_speed_alias_is_a_flat_km_h_add_scaled_by_the_base_speed_constant():
    # "Beasts of War" reward also sets category_cavalry "maximum_speed" -
    # our own field is "max_speed" (_DOCTRINE_FIELD_ALIASES). Originally
    # confirmed NOT a percentage of the unit's own speed (real gameplay:
    # Cavalry's 6.4 km/h went to 8.4, not 9.6 = 6.4 x 1.5) and NOT a literal
    # flat addition either (not 6.9 = 6.4 + 0.5) - it's a value x HOI4's
    # 4 km/h base land-unit speed constant, added flat. (1.19.3: the patch
    # reduced this reward's speed bonus from 0.5 to 0.4 - "Reduced the Speed
    # Bonus to Cavalry Recon and Cavalry to +40% (for a total of 8 kph
    # instead of the previous 8.4 kph)", confirming both the OLD (8.4) and
    # NEW (8.0) values directly: 6.4 + (0.4 x 4.0) = 8.0 exactly.) See
    # logic/stats.py's _DOCTRINE_SPEED_SCALED_FIELDS comment.
    doctrine = {
        "active_grand_doctrines": set(),
        "track_subdoctrines": {"infantry": "mounted_infantry"},
        "claimed_rewards": {"mounted_infantry": 4},
    }
    stats = calculate_item_stats("cavalry", doctrine=doctrine)
    assert stats["max_speed"] == pytest.approx(8.0)


def test_untracked_doctrine_field_does_not_change_the_result():
    # commandos' 1st reward (isolated_combat_elements) targets "field_hospital"
    # with only "casualty_trickleback" - a real doctrine field with no
    # tracked equivalent here, so it's silently skipped rather than guessed.
    baseline = calculate_item_stats("field_hospital", is_support_type=True)
    doctrine = {
        "active_grand_doctrines": set(),
        "track_subdoctrines": {"infantry": "commandos"},
        "claimed_rewards": {"commandos": 1},
    }
    with_doctrine = calculate_item_stats("field_hospital", is_support_type=True, doctrine=doctrine)
    assert with_doctrine == baseline


def test_terrain_nested_bonus_does_not_change_the_result():
    # rangers_1's immediate effect targets "ranger_battalion" with only
    # "acclimatization_cold_climate_gain_factor" (untracked) and a
    # terrain-nested {"forest": {...}} sub-dict - both compiled faithfully
    # but not applied here: doctrine's own terrain-nested bonus shape is
    # different from (and not cross-applied with) the Terrain feature's own
    # model (data/terrain.py/logic/terrain.py) - see logic/stats.py's
    # _doctrine_bonus_for_item comment. No reward is claimed, so this is
    # the only bonus in play.
    baseline = calculate_item_stats("ranger_battalion")
    doctrine = {
        "active_grand_doctrines": {"special_forces_quantity"},
        "track_subdoctrines": {"special_forces_first": "rangers_1"},
        "claimed_rewards": {},
    }
    with_doctrine = calculate_item_stats("ranger_battalion", doctrine=doctrine)
    assert with_doctrine == baseline

    # Researching the dedicated medium-tank tech resolves the gap, matching
    # the no-researched-arg baseline exactly.
    resolved = calculate_item_stats(
        "medium_armor", researched={"gwtank_chassis", "basic_medium_tank_chassis"}
    )
    assert resolved == calculate_item_stats("medium_armor")
    assert resolved["combat_stats_available"] is True


def test_category_army_catch_all_matches_a_real_division_screenshot():
    # A 9 Infantry division under Grand Battleplan's Infiltration Tactics
    # (operations track), with only its 1st reward (infiltration_assault)
    # claimed: category_army - a catch-all every land unit belongs to -
    # gets +10% breakthrough and +5 flat max_organisation. Confirmed exactly
    # against a real screenshot (Template Examples/
    # 9_infantry_grandBattleplan_infiltrationTactics.png): 65.0 org
    # (60 + 5) and 29.7 breakthrough (27 x 1.1), with every other stat
    # (soft/hard attack, defense, combat width, speed, strength) unchanged -
    # this reward doesn't touch any of them.
    doctrine = {
        "active_grand_doctrines": set(),
        "track_subdoctrines": {"operations": "infiltration_tactics"},
        "claimed_rewards": {"infiltration_tactics": 1},
    }
    stats = calculate_division_stats(["infantry"] * 9, doctrine=doctrine)

    assert stats["max_organisation"] == pytest.approx(65.0)
    assert stats["breakthrough"] == pytest.approx(29.7)
    assert stats["max_strength"] == 225
    assert stats["soft_attack"] == 54
    assert stats["hard_attack"] == 9
    assert stats["defense"] == 198
    assert stats["combat_width"] == 18
    assert stats["max_speed"] == 4.0


# --- Tank Designer pipeline integration (Phase 6) ---
# These prove calculate_item_stats/calculate_division_stats' optional
# `tank_designs` parameter is purely additive (omitting it is unaffected)
# and that a finished design's own computed stats (logic/tank_designer.py's
# calculate_tank_design_stats) flow through exactly like any other
# equipment family - `tank_designs` is keyed by equipment key, which is
# deliberately identical to the chassis/role key that produced it (see
# logic/stats.py's _equipment_stats).

_MEDIUM_TANK_DEFAULT_MODULES = {
    "turret_type_slot": "tank_medium_one_man_tank_turret",
    "suspension_type_slot": "tank_bogie_suspension",
    "armor_type_slot": "tank_riveted_armor",
    "engine_type_slot": "tank_gasoline_engine",
}

_LIGHT_TANK_DEFAULT_MODULES = {
    "turret_type_slot": "tank_light_one_man_tank_turret",
    "main_armament_slot": "tank_heavy_machine_gun",
    "suspension_type_slot": "tank_bogie_suspension",
    "armor_type_slot": "tank_riveted_armor",
    "engine_type_slot": "tank_gasoline_engine",
}


def test_tank_designs_none_matches_omitting_the_argument():
    assert calculate_item_stats("medium_armor", tank_designs=None) == calculate_item_stats("medium_armor")


def test_a_custom_design_replaces_the_equipment_family_it_was_built_for():
    # medium_armor needs 50x "medium_tank_chassis" - a Basic Medium Tank
    # (medium_tank_chassis tier 1) at its default loadout, matching
    # tank_designer_examples/medBasicChassis_noEdits.png exactly (Phase 5's
    # own confirmed numbers).
    tank_designs = {
        "medium_tank_chassis": {
            "chassis_key": "medium_tank_chassis", "tier": 1,
            "chosen_modules": _MEDIUM_TANK_DEFAULT_MODULES,
        }
    }
    stats = calculate_item_stats("medium_armor", tank_designs=tank_designs)

    # medium_armor's own +0.15 breakthrough stacks flat on top of the
    # design's own 11.5 (a battalion, not a support-company item).
    assert stats["breakthrough"] == pytest.approx(0.15 + 11.5)
    assert stats["armor_value"] == pytest.approx(30.0)
    assert stats["hardness"] == pytest.approx(0.85)
    # 50 units at the design's own 4.8 build_cost_ic each.
    assert stats["production_cost"] == pytest.approx(50 * 4.8)
    assert stats["combat_stats_available"] is True


def test_a_custom_design_takes_priority_over_researched_for_the_same_key():
    tank_designs = {
        "medium_tank_chassis": {
            "chassis_key": "medium_tank_chassis", "tier": 1,
            "chosen_modules": _MEDIUM_TANK_DEFAULT_MODULES,
        }
    }
    with_both = calculate_item_stats(
        "medium_armor",
        researched={"gwtank_chassis", "basic_medium_tank_chassis"},
        tank_designs=tank_designs,
    )
    with_design_only = calculate_item_stats("medium_armor", tank_designs=tank_designs)
    assert with_both == with_design_only


def test_a_role_variant_design_applies_its_own_role_combat_modifiers():
    # medium_tank_destroyer_brigade needs "medium_tank_destroyer_chassis" -
    # the same chassis/tier/modules as the plain case above, but built as
    # the Tank Destroyer role, matching
    # tank_designer_examples/medBasicChassis_TD_basicHighVelocityCannon.png's
    # confirmed -25% breakthrough / +15% piercing.
    modules = _MEDIUM_TANK_DEFAULT_MODULES | {"main_armament_slot": "tank_high_velocity_cannon"}
    tank_designs = {
        "medium_tank_destroyer_chassis": {
            "chassis_key": "medium_tank_chassis", "tier": 1,
            "chosen_modules": modules, "role_key": "medium_tank_destroyer_chassis",
        }
    }
    stats = calculate_item_stats("medium_tank_destroyer_brigade", tank_designs=tank_designs)
    # medium_tank_destroyer_brigade's own +0.15 ap_attack / -0.25 breakthrough
    # stack flat on top of the design's own 78.2 / 2.5 - the design's own
    # breakthrough dropped from 7.5 to 2.5 under 1.19.4's Tank Destroyer
    # breakthrough standardization (-25%->-75%, 0.75->0.25 multiplier).
    assert stats["ap_attack"] == pytest.approx(0.15 + 78.2)
    assert stats["breakthrough"] == pytest.approx(-0.25 + 2.5)  # (1.19.4)


# --- Reliability-scaled max_strength (HP), added 1.19.4, formula
# empirically confirmed 2026-11-02 against 4 real Tank Designer screenshots
# (Template Examples/Light_Tank_HMG*.png) - see CLAUDE.md's Tank Designer
# section for the full derivation. ---

def test_reliability_scaled_hp_matches_the_real_base_chassis_screenshots():
    # Basic Light Tank + HMG, no extra modules - real screenshot shows
    # Reliability 95.0% / HP 3.4 exactly (2.0 + 1.5 x 0.95 = 3.425 -> 3.4).
    tank_designs = {
        "light_tank_chassis": {
            "chassis_key": "light_tank_chassis", "tier": 1,
            "chosen_modules": _LIGHT_TANK_DEFAULT_MODULES,
        }
    }
    stats = calculate_item_stats("light_armor", tank_designs=tank_designs)
    assert stats["max_strength"] == pytest.approx(3.425)

    # + Easy Maintenance - real screenshot shows Reliability 102.5% / HP 3.5
    # (2.0 + 1.5 x 1.025 = 3.5375 -> 3.5).
    modules_with_easy_maint = {**_LIGHT_TANK_DEFAULT_MODULES, "special_type_slot_1": "easy_maintenance"}
    tank_designs_2 = {
        "light_tank_chassis": {
            "chassis_key": "light_tank_chassis", "tier": 1,
            "chosen_modules": modules_with_easy_maint,
        }
    }
    stats_2 = calculate_item_stats("light_armor", tank_designs=tank_designs_2)
    assert stats_2["max_strength"] == pytest.approx(3.5375)


def test_reliability_scaled_hp_matches_the_real_screenshot_with_reliability_reducing_ticks():
    # + Sloped Armor + 5 armor ticks + 5 engine ticks (each tick reduces
    # reliability) - real screenshot shows Reliability 80.7% / HP 3.2
    # (2.0 + 1.5 x 0.807 ~= 3.2105 -> 3.2). Sloped Armor's own addition
    # confirmed via the same screenshot set to carry no separate HP bonus
    # of its own (a plain Sloped-Armor-only design, no ticks, showed the
    # exact same 95.0%/3.4 as the no-module baseline).
    modules = {**_LIGHT_TANK_DEFAULT_MODULES, "special_type_slot_1": "sloped_armor"}
    tank_designs = {
        "light_tank_chassis": {
            "chassis_key": "light_tank_chassis", "tier": 1, "chosen_modules": modules,
            "tick_levels": {"tank_nsb_armor_upgrade": 5, "tank_nsb_engine_upgrade": 5},
        }
    }
    stats = calculate_item_stats("light_armor", tank_designs=tank_designs)
    assert stats["max_strength"] == pytest.approx(3.2105, abs=0.001)


def test_reliability_scaled_hp_applies_to_line_and_regimental_support_tank_destroyer():
    modules = _MEDIUM_TANK_DEFAULT_MODULES | {"main_armament_slot": "tank_high_velocity_cannon"}
    tank_designs = {
        "medium_tank_destroyer_chassis": {
            "chassis_key": "medium_tank_chassis", "tier": 1,
            "chosen_modules": modules, "role_key": "medium_tank_destroyer_chassis",
        }
    }
    line = calculate_item_stats("medium_tank_destroyer_brigade", tank_designs=tank_designs)
    regimental = calculate_item_stats(
        "medium_tank_destroyer_support", is_support_type=True, tank_designs=tank_designs
    )
    # Design's own resolved reliability is 0.75 (the anti_tank role's stat
    # override). Line: 0.5 + 0.75 x 0.75 = 1.0625. Regimental Support:
    # 0.1 + 0.55 x 0.75 = 0.5125 - genuinely different base/factor from
    # Line, per the real patch note's own separate worked example.
    assert line["max_strength"] == pytest.approx(1.0625)
    assert regimental["max_strength"] == pytest.approx(0.5125)


def test_reliability_scaled_hp_is_a_no_op_without_a_custom_design():
    # Omitting tank_designs (or not having one for the needed equipment)
    # must stay byte-identical to before this mechanic existed - the
    # item's own flat data/battalion_stats.py max_strength value, untouched.
    assert calculate_item_stats("light_armor")["max_strength"] == pytest.approx(2.0)
    assert calculate_item_stats(
        "medium_tank_destroyer_brigade"
    )["max_strength"] == pytest.approx(0.5)


def test_reliability_scaled_hp_does_not_apply_to_land_cruiser():
    # Land Cruiser is explicitly excluded by the real patch note itself
    # ("All Tank Chassis except for Land Cruisers...") - its own flat
    # max_strength (15) never matches one of the 3 known base values
    # anyway, so it's excluded structurally, not via a special case.
    tank_designs = {"land_cruiser_chassis": {"chassis_key": "land_cruiser_chassis", "tier": 1, "chosen_modules": {}}}
    stats = calculate_item_stats("land_cruiser", tank_designs=tank_designs)
    assert stats["max_strength"] == pytest.approx(15)


# Armor-category battalions have no own max_speed in data/battalion_stats.py
# at all (unlike every leg/mounted/motorized battalion) - their speed comes
# entirely from their equipment. This was a known, deliberately deferred gap
# (Activity_Log.md, 2026-09-14/2026-09-16) that silently left every such
# item contributing max_speed=0, which calculate_division_stats' min() rule
# then propagated to the WHOLE division regardless of other battalions -
# reported directly by Ollie once Tank Designer made it possible to notice
# (a Medium SP Artillery with a real 5 km/h design still zeroed the
# division). Fixed 2026-09-23 in calculate_item_stats.

def test_max_speed_falls_back_to_the_default_chassis_when_no_design_is_set():
    # light_armor needs light_tank_chassis, whose real maximum_speed is 10
    # (data/equipment.py) - the "chassis' default stats" case Ollie asked
    # to make sure was covered, not just the custom-design case below.
    assert calculate_item_stats("light_armor")["max_speed"] == 10


def test_max_speed_uses_a_custom_designs_own_speed():
    tank_designs = {
        "medium_tank_chassis": {
            "chassis_key": "medium_tank_chassis", "tier": 1,
            "chosen_modules": _MEDIUM_TANK_DEFAULT_MODULES,
        }
    }
    expected_speed = calculate_tank_design_stats(**tank_designs["medium_tank_chassis"])["maximum_speed"]

    stats = calculate_item_stats("medium_armor", tank_designs=tank_designs)

    assert stats["max_speed"] == expected_speed


def test_max_speed_is_unaffected_for_battalions_with_their_own_real_value():
    # infantry and mot_artillery_brigade both already carry a real max_speed
    # directly in data/battalion_stats.py - the new equipment fallback must
    # never override it.
    assert calculate_item_stats("infantry")["max_speed"] == BATTALION_STATS["infantry"]["max_speed"]
    assert (
        calculate_item_stats("mot_artillery_brigade")["max_speed"]
        == BATTALION_STATS["mot_artillery_brigade"]["max_speed"]
    )


def test_a_tank_design_still_uses_the_support_company_percentage_formula():
    # medium_sp_anti_air_brigade needs "medium_tank_aa_chassis" as a support
    # company - its own combat-stat fields stay a percentage modifier on the
    # design's equipment stats, not a flat add (see the module's own header
    # comment on is_support_type), even though the equipment itself is now a
    # custom design rather than a fixed tier.
    modules = _MEDIUM_TANK_DEFAULT_MODULES | {"main_armament_slot": "tank_anti_air_cannon"}
    tank_designs = {
        "medium_tank_aa_chassis": {
            "chassis_key": "medium_tank_chassis", "tier": 1,
            "chosen_modules": modules, "role_key": "medium_tank_aa_chassis",
        }
    }
    design_stats = calculate_tank_design_stats(
        "medium_tank_chassis", 1, modules, role_key="medium_tank_aa_chassis"
    )
    own_soft_attack = BATTALION_STATS["medium_sp_anti_air_brigade"].get("soft_attack", 0)
    stats = calculate_item_stats(
        "medium_sp_anti_air_brigade", is_support_type=True, tank_designs=tank_designs
    )
    assert stats["soft_attack"] == pytest.approx(design_stats["soft_attack"] * (1 + own_soft_attack))


def test_division_stats_aggregate_a_division_with_a_custom_designed_tank():
    tank_designs = {
        "medium_tank_chassis": {
            "chassis_key": "medium_tank_chassis", "tier": 1,
            "chosen_modules": _MEDIUM_TANK_DEFAULT_MODULES,
        }
    }
    plain_tank_stats = calculate_item_stats("medium_armor")
    designed_tank_stats = calculate_item_stats("medium_armor", tank_designs=tank_designs)
    assert designed_tank_stats["breakthrough"] != plain_tank_stats["breakthrough"]

    division = calculate_division_stats(["infantry"] * 3 + ["medium_armor"] * 2, tank_designs=tank_designs)
    infantry_stats = calculate_item_stats("infantry")
    assert division["breakthrough"] == pytest.approx(
        3 * infantry_stats["breakthrough"] + 2 * designed_tank_stats["breakthrough"]
    )
    assert division["combat_stats_available"] is True

    # Regression guard for the exact bug Ollie reported: before the
    # max_speed fix above, designed_tank_stats["max_speed"] was always 0,
    # so this division's min()-based speed silently came out 0 regardless
    # of the tank's real (nonzero) design speed or infantry's own real 4.0.
    assert division["max_speed"] == pytest.approx(
        min(infantry_stats["max_speed"], designed_tank_stats["max_speed"])
    )
    assert division["max_speed"] > 0


# --- Terrain integration (data/terrain.py, logic/terrain.py) ---
# These prove calculate_item_stats/calculate_division_stats' optional
# `terrain` parameter is purely additive (omitting it is unaffected) and
# that the confirmed two-layer formula (see logic/terrain.py and CLAUDE.md's
# Terrain section) is applied correctly, including on top of doctrine and
# tank designs.

def test_terrain_none_matches_omitting_the_argument():
    assert calculate_item_stats("infantry", terrain=None) == calculate_item_stats("infantry")


# terrain_screenshots/5_mountaineers.png/mountaineer_attack.png/
# mountaineer_defense.png were taken with ONLY "infantry_weapons" researched
# (tier 0 infantry_equipment, soft_attack 3/hard_attack 0.5/defense 20) - NOT
# the no-researched-arg default (EQUIPMENT[key] directly, tier 1, soft_attack
# 6). Confirmed by Hard Attack (2.5), Defense (100.0), Max Strength (100.0),
# and Production Cost (301) all matching researched={"infantry_weapons"}
# exactly - Ollie caught this after an earlier draft of this test wrongly
# concluded Mountaineers' baseline soft_attack had its own unexplained ~50%
# gap, when it was really just the wrong equipment tier being compared.
_MOUNTAINEERS_ZERO_RESEARCH = {"infantry_weapons"}


def test_terrain_reproduces_the_mountaineers_attack_screenshot_exactly():
    # 5x Mountaineers attacking into Mountain: real screenshot base Soft
    # Attack 15.0, modified to exactly -15.00% (see terrain_screenshots/
    # mountaineer_attack.png, CLAUDE.md's Terrain section for the full
    # reconciliation: generic -50% + own +35% = -15%).
    baseline = calculate_item_stats("mountaineers", researched=_MOUNTAINEERS_ZERO_RESEARCH)
    assert baseline["soft_attack"] == pytest.approx(3)

    terrain = {"terrain_key": "mountain", "is_attacking": True}
    with_terrain = calculate_item_stats(
        "mountaineers", researched=_MOUNTAINEERS_ZERO_RESEARCH, terrain=terrain
    )
    assert with_terrain["soft_attack"] == pytest.approx(3 * 0.85)


def test_terrain_reproduces_the_mountaineers_defence_screenshot_exactly():
    # 5x Mountaineers defending within Mountain: real screenshot base Soft
    # Attack 14.9 (rounding of the same underlying 15.0/5=3.0), modified to
    # exactly +10.00% (own defence 0.1, no generic defence layer exists at
    # all - see terrain_screenshots/mountaineer_defense.png).
    terrain = {"terrain_key": "mountain", "is_attacking": False}
    with_terrain = calculate_item_stats(
        "mountaineers", researched=_MOUNTAINEERS_ZERO_RESEARCH, terrain=terrain
    )
    assert with_terrain["soft_attack"] == pytest.approx(3 * 1.1)


def test_terrain_with_no_effect_leaves_stats_unchanged():
    # infantry has no per-unit terrain data, and fort has no generic layer -
    # a real, confirmed 0, not a gap.
    baseline = calculate_item_stats("infantry")
    terrain = {"terrain_key": "fort", "is_attacking": True}
    assert calculate_item_stats("infantry", terrain=terrain) == baseline


def test_terrain_applies_after_doctrine_on_the_same_field():
    # infantry attacking into Forest: generic -15%, no per-unit data.
    # Stacked with mobile_infantry's +10% breakthrough doctrine bonus - the
    # two are independently sourced and applied as separate multiplication
    # stages (doctrine first, then terrain), not summed into one percentage.
    doctrine = {
        "active_grand_doctrines": {"new_mobile_warfare"},
        "track_subdoctrines": {"infantry": "mobile_infantry"},
        "claimed_rewards": {},
    }
    baseline = calculate_item_stats("infantry")
    terrain = {"terrain_key": "forest", "is_attacking": True}
    stats = calculate_item_stats("infantry", doctrine=doctrine, terrain=terrain)
    assert stats["breakthrough"] == pytest.approx(baseline["breakthrough"] * 1.1 * 0.85)


def test_division_stats_terrain_applies_to_every_item():
    # A division's terrain state is all-or-nothing (attacking or defending
    # as a whole), so every battalion in it gets the same modifier.
    infantry_defending = calculate_item_stats(
        "infantry", terrain={"terrain_key": "urban", "is_attacking": False}
    )
    division = calculate_division_stats(
        ["infantry"] * 5, terrain={"terrain_key": "urban", "is_attacking": False}
    )
    assert division["soft_attack"] == pytest.approx(5 * infantry_defending["soft_attack"])


def test_division_stats_attacking_and_defending_give_different_totals():
    # The same division, same terrain, opposite sides - matching HOI4's own
    # side-by-side attacker/defender UI, which is what this parameter split
    # (is_attacking) exists to support. Reproduces the real 5x Mountaineers
    # screenshots exactly (15.0 base, -15%/+10%) using the same zero-research
    # state those screenshots were taken under - see
    # _MOUNTAINEERS_ZERO_RESEARCH above.
    attacking = calculate_division_stats(
        ["mountaineers"] * 5, researched=_MOUNTAINEERS_ZERO_RESEARCH,
        terrain={"terrain_key": "mountain", "is_attacking": True},
    )
    defending = calculate_division_stats(
        ["mountaineers"] * 5, researched=_MOUNTAINEERS_ZERO_RESEARCH,
        terrain={"terrain_key": "mountain", "is_attacking": False},
    )
    assert attacking["soft_attack"] != defending["soft_attack"]
    assert attacking["soft_attack"] == pytest.approx(15.0 * 0.85)
    assert defending["soft_attack"] == pytest.approx(15.0 * 1.1)


# --- Technology unit_bonuses integration (Phase C, 2026-09-30; corrected
# 2026-10-08) ---
# Confirmed against real screenshots (Template Examples/) to follow TWO
# different rules from Doctrine's own unit_bonuses - see logic/stats.py's
# _tech_bonus_for_item block comment for the full reasoning and math.

def test_infantry_at_boosts_a_plain_infantry_division_as_a_percentage_multiplier():
    # CORRECTED 2026-10-08 - this test used to assert a "confirmed zero"
    # here, based on 5_infantry_guns_0.png vs
    # 5_infantry_guns_0_all_antiTank_research.png showing a byte-identical
    # Combat Stats panel. Re-examined after a real Marine-division screenshot
    # (ingame_7_marines_1_mountaineer_pioneerSupport.png) showed Hard Attack/
    # Piercing moving exactly as this multiplier predicts: that old "after"
    # screenshot's Soft Attack was ALSO byte-identical to "before" (15.0 both)
    # - impossible if infantry_at's own prerequisite chain
    # (improved_infantry_weapons, which unlocks a higher infantry_equipment
    # tier) had really been researched, since the tier change alone would
    # have moved Soft Attack. The original research state almost certainly
    # never actually included infantry_at/infantry_at2 in the real game (an
    # easy mix-up: "Infantry Anti-Tank I/II", an Infantry-branch tech, vs.
    # the regimental Anti-Tank Battery's own "Anti-Tank I-IV" line,
    # similarly named) - a mislabeled test, not a real negative result.
    researched = {"infantry_weapons"}
    with_infantry_at = researched | {"infantry_at", "infantry_at2"}
    before = calculate_division_stats(["infantry"] * 5, researched=researched)
    after = calculate_division_stats(["infantry"] * 5, researched=with_infantry_at)
    assert before["hard_attack"] == pytest.approx(2.5)
    # category_all_infantry hard_attack: 0.25 on EACH of infantry_at/
    # infantry_at2, summed to +50%, applied once: 2.5 * 1.5 = 3.75.
    assert after["hard_attack"] == pytest.approx(3.75)
    assert before["ap_attack"] == pytest.approx(1.0)
    # ap_attack: 1 (i.e. +100%) on EACH of infantry_at/infantry_at2, summed
    # to +200%, applied once: 1.0 * 3.0 = 3.0.
    assert after["ap_attack"] == pytest.approx(3.0)


def test_antitank1_bonus_reproduces_the_anti_tank_battery_screenshot_exactly():
    # 5_infantry_guns_0_1_antitankBattery.png (Anti-Tank/interwar_antitank
    # only, no category_anti_tank bonus yet) vs
    # 5_infantry_guns_0_1_antitankBattery_improvedAntitank.png (+ Improved
    # Anti-Tank/antitank1, category_anti_tank: {hard_attack: 0.1,
    # ap_attack: 0.2}): Hard Attack 9.5 -> 11.5 exactly, confirming the
    # bonus merges into the Anti-Tank Battery's own percentage BEFORE the
    # single equipment multiplication (20 x (1 - 0.65 + 0.1) = 9.0, +2.5
    # from Infantry = 11.5) rather than a separate multiplicative layer
    # (which would give 7.0 x 1.1 = 7.7, +2.5 = 10.2 - not what the real
    # screenshot shows).
    battalions = ["infantry"] * 5
    regimental_support = ["anti_tank_battery"]
    before_researched = {"infantry_weapons", "gw_artillery", "interwar_antitank"}
    after_researched = before_researched | {"antitank1"}

    before = calculate_division_stats(battalions, regimental_support=regimental_support, researched=before_researched)
    after = calculate_division_stats(battalions, regimental_support=regimental_support, researched=after_researched)

    assert before["hard_attack"] == pytest.approx(9.5)
    assert after["hard_attack"] == pytest.approx(11.5)


def test_logistics_company_supply_consumption_factor_matches_the_screenshots_exactly():
    # LogisticsCompany1.png: the logistics_company item's own
    # supply_consumption_factor (-0.10, data/battalion_stats.py) alone takes
    # a 5x Infantry division from 0.30 to 0.27 Supply Use
    # (5_infantry_guns_0_logisticsCompany_1.png). Researching Logistics
    # Company II's tech bonus (unit_bonuses: {"logistics_company":
    # {"supply_consumption_factor": -0.1}}) on top takes it to 0.24
    # (5_infantry_guns_0_logisticsCompany_2.png) - 0.30 x (1 - 0.10 - 0.10)
    # = 0.24 exactly, confirming the bonus SUMS into the same division-level
    # multiplier as the item's own factor and as suppression_factor already
    # does, rather than compounding (0.30 x 0.9 x 0.9 = 0.243, which would
    # also round to 0.24 - the exact-match assertion here is what
    # distinguishes the two).
    battalions = ["infantry"] * 5
    support = ["logistics_company"]
    logico1 = {"infantry_weapons", "tech_support", "tech_logistics_company"}
    logico2 = logico1 | {"tech_logistics_company2"}

    no_logistics = calculate_division_stats(battalions, researched={"infantry_weapons"})
    with_logico1 = calculate_division_stats(battalions, support_companies=support, researched=logico1)
    with_logico2 = calculate_division_stats(battalions, support_companies=support, researched=logico2)

    assert no_logistics["supply_consumption"] == pytest.approx(0.30)
    assert with_logico1["supply_consumption"] == pytest.approx(0.27)
    assert with_logico2["supply_consumption"] == pytest.approx(0.24)


def test_tech_bonus_none_matches_omitting_researched():
    # researched=None is calculate_item_stats' true "no research state"
    # default (fixed _1 tier, no equipment-tier resolution, no tech
    # bonuses) - distinct from researched=set() (a real, empty research
    # state, which DOES resolve equipment tiers and DOES query tech bonuses,
    # just finds none active).
    assert calculate_item_stats("anti_tank_battery", is_support_type=True) == calculate_item_stats(
        "anti_tank_battery", is_support_type=True, researched=None
    )


# --- Special Project unit_bonuses (added 2026-10-07 - see
# data/special_projects.py's header and
# Special_Projects_Screenshots/large_caliber_sabot_1.PNG/_2.PNG) ---

def test_completed_special_project_bonus_none_matches_omitting_the_parameter():
    # Mirrors test_tech_bonus_none_matches_omitting_researched: omitting
    # completed_special_projects entirely must stay byte-identical to never
    # having added this parameter at all.
    assert calculate_item_stats("field_guns", is_support_type=True) == calculate_item_stats(
        "field_guns", is_support_type=True, completed_special_projects=None
    )


def test_large_caliber_kinetic_energy_sabot_bumps_field_guns_piercing_by_ten_percent():
    # field_guns has no own ap_attack field at all (data/battalion_stats.py)
    # - the project's +0.1 bonus is the item's entire "own%" contribution,
    # so the equipment's resolved Piercing should move by exactly x1.1
    # (equipment_total * (1 + 0 vs 1 + 0.1)), the same
    # equipment-multiplication-before rule Technology's own bonuses already
    # follow (see _tech_bonus_for_item's block comment in logic/stats.py).
    before = calculate_item_stats("field_guns", is_support_type=True, researched=set())
    after = calculate_item_stats(
        "field_guns", is_support_type=True, researched=set(),
        completed_special_projects={"sp_land_large_caliber_kinetic_energy_sabot"},
    )
    assert before["ap_attack"] > 0
    assert after["ap_attack"] == pytest.approx(before["ap_attack"] * 1.1)


def test_marines_2_doctrine_grants_pioneer_support_a_real_amphibious_bonus():
    # Reproduces Ollie's own real-world report (2026-10-07): claimed
    # "Marines: Amphibious Expeditionary" (data/doctrines.py's marines_2),
    # picked Pioneer Support, selected Amphibious Assault terrain, and saw
    # no bonus at all. Confirmed correct per HOI4 but previously unapplied
    # by this app: Pioneer Support has no own per-unit amphibious entry at
    # all (data/terrain.py), but marines_2's own immediate effect grants it
    # a real +15% Attack/Defence bonus specifically in Amphibious terrain -
    # see logic/terrain.py's _doctrine_terrain_percentage.
    doctrine_state = {
        "active_grand_doctrines": set(),
        "track_subdoctrines": {"special_forces_first": "marines_2"},
        "claimed_rewards": {},
    }
    terrain = {"terrain_key": "amphibious", "is_attacking": True}

    baseline = calculate_item_stats("pioneer_support", is_support_type=True)
    terrain_only = calculate_item_stats("pioneer_support", is_support_type=True, terrain=terrain)
    terrain_and_doctrine = calculate_item_stats(
        "pioneer_support", is_support_type=True, doctrine=doctrine_state, terrain=terrain
    )

    assert baseline["soft_attack"] > 0

    # The originally-reported symptom: terrain alone changes nothing, since
    # Pioneer Support's own per-unit terrain data has no "amphibious" entry.
    assert terrain_only["soft_attack"] == baseline["soft_attack"]
    assert terrain_only["breakthrough"] == baseline["breakthrough"]

    # The fix: marines_2's own terrain-nested bonus now applies, on the
    # attack-side fields only (is_attacking=True).
    assert terrain_and_doctrine["soft_attack"] == pytest.approx(baseline["soft_attack"] * 1.15)
    assert terrain_and_doctrine["breakthrough"] == pytest.approx(baseline["breakthrough"] * 1.15)


def test_large_caliber_kinetic_energy_sabot_boosts_artillery_brigade_as_a_percentage_multiplier():
    # CORRECTED 2026-10-08, same correction as infantry_at above -
    # artillery_brigade is a BATTALION, and the sabot's ap_attack bonus now
    # correctly applies as a multiplicative layer on its own+equipment total.
    before = calculate_division_stats(["artillery_brigade"] * 5, researched=set())
    after = calculate_division_stats(
        ["artillery_brigade"] * 5, researched=set(),
        completed_special_projects={"sp_land_large_caliber_kinetic_energy_sabot"},
    )
    assert before["ap_attack"] == pytest.approx(5.0)
    # ap_attack: 0.15 on artillery_brigade directly - 5.0 * 1.15 = 5.75.
    assert after["ap_attack"] == pytest.approx(5.75)


# --- Battalion own-breakthrough-field is a percentage, not a flat add
# (corrected 2026-10-08) ---
#
# Resolves a dormant lead from 2026-09-29 (tests/test_division_stats.py's
# "Mountaineers breakthrough anomaly") and today's own Marine/Special-Forces
# investigation (Template Examples/*_fulltech_elite_expeditionary.png -
# Infantry/Marine/Mountaineer/Ranger/Paratrooper, all under the identical
# real research+doctrine state) at once: a battalion's own "breakthrough"
# field (data/battalion_stats.py - Marine/Mountaineer/Ranger's own 0.3,
# every Armor battalion's own 0.15/-0.25/-0.42/etc.) is a PERCENTAGE of its
# equipment's own breakthrough, not a flat add like every other battalion
# field. No hidden per-unit multiplier needed - the percentage-vs-flat
# distinction alone explains why Infantry/Paratrooper (no own breakthrough
# field) matched the old flat-add formula exactly while Marine/Mountaineer/
# Ranger (own field 0.3) didn't.

def test_mountaineers_breakthrough_matches_the_real_screenshot_with_zero_ambiguity():
    # The 2026-09-29 data point: 5x Mountaineers, "infantry_weapons" only
    # researched (tier 0 equipment, breakthrough=2), NO doctrine at all -
    # real Breakthrough 13.0. 5 x (2 x (1 + 0.3)) = 13.0 exactly, no
    # rounding ambiguity whatsoever (unlike every other data point today,
    # which all involve a doctrine milestone and HOI4's own tooltip
    # rounding/truncation).
    stats = calculate_division_stats(["mountaineers"] * 5, researched={"infantry_weapons"})
    assert stats["breakthrough"] == pytest.approx(13.0)


def test_infantry_and_paratrooper_have_no_own_breakthrough_field_so_are_unaffected():
    # Confirms the fix is a true no-op for any battalion without its own
    # breakthrough field - infantry_equipment_3's breakthrough (5) passes
    # through unchanged, matching data/terrain.py's own long-standing
    # Infantry baseline and today's real infantry_fulltech screenshot (5.0)
    # and paratrooper_fulltech screenshot (5.2, from the 5% doctrine
    # milestone alone: 5 * 1.05 = 5.25).
    infantry = calculate_item_stats("infantry", researched={"advanced_infantry_weapons"})
    assert infantry["breakthrough"] == pytest.approx(5.0)


def test_medium_armor_own_breakthrough_is_a_percentage_of_default_equipment():
    # light_armor/medium_armor/etc.'s own breakthrough (0.15) is the exact
    # same real value already compiled separately in
    # data/tank_role_combat_modifiers.py for Tank Designer's own custom-
    # design calculation - this confirms plain Composition (default,
    # non-custom equipment) now applies it the same way.
    stats = calculate_item_stats("medium_armor")
    equipment_breakthrough = stats["breakthrough"] / 1.15
    assert stats["breakthrough"] == pytest.approx(equipment_breakthrough * 1.15)


def test_medium_armor_own_breakthrough_stays_flat_when_using_a_custom_tank_design():
    # Scoped out deliberately (see _BATTALION_OWN_PERCENTAGE_FIELDS' own
    # block comment in logic/stats.py) - a custom Tank Designer design's own
    # calculation already bakes in the hidden role-combat multiplier for
    # whichever equipment family it replaces, so applying medium_armor's own
    # breakthrough as a SECOND percentage on top would double-count an
    # effect with no screenshot evidence either way. Preserves the exact,
    # already-tested behaviour from Tank Designer Phase 6
    # (tests/test_stats.py's test_a_custom_design_replaces_the_equipment_family_it_was_built_for).
    tank_designs = {
        "medium_tank_chassis": {
            "chassis_key": "medium_tank_chassis", "tier": 1,
            "chosen_modules": _MEDIUM_TANK_DEFAULT_MODULES,
        }
    }
    stats = calculate_item_stats("medium_armor", tank_designs=tank_designs)
    assert stats["breakthrough"] == pytest.approx(0.15 + 11.5)


# --- battalion_mult: cross-unit auras (added 2026-10-08) ---
#
# A real, previously-out-of-scope mechanic (see data/battalion_stats.py's
# own header and Specification.md's "modifier interaction engine" decisions
# log) - a unit's own innate aura (data/battalion_stats.py), or one nested
# inside a Doctrine/Technology unit_bonuses entry (data/doctrines.py,
# data/technologies.py - already compiled, previously always ignored),
# granting a bonus to every OTHER item in the division belonging to a given
# category. Found and confirmed via the same Marine-division investigation
# as the breakthrough-percentage fix above (Pioneer Support's own
# category_marines Breakthrough aura was the final missing piece), then
# verified completely independently via Cavalry Recon's own long-documented
# category_artillery aura (tests/test_division_stats.py's own
# test_seven_infantry_two_artillery_with_support_companies - real screenshot
# soft_attack 117.1, now matched EXACTLY).

def test_cavalry_recon_aura_reproduces_the_real_screenshot_exactly():
    # The clearest possible confirmation: an independent, pre-existing real
    # screenshot value (Activity_Log.md, 2026-09-14) this project had
    # deliberately left unreconciled for three weeks.
    stats = calculate_division_stats(
        battalions=["infantry"] * 7 + ["artillery_brigade"] * 2,
        support_companies=["engineer", "artillery", "recon"],
    )
    assert stats["soft_attack"] == pytest.approx(117.1)


def test_battalion_mult_aura_requires_the_granting_item_to_actually_be_present():
    # Cavalry Recon's own aura (category_artillery, soft_attack +10%) only
    # applies when Recon itself is in the division - 2 Artillery battalions
    # alone, no Recon, get no boost at all.
    with_recon = calculate_division_stats(
        ["artillery_brigade"] * 2, support_companies=["engineer", "artillery", "recon"]
    )
    without_recon = calculate_division_stats(
        ["artillery_brigade"] * 2, support_companies=["engineer", "artillery"]
    )
    recon_alone_contribution = calculate_item_stats("recon", is_support_type=True)["soft_attack"]
    assert with_recon["soft_attack"] - without_recon["soft_attack"] != pytest.approx(recon_alone_contribution)
    # The difference is strictly MORE than Recon's own flat contribution,
    # confirming the extra amount is the +10% aura on the two Artillery
    # battalions, not just Recon's own stats being added.
    assert with_recon["soft_attack"] - without_recon["soft_attack"] > recon_alone_contribution


def test_battalion_mult_applies_to_the_granting_item_itself_when_it_matches_its_own_category():
    # armored_engineer's own aura (category_all_armor, breakthrough +0.05,
    # flat - "add": True) targets a category armored_engineer itself
    # belongs to (confirmed via data/unit_categories.py) - HOI4's real aura
    # convention is self-inclusion, not exclusion, and this app's
    # implementation matches: armored_engineer should receive its own bonus
    # too, not just grant it to others.
    infantry_breakthrough = calculate_item_stats("infantry")["breakthrough"]
    stats = calculate_division_stats(["infantry"], support_companies=["armored_engineer"])
    armored_engineer_contribution = stats["breakthrough"] - infantry_breakthrough
    armored_engineer_alone = calculate_item_stats("armored_engineer", is_support_type=True)["breakthrough"]
    assert armored_engineer_contribution == pytest.approx(armored_engineer_alone + 0.05)


def test_doctrine_battalion_mult_requires_both_the_bonus_active_and_its_target_present():
    # marines_1's reward_5 grants Pioneer Support a battalion_mult
    # (category_amphibious_tanks: armor +15%, breakthrough +15%) - real,
    # compiled doctrine data, previously always ignored. Requires BOTH the
    # reward claimed AND Pioneer Support actually present in the division -
    # not just the reward being claimed in the abstract.
    doctrine = {
        "active_grand_doctrines": set(),
        "track_subdoctrines": {"special_forces_first": "marines_1"},
        "claimed_rewards": {"marines_1": 5},
    }
    baseline = calculate_item_stats("amphibious_armor")["armor_value"]

    without_pioneer = calculate_division_stats(["amphibious_armor"], doctrine=doctrine)
    assert without_pioneer["armor_value"] == pytest.approx(baseline)

    with_pioneer = calculate_division_stats(
        ["amphibious_armor"], support_companies=["pioneer_support"], doctrine=doctrine
    )
    # armor_value is a DIVISION_MAX_AND_AVERAGE_FIELDS field (0.4 x highest
    # + 0.6 x average, same formula as Piercing), not a plain sum -
    # amphibious_armor's own value boosted by +15% (23.0) and Pioneer
    # Support's own 0 (not a tank): 0.4 x 23.0 + 0.6 x (23.0 + 0) / 2 = 16.1.
    boosted_amphibious = baseline * 1.15
    expected = 0.4 * boosted_amphibious + 0.6 * (boosted_amphibious / 2)
    assert with_pioneer["armor_value"] == pytest.approx(expected)


def test_battalion_mult_is_a_true_no_op_when_no_aura_source_is_present():
    # A plain 5x Infantry division (no aura-granting unit anywhere) must be
    # byte-identical to before this feature existed.
    stats = calculate_division_stats(["infantry"] * 5)
    assert stats["soft_attack"] == pytest.approx(5 * calculate_item_stats("infantry")["soft_attack"])


# --- Officer Corps: Operational Reserves' army_strength_factor (added
# 2026-11-02) - the one Army Spirit bonus confirmed directly in-game
# ("HP: +10.00%") rather than guessed, unlike the other 8 compiled entries
# which stay unapplied. A country-wide bonus, not a per-item one - applied
# once at the division level (see logic/army_spirits.py's
# active_army_strength_factor and calculate_division_stats' own max_strength
# calculation), not inside calculate_item_stats.

def test_operational_reserves_boosts_division_max_strength_by_ten_percent():
    baseline = calculate_division_stats(["infantry"] * 5)
    boosted = calculate_division_stats(["infantry"] * 5, army_spirits=["operational_reserve_spirit"])
    assert boosted["max_strength"] == pytest.approx(baseline["max_strength"] * 1.1)


def test_army_strength_factor_is_a_true_no_op_when_no_spirit_is_active():
    # Omitting army_spirits (None, the default) and passing an empty list
    # must both be byte-identical to before this feature existed.
    stats = calculate_division_stats(["infantry"] * 5)
    stats_empty = calculate_division_stats(["infantry"] * 5, army_spirits=[])
    assert stats["max_strength"] == stats_empty["max_strength"]
    assert stats["max_strength"] == pytest.approx(5 * calculate_item_stats("infantry")["max_strength"])


def test_army_strength_factor_does_not_affect_an_unrelated_spirit():
    # subsidized_contracts_army_spirit has no army_strength_factor of its
    # own - being active must not change max_strength at all.
    baseline = calculate_division_stats(["infantry"] * 5)
    other = calculate_division_stats(["infantry"] * 5, army_spirits=["subsidized_contracts_army_spirit"])
    assert other["max_strength"] == baseline["max_strength"]


# --- The remaining 8 Officer Corps formula items, confirmed via real
# in-game tooltips (Ollie's own screenshots, 2026-11-03) and applied the
# same day - all percentages, matching Operational Reserves' own
# precedent. 4 are country-wide (applied once at calculate_division_stats'
# own level, same army_strength_factor pattern); 4 are equipment_bonus
# entries targeting an equipment FAMILY directly (applied inside
# calculate_item_stats, per equipment key, before combination with an
# item's own stats - a structurally different application point from
# unit_bonuses' item/category matching).

def test_all_arms_at_defense_boosts_infantry_equipment_hard_attack():
    # Real tooltip: "Infantry Equipment: Hard Attack: +25%". Infantry has
    # no own hard_attack field at all, so its whole hard_attack comes from
    # infantry_equipment (baseline 1) - boosted stat must be exactly 1.25.
    baseline = calculate_item_stats("infantry")
    boosted = calculate_item_stats("infantry", army_spirits=["all_arms_at_defense_army_spirit"])
    assert baseline["hard_attack"] == 1
    assert boosted["hard_attack"] == pytest.approx(1.25)


def test_direct_fire_support_boosts_tank_artillery_chassis_hard_attack_and_piercing():
    # Real tooltip (all 4 SP Artillery sizes): "Hard Attack: +50%",
    # "Piercing: +100%". light_sp_artillery_brigade needs
    # light_tank_artillery_chassis.
    baseline = calculate_item_stats("light_sp_artillery_brigade")
    boosted = calculate_item_stats("light_sp_artillery_brigade", army_spirits=["direct_fire_support_army_spirit"])
    assert boosted["hard_attack"] == pytest.approx(baseline["hard_attack"] * 1.5)
    assert boosted["ap_attack"] == pytest.approx(baseline["ap_attack"] * 2)


def test_rapid_emplacement_boosts_artillery_equipment_breakthrough_and_defense():
    # Real tooltip: "Towed Artillery: Breakthrough: +10%, Defense: +10%".
    # artillery_brigade has no own breakthrough/defense field, so both come
    # entirely from artillery_equipment.
    baseline = calculate_item_stats("artillery_brigade")
    boosted = calculate_item_stats("artillery_brigade", army_spirits=["rapid_emplacement_army_spirit"])
    assert boosted["breakthrough"] == pytest.approx(baseline["breakthrough"] * 1.1)
    assert boosted["defense"] == pytest.approx(baseline["defense"] * 1.1)


def test_subsidized_contracts_reduces_armored_car_equipment_production_cost():
    # Real tooltip: "Armored Car: Production Cost: -15.00%".
    baseline = calculate_item_stats("armored_car")
    boosted = calculate_item_stats("armored_car", army_spirits=["subsidized_contracts_army_spirit"])
    assert boosted["production_cost"] == pytest.approx(baseline["production_cost"] * 0.85)


def test_equipment_bonus_does_not_affect_an_item_that_doesnt_use_that_equipment():
    # all_arms_at_defense_army_spirit only targets infantry_equipment -
    # artillery_brigade (artillery_equipment) must be completely unaffected.
    baseline = calculate_item_stats("artillery_brigade")
    other = calculate_item_stats("artillery_brigade", army_spirits=["all_arms_at_defense_army_spirit"])
    assert other == baseline


def test_breakthrough_factor_applies_once_at_the_division_level():
    # Real tooltip (Smoke and Fire): "Breakthrough: +6.00%".
    baseline = calculate_division_stats(["artillery_brigade"] * 2)
    boosted = calculate_division_stats(["artillery_brigade"] * 2, army_spirits=["smoke_and_fire_spirit"])
    assert boosted["breakthrough"] == pytest.approx(baseline["breakthrough"] * 1.06)


def test_supply_consumption_factor_combines_into_the_existing_division_multiplier():
    # Real tooltip (Logistical Focus): "Supply Consumption: -10.0%" -
    # a country-wide contribution into the SAME multiplier Technology's own
    # per-item supply_consumption_factor bonuses already feed, not a
    # second separate layer.
    baseline = calculate_division_stats(["infantry"] * 5)
    boosted = calculate_division_stats(["infantry"] * 5, army_spirits=["logistical_focus_spirit"])
    assert boosted["supply_consumption"] == pytest.approx(baseline["supply_consumption"] * 0.9)


def test_army_speed_factor_multiplies_the_divisions_bottleneck_speed():
    # Real tooltip (Flexible Organization / Maneuver Warfare, identical):
    # "Divisions speed: +5.00%".
    baseline = calculate_division_stats(["infantry"] * 5)
    boosted = calculate_division_stats(["infantry"] * 5, army_spirits=["maneuver_warfare_spirit"])
    assert boosted["max_speed"] == pytest.approx(baseline["max_speed"] * 1.05)


def test_officer_corps_formulas_are_a_true_no_op_when_omitted():
    # Omitting army_spirits (None) and an empty list must both stay
    # byte-identical to before any of these 8 formulas existed.
    stats = calculate_item_stats("infantry")
    stats_empty = calculate_item_stats("infantry", army_spirits=[])
    assert stats == stats_empty

    division = calculate_division_stats(["infantry"] * 5)
    division_empty = calculate_division_stats(["infantry"] * 5, army_spirits=[])
    assert division == division_empty


# --- Patch Impact Preview: equipment_overrides/battalion_overrides (added
# 2026-11-03, see data/patches.py) - a staged, hypothetical data change
# previewed without touching the real data/*.py files. Both are ABSOLUTE
# replacement values (the patch's own "changed to" number), applied on
# top of whichever branch (tank_designs/researched tier/raw baseline)
# would otherwise have resolved.

def test_equipment_overrides_replaces_a_resolved_field():
    # Infantry's own soft_attack comes entirely from infantry_equipment -
    # overriding that family's soft_attack must change Infantry's own
    # resolved soft_attack to exactly the override value.
    stats = calculate_item_stats(
        "infantry", equipment_overrides={"infantry_equipment": {"soft_attack": 999}},
    )
    assert stats["soft_attack"] == 999


def test_equipment_overrides_leaves_unmentioned_fields_at_their_real_value():
    stats = calculate_item_stats(
        "infantry", equipment_overrides={"infantry_equipment": {"soft_attack": 999}},
    )
    baseline = calculate_item_stats("infantry")
    assert stats["hard_attack"] == baseline["hard_attack"]
    assert stats["defense"] == baseline["defense"]
    assert stats["production_cost"] == baseline["production_cost"]


def test_equipment_overrides_wins_over_a_researched_tier():
    # improved_infantry_weapons unlocks infantry_equipment_2 (soft_attack
    # 9, tier-resolved) - an override targeting the same field must still
    # win over that tier resolution, not just the "_1" baseline.
    tier_only = calculate_item_stats("infantry", researched={"improved_infantry_weapons"})
    assert tier_only["soft_attack"] == 9

    overridden = calculate_item_stats(
        "infantry", researched={"improved_infantry_weapons"},
        equipment_overrides={"infantry_equipment": {"soft_attack": 999}},
    )
    assert overridden["soft_attack"] == 999


def test_battalion_overrides_replaces_an_own_stat_field():
    baseline = calculate_item_stats("infantry")
    assert baseline["max_strength"] == 25

    overridden = calculate_item_stats("infantry", battalion_overrides={"infantry": {"max_strength": 999}})
    assert overridden["max_strength"] == 999
    # Everything else (equipment-derived) stays untouched.
    assert overridden["soft_attack"] == baseline["soft_attack"]


def test_omitting_equipment_and_battalion_overrides_is_byte_identical_to_before():
    baseline = calculate_item_stats("infantry")
    explicit_none = calculate_item_stats("infantry", equipment_overrides=None, battalion_overrides=None)
    assert baseline == explicit_none

    division_baseline = calculate_division_stats(["infantry"] * 5)
    division_explicit_none = calculate_division_stats(
        ["infantry"] * 5, equipment_overrides=None, battalion_overrides=None,
    )
    assert division_baseline == division_explicit_none


def test_calculate_division_stats_threads_overrides_to_every_item():
    boosted = calculate_division_stats(
        ["infantry"] * 3, support_companies=["signal_company"],
        equipment_overrides={"infantry_equipment": {"soft_attack": 999}},
    )
    # Infantry's soft_attack is a plain sum across battalions - 3 x 999.
    assert boosted["soft_attack"] == pytest.approx(3 * 999)

    other = calculate_division_stats(["infantry"] * 3, battalion_overrides={"infantry": {"max_strength": 999}})
    assert other["max_strength"] == pytest.approx(3 * 999)
