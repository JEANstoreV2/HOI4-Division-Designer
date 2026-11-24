from data.battalion_stats import BATTALION_STATS
from data.battalions import BATTALIONS
from data.regimental_support import REGIMENTAL_SUPPORT
from data.support_companies import SUPPORT_COMPANIES
from data.unit_categories import UNIT_CATEGORIES

ALL_ITEM_KEYS = (
    {b["key"] for b in BATTALIONS}
    | {c["key"] for c in SUPPORT_COMPANIES}
    | {r["key"] for r in REGIMENTAL_SUPPORT}
)
ALL_CATEGORY_KEYS = {category for categories in UNIT_CATEGORIES.values() for category in categories}


def test_every_item_has_a_stats_entry():
    assert ALL_ITEM_KEYS <= set(BATTALION_STATS)


def test_no_orphan_stats_entries():
    assert set(BATTALION_STATS) <= ALL_ITEM_KEYS


def test_all_stat_values_are_numeric():
    # battalion_mult (added 2026-10-08) is the one deliberate exception - a
    # list of aura dicts, not a plain numeric stat - see tests/test_stats.py
    # for its own dedicated coverage.
    for item_key, stats in BATTALION_STATS.items():
        for field, value in stats.items():
            if field == "battalion_mult":
                continue
            assert isinstance(value, (int, float)), (item_key, field)


def test_expected_entry_count():
    assert len(BATTALION_STATS) == 101


# --- battalion_mult (added 2026-10-08) ---

def test_every_item_has_a_battalion_mult_field():
    for item_key, stats in BATTALION_STATS.items():
        assert "battalion_mult" in stats, item_key


def test_expected_battalion_mult_count():
    # A regression tripwire: if this changes, it should be a deliberate
    # addition/removal (a new units_copy/*.txt read), not an accident.
    # 21 owning items, 23 total blocks (armored_engineer and
    # motorized_military_police each have two).
    items_with_mult = [key for key, stats in BATTALION_STATS.items() if stats["battalion_mult"]]
    total_blocks = sum(len(stats["battalion_mult"]) for stats in BATTALION_STATS.values())
    assert len(items_with_mult) == 21
    assert total_blocks == 23


def test_battalion_mult_categories_reference_real_categories():
    for item_key, stats in BATTALION_STATS.items():
        for mult in stats["battalion_mult"]:
            assert mult["category"] in ALL_CATEGORY_KEYS, (item_key, mult["category"])


def test_battalion_mult_add_flag_is_only_ever_true_or_absent():
    # "add" should never compile as False/0/anything else - the raw source
    # either has an active `add = yes` (True) or doesn't mention `add` at
    # all (absent, meaning percentage) - see this file's own header comment.
    for item_key, stats in BATTALION_STATS.items():
        for mult in stats["battalion_mult"]:
            assert mult.get("add", True) is True, (item_key, mult)


def test_logistics_company_has_its_own_supply_and_fuel_consumption_factors():
    # Confirmed via its tech tooltip (Template Examples/LogisticsCompany1.png
    # - "Supply Usage: -10.00%", "Fuel Usage: -5.00%") - previously missing
    # entirely, a real compilation gap found during the 2026-09-30 Technology
    # stat bonuses investigation (see logic/stats.py's Technology
    # unit_bonuses block comment).
    assert BATTALION_STATS["logistics_company"]["supply_consumption_factor"] == -0.10
    assert BATTALION_STATS["logistics_company"]["fuel_consumption_factor"] == -0.05
