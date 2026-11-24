from data.doctrines import DOCTRINE_TRACKS, GRAND_DOCTRINES, SUBDOCTRINES

_TRACKS_BY_KEY = {track["key"]: track for track in DOCTRINE_TRACKS}
_GRAND_DOCTRINES_BY_KEY = {gd["key"]: gd for gd in GRAND_DOCTRINES}
_SUBDOCTRINES_BY_KEY = {sd["key"]: sd for sd in SUBDOCTRINES}


def is_grand_doctrine_selectable(grand_doctrine_key, active_grand_doctrines):
    """Whether the grand doctrine at grand_doctrine_key can be selected,
    given the set of grand doctrine keys already active. Grand doctrines
    are mutually exclusive within their own folder (a country runs one
    land doctrine and, independently, one special_forces doctrine) - true
    unless another grand doctrine in the same folder is already active.
    """
    if grand_doctrine_key in active_grand_doctrines:
        return False

    folder = _GRAND_DOCTRINES_BY_KEY[grand_doctrine_key]["folder"]
    return not any(
        _GRAND_DOCTRINES_BY_KEY[key]["folder"] == folder for key in active_grand_doctrines
    )


def is_subdoctrine_selectable(subdoctrine_key, track_key, active_grand_doctrines, track_subdoctrines, researched):
    """Whether the subdoctrine at subdoctrine_key can be assigned to
    track_key right now, given which grand doctrines are active, which
    subdoctrine (if any) is already assigned to each track, and the set of
    researched technology keys (see logic/research.py).

    True when: track_key belongs to at least one currently active grand
    doctrine (all 4 land grand doctrines share the same 4 track names, so
    this is deliberately "any active grand doctrine has it", not a single
    fixed "owner" - whichever land grand doctrine is actually active is
    what makes its tracks available); track_key is one of the
    subdoctrine's own `tracks`; this exact subdoctrine isn't ALREADY
    assigned to a different track (real bug, found 2026-11-02 while
    building AI Design Comparison's own Doctrine search - a Special
    Forces subdoctrine's own `tracks` lists BOTH Special Forces tracks as
    eligible, since real HOI4 lets you put it on either one, but nothing
    here stopped it being assigned to EVERY eligible track simultaneously;
    reassigning this exact track to the key already there is still a
    no-op fine); no `xor` partner is already assigned to a *different*
    track; and, for the handful of Special Forces subdoctrines with a
    `requires_technology`, that technology is in `researched`.
    """
    subdoctrine = _SUBDOCTRINES_BY_KEY[subdoctrine_key]

    track_is_available = any(
        track_key in _GRAND_DOCTRINES_BY_KEY[gd_key]["tracks"] for gd_key in active_grand_doctrines
    )
    if not track_is_available:
        return False

    if track_key not in subdoctrine["tracks"]:
        return False

    for other_track, other_subdoctrine_key in track_subdoctrines.items():
        if other_track == track_key:
            continue
        if other_subdoctrine_key == subdoctrine_key:
            return False
        if other_subdoctrine_key in subdoctrine["xor"]:
            return False

    if subdoctrine["requires_technology"] is not None and subdoctrine["requires_technology"] not in researched:
        return False

    return True


def can_claim_next_reward(subdoctrine_key, claimed_rewards):
    """Whether the next reward (in listed order) of subdoctrine_key can be
    claimed. Rewards are a plain sequential checklist - no mastery-point
    simulation - so this is just "are there any left", but the name makes
    the sequential-only intent explicit at every call site.
    """
    total_rewards = len(_SUBDOCTRINES_BY_KEY[subdoctrine_key]["rewards"])
    already_claimed = claimed_rewards.get(subdoctrine_key, 0)
    return already_claimed < total_rewards


def is_track_mastered(track_key, track_subdoctrines, claimed_rewards):
    """Whether track_key's assigned subdoctrine has had every one of its
    rewards claimed. False if no subdoctrine is assigned yet.
    """
    subdoctrine_key = track_subdoctrines.get(track_key)
    if subdoctrine_key is None:
        return False

    total_rewards = len(_SUBDOCTRINES_BY_KEY[subdoctrine_key]["rewards"])
    return claimed_rewards.get(subdoctrine_key, 0) >= total_rewards


