from data.battalion_stats import BATTALION_STATS
from data.terrain import GENERIC_TERRAIN_MODIFIERS, UNIT_TERRAIN_MODIFIERS
from data.unit_categories import UNIT_CATEGORIES

# Confirmed 2026-09-29 against two real screenshots (see CLAUDE.md's Terrain
# section for the exact reconciliation) - matches the HOI4 wiki's own
# statement (https://hoi4.paradoxwikis.com/Terrain): "the attack value
# modifies the attacker's soft attack, hard attack, and breakthrough, and
# the defense value modifies the defender's soft attack, hard attack, and
# defense." One flat percentage per side (attack/defence), applied
# uniformly across all three of that side's fields - not a separate value
# per field, and not the same three fields on both sides (breakthrough is
# attack-only, defense is defence-only; soft_attack/hard_attack are shared).
ATTACK_SIDE_FIELDS = ["soft_attack", "hard_attack", "breakthrough"]
DEFENCE_SIDE_FIELDS = ["soft_attack", "hard_attack", "defense"]


def _doctrine_terrain_percentage(item_key, terrain_key, side_field, doctrine_bonuses):
    """A THIRD source of terrain percentage, added 2026-10-07: Doctrine's own
    terrain-nested unit_bonuses (data/doctrines.py - e.g. marines_2's
    "Marines: Amphibious Expeditionary" granting Pioneer Support
    `{"amphibious": {"attack": 0.15, "defence": 0.15, "movement": 0.15}}`
    the moment that subdoctrine is assigned to a track). This data was
    already compiled and already flows through logic/doctrines.py's
    active_unit_bonuses, but was never read here before - Ollie hit this
    directly (claimed Marines: Amphibious Expeditionary, picked Pioneer
    Support, selected Amphibious Assault terrain, saw no bonus at all) and
    confirmed it's a real, correct HOI4 mechanic this app was simply not
    applying, not a misremembered one.

    doctrine_bonuses is the raw (target_key, stat_dict) pair list
    logic/doctrines.py's active_unit_bonuses already returns (the SAME list
    logic/stats.py's own doctrine-bonus application already computes once
    per item - passed in here rather than recomputed, and rather than this
    module importing logic/doctrines.py itself, to keep every logic/*.py
    module other than stats.py - the one deliberate integration point -
    independent of each other). Category matching (a target_key may be a
    real item key or a HOI4 category_* tag) mirrors logic/stats.py's
    _sum_bonus_fields exactly. Stacks additively with the generic/per-unit
    layers below by the same established "sum every source, apply once"
    convention this project already uses everywhere else a percentage can
    have multiple contributors (doctrine's own flat-field bonuses, support-
    company equipment modifiers, Technology's unit_bonuses) - not
    independently confirmed by a screenshot for THIS specific stacking
    (unlike the generic+per-unit terrain stack, which is), but there's no
    HOI4-documented reason terrain percentages would stack under a
    different rule than every other percentage in this engine.

    Like the per-unit layer below, only "attack"/"defence" are ever read -
    a terrain-nested bonus's own "movement" field (present on marines_2's
    bonus above) is compiled but never applied anywhere in this app, same
    as every per-unit UNIT_TERRAIN_MODIFIERS movement field already is.
    """
    if not doctrine_bonuses:
        return 0.0
    item_categories = UNIT_CATEGORIES.get(item_key, set())
    total = 0.0
    for target_key, stat_dict in doctrine_bonuses:
        if target_key != item_key and target_key not in item_categories:
            continue
        total += stat_dict.get(terrain_key, {}).get(side_field, 0)
    return total


def terrain_percentage(item_key, terrain_key, is_attacking, doctrine_bonuses=None):
    """The total terrain percentage modifier for one item, in one terrain,
    on one side of combat. is_attacking=True means this item's division is
    attacking INTO terrain_key; False means it's defending WITHIN it - the
    same distinction the wiki quote above draws.

    Three sources stack additively:
    - A generic per-terrain-TYPE layer (data/terrain.py's
      GENERIC_TERRAIN_MODIFIERS, sourced from HOI4's own common/terrain/
      file) that applies to every unit regardless of type. It ONLY ever has
      an attack-side value in this game version - no terrain type defines a
      generic defence penalty at all, confirmed by direct read of
      terrain_copy/00_terrain.txt - so it contributes nothing when
      is_attacking is False.
    - A per-unit layer (UNIT_TERRAIN_MODIFIERS) specific to item_key,
      compiled from that item's own sub_unit block.
    - An optional Doctrine layer (doctrine_bonuses, see
      _doctrine_terrain_percentage above) - omitting it (the default) is
      byte-identical to before this source existed, matching every other
      optional parameter in this project (researched/doctrine/tank_designs
      on calculate_item_stats, etc.).

    The first two sources are both confirmed against real screenshots (see
    CLAUDE.md's Terrain section for the exact reconciliation math). Any of
    the three may be absent for a given item_key/terrain_key pair, which
    means a real, confirmed 0 (e.g. plain Infantry has no terrain data at
    all) - not a gap to guess at.
    """
    side_field = "attack" if is_attacking else "defence"
    total = 0.0
    if is_attacking:
        total += GENERIC_TERRAIN_MODIFIERS.get(terrain_key, {}).get("attack", 0)
    total += UNIT_TERRAIN_MODIFIERS.get(item_key, {}).get(terrain_key, {}).get(side_field, 0)
    total += _doctrine_terrain_percentage(item_key, terrain_key, side_field, doctrine_bonuses)
    return total


