from data.tank_upgrades import TANK_UPGRADES
from data.technologies import TECHNOLOGIES

TECH_KEYS = {t["key"] for t in TECHNOLOGIES}
KNOWN_RESOURCES = {"steel", "tungsten", "chromium"}


def test_expected_upgrade_count():
    # Only the two real NSB ticks - see data/tank_upgrades.py's header for
    # why the file's nine older 5-level upgrade types are excluded.
    assert len(TANK_UPGRADES) == 2


def test_no_duplicate_keys():
    keys = [u["key"] for u in TANK_UPGRADES]
    assert len(keys) == len(set(keys))


def test_every_level_requirement_tech_is_real():
    for upgrade in TANK_UPGRADES:
        for requirement in upgrade["level_requirements"]:
            assert requirement["tech"] in TECH_KEYS, (upgrade["key"], requirement)


def test_level_requirements_are_strictly_ascending():
    for upgrade in TANK_UPGRADES:
        levels = [r["level"] for r in upgrade["level_requirements"]]
        assert levels == sorted(levels), upgrade["key"]
        assert len(levels) == len(set(levels)), upgrade["key"]


def test_level_requirements_never_exceed_max_level():
    for upgrade in TANK_UPGRADES:
        for requirement in upgrade["level_requirements"]:
            assert requirement["level"] <= upgrade["max_level"], (upgrade["key"], requirement)


def test_add_stats_and_reliability_values_are_numeric():
    for upgrade in TANK_UPGRADES:
        for field, value in upgrade["add_stats"].items():
            assert isinstance(value, (int, float)), (upgrade["key"], field)
        assert isinstance(upgrade["per_level_reliability"], (int, float)), upgrade["key"]


def test_resource_cost_thresholds_use_known_resource_keys():
    for upgrade in TANK_UPGRADES:
        for level, resources in upgrade["resource_cost_thresholds"].items():
            assert isinstance(level, int), upgrade["key"]
            for resource in resources:
                assert resource in KNOWN_RESOURCES, (upgrade["key"], level, resource)
