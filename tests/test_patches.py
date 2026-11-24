from data.patches import STAGED_PATCHES


def test_staged_patches_is_a_list():
    assert isinstance(STAGED_PATCHES, list)


def test_every_staged_patch_has_the_required_shape():
    for patch in STAGED_PATCHES:
        assert isinstance(patch["key"], str) and patch["key"]
        assert isinstance(patch["label"], str) and patch["label"]
        assert isinstance(patch["source_notes"], str)
        assert isinstance(patch["equipment_overrides"], dict)
        assert isinstance(patch["battalion_overrides"], dict)


def test_no_duplicate_staged_patch_keys():
    keys = [patch["key"] for patch in STAGED_PATCHES]
    assert len(keys) == len(set(keys))
