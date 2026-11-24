from logic.composition import regimental_support_unlocked


def test_locked_with_no_battalions():
    assert regimental_support_unlocked(0) is False


def test_locked_below_threshold():
    assert regimental_support_unlocked(2) is False


def test_unlocked_at_threshold():
    assert regimental_support_unlocked(3) is True


def test_unlocked_above_threshold():
    assert regimental_support_unlocked(4) is True
