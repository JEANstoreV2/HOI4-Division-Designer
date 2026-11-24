import pytest

from data.tank_chassis import TANK_CHASSIS
from data.tank_modules import TANK_MODULES
from logic.tank_designer import (
    build_candidate_design,
    calculate_tank_design_stats,
    effective_module_slots,
    equipment_type_tags,
    is_design_legal,
    max_tick_level,
    validate_design,
)

MODULES_BY_KEY = {m["key"]: m for m in TANK_MODULES}


def _medium_defaults():
    # Basic Medium Tank (medium_tank_chassis_1) at its default loadout -
    # the exact chassis/tier every tank_designer_examples/ screenshot uses.
    return {
        "turret_type_slot": "tank_medium_one_man_tank_turret",
        "suspension_type_slot": "tank_bogie_suspension",
        "armor_type_slot": "tank_riveted_armor",
        "engine_type_slot": "tank_gasoline_engine",
    }


def _base_light_tank_modules():
    # A minimal legal light_tank_chassis loadout: every default module plus
    # an explicit main armament (whose default is always None - see
    # data/tank_chassis.py's header).
    return {
        "turret_type_slot": "tank_light_one_man_tank_turret",
        "main_armament_slot": "tank_heavy_machine_gun",
        "suspension_type_slot": "tank_bogie_suspension",
        "armor_type_slot": "tank_riveted_armor",
        "engine_type_slot": "tank_gasoline_engine",
    }


def test_equipment_type_tags_role_adds_to_armor_not_replaces_it():
    assert equipment_type_tags() == {"armor"}
    assert equipment_type_tags("light_tank_amphibious_chassis") == {"armor", "amphibious"}
    assert equipment_type_tags("light_tank_destroyer_chassis") == {"armor", "anti_tank"}


def test_baseline_light_tank_design_is_legal():
    assert is_design_legal("light_tank_chassis", _base_light_tank_modules())


def test_missing_required_slot_is_illegal():
    modules = _base_light_tank_modules()
    del modules["engine_type_slot"]
    violations = validate_design("light_tank_chassis", modules)
    assert {"type": "missing_required_module", "slot": "engine_type_slot"} in violations


def test_unknown_module_key_is_illegal():
    modules = _base_light_tank_modules()
    modules["main_armament_slot"] = "not_a_real_module"
    violations = validate_design("light_tank_chassis", modules)
    assert violations == [{"type": "unknown_module", "slot": "main_armament_slot", "module": "not_a_real_module"}]


def test_wrong_category_module_in_a_slot_is_illegal():
    modules = _base_light_tank_modules()
    # A suspension module has no business in the main armament slot.
    modules["main_armament_slot"] = "tank_torsion_bar_suspension"
    violations = validate_design("light_tank_chassis", modules)
    assert any(v["type"] == "invalid_category" and v["slot"] == "main_armament_slot" for v in violations)


def test_two_radio_modules_exceeds_the_category_count_limit():
    modules = _base_light_tank_modules()
    modules["special_type_slot_1"] = "tank_radio_1"
    modules["special_type_slot_2"] = "tank_radio_2"
    violations = validate_design("light_tank_chassis", modules)
    assert violations == [
        {"type": "count_limit_exceeded", "limit": "tank_radio_module", "count": 2, "max_count": 1}
    ]


def test_duplicate_named_module_exceeds_its_count_limit():
    modules = _base_light_tank_modules()
    modules["special_type_slot_1"] = "wet_ammo_storage"
    modules["special_type_slot_2"] = "wet_ammo_storage"
    violations = validate_design("light_tank_chassis", modules)
    assert violations == [
        {"type": "count_limit_exceeded", "limit": "wet_ammo_storage", "count": 2, "max_count": 1}
    ]


