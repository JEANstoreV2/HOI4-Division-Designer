from data.doctrines import GRAND_DOCTRINES
from logic.doctrines import (
    active_unit_bonuses,
    can_claim_next_reward,
    is_grand_doctrine_selectable,
    is_subdoctrine_selectable,
    is_track_mastered,
    unlocked_subunit_keys,
    unlocks_fifth_battalion_row,
)


def test_grand_doctrine_selectable_with_nothing_active():
    assert is_grand_doctrine_selectable("new_mobile_warfare", active_grand_doctrines=set())


def test_grand_doctrine_not_selectable_if_already_active():
    assert not is_grand_doctrine_selectable("new_mobile_warfare", {"new_mobile_warfare"})


def test_grand_doctrine_blocked_by_another_in_the_same_folder():
    assert not is_grand_doctrine_selectable("superior_firepower", {"new_mobile_warfare"})


def test_grand_doctrines_in_different_folders_dont_block_each_other():
    # new_mobile_warfare (land) and special_forces_quantity (special_forces)
    # can both be active at once - different folders.
    assert is_grand_doctrine_selectable("special_forces_quantity", {"new_mobile_warfare"})


def test_subdoctrine_not_selectable_without_its_grand_doctrine_active():
    assert not is_subdoctrine_selectable(
        "mobile_infantry", "infantry",
        active_grand_doctrines=set(), track_subdoctrines={}, researched=set(),
    )


def test_subdoctrine_selectable_once_its_grand_doctrine_is_active():
    assert is_subdoctrine_selectable(
        "mobile_infantry", "infantry",
        active_grand_doctrines={"new_mobile_warfare"}, track_subdoctrines={}, researched=set(),
    )


def test_subdoctrine_not_selectable_for_a_track_it_doesnt_belong_to():
    assert not is_subdoctrine_selectable(
        "mobile_infantry", "armor",
        active_grand_doctrines={"new_mobile_warfare"}, track_subdoctrines={}, researched=set(),
    )


def test_xor_partner_blocks_selection_on_a_different_track():
    # mountaineers_1/mountaineers_2 are xor'd. If mountaineers_1 is already
    # assigned to special_forces_first, mountaineers_2 can't go on
    # special_forces_second.
    assert not is_subdoctrine_selectable(
        "mountaineers_2", "special_forces_second",
        active_grand_doctrines={"special_forces_quantity"},
        track_subdoctrines={"special_forces_first": "mountaineers_1"},
        researched={"tech_mountaineers"},
    )


def test_xor_partner_does_not_block_reassigning_the_same_track():
    # Replacing mountaineers_1 with mountaineers_2 on the SAME track is
    # explicitly allowed (only a *different* track is blocked).
    assert is_subdoctrine_selectable(
        "mountaineers_2", "special_forces_first",
        active_grand_doctrines={"special_forces_quantity"},
        track_subdoctrines={"special_forces_first": "mountaineers_1"},
        researched={"tech_mountaineers"},
    )


def test_a_subdoctrine_cannot_be_assigned_to_two_tracks_at_once():
    # Real bug, found 2026-11-02 while building AI Design Comparison's own
    # Doctrine search: mountaineers_1's own `tracks` lists BOTH Special
    # Forces tracks as eligible (real HOI4 lets you put it on either one),
    # but nothing previously stopped the SAME subdoctrine being assigned
    # to both simultaneously - a real, pre-existing gap in the live
    # Doctrine tab too (static/js/doctrines.js's own openTrackPicker calls
    # this identical function with no extra filtering).
    assert not is_subdoctrine_selectable(
        "mountaineers_1", "special_forces_second",
        active_grand_doctrines={"special_forces_quantity"},
        track_subdoctrines={"special_forces_first": "mountaineers_1"},
        researched={"tech_mountaineers"},
    )


