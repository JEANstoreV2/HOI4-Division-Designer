from data.battalions import BATTALIONS
from data.regimental_support import REGIMENTAL_SUPPORT
from data.support_companies import SUPPORT_COMPANIES
from data.tank_chassis import TANK_CHASSIS, TANK_ROLES

ALL_COMPOSITION_KEYS = (
    {b["key"] for b in BATTALIONS}
    | {s["key"] for s in SUPPORT_COMPANIES}
    | {r["key"] for r in REGIMENTAL_SUPPORT}
)

CHASSIS_BY_KEY = {c["key"]: c for c in TANK_CHASSIS}


def test_expected_chassis_count():
    assert len(TANK_CHASSIS) == 7


def test_expected_role_count():
    # 5 roles x 3 sizes (light/medium/heavy) + 3 roles x 2 sizes (super
    # heavy/modern) = 15 + 6 = 21.
    assert len(TANK_ROLES) == 21


def test_no_duplicate_chassis_keys():
    keys = [c["key"] for c in TANK_CHASSIS]
    assert len(keys) == len(set(keys))


def test_no_duplicate_role_keys():
    keys = [r["key"] for r in TANK_ROLES]
    assert len(keys) == len(set(keys))


def test_every_base_chassis_feeds_a_real_composition_key():
    for chassis in TANK_CHASSIS:
        assert chassis["feeds"] in ALL_COMPOSITION_KEYS, chassis["key"]


def test_every_role_feeds_real_composition_keys():
    for role in TANK_ROLES:
        for key in role["feeds"]:
            assert key in ALL_COMPOSITION_KEYS, (role["key"], key)


def test_every_role_references_a_real_base_chassis():
    for role in TANK_ROLES:
        assert role["base_chassis"] in CHASSIS_BY_KEY, role["key"]


def test_every_tier_stat_override_field_is_also_a_base_stat_field():
    # A tier's stat_overrides should only ever touch fields the archetype
    # itself defines - if a tier introduces a brand new field, that's worth
    # a second look rather than silently accepting it.
    for chassis in TANK_CHASSIS:
        base_fields = set(chassis["base_stats"])
        for tier in chassis["tiers"]:
            assert set(tier["stat_overrides"]) <= base_fields, (chassis["key"], tier["key"])


def test_upgrades_only_appear_on_a_chassis_lowest_tier():
    # Confirmed by direct read: only the lowest tier of each chassis lists
    # `upgrades` - every higher tier has none (they override stats directly
    # instead). A regression here would mean tick availability silently
    # duplicated or moved to the wrong tier.
    for chassis in TANK_CHASSIS:
        tiers_sorted = sorted(chassis["tiers"], key=lambda t: t["tier"])
        assert tiers_sorted[0]["upgrades"], chassis["key"]
        for tier in tiers_sorted[1:]:
            assert tier["upgrades"] == [], (chassis["key"], tier["key"])


def test_required_slots_have_no_default_of_none_except_main_armament():
    # Every chassis ships un-armed by default (main_armament_slot = empty
    # in the source) but every other required slot has a real default
    # module - confirmed by direct read for every archetype except Land
    # Cruiser, whose defaults are commented out in the source entirely.
    for chassis in TANK_CHASSIS:
        if chassis["key"] == "land_cruiser_chassis":
            continue
        for slot_name, slot in chassis["module_slots"].items():
            if not slot["required"]:
                continue
            default = chassis["default_modules"].get(slot_name, "MISSING")
            if slot_name == "main_armament_slot":
                assert default is None, chassis["key"]
            else:
                assert default is not None and default != "MISSING", (chassis["key"], slot_name)


def test_super_heavy_and_modern_have_no_amphibious_or_flame_role():
    roles_by_chassis = {}
    for role in TANK_ROLES:
        roles_by_chassis.setdefault(role["base_chassis"], set()).add(role["role"])

    assert roles_by_chassis["super_heavy_tank_chassis"] == {"anti_air", "artillery", "anti_tank"}
    assert roles_by_chassis["modern_tank_chassis"] == {"anti_air", "artillery", "anti_tank"}
    assert roles_by_chassis["light_tank_chassis"] == {"anti_air", "artillery", "anti_tank", "amphibious", "flame"}


def test_amphibious_tank_chassis_is_not_role_duplicated():
    assert not any(role["base_chassis"] == "amphibious_tank_chassis" for role in TANK_ROLES)


def test_land_cruiser_has_no_role_duplicates():
    assert not any(role["base_chassis"] == "land_cruiser_chassis" for role in TANK_ROLES)


def test_module_count_limits_are_non_negative():
    for chassis in TANK_CHASSIS:
        for limit in chassis["module_count_limits"]:
            assert limit["max_count"] >= 0, (chassis["key"], limit)