def division_terrain_percentage(item_keys, terrain_key, is_attacking, doctrine_bonuses=None):
    """The division's single representative terrain percentage, for a
    compact UI readout - not the same value calculate_item_stats' per-item
    terrain application uses internally (that stays exact, per item,
    untouched by this function), since a division mixing several item types
    has no single "the" terrain percentage the way one real HOI4 unit
    type's own tooltip does.

    NOT a plain average (corrected 2026-10-08 - see below). The real
    formula, reverse-engineered from a real screenshot (Template Examples/
    ingame_7_marines_1_mountaineer_pioneerSupport.png, a 9 Marine + 1
    Mountaineer + 1 Pioneer Support division with "Marines: Amphibious
    Expeditionary" active): the real Amphibious tooltip shows
    `Attack: 160% (Base: 145%, Pioneers: +15%)` and
    `Defence: 115% (Base: 100%, Pioneers: +15%)` - TWO separate numbers, not
    one blended average, and "Base" alone doesn't match a plain per-item
    average of the 11 items (that gives ~41%, not 45%).

    Reconciled exactly (both Attack AND Defence, to the percentage point) by
    COMBAT-WIDTH-WEIGHTED averaging across only the items with real combat
    width (battalions: Marine's own amphibious attack is 0.5 each,
    Mountaineer has none - (9*2*0.5 + 1*2*0) / (9*2+1*2) = 9.0/20 = 0.45,
    exactly "Base: 145%"), with items that have NO combat width (Pioneer
    Support - support companies are combat_width=0 by design, confirmed in
    units_copy/engineer.txt) contributing their own terrain_percentage() as
    a flat, UNWEIGHTED addition on top instead of being folded into the
    weighted average (where their own zero width would otherwise silently
    zero them out) - Pioneer Support's own 0 (no per-unit amphibious entry)
    + 0.15 (marines_2's doctrine bonus) = 0.15, exactly "Pioneers: +15%",
    and 0.45 + 0.15 = 0.60 matches the real 160% (+60%) exactly. The
    Defence side confirms the same split independently: weighted part is 0
    (neither Marine nor Mountaineer has an own amphibious defence value),
    flat part is Pioneer Support's own 0.15, total 0.15 - exactly matching
    the real "Defence: 115%".

    This makes intuitive HOI4 sense too: a battalion's own terrain modifier
    represents how THAT unit type performs and should scale with how much
    of the division's combat width it represents (same reasoning Piercing's
    own 40%-max/60%-average division formula already uses - a unit's
    influence should track its real battlefield presence); a support
    company's granted bonus (whether its own base value or a doctrine
    reward routed through it) is a division-wide perk, not diluted by unit
    count, matching how support-company equipment bonuses already apply as
    an undiluted percentage elsewhere in this app, not something to
    silently zero out just because the company itself has no combat width.

    For a division where EVERY item happens to have 0 total combat width
    (not reachable via the real /api/stats route, which always requires at
    least one battalion), the weighted-average term contributes 0 rather
    than dividing by zero.

    **The flat group is itself an AVERAGE, not a running sum (corrected
    2026-11-02)**: the single real screenshot above only ever exercised ONE
    zero-combat-width item (Pioneer Support) at a time, so "add every
    flat contributor's own percentage" and "average every flat
    contributor's own percentage" were indistinguishable by that evidence -
    they agree whenever there's only one. Ollie reported a real division
    mixing several Tank-Designer-fed support-company roles (e.g. an Anti-Air/
    Tank-Destroyer/SP-Artillery support trio) plus Mechanized showing an
    obviously-impossible terrain badge (over -300% in Mountain) - each of
    those support-role items is a genuine `combat_width = 0` HOI4 unit
    (confirmed directly against `Copies/units_copy/tank_destroyer_brigade.txt`/
    `flame_tank.txt`/`super_heavy_armor.txt` - these really are
    `group = support` with `combat_width = 0` in the real game files, not a
    data gap), so a SUM let their own, uncapped mountain penalties
    (generic -50% plus each one's own -10% to -90%) pile up without the
    bound a weighted AVERAGE already enforces on the battalion side -
    mathematically, a true average can never exceed the most extreme single
    contributor, while an unbounded sum of N contributors can reach N times
    that. Averaging the flat group the same way fixes the runaway blow-up
    while staying byte-identical to the one confirmed real screenshot (a
    single flat contributor's average of 1 value is that same value).

    **A second correction, same investigation (2026-11-02)**: averaging
    over EVERY flat (zero-combat-width) item - including ones with no
    terrain data at all for the selected terrain, which is most support
    companies most of the time - silently diluted a real contributor's
    percentage just by that irrelevant item's presence (e.g. adding a
    Signal Company, which has no terrain effect anywhere, alongside
    Pioneer Support dropped the screenshot-confirmed Amphibious attack
    badge from 0.60 to 0.525 with no other change). Fixed by excluding a
    flat item from the average's denominator entirely when its own
    terrain_percentage() is exactly 0 - a structural non-participant,
    not a real 0%-contributor the average should still be divided by.

    doctrine_bonuses is passed straight through to terrain_percentage for
    each item - see its own docstring. Omitting it (the default) is
    byte-identical to before this parameter existed.

    Returns 0 for an empty list - defensive only; the real /api/stats route
    never calls this with one, since it already returns early when no
    battalions are selected at all.
    """
    if not item_keys:
        return 0

    weighted_total = 0.0
    total_width = 0.0
    flat_total = 0.0
    flat_count = 0
    for key in item_keys:
        percentage = terrain_percentage(key, terrain_key, is_attacking, doctrine_bonuses)
        width = BATTALION_STATS[key].get("combat_width", 0)
        if width > 0:
            weighted_total += width * percentage
            total_width += width
        elif percentage != 0:
            # Only a flat item that actually HAS a terrain effect here joins
            # the average's denominator (real bug, found 2026-11-02): a
            # support company with no terrain data at all for this
            # terrain_key (the common case - 36 of 101 items have none)
            # contributes a true 0, and averaging it in anyway dilutes a
            # genuine contributor's percentage for no reason - e.g. adding
            # an inert Signal Company alongside Pioneer Support dropped the
            # real, screenshot-confirmed Amphibious attack badge from the
            # correct 0.60 to 0.525, just by being present. A flat item
            # with a real (possibly 0-valued-by-coincidence) contribution
            # is covered the same as before; only a structural non-
            # participant is excluded from the denominator.
            flat_total += percentage
            flat_count += 1

    weighted_average = (weighted_total / total_width) if total_width > 0 else 0.0
    flat_average = (flat_total / flat_count) if flat_count > 0 else 0.0
    return weighted_average + flat_average


