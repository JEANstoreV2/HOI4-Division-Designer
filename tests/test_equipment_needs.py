from data.battalions import BATTALIONS
from data.equipment import EQUIPMENT
from data.equipment_needs import EQUIPMENT_NEEDS
from data.regimental_support import REGIMENTAL_SUPPORT
from data.support_companies import SUPPORT_COMPANIES

ALL_ITEM_KEYS = (
    {b["key"] for b in BATTALIONS}
    | {c["key"] for c in SUPPORT_COMPANIES}
    | {r["key"] for r in REGIMENTAL_SUPPORT}
)


def test_every_item_has_an_equipment_needs_entry():
    assert ALL_ITEM_KEYS <= set(EQUIPMENT_NEEDS)


def test_no_orphan_equipment_needs_entries():
    assert set(EQUIPMENT_NEEDS) <= ALL_ITEM_KEYS


def test_every_referenced_equipment_type_exists():
    for item_key, needs in EQUIPMENT_NEEDS.items():
        for equipment_key in needs:
            assert equipment_key in EQUIPMENT, (item_key, equipment_key)


def test_all_quantities_are_positive_numbers():
    for item_key, needs in EQUIPMENT_NEEDS.items():
        for equipment_key, quantity in needs.items():
            assert isinstance(quantity, (int, float)) and quantity > 0, (item_key, equipment_key)


def test_expected_entry_count():
    # A regression tripwire: if this changes, it should be a deliberate
    # addition/removal, not an accidental one.
    assert len(EQUIPMENT_NEEDS) == 101
