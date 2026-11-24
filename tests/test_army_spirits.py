from data.army_spirits import ARMY_SPIRIT_CATEGORIES, ARMY_SPIRITS
from data.doctrines import GRAND_DOCTRINES, SUBDOCTRINES
from data.equipment import EQUIPMENT

CATEGORY_KEYS = {c["key"] for c in ARMY_SPIRIT_CATEGORIES}
DOCTRINE_AND_SUBDOCTRINE_KEYS = {gd["key"] for gd in GRAND_DOCTRINES} | {sd["key"] for sd in SUBDOCTRINES}
ARMY_SPIRITS_BY_KEY = {s["key"]: s for s in ARMY_SPIRITS}


def test_two_categories_after_the_rescope():
    # academy_spirit dropped entirely (2026-11-02 rescope) - none of its
    # entries bore on a tracked stat, so nothing was ever selectable there.
    assert [c["key"] for c in ARMY_SPIRIT_CATEGORIES] == ["army_spirit", "division_command_spirit"]


def test_no_duplicate_spirit_keys():
    keys = [s["key"] for s in ARMY_SPIRITS]
    assert len(keys) == len(set(keys))


def test_total_and_per_category_counts():
    # Re-scoped 2026-11-02 to only the entries that bear on a stat this
    # app tracks - see data/army_spirits.py's own header for the full
    # derivation (4 with a real equipment_bonus + 5 whose country-wide
    # modifiers field name matches a tracked stat).
    assert len(ARMY_SPIRITS) == 9
    counts = {}
    for spirit in ARMY_SPIRITS:
        counts[spirit["category"]] = counts.get(spirit["category"], 0) + 1
    assert counts == {"army_spirit": 1, "division_command_spirit": 8}


def test_every_spirit_belongs_to_a_real_category():
    for spirit in ARMY_SPIRITS:
        assert spirit["category"] in CATEGORY_KEYS, spirit["key"]


def test_every_spirit_has_a_real_non_empty_name():
    for spirit in ARMY_SPIRITS:
        assert isinstance(spirit["name"], str) and spirit["name"], spirit["key"]


def test_every_available_reference_resolves_to_a_real_doctrine_or_subdoctrine():
    for spirit in ARMY_SPIRITS:
        for key in spirit["available"]:
            assert key in DOCTRINE_AND_SUBDOCTRINE_KEYS, (spirit["key"], key)


def test_every_surviving_spirit_bears_on_a_tracked_stat():
    # Each of the 9 either has a real equipment_bonus, or a country-wide
    # modifiers field matching a stat this app computes - that's the whole
    # point of the rescope, so guard it directly rather than just trusting
    # the count above.
    tracked_modifier_fields = {"breakthrough_factor", "supply_consumption_factor", "army_strength_factor", "army_speed_factor"}
    for spirit in ARMY_SPIRITS:
        has_equipment_bonus = bool(spirit["equipment_bonus"])
        has_tracked_modifier = bool(tracked_modifier_fields & set(spirit["modifiers"]))
        assert has_equipment_bonus or has_tracked_modifier, spirit["key"]


# --- Spot checks pinning the real, screenshot-free-but-source-confirmed
# values for the 4 compiled entries with a real equipment_bonus (added
# 2026-11-02, Officer Corps build) - these deliberately stay UNAPPLIED in
# logic/stats.py (see data/army_spirits.py's own header for why), but the
# compiled data itself should still be exactly right.

def test_subsidized_contracts_equipment_bonus():
    spirit = ARMY_SPIRITS_BY_KEY["subsidized_contracts_army_spirit"]
    assert spirit["equipment_bonus"] == {
        "armored_car_equipment": {"build_cost_ic": -0.15},
        "light_tank_chassis": {"build_cost_ic": -0.10},
        "armored_support_vehicle": {"build_cost_ic": -0.10},
    }


def test_all_arms_at_defense_equipment_bonus():
    spirit = ARMY_SPIRITS_BY_KEY["all_arms_at_defense_army_spirit"]
    assert spirit["equipment_bonus"] == {"infantry_equipment": {"hard_attack": 0.25}}


def test_direct_fire_support_equipment_bonus_covers_all_four_tank_artillery_chassis():
    spirit = ARMY_SPIRITS_BY_KEY["direct_fire_support_army_spirit"]
    expected_keys = {
        "light_tank_artillery_chassis", "medium_tank_artillery_chassis",
        "heavy_tank_artillery_chassis", "modern_tank_artillery_chassis",
    }
    assert set(spirit["equipment_bonus"]) == expected_keys
    for bonus in spirit["equipment_bonus"].values():
        assert bonus == {"hard_attack": 0.50, "ap_attack": 1}


def test_rapid_emplacement_equipment_bonus_includes_the_unmodeled_motorized_rocket_key():
    spirit = ARMY_SPIRITS_BY_KEY["rapid_emplacement_army_spirit"]
    assert set(spirit["equipment_bonus"]) == {
        "artillery_equipment", "rocket_artillery_equipment", "motorized_rocket_equipment",
        "anti_tank_equipment", "anti_air_equipment",
    }
    for bonus in spirit["equipment_bonus"].values():
        assert bonus == {"breakthrough": 0.10, "defense": 0.10}
    # Confirms the deliberately-inert key really is absent from this app's
    # equipment data - not a gap, a real unmodeled HOI4 equipment archetype.
    assert "motorized_rocket_equipment" not in EQUIPMENT


def test_only_four_spirits_have_a_real_equipment_bonus():
    bearing = {s["key"] for s in ARMY_SPIRITS if s["equipment_bonus"]}
    assert bearing == {
        "subsidized_contracts_army_spirit", "all_arms_at_defense_army_spirit",
        "direct_fire_support_army_spirit", "rapid_emplacement_army_spirit",
    }


# --- Spot checks pinning the 5 country-wide-modifier entries kept per
# Ollie's explicit call (2026-11-02 rescope) despite being a structurally
# different kind of bonus from the 4 above.

def test_smoke_and_fire_breakthrough_factor():
    assert ARMY_SPIRITS_BY_KEY["smoke_and_fire_spirit"]["modifiers"] == {"breakthrough_factor": 0.06}


def test_logistical_focus_supply_consumption_factor():
    spirit = ARMY_SPIRITS_BY_KEY["logistical_focus_spirit"]
    assert spirit["modifiers"]["supply_consumption_factor"] == -0.10


def test_operational_reserve_army_strength_factor():
    assert ARMY_SPIRITS_BY_KEY["operational_reserve_spirit"]["modifiers"] == {"army_strength_factor": 0.1}


def test_flexible_organization_and_maneuver_warfare_both_have_army_speed_factor():
    assert ARMY_SPIRITS_BY_KEY["flexible_organization_spirit"]["modifiers"]["army_speed_factor"] == 0.05
    assert ARMY_SPIRITS_BY_KEY["maneuver_warfare_spirit"]["modifiers"]["army_speed_factor"] == 0.05