def apply_terrain_modifier(stats, item_key, terrain_key, is_attacking, doctrine_bonuses=None):
    """Return a copy of an already-computed item stat block (from
    logic/stats.py's calculate_item_stats) with the relevant combat fields
    (ATTACK_SIDE_FIELDS or DEFENCE_SIDE_FIELDS, chosen by is_attacking)
    multiplied by (1 + terrain_percentage(...)) - a single percentage
    applied uniformly across that side's fields, exactly matching the wiki
    quote above. Multiple stacked sources (generic + per-unit + doctrine)
    are summed first, then applied as one multiplier - the same "sum
    same-field bonuses, then one (1 + total) multiplication" convention
    this project already uses for doctrine bonuses and support-company
    equipment modifiers, not compounding.

    doctrine_bonuses is passed straight through to terrain_percentage - see
    its own docstring. Omitting it (the default) is byte-identical to
    before this parameter existed.

    Returns the same stats dict unchanged when the percentage is exactly 0
    (the common case - most items have no terrain data for most terrain
    types), so calling this for a no-effect combination is always cheap and
    never risks a spurious floating-point edit.
    """
    percentage = terrain_percentage(item_key, terrain_key, is_attacking, doctrine_bonuses)
    if percentage == 0:
        return stats

    fields = ATTACK_SIDE_FIELDS if is_attacking else DEFENCE_SIDE_FIELDS
    new_stats = dict(stats)
    for field in fields:
        new_stats[field] = stats[field] * (1 + percentage)
    return new_stats
