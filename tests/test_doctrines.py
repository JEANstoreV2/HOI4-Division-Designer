from data.doctrines import DOCTRINE_TRACKS, GRAND_DOCTRINES, SUBDOCTRINES
from data.technologies import TECHNOLOGIES

TECHNOLOGY_KEYS = {tech["key"] for tech in TECHNOLOGIES}
TRACK_KEYS = {track["key"] for track in DOCTRINE_TRACKS}
SUBDOCTRINE_KEYS = {sd["key"] for sd in SUBDOCTRINES}
DOCTRINE_TRACKS_BY_KEY = {t["key"]: t for t in DOCTRINE_TRACKS}


def test_no_duplicate_track_keys():
    keys = [t["key"] for t in DOCTRINE_TRACKS]
    assert len(keys) == len(set(keys))


def test_no_duplicate_grand_doctrine_keys():
    keys = [gd["key"] for gd in GRAND_DOCTRINES]
    assert len(keys) == len(set(keys))


def test_no_duplicate_subdoctrine_keys():
    keys = [sd["key"] for sd in SUBDOCTRINES]
    assert len(keys) == len(set(keys))


def test_every_grand_doctrine_track_is_real():
    for gd in GRAND_DOCTRINES:
        for track_key in gd["tracks"]:
            assert track_key in TRACK_KEYS, (gd["key"], track_key)


def test_every_grand_doctrine_has_one_milestone_per_track():
    for gd in GRAND_DOCTRINES:
        assert len(gd["milestones"]) == len(gd["tracks"]), gd["key"]


def test_every_track_folder_matches_its_referencing_grand_doctrines():
    for gd in GRAND_DOCTRINES:
        for track_key in gd["tracks"]:
            assert DOCTRINE_TRACKS_BY_KEY[track_key]["folder"] == gd["folder"], (gd["key"], track_key)


def test_every_subdoctrine_track_is_real():
    for sd in SUBDOCTRINES:
        for track_key in sd["tracks"]:
            assert track_key in TRACK_KEYS, (sd["key"], track_key)


def test_every_subdoctrine_has_at_least_one_track():
    for sd in SUBDOCTRINES:
        assert len(sd["tracks"]) >= 1, sd["key"]


def test_xor_references_real_subdoctrines():
    for sd in SUBDOCTRINES:
        for other in sd["xor"]:
            assert other in SUBDOCTRINE_KEYS, (sd["key"], other)


def test_xor_is_symmetric():
    by_key = {sd["key"]: sd for sd in SUBDOCTRINES}
    for sd in SUBDOCTRINES:
        for other in sd["xor"]:
            assert sd["key"] in by_key[other]["xor"], (sd["key"], other)


def test_no_subdoctrine_lists_itself_in_xor():
    for sd in SUBDOCTRINES:
        assert sd["key"] not in sd["xor"]


def test_requires_technology_is_a_real_technology_or_none():
    for sd in SUBDOCTRINES:
        if sd["requires_technology"] is not None:
            assert sd["requires_technology"] in TECHNOLOGY_KEYS, (sd["key"], sd["requires_technology"])


def test_every_subdoctrine_has_at_least_one_reward():
    for sd in SUBDOCTRINES:
        assert len(sd["rewards"]) >= 1, sd["key"]


def test_reward_keys_are_unique_within_their_subdoctrine():
    for sd in SUBDOCTRINES:
        reward_keys = [r["key"] for r in sd["rewards"]]
        assert len(reward_keys) == len(set(reward_keys)), sd["key"]


def test_expected_track_count():
    assert len(DOCTRINE_TRACKS) == 6


def test_expected_grand_doctrine_count():
    assert len(GRAND_DOCTRINES) == 6


def test_expected_subdoctrine_count():
    assert len(SUBDOCTRINES) == 40


# --- Real display names (fixed 2026-10-08) ---
#
# The original 2026-09-15 compile invented several names by guesswork, since
# doctrines_copy/'s own .txt files hold no display text at all (that lives
# in HOI4's separate localisation files, which weren't cross-checked at the
# time). An audit against the real installed game's own
# localisation/english/*.yml confirmed 14 names were wrong, not just the two
# (special_forces_quality, marines_2) already flagged - everything from
# outright invented names (commandos: "Commandos" -> "Individual
# Excellence", marines_1: "Jungle Assault" -> "Commandos", rangers_1: "Cold
# Climate" -> "Jaeger Traditions") to small punctuation/capitalization drift
# (self_propelled_support's real string literally capitalizes "propelled"
# lowercase). Not re-run live here (the real install isn't on every
# machine/CI, and isn't committed) - these are the audit's resulting exact
# strings, pinned as an ordinary regression the way every other
# screenshot/source-derived fix in this project already is.
_EXPECTED_NAMES = {
    "special_forces_quantity": "Expanded Special Forces",
    "special_forces_quality": "Elite Special Forces",
    "commandos": "Individual Excellence",
    "peoples_war": "People's Militia",
    "mobile_recon_and_assault": "Mobile Recon & Assault",
    "self_propelled_support": "Self-propelled Support",
    "mission_type_tactics": "Mission-Type Tactics",
    "last_stand": "Desperate Defense",
    "mountaineers_2": "Mountaineers: Elevate the Mountaineers",
    "marines_1": "Marines: Commandos",
    "marines_2": "Marines: Expeditionary Units",
    "paratroopers_1": "Paratroopers: Sabotage Parties",
    "paratroopers_2": "Paratroopers: Concentrated Drops",
    "rangers_1": "Rangers: Jaeger Traditions",
    "rangers_2": "Rangers: Jungle Training",
}