def test_amphibious_drive_requires_the_amphibious_role():
    modules = _base_light_tank_modules()
    modules["special_type_slot_1"] = "amphibious_drive"

    plain_violations = validate_design("light_tank_chassis", modules, role_key=None)
    assert any(v["type"] == "requires_equipment_type" for v in plain_violations)
    assert any(v["type"] == "forbidden_for_exact_equipment_type" for v in plain_violations)

    amphibious_violations = validate_design(
        "light_tank_chassis", modules, role_key="light_tank_amphibious_chassis"
    )
    assert amphibious_violations == []


def test_anti_air_cannon_requires_the_anti_air_role():
    modules = _base_light_tank_modules()
    modules["main_armament_slot"] = "tank_anti_air_cannon"

    plain_violations = validate_design("light_tank_chassis", modules, role_key=None)
    assert any(v["type"] == "requires_equipment_type" for v in plain_violations)
    assert any(v["type"] == "forbidden_for_exact_equipment_type" for v in plain_violations)

    aa_violations = validate_design("light_tank_chassis", modules, role_key="light_tank_aa_chassis")
    assert aa_violations == []


def test_fixed_superstructure_turret_widens_main_armament_category():
    modules = _base_light_tank_modules()
    modules["turret_type_slot"] = "tank_light_fixed_superstructure_turret"
    modules["main_armament_slot"] = "tank_medium_cannon"

    # Without the wider turret, tank_medium_cannon's category never fits
    # light_tank_chassis's own main_armament_slot at all.
    default_turret_violations = validate_design(
        "light_tank_chassis", _base_light_tank_modules() | {"main_armament_slot": "tank_medium_cannon"},
        role_key="light_tank_destroyer_chassis",
    )
    assert any(v["type"] == "invalid_category" for v in default_turret_violations)

    # On a plain (role-less) design, the category becomes legal via the
    # turret's override, but tank_medium_cannon's own allow_equipment_type
    # AND the turret's forbid_equipment_type_exact_match_for_category both
    # still bar it - a fixed superstructure is a Tank Destroyer trick, not a
    # free upgrade for a plain tank.
    plain_violations = validate_design("light_tank_chassis", modules, role_key=None)
    assert not any(v["type"] == "invalid_category" for v in plain_violations)
    assert any(v["type"] == "requires_equipment_type" for v in plain_violations)
    assert any(v["type"] == "category_forbidden_for_exact_equipment_type" for v in plain_violations)

    # Assigned to the Tank Destroyer (anti_tank) role, every rule is
    # satisfied - a real, legal design.
    destroyer_violations = validate_design(
        "light_tank_chassis", modules, role_key="light_tank_destroyer_chassis"
    )
    assert destroyer_violations == []


def test_effective_module_slots_only_widens_the_targeted_slot():
    base = effective_module_slots("light_tank_chassis", {})
    widened = effective_module_slots(
        "light_tank_chassis", {"turret_type_slot": "tank_light_fixed_superstructure_turret"}
    )
    # A union, not a replace (see effective_module_slots's own docstring) -
    # the turret's own bigger gun category is ADDED to the chassis's base
    # main_armament_slot categories, not swapped in for them.
    assert set(widened["main_armament_slot"]) == {*base["main_armament_slot"], "tank_medium_main_armament"}
    assert widened["turret_type_slot"] == base["turret_type_slot"]
    assert widened["engine_type_slot"] == base["engine_type_slot"]


