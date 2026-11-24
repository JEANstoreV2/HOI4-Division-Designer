from data.equipment import EQUIPMENT

GAP_KEYS = {
    "light_tank_amphibious_chassis",
    "medium_tank_amphibious_chassis",
    "heavy_tank_amphibious_chassis",
    "light_tank_flame_chassis",
    "medium_tank_flame_chassis",
    "heavy_tank_flame_chassis",
}


def test_every_entry_has_a_name():
    for key, entry in EQUIPMENT.items():
        assert "name" in entry, key


def test_every_stat_value_is_numeric():
    for key, entry in EQUIPMENT.items():
        for field, value in entry.items():
            if field in ("name",):
                continue
            if field == "combat_stats_available":
                assert isinstance(value, bool), (key, field)
            else:
                assert isinstance(value, (int, float)), (key, field)


def test_only_the_confirmed_gaps_are_missing_combat_stats():
    flagged = {
        key for key, entry in EQUIPMENT.items()
        if entry.get("combat_stats_available") is False
    }
    assert flagged == GAP_KEYS


def test_expected_entry_count():
    # A regression tripwire: if this changes, it should be a deliberate
    # addition/removal, not an accidental one.
    assert len(EQUIPMENT) == 43
