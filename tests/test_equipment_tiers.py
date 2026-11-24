from data.equipment import EQUIPMENT
from data.equipment_tiers import EQUIPMENT_TIERS
from data.technologies import TECHNOLOGIES

ALL_UNLOCKS_EQUIPMENT_KEYS = {
    key for tech in TECHNOLOGIES for key in tech["unlocks_equipment"]
}


def test_every_tier_key_matches_a_real_technology_unlock():
    assert set(EQUIPMENT_TIERS) <= ALL_UNLOCKS_EQUIPMENT_KEYS


def test_every_family_is_a_real_equipment_key():
    for tier_key, tier in EQUIPMENT_TIERS.items():
        assert tier["family"] in EQUIPMENT, (tier_key, tier["family"])


def test_tier_numbers_are_non_negative_ints():
    for tier_key, tier in EQUIPMENT_TIERS.items():
        assert isinstance(tier["tier"], int) and tier["tier"] >= 0, tier_key


def test_no_duplicate_family_tier_pairs():
    seen = set()
    for tier_key, tier in EQUIPMENT_TIERS.items():
        pair = (tier["family"], tier["tier"])
        assert pair not in seen, (tier_key, pair)
        seen.add(pair)


def test_every_technology_that_unlocks_a_tiered_equipment_key_is_findable():
    # Every EQUIPMENT_TIERS key must be reachable from at least one real
    # technology's unlocks_equipment list, so logic/stats.py's reverse
    # lookup (_TIER_UNLOCK_TECH) never silently drops a tier.
    for tier_key in EQUIPMENT_TIERS:
        owning_techs = [t["key"] for t in TECHNOLOGIES if tier_key in t["unlocks_equipment"]]
        assert owning_techs, tier_key


def test_expected_entry_count():
    # A regression tripwire: if this changes, it should be a deliberate
    # addition/removal, not an accidental one.
    assert len(EQUIPMENT_TIERS) == 74
