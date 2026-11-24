from data.army_spirits import ARMY_SPIRITS

_ARMY_SPIRITS_BY_KEY = {spirit["key"]: spirit for spirit in ARMY_SPIRITS}


def is_army_spirit_selectable(spirit_key, active_spirits, active_grand_doctrines, track_subdoctrines):
    """Whether the Army Spirit at spirit_key can be selected right now.

    Mirrors logic/doctrines.py's is_grand_doctrine_selectable: Army Spirits
    are mutually exclusive within their own category (this app's whole
    analog to the real game's "idea slot" - one Academy, one Army, one
    Division Command spirit active at a time), so already being active
    makes no difference here - selecting it again is a no-op the caller
    handles, not a reason to say no.

    Also requires spirit_key's own `available` list (a flat list of
    doctrine/subdoctrine keys, OR semantics - see data/army_spirits.py's
    header) to intersect whichever doctrines/subdoctrines are currently
    active. An empty `available` list (most academy_spirit entries, plus
    any entry gated by something this app doesn't model - a building, a
    government type, a DLC flag) means always selectable.
    """
    spirit = _ARMY_SPIRITS_BY_KEY[spirit_key]
    if not spirit["available"]:
        return True

    active = active_grand_doctrines | set(track_subdoctrines.values())
    return any(key in active for key in spirit["available"])


def _active_modifier_factor(field_name, active_spirits):
    """Sum of every currently active Army Spirit's own `field_name` entry in
    its `modifiers` dict - the shared country-wide-percentage-bonus
    mechanism behind active_army_strength_factor/active_breakthrough_factor/
    active_supply_consumption_factor/active_army_speed_factor below (all 4
    of this app's compiled country-wide fields, confirmed 2026-11-02/03 via
    real in-game tooltips to be percentages applying once at the whole-
    division level, not a per-item/category one like unit_bonuses/
    equipment_bonus elsewhere in this app). Summing (rather than hardcoding
    one key per field) means a second Army Spirit sharing the same field
    would combine correctly too, matching every other additive-percentage-
    bonus convention in this app (suppression_factor, supply_consumption_factor,
    etc.) - today Flexible Organization/Maneuver Warfare both carry
    `army_speed_factor`, though being the same `division_command_spirit`
    category means at most one is ever active at once in practice.

    A key in active_spirits that ISN'T in the current ARMY_SPIRITS compile
    is skipped rather than raising KeyError - real, found 2026-11-02: the
    same-day rescope from 40 to 9 entries removed 31 keys a real persisted
    session could already have selected (e.g. bold_attack_spirit, an
    academy_spirit entry that no longer exists at all), and this function
    is called on every /api/stats and /api/design-search request - this
    was the first time this project ever REMOVED an already-shippable
    selectable entry, so this exact "stale persisted key" risk never came
    up for Research/Doctrine/Tank Designer, which have only ever added or
    renamed entries, never deleted one a save could reference.
    """
    return sum(
        spirit["modifiers"].get(field_name, 0)
        for key in active_spirits
        if (spirit := _ARMY_SPIRITS_BY_KEY.get(key)) is not None
    )


def active_army_strength_factor(active_spirits):
    """Confirmed directly in-game (2026-11-02): Operational Reserves' own
    real tooltip reads "HP: +10.00%" for its compiled `army_strength_factor:
    0.1` - HP being this app's Max Strength field.
    """
    return _active_modifier_factor("army_strength_factor", active_spirits)


def active_breakthrough_factor(active_spirits):
    """Confirmed directly in-game (2026-11-03): Smoke and Fire's own real
    tooltip reads "Breakthrough: +6.00%" for its compiled
    `breakthrough_factor: 0.06` - a country-wide bonus to the whole
    division's Breakthrough, applied the same `(1 + bonus)` way
    active_army_strength_factor's own field already is.
    """
    return _active_modifier_factor("breakthrough_factor", active_spirits)


def active_supply_consumption_factor(active_spirits):
    """Confirmed directly in-game (2026-11-03): Logistical Focus's own real
    tooltip reads "Supply Consumption: -10.0%" for its compiled
    `supply_consumption_factor: -0.10` - a country-wide contribution into
    the SAME division-level `(1 + total)` multiplier Technology's own
    per-item supply_consumption_factor bonuses already feed
    (logic/stats.py's calculate_division_stats), not a second, separate
    multiplier layer.
    """
    return _active_modifier_factor("supply_consumption_factor", active_spirits)


def active_army_speed_factor(active_spirits):
    """Confirmed directly in-game (2026-11-03): both Flexible Organization
    and Maneuver Warfare's real tooltips read "Divisions speed: +5.00%"
    for their identically-named compiled `army_speed_factor: 0.05` fields -
    a country-wide bonus applied to the division's already-computed
    (bottleneck/min) Max Speed, the same `(1 + bonus)` pattern as every
    other country-wide field here.
    """
    return _active_modifier_factor("army_speed_factor", active_spirits)


def active_equipment_bonuses(active_spirits):
    """Every currently active Army Spirit's own `equipment_bonus` entries,
    flattened to (equipment_key, stat_dict) pairs - mirrors
    logic/doctrines.py's active_unit_bonuses/logic/research.py's
    active_tech_unit_bonuses own return shape, but targets an EQUIPMENT
    family directly (data/equipment.py's own key space - e.g.
    "infantry_equipment"), not an item/category the way unit_bonuses does.
    A structurally different application point: these are applied at
    logic/stats.py's own equipment-resolution step, before an item's own
    stats are combined in, not via the UNIT_CATEGORIES-based item/category
    matching unit_bonuses uses.

    Confirmed 2026-11-03 via real in-game tooltips (all 4 of this app's
    compiled equipment_bonus-bearing spirits) to be PERCENTAGE bonuses on
    the equipment's own resolved stat, not flat adds - e.g. All-Arms
    Anti-tank Defense's own tooltip reads "Infantry Equipment: Hard
    Attack: +25%" for its compiled {"infantry_equipment": {"hard_attack":
    0.25}}; Direct Fire Support's reads "Hard Attack: +50%"/"Piercing:
    +100%" per tank-artillery-chassis size for its compiled 0.50/1 values;
    Rapid Emplacement's reads "Breakthrough: +10%"/"Defense: +10%" per
    equipment type; Subsidized Contracts' reads "Production Cost: -15.00%"/
    "-10.00%" per equipment type.
    """
    pairs = []
    for key in active_spirits:
        spirit = _ARMY_SPIRITS_BY_KEY.get(key)
        if spirit is None:
            continue
        for equipment_key, stat_dict in spirit["equipment_bonus"].items():
            pairs.append((equipment_key, stat_dict))
    return pairs


def active_spirit_in_category(category, active_spirits):
    """The spirit key currently active in `category`, or None - mirrors
    doctrines.js's own "find the active key in this folder" lookup
    (static/js/doctrines.js's renderFolders), exposed here so callers on
    both sides of the stack (Python tests, the JS mirror) share the same
    definition of "the category's current selection."
    """
    for key in active_spirits:
        if _ARMY_SPIRITS_BY_KEY[key]["category"] == category:
            return key
    return None
