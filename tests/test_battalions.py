from data.battalions import BATTALIONS, CATEGORIES, CATEGORY_LABELS


def test_no_duplicate_keys():
    keys = [b["key"] for b in BATTALIONS]
    assert len(keys) == len(set(keys))


def test_all_categories_are_declared():
    assert {b["category"] for b in BATTALIONS} <= set(CATEGORIES)


def test_every_category_has_a_label():
    assert set(CATEGORY_LABELS) == set(CATEGORIES)
