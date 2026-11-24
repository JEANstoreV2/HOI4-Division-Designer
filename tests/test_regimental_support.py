from data.battalions import CATEGORIES
from data.regimental_support import REGIMENTAL_SUPPORT


def test_no_duplicate_keys():
    keys = [item["key"] for item in REGIMENTAL_SUPPORT]
    assert len(keys) == len(set(keys))


def test_allowed_battalion_groups_are_real_categories():
    for item in REGIMENTAL_SUPPORT:
        assert set(item["allowed_battalion_groups"]) <= set(CATEGORIES)


def test_every_item_allows_at_least_one_category():
    for item in REGIMENTAL_SUPPORT:
        assert len(item["allowed_battalion_groups"]) > 0