def test_flame_role_locks_main_armament_to_flamethrowers_only():
    # Ollie reported a real bug: after the union fix above, a Flame Tank
    # could also mount an ordinary cannon, which isn't accurate - real
    # Flame Tanks can ONLY use the flamethrower category, a hidden
    # role-level restriction absent from x_tank_chassis.txt's own flame
    # duplicate_archetypes block (see effective_module_slots's docstring).
    plain = effective_module_slots(
        "medium_tank_chassis", {"turret_type_slot": "tank_medium_one_man_tank_turret"}
    )
    flame = effective_module_slots(
        "medium_tank_chassis", {"turret_type_slot": "tank_medium_one_man_tank_turret"},
        role_key="medium_tank_flame_chassis",
    )
    assert "tank_medium_main_armament" in plain["main_armament_slot"]
    assert flame["main_armament_slot"] == ["tank_flamethrower"]

    modules = _medium_defaults() | {
        "turret_type_slot": "tank_medium_one_man_tank_turret",
        "main_armament_slot": "tank_small_cannon",
    }
    violations = validate_design("medium_tank_chassis", modules, role_key="medium_tank_flame_chassis")
    assert any(v["type"] == "invalid_category" for v in violations)

    legal_modules = modules | {"main_armament_slot": "flamethrower"}
    assert is_design_legal("medium_tank_chassis", legal_modules, role_key="medium_tank_flame_chassis")


def test_every_chassis_default_module_fits_its_own_slot_category():
    # A cross-check tying Phase 1 (chassis/slots) and Phase 2 (modules)
    # together: every non-empty default module a chassis ships with must
    # satisfy its own slot's base category list. land_cruiser_chassis has no
    # real defaults at all (commented out in the source) and is skipped, per
    # data/tank_chassis.py's own header note.
    for chassis in TANK_CHASSIS:
        if chassis["key"] == "land_cruiser_chassis":
            continue
        effective = effective_module_slots(chassis["key"], chassis["default_modules"])
        for slot_name, module_key in chassis["default_modules"].items():
            if module_key is None:
                continue
            module = MODULES_BY_KEY[module_key]
            assert module["category"] in effective[slot_name], (chassis["key"], slot_name)


def test_module_count_limits_of_zero_make_an_otherwise_legal_module_illegal():
    # modern_tank_chassis caps amphibious_drive at 0 - even though it has no
    # amphibious role at all (so allow_equipment_type would already block it
    # too), the count limit itself must independently flag it.
    modules = {
        "turret_type_slot": "tank_modern_tank_turret",
        "main_armament_slot": "tank_heavy_machine_gun",
        "suspension_type_slot": "tank_bogie_suspension",
        "armor_type_slot": "tank_riveted_armor",
        "engine_type_slot": "tank_gasoline_engine",
        "special_type_slot_1": "amphibious_drive",
    }
    violations = validate_design("modern_tank_chassis", modules)
    assert any(
        v["type"] == "count_limit_exceeded" and v["limit"] == "amphibious_drive" and v["max_count"] == 0
        for v in violations
    )


# --- calculate_tank_design_stats: every case below is a real screenshot in
# tank_designer_examples/ (gitignored, Ollie's own gameplay - see
# Activity_Log.md 2026-09-16), not an invented number. Values are compared
# with pytest.approx since HOI4 truncates its own display to 1 decimal
# (e.g. 4.75 shows as "4.7") while this function returns full precision.

def test_stats_baseline_no_edits():
    # medBasicChassis_noEdits.png
    stats = calculate_tank_design_stats("medium_tank_chassis", 1, _medium_defaults())
    assert stats["maximum_speed"] == pytest.approx(6.325)
    assert stats["reliability"] == pytest.approx(0.8)
    assert stats["armor_value"] == pytest.approx(30.0)
    assert stats["hardness"] == pytest.approx(0.85)
    assert stats["breakthrough"] == pytest.approx(11.5)
    assert stats["defense"] == pytest.approx(2.0)
    assert stats["soft_attack"] == pytest.approx(0.0)
    assert stats["max_strength"] == pytest.approx(3.2)  # (1.19.4) 2.0 + 1.5 x 0.8


