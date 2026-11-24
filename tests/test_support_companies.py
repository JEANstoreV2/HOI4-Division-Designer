from data.support_companies import SUPPORT_COMPANIES


def test_no_duplicate_keys():
    keys = [c["key"] for c in SUPPORT_COMPANIES]
    assert len(keys) == len(set(keys))