def unlocks_fifth_battalion_row(active_grand_doctrines, track_subdoctrines, claimed_rewards):
    """Whether the 5th battalion row is unlocked: true if any active grand
    doctrine has a track whose milestone sets additional_brigade_column_size
    AND that track is_track_mastered. Reads which track qualifies directly
    from the compiled milestone data (data/doctrines.py) rather than a
    hardcoded per-grand-doctrine mapping - see that file's header for how
    this was confirmed against the real game data.
    """
    for grand_doctrine_key in active_grand_doctrines:
        grand_doctrine = _GRAND_DOCTRINES_BY_KEY[grand_doctrine_key]
        for track_key, milestone in zip(grand_doctrine["tracks"], grand_doctrine["milestones"]):
            if "additional_brigade_column_size" not in milestone.get("modifiers", {}):
                continue
            if is_track_mastered(track_key, track_subdoctrines, claimed_rewards):
                return True

    return False


def active_unit_bonuses(active_grand_doctrines, track_subdoctrines, claimed_rewards):
    """Every `unit_bonuses` dict currently active, as a list of
    (target_key, stat_dict) pairs - target_key is either a real item key or a
    HOI4 `category_*` tag, exactly as data/doctrines.py stores it. Mirrors
    unlocked_subunit_keys's traversal (grand doctrine immediate effects; grand
    doctrine milestones, gated on is_track_mastered for that milestone's own
    track; subdoctrine immediate effects once assigned; claimed subdoctrine
    rewards in order) but collects `unit_bonuses` instead of
    `unlocks_subunits`. Returns the raw stat dicts as compiled - a dict may
    still contain a nested `battalion_mult` list or terrain-nested sub-dicts
    alongside plain fields; filtering to what's actually applicable is
    logic/stats.py's job, not this function's.
    """
    bonuses = []

    for grand_doctrine_key in active_grand_doctrines:
        grand_doctrine = _GRAND_DOCTRINES_BY_KEY[grand_doctrine_key]
        bonuses.extend(grand_doctrine["effects"].get("unit_bonuses", {}).items())

        for track_key, milestone in zip(grand_doctrine["tracks"], grand_doctrine["milestones"]):
            if is_track_mastered(track_key, track_subdoctrines, claimed_rewards):
                bonuses.extend(milestone.get("unit_bonuses", {}).items())

    for subdoctrine_key in track_subdoctrines.values():
        if subdoctrine_key is None:
            continue
        subdoctrine = _SUBDOCTRINES_BY_KEY[subdoctrine_key]
        bonuses.extend(subdoctrine["effects"].get("unit_bonuses", {}).items())

        claimed = claimed_rewards.get(subdoctrine_key, 0)
        for reward in subdoctrine["rewards"][:claimed]:
            bonuses.extend(reward["effects"].get("unit_bonuses", {}).items())

    return bonuses


def unlocked_subunit_keys(active_grand_doctrines, track_subdoctrines, claimed_rewards):
    """Every battalion/support-company/regimental-support key Doctrine has
    unlocked so far: the union of `unlocks_subunits` from every active
    grand doctrine's own effects (none currently define any, but checked
    for completeness/future-proofing), every subdoctrine currently
    assigned to a track, and every reward claimed so far on those
    subdoctrines. Mirrors logic/research.py's function of the same name -
    Composition's eventual picker filtering needs to check both once
    Doctrine is wired in, not just this one.
    """
    unlocked = set()

    for grand_doctrine_key in active_grand_doctrines:
        unlocked.update(_GRAND_DOCTRINES_BY_KEY[grand_doctrine_key]["effects"].get("unlocks_subunits", []))

    for subdoctrine_key in track_subdoctrines.values():
        if subdoctrine_key is None:
            continue
        subdoctrine = _SUBDOCTRINES_BY_KEY[subdoctrine_key]
        unlocked.update(subdoctrine["effects"].get("unlocks_subunits", []))

        claimed = claimed_rewards.get(subdoctrine_key, 0)
        for reward in subdoctrine["rewards"][:claimed]:
            unlocked.update(reward["effects"].get("unlocks_subunits", []))

    return unlocked