def test_corrected_doctrine_and_subdoctrine_names():
    by_key = {gd["key"]: gd["name"] for gd in GRAND_DOCTRINES}
    by_key.update({sd["key"]: sd["name"] for sd in SUBDOCTRINES})
    for key, expected_name in _EXPECTED_NAMES.items():
        assert by_key[key] == expected_name, key


SUBDOCTRINES_BY_KEY = {sd["key"]: sd for sd in SUBDOCTRINES}


def _reward_name(subdoctrine_key, reward_key):
    rewards = SUBDOCTRINES_BY_KEY[subdoctrine_key]["rewards"]
    return next(r["name"] for r in rewards if r["key"] == reward_key)


def test_every_reward_has_a_name():
    # Added 2026-11-01 - every reward previously had only a bare key, with
    # no real compiled display name anywhere (unlike every other named
    # entity in this app) - a full audit against the real installed
    # game's own localisation/english/doctrines_l_english.yml gave every
    # one of the 199 rewards across all 40 subdoctrines a real name.
    for sd in SUBDOCTRINES:
        for reward in sd["rewards"]:
            assert isinstance(reward.get("name"), str) and reward["name"], (sd["key"], reward["key"])


def test_reward_names_match_the_real_localisation():
    # A representative sample, not all 199 - covering plain land rewards,
    # the 4 reward keys with a genuine missing-underscore typo baked into
    # the source itself (title-casing alone could never have fixed these -
    # see CLAUDE.md), two cases where the SAME reward key means something
    # different on two different subdoctrines (confirming names are
    # correctly scoped per-subdoctrine, not looked up from one flat global
    # table), peoples_war's real reward count (4, not 5 - the yml's own
    # unused "protracted_war" line was deliberately left uncompiled), and
    # several Special Forces rewards whose real name needed resolving
    # through a $variable$ indirection into research_l_english.yml/
    # unit_l_english.yml (the same cross-file pattern the 2026-10-08
    # subdoctrine-name audit already established).
    assert _reward_name("mobile_infantry", "cavalry_charge") == "Modernized Cavalry"
    assert _reward_name("large_unit_tactics", "wide_trench_networks") == "Overnight Entrenchment"

    # The 4 genuine source typos.
    assert _reward_name("field_engineering", "engineerdug_gun_emplacements") == "Engineer-dug Gun Emplacements"
    assert _reward_name("mission_type_tactics", "maneouver_drills") == "Combined Arms Battle Groups"
    assert _reward_name("anti_tank_frontline", "pakfront") == "Pakfront"
    assert _reward_name("tank_destroyer_force", "selfsufficient_battalion") == "Radio-Directed Breakthrough Containment"

    # Same reward key, different subdoctrine, genuinely different name.
    assert _reward_name("fire_concentration", "weakpoint_studies") == "Flanking Fire Emplacement"
    assert _reward_name("anti_tank_frontline", "weakpoint_studies") == "Weak-point Studies"
    assert _reward_name("assault_infantry", "assault_detachments") == "Assault Detachments"
    assert _reward_name("armored_spearhead", "assault_detachments") == "Flank Protection"

    assert len(SUBDOCTRINES_BY_KEY["peoples_war"]["rewards"]) == 4

    # Special Forces - real names resolved through a further indirection.
    assert _reward_name("mountaineers_1", "reward_2") == "Shared Instructors"
    assert _reward_name("mountaineers_2", "reward_1") == "Rough Terrain Specialists"
    assert _reward_name("marines_1", "reward_5") == "Mechanized Marine Corps"
    assert _reward_name("marines_2", "reward_1") == "Shore Parties"
    assert _reward_name("paratroopers_1", "reward_5") == "Best of the Best"
    assert _reward_name("paratroopers_2", "reward_1") == "Combat Insertion"
    assert _reward_name("rangers_1", "reward_5") == "Elite Rangers"
    assert _reward_name("rangers_2", "reward_2") == "Elevate the Rangers"