def test_special_forces_subdoctrine_requires_its_technology():
    assert not is_subdoctrine_selectable(
        "mountaineers_1", "special_forces_first",
        active_grand_doctrines={"special_forces_quantity"}, track_subdoctrines={}, researched=set(),
    )
    assert is_subdoctrine_selectable(
        "mountaineers_1", "special_forces_first",
        active_grand_doctrines={"special_forces_quantity"}, track_subdoctrines={}, researched={"tech_mountaineers"},
    )


def test_land_subdoctrine_has_no_technology_requirement():
    assert is_subdoctrine_selectable(
        "mobile_infantry", "infantry",
        active_grand_doctrines={"new_mobile_warfare"}, track_subdoctrines={}, researched=set(),
    )


def test_can_claim_next_reward_until_all_are_claimed():
    # mobile_infantry has 5 rewards.
    assert can_claim_next_reward("mobile_infantry", claimed_rewards={})
    assert can_claim_next_reward("mobile_infantry", claimed_rewards={"mobile_infantry": 4})
    assert not can_claim_next_reward("mobile_infantry", claimed_rewards={"mobile_infantry": 5})


def test_track_not_mastered_with_no_subdoctrine_assigned():
    assert not is_track_mastered("infantry", track_subdoctrines={}, claimed_rewards={})


def test_track_not_mastered_until_every_reward_is_claimed():
    assert not is_track_mastered(
        "infantry", {"infantry": "mobile_infantry"}, {"mobile_infantry": 4}
    )
    assert is_track_mastered(
        "infantry", {"infantry": "mobile_infantry"}, {"mobile_infantry": 5}
    )


def test_fifth_battalion_row_locked_before_the_qualifying_track_is_mastered():
    assert not unlocks_fifth_battalion_row(
        active_grand_doctrines={"new_mobile_warfare"},
        track_subdoctrines={"armor": "armored_spearhead"},
        claimed_rewards={"armored_spearhead": 4},
    )


def test_fifth_battalion_row_unlocks_once_the_qualifying_track_is_mastered():
    # Mobile Warfare's row-5 track is armor (its milestone sets
    # additional_brigade_column_size) - confirmed derived from real
    # compiled data, not a hardcoded map, by checking every land grand
    # doctrine's documented track below.
    assert unlocks_fifth_battalion_row(
        active_grand_doctrines={"new_mobile_warfare"},
        track_subdoctrines={"armor": "armored_spearhead"},
        claimed_rewards={"armored_spearhead": 5},
    )


def test_fifth_battalion_row_qualifying_track_per_land_grand_doctrine():
    # Documents (and proves, via the real derivation) which track unlocks
    # the 5th row for each land grand doctrine, per Specification.md:
    # Mobile Warfare -> armor, Superior Firepower -> combat_support,
    # Grand Battleplan -> infantry. Mass Assault moved from infantry to
    # combat_support under the 1.19.4 patch (additional_brigade_column_size
    # removed from its Infantry milestone, added to its Combat Support one).
    expected_track_by_doctrine = {
        "new_mobile_warfare": "armor",
        "superior_firepower": "combat_support",
        "grand_battleplan": "infantry",
        "mass_assault": "combat_support",  # (1.19.4) was infantry
    }
    by_key = {gd["key"]: gd for gd in GRAND_DOCTRINES}

    for doctrine_key, expected_track in expected_track_by_doctrine.items():
        gd = by_key[doctrine_key]
        qualifying_tracks = [
            track_key
            for track_key, milestone in zip(gd["tracks"], gd["milestones"])
            if "additional_brigade_column_size" in milestone.get("modifiers", {})
        ]
        assert qualifying_tracks == [expected_track], doctrine_key


def test_unlocked_subunit_keys_empty_with_nothing_active():
    assert unlocked_subunit_keys(set(), {}, {}) == set()