def test_stats_high_velocity_cannon():
    # medBasicChassis_basicHighVelocityCannon.png (pre-1.19.4). soft_attack/
    # hard_attack both gained +5% under 1.19.4's new tier module-additive
    # multiplier (medium tank tier 1 = "Improved", +5% on modules' own
    # soft/hard/air_attack contributions - see data/tank_chassis.py).
    modules = _medium_defaults() | {"main_armament_slot": "tank_high_velocity_cannon"}
    stats = calculate_tank_design_stats("medium_tank_chassis", 1, modules)
    assert stats["soft_attack"] == pytest.approx(9.975)  # (1.19.4) 9.5->9.975
    assert stats["hard_attack"] == pytest.approx(25.935)  # (1.19.4) 24.7->25.935
    assert stats["ap_attack"] == pytest.approx(68.0)
    assert stats["maximum_speed"] == pytest.approx(6.21)
    assert stats["reliability"] == pytest.approx(0.75)
    assert stats["breakthrough"] == pytest.approx(11.5)


def test_stats_welded_armor():
    # medBasicChassis_weldedArmor.png
    modules = _medium_defaults() | {"armor_type_slot": "tank_welded_armor"}
    stats = calculate_tank_design_stats("medium_tank_chassis", 1, modules)
    assert stats["armor_value"] == pytest.approx(39.0)
    assert stats["breakthrough"] == pytest.approx(13.8)
    assert stats["defense"] == pytest.approx(4.0)


def test_stats_welded_and_sloped_armor():
    # medBasicChassis_weldedArmor_slopedArmor.png - proves module
    # percentages on the same field SUM (30 x 1.55 = 46.5), not compound
    # (30 x 1.3 x 1.25 = 48.75).
    modules = _medium_defaults() | {
        "armor_type_slot": "tank_welded_armor",
        "special_type_slot_1": "sloped_armor",
    }
    stats = calculate_tank_design_stats("medium_tank_chassis", 1, modules)
    assert stats["armor_value"] == pytest.approx(46.5)
    assert stats["breakthrough"] == pytest.approx(13.8)
    assert stats["defense"] == pytest.approx(4.0)


def test_stats_nine_armor_ticks():
    # medBasicChassis_nineArmorTicks.png - proves a tick's own reliability
    # is a percentage multiplier (0.8 x (1 - 9x0.015) = 0.692), not a flat
    # addition (which would give 0.665).
    stats = calculate_tank_design_stats(
        "medium_tank_chassis", 1, _medium_defaults(),
        tick_levels={"tank_nsb_armor_upgrade": 9},
    )
    assert stats["armor_value"] == pytest.approx(52.5)
    assert stats["reliability"] == pytest.approx(0.692)


def test_stats_extra_ammo_and_radio():
    # medBasicChassis_extraAmmunitionStorage_basicRadio.png - proves
    # TANK_ROLE_COMBAT_MODIFIERS is a SEPARATE multiplication stage: 12 x
    # 1.15 (radio) x 1.15 (chassis) = 15.87, truncating to the screenshot's
    # displayed 15.8. Summed into one bucket (12 x 1.30) would give 15.6.
    modules = _medium_defaults() | {
        "special_type_slot_1": "extra_ammo_storage",
        "special_type_slot_2": "tank_radio_1",
    }
    stats = calculate_tank_design_stats("medium_tank_chassis", 1, modules)
    assert stats["defense"] == pytest.approx(7.2)
    assert stats["reliability"] == pytest.approx(0.7)
    assert stats["breakthrough"] == pytest.approx(15.87)


def test_stats_anti_air_role():
    # medBasicChassis_SPAA_basicAntiAirGun.png (pre-1.19.4). soft_attack/
    # hard_attack/air_attack all gained +5% from the tier module-additive
    # multiplier; breakthrough's role modifier was separately standardized
    # from -53% (0.47) to -75% (0.25) by 1.19.4 - see
    # data/tank_role_combat_modifiers.py.
    modules = _medium_defaults() | {"main_armament_slot": "tank_anti_air_cannon"}
    stats = calculate_tank_design_stats(
        "medium_tank_chassis", 1, modules, role_key="medium_tank_aa_chassis"
    )
    assert stats["hardness"] == pytest.approx(0.65)
    assert stats["reliability"] == pytest.approx(0.7)
    assert stats["soft_attack"] == pytest.approx(5.985)  # (1.19.4) 5.7->5.985
    assert stats["hard_attack"] == pytest.approx(1.995)  # (1.19.4) 1.9->1.995
    assert stats["ap_attack"] == pytest.approx(10.0)
    assert stats["air_attack"] == pytest.approx(21.735)  # (1.19.4) 20.7->21.735
    assert stats["breakthrough"] == pytest.approx(2.5)  # (1.19.4) 4.7->2.5


