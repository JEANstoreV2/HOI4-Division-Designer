from data.battalions import BATTALIONS
from data.regimental_support import REGIMENTAL_SUPPORT
from data.support_companies import SUPPORT_COMPANIES
from data.unit_categories import UNIT_CATEGORIES

ALL_ITEM_KEYS = (
    {b["key"] for b in BATTALIONS}
    | {s["key"] for s in SUPPORT_COMPANIES}
    | {r["key"] for r in REGIMENTAL_SUPPORT}
)


def test_every_composition_item_has_a_category_entry():
    assert ALL_ITEM_KEYS <= set(UNIT_CATEGORIES)


def test_every_entry_is_a_non_empty_set_of_category_tags():
    for key, categories in UNIT_CATEGORIES.items():
        assert categories, key
        for tag in categories:
            assert tag.startswith("category_"), (key, tag)


def test_marine_is_special_forces_and_light_infantry():
    # Spot-checked directly against units_copy/infantry.txt's `marine` block.
    assert {"category_special_forces", "category_marines", "category_all_infantry", "category_army"} <= UNIT_CATEGORIES["marine"]


def test_plain_infantry_is_not_special_forces():
    assert "category_all_infantry" in UNIT_CATEGORIES["infantry"]
    assert "category_special_forces" not in UNIT_CATEGORIES["infantry"]


def test_tanks_are_category_all_armor_and_category_tanks():
    for key in ["light_armor", "medium_armor", "heavy_armor"]:
        assert {"category_all_armor", "category_tanks"} <= UNIT_CATEGORIES[key]


def test_artillery_support_company_is_line_and_support_artillery():
    # "artillery" (data/support_companies.py) is category_support_artillery,
    # not category_line_artillery - that tag belongs to the battalion-grid
    # artillery_brigade instead. Confirmed against units_copy/artillery_brigade.txt.
    assert "category_support_artillery" in UNIT_CATEGORIES["artillery"]
    assert "category_line_artillery" in UNIT_CATEGORIES["artillery_brigade"]


def test_expected_entry_count():
    # A regression tripwire: if this changes, it should be a deliberate
    # addition/removal, not an accidental one.
    assert len(UNIT_CATEGORIES) == 101