def test_unlocked_subunit_keys_from_subdoctrine_effects():
    # mountaineers_1's own effects unlock rangers_support immediately on
    # selection, before any reward is claimed.
    unlocked = unlocked_subunit_keys(
        active_grand_doctrines={"special_forces_quantity"},
        track_subdoctrines={"special_forces_first": "mountaineers_1"},
        claimed_rewards={},
    )
    assert "rangers_support" in unlocked


def test_unlocked_subunit_keys_from_a_claimed_reward():
    # marines_1's reward_1 (the first reward) unlocks marine_commando -
    # not present before that reward is claimed, present after.
    not_yet = unlocked_subunit_keys(
        active_grand_doctrines={"special_forces_quantity"},
        track_subdoctrines={"special_forces_first": "marines_1"},
        claimed_rewards={"marines_1": 0},
    )
    assert "marine_commando" not in not_yet

    after = unlocked_subunit_keys(
        active_grand_doctrines={"special_forces_quantity"},
        track_subdoctrines={"special_forces_first": "marines_1"},
        claimed_rewards={"marines_1": 1},
    )
    assert "marine_commando" in after


def test_active_unit_bonuses_empty_with_nothing_active():
    assert active_unit_bonuses(set(), {}, {}) == []


def test_active_unit_bonuses_from_grand_doctrine_immediate_effects():
    # superior_firepower's own effects give category_line_artillery a
    # soft_attack bonus immediately, before any track is touched.
    bonuses = active_unit_bonuses(
        active_grand_doctrines={"superior_firepower"}, track_subdoctrines={}, claimed_rewards={},
    )
    assert ("category_line_artillery", {"soft_attack": 0.1}) in bonuses


def test_active_unit_bonuses_from_subdoctrine_immediate_effects():
    # mobile_infantry's own effects give category_all_infantry a breakthrough
    # bonus immediately, once assigned to a track.
    bonuses = active_unit_bonuses(
        active_grand_doctrines={"new_mobile_warfare"},
        track_subdoctrines={"infantry": "mobile_infantry"},
        claimed_rewards={},
    )
    assert ("category_all_infantry", {"breakthrough": 0.1}) in bonuses


def test_active_unit_bonuses_appear_progressively_as_rewards_are_claimed():
    # mobile_infantry's first reward (cavalry_charge) gives "recon" (Cavalry
    # Recon) a defense/breakthrough bonus - absent before it's claimed,
    # present after. (1.19.3) retargeted from category_cavalry to "recon".
    not_yet = active_unit_bonuses(
        active_grand_doctrines={"new_mobile_warfare"},
        track_subdoctrines={"infantry": "mobile_infantry"},
        claimed_rewards={"mobile_infantry": 0},
    )
    assert ("recon", {"defense": 0.10, "breakthrough": 0.10}) not in not_yet

    after = active_unit_bonuses(
        active_grand_doctrines={"new_mobile_warfare"},
        track_subdoctrines={"infantry": "mobile_infantry"},
        claimed_rewards={"mobile_infantry": 1},
    )
    assert ("recon", {"defense": 0.10, "breakthrough": 0.10}) in after


def test_active_unit_bonuses_from_a_milestone_only_once_its_track_is_mastered():
    # new_mobile_warfare's operations-track milestone gives
    # category_regimental_support_battalions a bonus - absent until the
    # assigned operations subdoctrine (mission_type_tactics) is fully
    # mastered (all 5 rewards claimed), present after.
    target = "category_regimental_support_battalions"
    expected = {"max_organisation": 10, "breakthrough": 0.1}

    not_yet = active_unit_bonuses(
        active_grand_doctrines={"new_mobile_warfare"},
        track_subdoctrines={"operations": "mission_type_tactics"},
        claimed_rewards={"mission_type_tactics": 4},
    )
    assert (target, expected) not in not_yet

    after = active_unit_bonuses(
        active_grand_doctrines={"new_mobile_warfare"},
        track_subdoctrines={"operations": "mission_type_tactics"},
        claimed_rewards={"mission_type_tactics": 5},
    )
    assert (target, expected) in after