def test_stats_anti_air_gun_without_the_role_gets_no_bonus():
    # medBasicChassis_basicAntiAirGun.png - the SAME weapon on a plain
    # (role-less) chassis: air_attack still gets no ROLE bonus (no +15%),
    # but does gain 1.19.4's tier module-additive +5% (18.0->18.9).
    # breakthrough still gets the PLAIN tank's own +15%, not AA's -75%.
    modules = _medium_defaults() | {"main_armament_slot": "tank_anti_air_cannon"}
    stats = calculate_tank_design_stats("medium_tank_chassis", 1, modules)
    assert stats["air_attack"] == pytest.approx(18.9)  # (1.19.4) 18.0->18.9
    assert stats["breakthrough"] == pytest.approx(11.5)
    assert stats["reliability"] == pytest.approx(0.7)


def test_stats_tank_destroyer_role():
    # medBasicChassis_TD_basicHighVelocityCannon.png (pre-1.19.4) - proves the
    # role modifier table also covers ap_attack (Piercing), not just
    # breakthrough: 68 x 1.15 = 78.2 (unaffected by 1.19.4, ap_attack isn't a
    # tier-module-additive field). breakthrough's role modifier was separately
    # standardized from -25% (0.75) to -75% (0.25) by 1.19.4; soft/hard_attack
    # both gained the same +5% tier bonus as the plain case above.
    modules = _medium_defaults() | {"main_armament_slot": "tank_high_velocity_cannon"}
    stats = calculate_tank_design_stats(
        "medium_tank_chassis", 1, modules, role_key="medium_tank_destroyer_chassis"
    )
    assert stats["ap_attack"] == pytest.approx(78.2)
    assert stats["breakthrough"] == pytest.approx(2.5)  # (1.19.4) 7.5->2.5
    assert stats["soft_attack"] == pytest.approx(9.975)  # (1.19.4) 9.5->9.975
    assert stats["hard_attack"] == pytest.approx(25.935)  # (1.19.4) 24.7->25.935
    assert stats["hardness"] == pytest.approx(0.85)


def test_stats_flame_role():
    # medBasicChassis_FT_flamethrower.png (pre-1.19.4) - proves the Flame
    # role's hidden hardness=0 override (not present in x_tank_chassis.txt's
    # for_each block at all - found by hand-checking this exact screenshot)
    # and its -70%/-45% stat reductions. soft_attack alone gained 1.19.4's
    # +5% tier module-additive bonus (breakthrough isn't a tier-module-
    # additive field, so it's unaffected).
    modules = _medium_defaults() | {"main_armament_slot": "flamethrower"}
    stats = calculate_tank_design_stats(
        "medium_tank_chassis", 1, modules, role_key="medium_tank_flame_chassis"
    )
    assert stats["hardness"] == pytest.approx(0.0)
    assert stats["armor_value"] == pytest.approx(9.0)
    assert stats["defense"] == pytest.approx(0.6)
    assert stats["breakthrough"] == pytest.approx(5.5)
    assert stats["soft_attack"] == pytest.approx(2.743125)  # (1.19.4) 2.6125->2.743125
    assert stats["reliability"] == pytest.approx(0.75)


def test_stats_flamethrower_without_the_role_keeps_full_hardness():
    # medBasicChassis_flamethrower.png - the SAME weapon on a plain
    # (role-less) chassis keeps full hardness and the plain +15% breakthrough.
    # soft_attack gains 1.19.4's +5% tier module-additive bonus.
    modules = _medium_defaults() | {"main_armament_slot": "flamethrower"}
    stats = calculate_tank_design_stats("medium_tank_chassis", 1, modules)
    assert stats["hardness"] == pytest.approx(0.85)
    assert stats["breakthrough"] == pytest.approx(11.5)
    assert stats["reliability"] == pytest.approx(0.75)
    assert stats["soft_attack"] == pytest.approx(4.9875)  # (1.19.4) 4.75->4.9875


def test_max_tick_level_with_no_research_stops_below_the_first_checkpoint():
    # Levels 1-4 need no technology at all - only level 5 onward does.
    assert max_tick_level("tank_nsb_engine_upgrade", researched=set()) == 4
    assert max_tick_level("tank_nsb_armor_upgrade", researched=set()) == 4


def test_max_tick_level_rises_with_each_researched_checkpoint():
    assert max_tick_level("tank_nsb_engine_upgrade", researched={"engine_tech_1"}) == 9
    assert max_tick_level(
        "tank_nsb_engine_upgrade", researched={"engine_tech_1", "engine_tech_2"}
    ) == 14
    assert max_tick_level(
        "tank_nsb_engine_upgrade",
        researched={"engine_tech_1", "engine_tech_2", "engine_tech_3"},
    ) == 17


def test_max_tick_level_reaches_the_cap_once_every_checkpoint_is_researched():
    assert max_tick_level(
        "tank_nsb_engine_upgrade",
        researched={"engine_tech_1", "engine_tech_2", "engine_tech_3", "engine_tech_4"},
    ) == 20


def test_max_tick_level_ignores_a_gap_past_the_first_unmet_checkpoint():
    # Having engine_tech_3 without engine_tech_1/2 first shouldn't skip ahead
    # - the first unmet checkpoint (level 5) is still the real ceiling.
    assert max_tick_level("tank_nsb_engine_upgrade", researched={"engine_tech_3"}) == 4


def _base_design_for_candidates():
    # A light tank mid-design - tier/role/modules/ticks all set to
    # something distinctive, so a candidate that's supposed to leave a
    # field untouched can be told apart from one that resets it.
    return {
        "chassis_key": "light_tank_chassis",
        "tier": 1,
        "role_key": None,
        "chosen_modules": _base_light_tank_modules(),
        "tick_levels": {"tank_nsb_engine_upgrade": 2},
    }


def test_build_candidate_design_chassis_resets_tier_role_modules_and_ticks():
    base = _base_design_for_candidates()
    design = build_candidate_design(base, {"type": "chassis", "chassis_key": "medium_tank_chassis"})

    medium_chassis = next(c for c in TANK_CHASSIS if c["key"] == "medium_tank_chassis")
    assert design["chassis_key"] == "medium_tank_chassis"
    assert design["tier"] == medium_chassis["tiers"][0]["tier"]
    assert design["role_key"] is None
    assert design["chosen_modules"] == medium_chassis["default_modules"]
    assert design["tick_levels"] == {}


def test_build_candidate_design_tier_changes_only_tier():
    base = _base_design_for_candidates()
    design = build_candidate_design(base, {"type": "tier", "tier": 2})

    assert design["tier"] == 2
    assert design["chassis_key"] == base["chassis_key"]
    assert design["role_key"] == base["role_key"]
    assert design["chosen_modules"] == base["chosen_modules"]
    assert design["tick_levels"] == base["tick_levels"]


def test_build_candidate_design_role_resets_modules_to_the_base_chassis_defaults():
    base = _base_design_for_candidates()
    design = build_candidate_design(base, {"type": "role", "role_key": "light_tank_destroyer_chassis"})

    light_chassis = next(c for c in TANK_CHASSIS if c["key"] == "light_tank_chassis")
    assert design["role_key"] == "light_tank_destroyer_chassis"
    assert design["chosen_modules"] == light_chassis["default_modules"]
    assert design["tier"] == base["tier"]
    assert design["tick_levels"] == base["tick_levels"]


def test_build_candidate_design_module_changes_only_that_slot():
    base = _base_design_for_candidates()
    design = build_candidate_design(
        base, {"type": "module", "slot": "armor_type_slot", "module_key": "tank_welded_armor"}
    )

    assert design["chosen_modules"]["armor_type_slot"] == "tank_welded_armor"
    for slot, key in base["chosen_modules"].items():
        if slot != "armor_type_slot":
            assert design["chosen_modules"][slot] == key
    assert design["chassis_key"] == base["chassis_key"]
    assert design["tier"] == base["tier"]
    assert design["role_key"] == base["role_key"]
    assert design["tick_levels"] == base["tick_levels"]


def test_build_candidate_design_never_mutates_the_base_design():
    base = _base_design_for_candidates()
    original = {
        "chassis_key": base["chassis_key"],
        "tier": base["tier"],
        "role_key": base["role_key"],
        "chosen_modules": dict(base["chosen_modules"]),
        "tick_levels": dict(base["tick_levels"]),
    }

    build_candidate_design(base, {"type": "chassis", "chassis_key": "medium_tank_chassis"})
    build_candidate_design(base, {"type": "role", "role_key": "light_tank_destroyer_chassis"})
    build_candidate_design(base, {"type": "module", "slot": "armor_type_slot", "module_key": "tank_welded_armor"})

    assert base == original


# --- Reliability-scaled max_strength (HP), added 1.19.4, formula
# empirically confirmed 2026-11-02 against 4 real Tank Designer screenshots
# (Template Examples/Light_Tank_HMG*.png) - see CLAUDE.md's Tank Designer
# section for the full derivation. ---

def test_max_strength_matches_the_real_light_tank_screenshots():
    stats = calculate_tank_design_stats("light_tank_chassis", 1, _base_light_tank_modules())
    assert stats["reliability"] == pytest.approx(0.95)
    assert stats["max_strength"] == pytest.approx(3.425)  # real screenshot: 95.0% -> 3.4

    modules = {**_base_light_tank_modules(), "special_type_slot_1": "easy_maintenance"}
    stats_easy_maint = calculate_tank_design_stats("light_tank_chassis", 1, modules)
    assert stats_easy_maint["reliability"] == pytest.approx(1.025)
    assert stats_easy_maint["max_strength"] == pytest.approx(3.5375)  # real: 102.5% -> 3.5


def test_max_strength_for_a_role_converted_design_uses_the_line_base_and_factor():
    # Tank Destroyer/SP-Anti-Air/SP-Artillery designs show the "Line"
    # battalion's own base (0.5) and factor (0.75) here - every one of
    # those roles always feeds at least a Line battalion, even the ones
    # that also feed a Regimental Support item with its own lower values
    # (applied separately once a saved design is actually used - see
    # tests/test_stats.py's matching reliability-scaled-HP tests).
    modules = _medium_defaults() | {"main_armament_slot": "tank_high_velocity_cannon"}
    stats = calculate_tank_design_stats(
        "medium_tank_chassis", 1, modules, role_key="medium_tank_destroyer_chassis"
    )
    assert stats["reliability"] == pytest.approx(0.75)
    assert stats["max_strength"] == pytest.approx(1.0625)  # 0.5 + 0.75 x 0.75


def test_max_strength_for_land_cruiser_is_flat_and_unaffected_by_reliability():
    # Land Cruiser is explicitly excluded by the real patch note itself.
    stats = calculate_tank_design_stats("land_cruiser_chassis", 1, {})
    assert stats["max_strength"] == pytest.approx(15.0)
