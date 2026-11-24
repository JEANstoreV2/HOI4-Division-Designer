from data.battalion_stats import BATTALION_STATS
from data.equipment import EQUIPMENT
from data.equipment_needs import EQUIPMENT_NEEDS
from data.equipment_tiers import EQUIPMENT_TIERS
from data.technologies import TECHNOLOGIES
from data.unit_categories import UNIT_CATEGORIES
from logic.army_spirits import (
    active_army_speed_factor,
    active_army_strength_factor,
    active_breakthrough_factor,
    active_equipment_bonuses,
    active_supply_consumption_factor,
)
from logic.doctrines import active_unit_bonuses
from logic.research import active_tech_unit_bonuses
from logic.special_projects import active_special_project_unit_bonuses
from logic.tank_designer import calculate_tank_design_stats
from logic.terrain import apply_terrain_modifier

# Combat stats come from two places: the item's own sub_unit definition
# (data/battalion_stats.py) and whatever equipment it needs
# (data/equipment.py). For a line battalion these combine as own + equipment
# (flat addition), equipment applying at full value regardless of quantity
# needed - confirmed extensively (e.g. Mechanized's own +4.0 hard_attack
# plus Infantry Equipment's own value, matching real screenshots exactly).
#
# Support companies and regimental support items work differently: the
# same-named fields on their sub_unit entry (e.g. "Support Artillery"'s
# `soft_attack = -0.4` in units_copy/artillery.txt) are PERCENTAGE
# modifiers on the equipment's stat, not flat additions - own is really
# "own% of equipment", i.e. equipment x (1 + own). The HOI4 wiki documents
# this directly ("Equipment Modifier: -40% Soft Atk., Hard Atk., Defence &
# Breakthrough" for Support Artillery), and it reproduces real numbers
# exactly: Support Artillery (needs 12 Artillery Equipment, own -0.4) gives
# 25 x 0.6 = 15.0 real soft attack contribution; Infantry Gun/field_guns
# (needs 4, own -0.7) gives 25 x 0.3 = 7.5; Anti-Air Battery (needs 12
# anti_air_equipment, own -0.8/-0.8/-0.6/-0.8/air -0.6) matches on every
# one of soft/hard/defense/breakthrough/air_attack. The raw game files use
# the identical field name for both mechanics - there's no way to tell
# them apart syntactically, only by which composition slot the item is
# used in.
#
# That last point matters: a handful of keys (e.g. "light_flame_tank")
# are selectable as BOTH a battalion and a support company - the exact
# same sub_unit definition, offered in two different slots - so which
# formula applies can't be looked up from the key alone. calculate_item_stats
# takes it as an explicit parameter instead.
COMBAT_STAT_FIELDS = [
    "soft_attack", "hard_attack", "defense", "breakthrough",
    "ap_attack", "air_attack", "armor_value", "hardness",
]

# A battalion's own "breakthrough" field (data/battalion_stats.py) is a
# PERCENTAGE of its equipment's own breakthrough, not a flat add like every
# other battalion combat-stat field - confirmed 2026-10-08 (see
# calculate_item_stats' COMBAT_STAT_FIELDS loop) against six independent
# real data points: an old, zero-ambiguity one from 2026-09-29
# (tests/test_division_stats.py's "Mountaineers breakthrough anomaly" -
# 5x Mountaineers, NO doctrine/tech involved at all, real Breakthrough 13.0
# vs the old flat-add formula's 11.5; `5 x (2 x (1 + 0.3)) = 13.0` matches
# EXACTLY, no rounding ambiguity whatsoever) and five from the same-day
# Marine/Special-Forces investigation (Infantry/Paratrooper, which have NO
# own breakthrough field at all, vs Marine/Mountaineer/Ranger, which do -
# the percentage-vs-flat distinction fully explains why only the latter
# three showed an unexplained gap, with no hidden per-unit multiplier
# needed at all). This is the SAME real value already compiled separately
# in data/tank_role_combat_modifiers.py for Tank Designer's own custom-
# design calculation (light_armor's own 0.15 there matches its own 0.15
# here, light_tank_destroyer_brigade's -0.42 matches too, etc.) - that
# finding (Tank Designer Phase 5, 2026-09-16) and this one are almost
# certainly the exact same underlying HOI4 mechanic, independently
# rediscovered; fixing it here brings plain Composition (default equipment,
# no custom Tank Designer save) in line with what Tank Designer's own
# calculation has used for Armor battalions all along.
_BATTALION_OWN_PERCENTAGE_FIELDS = {"breakthrough"}

STRUCTURAL_STAT_FIELDS = [
    "max_strength", "max_organisation", "default_morale", "manpower",
    "training_time", "weight", "supply_consumption", "suppression",
    "combat_width", "max_speed",
]

# Not a flat stat - a percentage bonus to division Suppression (see
# calculate_division_stats). Kept separate from STRUCTURAL_STAT_FIELDS
# since it doesn't sum in the same way; currently only Military Police
# variants define it.
SUPPRESSION_FACTOR_FIELD = "suppression_factor"

# Same shape as SUPPRESSION_FACTOR_FIELD - a percentage bonus to division
# Supply Use (see calculate_division_stats), summed across every item then
# applied once. Confirmed via Logistics Company's own innate -10% (see
# data/battalion_stats.py) plus Logistics Company II's technology bonus
# stacking on top of it (Template Examples/, 2026-09-30 - see the Technology
# unit_bonuses block below for the full reasoning). fuel_consumption_factor
# is the same shape but has no tracked division stat to multiply, so it
# stays compiled-but-unapplied like every other untracked field.
SUPPLY_CONSUMPTION_FACTOR_FIELD = "supply_consumption_factor"

# Reverse lookup built once: which technology unlocks a given
# EQUIPMENT_TIERS entry, keyed the same way EQUIPMENT_TIERS is (e.g.
# "infantry_equipment_2" -> "improved_infantry_weapons"). Used by
# _equipment_stats to check whether a tier has actually been researched.
_TIER_UNLOCK_TECH = {
    tier_key: tech["key"]
    for tech in TECHNOLOGIES
    for tier_key in tech["unlocks_equipment"]
    if tier_key in EQUIPMENT_TIERS
}


def _equipment_stats(equipment_key, researched, tank_designs, equipment_overrides=None):
    """Resolve one equipment family's stat block. `tank_designs` is checked
    first: an optional {equipment_key: design_params} dict (see
    calculate_item_stats' docstring) - a custom Tank Designer design always
    wins over the research-tier lookup below when one's been built for that
    equipment family, exactly the way a real HOI4 player's saved design
    replaces the family's default tier the moment it exists. This is why
    data/tank_chassis.py's/data/tank_role_combat_modifiers.py's chassis/role
    keys were worth keeping identical to data/equipment.py's own equipment
    keys back in Phase 1 (confirmed, not a coincidence: "medium_tank_chassis"
    names both) - no separate mapping is needed to find which equipment
    family a design replaces.

    Falling through to the pre-Tank-Designer behaviour: `researched` is
    None means "no research state passed" - callers that never pass it get
    today's exact behaviour (EQUIPMENT[key] directly), so this is purely
    additive over the pre-Research baseline.

    When a research state IS passed, the highest tier whose unlocking
    technology is in `researched` wins - not the highest tier that exists,
    and not assuming EQUIPMENT[key] is the floor (motorized_equipment and
    armored_car_equipment both have a real tier BELOW today's baseline,
    unlocked before their "no research done" tier - see
    data/equipment_tiers.py). Falls back to EQUIPMENT[key] if no tier of
    this family has been researched at all - this shouldn't normally
    happen, since a subunit and its baseline equipment tier are always
    unlocked by the same technology, but stays safe rather than crashing if
    a caller passes an inconsistent research state (e.g. in a test).

    `equipment_overrides` (added 2026-11-03, Patch Impact Preview - see
    data/patches.py) is an optional {equipment_key: {field: value}} dict of
    ABSOLUTE replacement values, applied LAST, on top of whichever of the
    3 branches above resolved - independent of research state or a custom
    Tank Designer design, exactly what "this field changes in the next
    patch" should mean. Omitting it (the default) is byte-identical to
    before this parameter existed.
    """
    if tank_designs and equipment_key in tank_designs:
        resolved = calculate_tank_design_stats(**tank_designs[equipment_key])
    elif researched is None:
        resolved = EQUIPMENT[equipment_key]
    else:
        candidates = [
            tier for key, tier in EQUIPMENT_TIERS.items()
            if tier["family"] == equipment_key and _TIER_UNLOCK_TECH.get(key) in researched
        ]
        resolved = max(candidates, key=lambda tier: tier["tier"]) if candidates else EQUIPMENT[equipment_key]

    if equipment_overrides and equipment_key in equipment_overrides:
        resolved = {**resolved, **equipment_overrides[equipment_key]}
    return resolved


def _apply_equipment_bonus(equipment_key, stats, equipment_bonus_pairs):
    """Officer Corps' own equipment_bonus (added 2026-11-03, see
    logic/army_spirits.py's active_equipment_bonuses) targets an equipment
    FAMILY directly, not an item/category - applied here, once per
    equipment key, AFTER _equipment_stats has already resolved (and
    possibly Patch-Preview-overridden) that family's base stats, so an
    active Army Spirit's bonus always modifies whatever the real/patched
    base currently is. Multiple matching bonuses to the same field sum
    first, then apply as one `(1 + total)` multiplier - the same
    convention every other percentage-stacking case in this app already
    uses (suppression, doctrine/tech percentage fields, etc.). A no-op
    (same dict returned) when nothing targets this equipment_key.
    """
    totals = {}
    for target_key, stat_dict in equipment_bonus_pairs:
        if target_key != equipment_key:
            continue
        for field, value in stat_dict.items():
            totals[field] = totals.get(field, 0) + value
    if not totals:
        return stats
    return {**stats, **{field: stats.get(field, 0) * (1 + total) for field, total in totals.items()}}


# Doctrine effect field names that mean the same thing as one of our own
# STRUCTURAL_STAT_FIELDS/COMBAT_STAT_FIELDS/SUPPRESSION_FACTOR_FIELD entries,
# just spelled differently in doctrines_copy/ - confirmed by hand rather than
# guessed at (only one found so far).
_DOCTRINE_FIELD_ALIASES = {"maximum_speed": "max_speed"}

# max_organisation is a genuine flat addition - confirmed by every value in
# data/doctrines.py being a whole number (2, 5, 10, 20...) matching HOI4's
# own "+X Org" tooltip convention, never a fraction. suppression_factor is
# also treated as a flat add to the item's own field: it's already a
# fraction that gets summed across every item and applied once as a single
# (1 + total) multiplier at the division level (see calculate_division_stats)
# - a doctrine bonus to it is just another flat contribution into that same
# sum, not a second layer of percentage-on-percentage.
#
# combat_width and max_strength are ALSO flat, despite being small fractions
# in the source data like the percentage fields below - both were gotten
# wrong on the first pass (assumed percentage by analogy with the combat-stat
# fields) and corrected from real gameplay evidence Ollie supplied
# (Template Examples/, 2026-09-16):
# - combat_width: Large Unit Tactics' "Flexible Division Structures" reward
#   (combat_width: -0.3 on category_all_infantry) took Infantry from 2 to
#   1.7 in-game (flat -0.3), not 1.4 (2 x 0.7, this tool's answer before the
#   fix).
# - max_strength: Grand Battleplan + Mounted Infantry's "Beasts of War"
#   reward (max_strength: 0.05 on category_cavalry) took a 5-Cavalry
#   division's HP from 125.0 to 125.2 (~125.25, i.e. +0.05 per battalion x 5,
#   flat), nowhere near the ~131.25 a percentage reading would give
#   (25 x 1.05 x 5). Cross-checked against a second, independent example
#   (Grand Battleplan + Field Engineering's "Sapper Fieldcraft" reward,
#   max_strength: 0.25 on the Engineer support company: 127.0 -> 127.2,
#   consistent with flat +0.25 and nowhere near flat/percentage's ~127.5).
_DOCTRINE_FLAT_FIELDS = {"max_organisation", SUPPRESSION_FACTOR_FIELD, "combat_width", "max_strength"}

# max_speed is neither simple flat nor a percentage of the item's own current
# speed - it's a percentage of HOI4's fixed base land-unit speed constant
# (4 km/h, the same reference leg/mounted units' own listed speed is already
# built from - see the note in Activity_Log.md, 2026-09-14, on how
# data/battalion_stats.py's own max_speed values were derived), added as a
# flat km/h delta. Confirmed exactly by the same Beasts of War example above:
# Cavalry's max_speed went from 6.4 to 8.4 km/h - not 6.9 (a literal flat
# +0.5) and not 9.6 (6.4 x 1.5, a percentage-of-current reading) - but
# exactly 6.4 + (0.5 x 4.0) = 8.4. Only confirmed for a leg/mounted unit;
# vehicle-transported units (whose own speed instead comes from equipment
# tier, a different mechanic entirely per that same 2026-09-14 note) aren't
# independently verified to follow this same rule yet.
_DOCTRINE_SPEED_SCALED_FIELDS = {"max_speed"}
_LEG_UNIT_BASE_SPEED_KMH = 4.0

# Every other doctrine-targetable field (every COMBAT_STAT_FIELDS entry, plus
# default_morale/supply_consumption) is treated as a PERCENTAGE bonus applied
# to the item's own already-resolved (own+equipment) stat - inferred the same
# way combat_width/max_strength originally were (small-fraction values in
# data/doctrines.py, matching HOI4's well-known "+10% Soft Attack"-style
# tooltips for the combat stats specifically), which those two corrections
# prove is not, by itself, reliable evidence for every field. Confidence is
# highest for the COMBAT_STAT_FIELDS entries (soft/hard attack, defense,
# breakthrough, piercing, air attack, armor, hardness) - percentage combat
# bonuses are one of the most commonly cited HOI4 doctrine mechanics, and
# this reading has now been cross-checked against two independent
# Template Examples/ screenshots without contradiction (small residual
# differences in both were consistent with data/battalion_stats.py's own
# already-flagged "first pass, worth spot-checking" caveat on the affected
# support company, not a formula error). default_morale/supply_consumption
# remain unconfirmed either way - not yet contradicted, but not
# independently verified either.
# Multiple bonuses to the same field stack additively as percentages
# (summed first, then one (1 + total) multiplication) rather than
# compounding - the same convention this project already uses for
# suppression and for support companies' own equipment-modifier fields.
#
# Only fields matching one of these three sets (after aliasing) are ever
# applied - everything else data/doctrines.py compiled (recon, initiative,
# reliability, entrenchment, acclimatization_*, equipment_capture_factor,
# casualty_trickleback, terrain-nested sub-dicts, battalion_mult lists) has
# no tracked equivalent here and is silently skipped, not guessed at.
# Doctrine's own terrain-nested sub-dicts (e.g. rangers_1's own
# {"forest": {...}}) are a different data shape from the standalone
# Terrain feature (data/terrain.py/logic/terrain.py, applied separately via
# calculate_item_stats' own `terrain` parameter below) - the two are not
# cross-applied. See Specification.md's "Modifier interaction engine" note
# and Activity_Log.md, 2026-09-15, for what's deliberately left unapplied
# and why (battalion_mult, equipment_bonus, doctrine's terrain-nested
# bonuses, and country/army-wide `modifiers` all fall outside
# calculate_item_stats' doctrine-bonus handling).
_DOCTRINE_PERCENTAGE_FIELDS = (
    set(STRUCTURAL_STAT_FIELDS) | set(COMBAT_STAT_FIELDS)
) - _DOCTRINE_FLAT_FIELDS - _DOCTRINE_SPEED_SCALED_FIELDS
_APPLICABLE_DOCTRINE_FIELDS = _DOCTRINE_FLAT_FIELDS | _DOCTRINE_SPEED_SCALED_FIELDS | _DOCTRINE_PERCENTAGE_FIELDS


def _sum_bonus_fields(item_key, bonus_pairs, applicable_fields, field_aliases=None):
    """Shared by _doctrine_bonus_for_item and _tech_bonus_for_item: sum
    every applicable stat field from bonus_pairs (a list of (target_key,
    stat_dict) pairs) that targets item_key directly or a category item_key
    belongs to (data/unit_categories.py). Field names are aliased first when
    field_aliases is given; anything not in applicable_fields afterwards is
    ignored. Every matching field's contributions are summed together
    regardless of source - the caller decides how to apply the total.
    """
    item_categories = UNIT_CATEGORIES.get(item_key, set())
    totals = {}

    for target_key, stat_dict in bonus_pairs:
        if target_key != item_key and target_key not in item_categories:
            continue
        for field, value in stat_dict.items():
            if field_aliases:
                field = field_aliases.get(field, field)
            if field not in applicable_fields:
                continue
            totals[field] = totals.get(field, 0) + value

    return totals


def _doctrine_bonus_for_item(item_key, doctrine_bonuses):
    """doctrine_bonuses is a list of (target_key, stat_dict) pairs from
    logic/doctrines.py's active_unit_bonuses - see _sum_bonus_fields. The
    caller (calculate_item_stats) decides whether the summed total is a flat
    add or a single percentage multiplier based on _DOCTRINE_FLAT_FIELDS.
    """
    return _sum_bonus_fields(item_key, doctrine_bonuses, _APPLICABLE_DOCTRINE_FIELDS, _DOCTRINE_FIELD_ALIASES)


# --- Technology-granted unit_bonuses (Phase C, 2026-09-30; corrected 2026-10-08) ---
#
# data/technologies.py's own unit_bonuses field (compiled 2026-09-29) is the
# exact same shape as data/doctrines.py's, but Ollie's real screenshots
# (Template Examples/, 2026-09-30) proved it does NOT follow the same
# application rule for SUPPORT-TYPE items - confirming the plan's own
# warning not to assume Doctrine's classification carries over.
#
# 1. For support-company/regimental-support items (is_support_type=True),
#    COMBAT_STAT_FIELDS bonuses are summed into the item's OWN percentage
#    field BEFORE the single equipment multiplication - a different rule
#    from Doctrine's, which multiplies a SEPARATE layer on top of the
#    already-resolved stat. Confirmed by antitank1's category_anti_tank
#    bonus (hard_attack: 0.1, ap_attack: 0.2) moving a 5x Infantry + 1x
#    Anti-Tank Battery division exactly
#    (5_infantry_guns_0_1_antitankBattery.png, "Anti-Tank" only, vs
#    5_infantry_guns_0_1_antitankBattery_improvedAntitank.png, + "Improved
#    Anti-Tank" = antitank1): Hard Attack 9.5 -> 11.5, matching
#    equipment_total x (1 + own% + tech%) = 20 x (1 - 0.65 + 0.1) = 9.0
#    (+2.5 from Infantry) exactly; Piercing 24.4 -> 30.4, matching
#    60 x (1 - 0.2 + 0.2) = 60.0 within the same ~0.1 display-rounding the
#    pre-bonus baseline already showed.
#
#    For BATTALIONS (is_support_type=False), which have no "own%" slot to
#    merge a tech bonus into (their own combat stats are flat adds), the
#    bonus instead applies as a SEPARATE multiplicative layer on the
#    already-resolved own+equipment total - the same mechanism Doctrine's
#    own percentage fields already use for battalions. This corrects a
#    2026-09-30 "confirmed zero on battalions" conclusion (infantry_at's
#    category_all_infantry bonus allegedly producing a byte-identical
#    Combat Stats panel on a plain 5x Infantry division,
#    5_infantry_guns_0.png vs 5_infantry_guns_0_all_antiTank_research.png)
#    that turned out to be a mislabeled test, not a real negative result -
#    that "after" screenshot's Soft Attack was ALSO byte-identical to
#    "before" (15.0 both), which is impossible if infantry_at's own
#    prerequisite chain (improved_infantry_weapons, which unlocks a higher
#    infantry_equipment tier) had genuinely been researched, since the tier
#    change alone would have moved Soft Attack. The real research state
#    almost certainly never included infantry_at/infantry_at2 at all - an
#    easy mix-up given "Infantry Anti-Tank I/II" (an Infantry-branch tech)
#    and the regimental Anti-Tank Battery's own "Anti-Tank I-IV" line
#    (Artillery branch) share near-identical names but are structurally
#    unrelated. Found and corrected 2026-10-08 via a real Marine-division
#    screenshot (Template Examples/ingame_7_marines_1_mountaineer_pioneerSupport.png)
#    whose Hard Attack (32.0) and Piercing (28.9) only reconciled exactly
#    once this multiplicative battalion rule was applied - confirmed
#    against the live division, not just reasoned about; see
#    Activity_Log.md, 2026-10-08, for the full investigation and the real
#    in-game "Infantry Anti-Tank I/II" tooltip
#    (infantry_antitank_research.png) that first suggested it.
#
# 2. SUPPLY_CONSUMPTION_FACTOR_FIELD bonuses mirror SUPPRESSION_FACTOR_FIELD's
#    EXISTING division-level mechanic exactly - summed across every item's
#    own factor value plus every applicable tech bonus, applied ONCE as a
#    single (1 + total) multiplier on the division's aggregated stat.
#    Confirmed by Logistics Company (LogisticsCompany1.png,
#    5_infantry_guns_0_logisticsCompany_1.png,
#    5_infantry_guns_0_logisticsCompany_2.png): the item's own
#    supply_consumption_factor (-0.10, see data/battalion_stats.py) took a
#    5x Infantry division's Supply Use from 0.30 to 0.27 (0.30 x 0.90) with
#    no tech researched at all; adding Logistics Company II's tech bonus
#    (unit_bonuses: {"logistics_company": {"supply_consumption_factor": -0.1,
#    ...}}) took it to 0.24 (0.30 x (1 - 0.10 - 0.10) = 0.30 x 0.80 - summed,
#    not compounded, exactly matching suppression_factor's existing
#    convention) with no rounding ambiguity at all.
#
# Every other unit_bonuses field this project compiles (structural flat
# fields like max_organisation/combat_width/max_strength/hardness,
# fuel_consumption_factor and the other _factor fields with no tracked
# division stat to multiply, acclimatization_*, reliability_factor,
# equipment_capture_factor, recovery, casualty_trickleback,
# experience_loss_factor, battalion_mult, terrain-nested sub-dicts) stays
# compiled-but-unapplied - not independently verified, not guessed at,
# matching Doctrine's own precedent before its own fields were each checked.
#
# A completed Special Project's own direct unit_bonuses (data/special_projects.py,
# added 2026-10-07 - e.g. Large Caliber Kinetic Energy Sabot's hidden Piercing
# bonus, found via a real in-game screenshot with no equivalent anywhere in
# this app's previously-compiled data) feed into this exact same pipeline,
# not a separate one - mechanically it's just another unit_bonuses-carrying
# technology in HOI4's own engine (a hidden, unresearchable one, auto-granted
# the instant the project completes), so there's no reason to expect a
# different application rule, and nothing in the screenshot evidence
# suggested one.
#
# max_organisation (added 2026-10-08) was found missing entirely while
# investigating the same real Marine-division discrepancy as the battalion
# fix above: a whole cluster of real, compiled technologies
# (marines2/marines3/tech_mountaineers2/tech_mountaineers3, and surely
# others - elite_forces/advanced_special_forces were two more examples at
# the time this was written, since removed from the compile 2026-11-03,
# see data/technologies.py's own removal note) grant a flat
# max_organisation bonus, but this field was never in
# _APPLICABLE_TECH_FIELDS at all - neither the support-type nor the
# battalion branch below ever read it, so every one of these bonuses was
# silently dropped everywhere, unlike Doctrine's own max_organisation
# bonuses (_DOCTRINE_FLAT_FIELDS), which were always correctly applied.
# Structural, not combat-stat - applied as a flat add regardless of
# is_support_type, mirroring SUPPLY_CONSUMPTION_FACTOR_FIELD's own existing
# treatment exactly (both are read directly off own_stats + tech_bonus, not
# routed through the COMBAT_STAT_FIELDS loop at all).
_APPLICABLE_TECH_FIELDS = set(COMBAT_STAT_FIELDS) | {SUPPLY_CONSUMPTION_FACTOR_FIELD, "max_organisation"}


def _tech_bonus_for_item(item_key, tech_bonuses):
    """tech_bonuses is a list of (target_key, stat_dict) pairs, pooled from
    logic/research.py's active_tech_unit_bonuses AND
    logic/special_projects.py's active_special_project_unit_bonuses (both
    return the identical shape - see _sum_bonus_fields). The caller
    (calculate_item_stats/calculate_division_stats) applies COMBAT_STAT_FIELDS
    and SUPPLY_CONSUMPTION_FACTOR_FIELD differently - see the block comment
    above, not _DOCTRINE_FLAT_FIELDS-style field sets, since these bonuses
    don't share Doctrine's classification.
    """
    return _sum_bonus_fields(item_key, tech_bonuses, _APPLICABLE_TECH_FIELDS)


# --- battalion_mult: cross-unit auras (added 2026-10-08) ---
#
# A unit's own `battalion_mult` (data/battalion_stats.py's own field - a raw
# unit's innate aura, e.g. Pioneer Support granting +15% Breakthrough to
# every category_marines item in the division) or one nested inside a
# Doctrine/Technology/Special-Project `unit_bonuses` entry (data/doctrines.py,
# data/technologies.py - already compiled, previously always ignored) grants
# a bonus to every OTHER item in the SAME division belonging to a given
# category - a genuinely different shape from every other unit_bonuses field,
# which always targets the GRANTING item itself. This was deliberately out
# of scope project-wide until 2026-10-08 (Cavalry Recon's own +10% soft_attack
# to category_artillery, `tests/test_division_stats.py`'s own long-documented
# "battalion_mult gap"), when a real screenshot comparison confirmed Pioneer
# Support's own aura was the final missing piece of a Marine-division
# Breakthrough discrepancy - see Activity_Log.md, 2026-10-08, for the full
# investigation and confirmation math.
#
# Unlike every other bonus source in this module, battalion_mult cannot be
# resolved per-item in calculate_item_stats (it needs to know about every
# OTHER item in the division) - it's applied as a final pass in
# calculate_division_stats instead, after every item's own calculate_item_stats
# (own+equipment+tech+doctrine+terrain) is already fully resolved. Each
# source's own `"add"` key (present only when the raw HOI4 source has an
# active, uncommented `add = yes`) decides flat vs percentage per bonus,
# the exact same convention this project's own data/doctrines.py and
# data/technologies.py compiles already use for their own battalion_mult
# entries - matching the ONE real, confirmed case (Pioneer Support's own
# Breakthrough aura, `#add = yes` commented OUT = inactive = percentage).
_BATTALION_MULT_FIELD_ALIASES = {"maximum_speed": "max_speed", "armor": "armor_value"}
_APPLICABLE_BATTALION_MULT_FIELDS = (
    set(COMBAT_STAT_FIELDS) | set(STRUCTURAL_STAT_FIELDS) | {SUPPRESSION_FACTOR_FIELD, SUPPLY_CONSUMPTION_FACTOR_FIELD}
)


def _active_battalion_mult_auras(item_keys, researched, completed_special_projects, doctrine):
    """Every battalion_mult aura active in a division, as a flat list of
    aura dicts (each `{"category": ..., <field>: value, ..., "add"?: True}`,
    data/battalion_stats.py's/data/doctrines.py's/data/technologies.py's own
    compiled shape, unchanged).

    Three sources, mirroring this project's existing three unit_bonuses
    sources exactly:
    - A unit's own raw battalion_mult - active whenever that unit itself is
      present in item_keys (an innate ability, not gated on research/doctrine
      at all).
    - Doctrine's own unit_bonuses battalion_mult entries - active when the
      doctrine bonus itself is active (active_unit_bonuses) AND its target
      (the item/category the bonus is nested under) is present in item_keys
      - e.g. marines_1's reward_5 grants its aura only once Pioneer Support
      is actually in the division, not merely because the reward is claimed.
    - Technology's/Special Project's own unit_bonuses battalion_mult entries
      - same presence check, via active_tech_unit_bonuses/
      active_special_project_unit_bonuses.

    item_keys is intentionally not deduplicated-and-counted - a source's
    presence is a yes/no check (at least one matching item in the division),
    not something that stacks per extra instance; no real screenshot
    evidence suggests otherwise, and it matches how every other presence
    check in this app already works.
    """
    present_keys = set(item_keys)
    present_categories = {
        category for key in present_keys for category in UNIT_CATEGORIES.get(key, set())
    }

    def is_present(target_key):
        return target_key in present_keys or target_key in present_categories

    auras = []
    for key in present_keys:
        auras.extend(BATTALION_STATS[key].get("battalion_mult", []))

    bonus_pairs = []
    if doctrine is not None:
        bonus_pairs += active_unit_bonuses(
            doctrine["active_grand_doctrines"], doctrine["track_subdoctrines"], doctrine["claimed_rewards"]
        )
    if researched is not None or completed_special_projects is not None:
        bonus_pairs += active_tech_unit_bonuses(researched or set())
        bonus_pairs += active_special_project_unit_bonuses(completed_special_projects or set())

    for target_key, stat_dict in bonus_pairs:
        if is_present(target_key):
            auras.extend(stat_dict.get("battalion_mult", []))

    return auras


def _apply_battalion_mult(stats, item_key, auras):
    """Return a copy of an already-fully-resolved item stat block with every
    applicable active aura (see _active_battalion_mult_auras) applied, for
    auras whose own category matches one of item_key's own categories.
    Flat contributions (an aura's own "add": True fields) sum and add first;
    percentage contributions (every other field) sum and apply once as a
    single (1 + total) multiplier - the same "sum same-field bonuses, apply
    once" convention this project already uses everywhere else a stat can
    have multiple contributors. Returns the same stats dict unchanged if no
    aura applies (the common case), matching apply_terrain_modifier's own
    no-op-when-nothing-changes precedent.
    """
    item_categories = UNIT_CATEGORIES.get(item_key, set())
    flat_totals = {}
    percent_totals = {}

    for mult in auras:
        if mult["category"] not in item_categories:
            continue
        is_flat = mult.get("add", False)
        totals = flat_totals if is_flat else percent_totals
        for field, value in mult.items():
            if field in ("category", "add"):
                continue
            field = _BATTALION_MULT_FIELD_ALIASES.get(field, field)
            if field not in _APPLICABLE_BATTALION_MULT_FIELDS:
                continue
            totals[field] = totals.get(field, 0) + value

    if not flat_totals and not percent_totals:
        return stats

    new_stats = dict(stats)
    for field in set(flat_totals) | set(percent_totals):
        value = new_stats.get(field, 0) + flat_totals.get(field, 0)
        value *= 1 + percent_totals.get(field, 0)
        new_stats[field] = value
    return new_stats


def calculate_item_stats(
    item_key, is_support_type=False, researched=None, completed_special_projects=None,
    doctrine=None, tank_designs=None, terrain=None,
    equipment_overrides=None, battalion_overrides=None, army_spirits=None,
):
    """Combine a battalion/support-company/regimental-support item's own
    stats with its equipment's stats and cost into one final stat block.

    is_support_type must be passed as True when item_key is being used as a
    support company or regimental support item (own combat-stat fields are
    then a percentage modifier on equipment, not a flat addition) - see the
    module comment above. Defaults to False (battalion behaviour) since
    most callers deal with battalions and most keys only mean one thing;
    pass it explicitly for the handful of keys (e.g. "light_flame_tank")
    that are selectable as either.

    researched is an optional set of researched technology keys (see
    data/technologies.py and logic/research.py). Omitting it (the default)
    uses the fixed "_1 tier" baseline exactly as before Research existed and
    applies no technology unit_bonuses at all. Passing it resolves each
    needed equipment type through data/equipment_tiers.py, using whichever
    tier's unlocking tech is in `researched` - see _equipment_stats above -
    AND applies every applicable technology unit_bonus targeting item_key or
    one of its categories: COMBAT_STAT_FIELDS bonuses merge into a
    support-type item's own percentage field, apply as a separate
    multiplicative layer on a battalion's own+equipment total (corrected
    2026-10-08 - see below), and SUPPLY_CONSUMPTION_FACTOR_FIELD bonuses sum
    into the same division-level multiplier as suppression_factor - see
    _tech_bonus_for_item's block comment above for the full evidence trail
    (Template Examples/, 2026-09-30 and 2026-10-08) and exactly what's still
    left unapplied.

    completed_special_projects is an optional set of completed special
    project keys (see data/special_projects.py and
    logic/special_projects.py) - a completed project's own direct
    unit_bonuses (e.g. Large Caliber Kinetic Energy Sabot's hidden Piercing
    bonus) are pooled into the exact same tech-bonus pipeline as
    `researched` above and applied identically - see
    _tech_bonus_for_item's block comment. Omitting it (the default) is
    byte-identical to before this parameter existed, independent of whether
    `researched` is passed.

    doctrine is an optional dict of {"active_grand_doctrines", "track_subdoctrines",
    "claimed_rewards"} - the same three pieces of caller-owned state
    logic/doctrines.py's functions already take. Omitting it (the default)
    is byte-identical to before Doctrine's stats integration existed. Passing
    it applies every applicable doctrine unit_bonus targeting item_key or one
    of its categories - max_organisation/suppression_factor/combat_width/
    max_strength as a flat add, max_speed as a flat km/h add scaled by
    HOI4's base land-unit speed constant, everything else as a single
    percentage multiplier on the own+equipment total - see
    _DOCTRINE_FLAT_FIELDS/_DOCTRINE_SPEED_SCALED_FIELDS/
    _doctrine_bonus_for_item above for exactly what counts as "applicable"
    and the evidence behind each field's classification.

    tank_designs is an optional {equipment_key: design_params} dict, where
    design_params is exactly logic/tank_designer.py's
    calculate_tank_design_stats own keyword arguments
    ({"chassis_key", "tier", "chosen_modules", "role_key", "tick_levels"}
    - the last two optional, same as that function). Omitting it (the
    default) is byte-identical to before the Tank Designer's Stats
    integration existed. Passing an entry for one of item_key's needed
    equipment keys uses that finished design's own computed stats INSTEAD
    of the research-tier lookup for that one equipment family, taking
    priority over `researched` entirely for that key - see
    _equipment_stats above.

    terrain is an optional {"terrain_key", "is_attacking"} dict - see
    logic/terrain.py's terrain_percentage/apply_terrain_modifier for the
    full formula (confirmed 2026-09-29 against real screenshots; see
    CLAUDE.md's Terrain section). Omitting it (the default) is byte-
    identical to before Terrain's stats integration existed. Applies AFTER
    doctrine, since terrain is a further multiplier on the item's already-
    fully-resolved (own + equipment + doctrine) FLAT combat stats.

    The two mechanics DO interact in one specific way (added 2026-10-07,
    see logic/terrain.py's _doctrine_terrain_percentage): a Doctrine's own
    terrain-nested unit_bonuses (e.g. marines_2's "Marines: Amphibious
    Expeditionary" granting Pioneer Support a real Amphibious Assault
    bonus) feed into the SAME terrain percentage calculation as the
    generic/per-unit layers, not a separate multiplicative bucket - this is
    passed through automatically whenever both `doctrine` and `terrain` are
    given, using the same `doctrine_bonuses` list already computed above
    for the flat-field doctrine bonuses. Every OTHER doctrine/terrain
    interaction (e.g. a doctrine's own flat percentage bonus being affected
    by which terrain is selected) is still independently sourced and has
    never been observed to interact.

    equipment_overrides/battalion_overrides (added 2026-11-03, Patch
    Impact Preview - see data/patches.py) are optional
    {equipment_key/item_key: {field: value}} dicts of ABSOLUTE replacement
    values, previewing a staged/hypothetical data change without touching
    the real data/*.py files. `equipment_overrides` passes straight
    through to _equipment_stats, applied after whichever of
    tank_designs/researched/the raw baseline resolved; `battalion_overrides`
    overlays item_key's own BATTALION_STATS entry the same way, right
    where it's first read below. Omitting both (the default) is
    byte-identical to before this parameter pair existed.

    army_spirits (added 2026-11-03, an optional collection of active Army
    Spirit keys) is used here ONLY for Officer Corps' own `equipment_bonus`
    entries (logic/army_spirits.py's active_equipment_bonuses) - a
    percentage bonus targeting an equipment FAMILY directly, applied via
    _apply_equipment_bonus right after each needed equipment key is
    resolved, before it's combined into item_key's own total. This is a
    narrower use than calculate_division_stats' own `army_spirits`
    parameter, which ALSO applies country-wide factor fields
    (army_strength_factor/breakthrough_factor/supply_consumption_factor/
    army_speed_factor) once at the division level, not here - those have
    no per-item meaning. Omitting it (the default) is byte-identical to
    before this parameter existed.

    Returns a dict with every field in STRUCTURAL_STAT_FIELDS and
    COMBAT_STAT_FIELDS (defaulting to 0 where the source data has nothing),
    plus "production_cost" and "combat_stats_available" (False if any
    needed equipment is one of the confirmed gaps - see data/equipment.py
    and data/equipment_tiers.py; a tank_designs entry is always real
    numbers, never a gap).
    """
    own_stats = BATTALION_STATS[item_key]
    if battalion_overrides and item_key in battalion_overrides:
        own_stats = {**own_stats, **battalion_overrides[item_key]}
    needs = EQUIPMENT_NEEDS[item_key]
    equipment = {
        key: _equipment_stats(key, researched, tank_designs, equipment_overrides) for key in needs
    }
    if army_spirits:
        equipment_bonus_pairs = active_equipment_bonuses(army_spirits)
        equipment = {
            key: _apply_equipment_bonus(key, stats, equipment_bonus_pairs) for key, stats in equipment.items()
        }
    tech_bonus = {}
    if researched is not None or completed_special_projects is not None:
        bonus_pairs = (
            active_tech_unit_bonuses(researched or set())
            + active_special_project_unit_bonuses(completed_special_projects or set())
        )
        tech_bonus = _tech_bonus_for_item(item_key, bonus_pairs)

    stats = {field: own_stats.get(field, 0) for field in STRUCTURAL_STAT_FIELDS}

    # Armor/Armored Combat Support battalions carry no own max_speed at all
    # in data/battalion_stats.py, unlike every leg/mounted/motorized
    # battalion - a tank's speed comes entirely from its equipped chassis,
    # not a fixed per-battalion number. Deliberately left open since
    # 2026-09-14 pending Tank Designer's existence (see Activity_Log.md);
    # now that it's built, every equipment entry (EQUIPMENT[key], a
    # researched tier, or a tank_designs design - already resolved above
    # into `equipment` with exactly that priority by _equipment_stats)
    # always carries its own real "maximum_speed", so fall back to it here.
    if "max_speed" not in own_stats:
        equipment_speeds = [stat["maximum_speed"] for stat in equipment.values() if "maximum_speed" in stat]
        if equipment_speeds:
            stats["max_speed"] = max(equipment_speeds)

    # A custom Tank Designer design's own calculation (calculate_tank_design_stats)
    # already bakes in the hidden role-combat multiplier for breakthrough
    # (data/tank_role_combat_modifiers.py - e.g. Tank Destroyer's own -25%)
    # for whichever equipment family it replaces - so _BATTALION_OWN_PERCENTAGE_FIELDS'
    # own% treatment is scoped OUT for any field whose needed equipment comes
    # from tank_designs, to avoid double-applying the same real effect with
    # no screenshot evidence either way for that specific combination
    # (untouched: Marine/Mountaineer/Ranger/etc. structurally never have a
    # tank_designs entry at all, since they need infantry_equipment, never a
    # tank chassis - today's evidence is scoped exactly to where it applies).
    uses_tank_design = bool(tank_designs) and any(key in tank_designs for key in needs)

    # (added 1.19.4, formula empirically confirmed 2026-11-02 against 4 real
    # Tank Designer screenshots - see CLAUDE.md's Tank Designer section) a
    # custom design's own HP scales with its resolved reliability instead of
    # staying the fixed flat value every item's own data/battalion_stats.py
    # entry carries: max_strength = base + factor * reliability. The real
    # patch note describes 3 categories (plain tank chassis; Line Tank
    # Destroyer/SP-AA/SP-Artillery; Regimental Support Tank Destroyer/SP-AA -
    # SP-Artillery has no Regimental Support variant at all), and each
    # category's own `base` is exactly the item's already-correct flat
    # max_strength value from the earlier 1.19.4 pass (2 / 0.5 / 0.1) - that
    # value doubles as the lookup key here since it's already unique per
    # category. Land Cruiser (max_strength 15) and every non-tank item
    # structurally either don't match one of these 3 values or never have a
    # tank_designs-eligible equipment need (or both), so no separate
    # exclusion list is needed - confirmed directly against every Armor/
    # Armored Combat Support entry in data/battalion_stats.py, not assumed.
    _RELIABILITY_MAX_STRENGTH_FACTORS = {2.0: 1.5, 0.5: 0.75, 0.1: 0.55}
    if uses_tank_design:
        reliability_factor = _RELIABILITY_MAX_STRENGTH_FACTORS.get(stats["max_strength"])
        if reliability_factor is not None:
            design_reliability = next(
                (equipment[key]["reliability"] for key in needs if key in tank_designs),
                None,
            )
            if design_reliability is not None:
                stats["max_strength"] += reliability_factor * design_reliability

    for field in COMBAT_STAT_FIELDS:
        equipment_total = sum(equipment[key].get(field, 0) for key in needs)
        own = own_stats.get(field, 0)
        if is_support_type:
            # Technology bonuses to combat-stat fields merge into the item's
            # own percentage BEFORE the single equipment multiplication -
            # confirmed by real screenshots (see _tech_bonus_for_item's block
            # comment).
            own += tech_bonus.get(field, 0)
            stats[field] = equipment_total * (1 + own)
        elif field in _BATTALION_OWN_PERCENTAGE_FIELDS and not uses_tank_design:
            # breakthrough only - see _BATTALION_OWN_PERCENTAGE_FIELDS' own
            # block comment. own% applies to equipment the same way a
            # support-type item's own% does; the tech bonus layer (separate
            # from own%, matching every other battalion field below) stays
            # consistent with the rest of this loop.
            stats[field] = equipment_total * (1 + own) * (1 + tech_bonus.get(field, 0))
        else:
            # Battalions have no "own%" slot to merge a tech bonus into (own
            # combat stats are a flat add, not a percentage) - instead applies
            # as a separate multiplicative layer on the already-resolved
            # own+equipment total, the same mechanism Doctrine's own
            # percentage fields already use for battalions (corrected
            # 2026-10-08 - see _tech_bonus_for_item's block comment for the
            # real Marine screenshot this was confirmed against, after an
            # earlier "confirmed zero on battalions" conclusion from
            # 2026-09-30 turned out to be based on a mislabeled research
            # state, not a real negative result).
            stats[field] = (own + equipment_total) * (1 + tech_bonus.get(field, 0))

    stats["production_cost"] = sum(
        equipment[equipment_key]["build_cost_ic"] * quantity
        for equipment_key, quantity in needs.items()
    )
    stats["combat_stats_available"] = all(
        equipment[equipment_key].get("combat_stats_available", True)
        for equipment_key in needs
    )
    stats[SUPPRESSION_FACTOR_FIELD] = own_stats.get(SUPPRESSION_FACTOR_FIELD, 0)
    stats[SUPPLY_CONSUMPTION_FACTOR_FIELD] = (
        own_stats.get(SUPPLY_CONSUMPTION_FACTOR_FIELD, 0) + tech_bonus.get(SUPPLY_CONSUMPTION_FACTOR_FIELD, 0)
    )
    # A flat add, same as Doctrine's own max_organisation bonus - see
    # _APPLICABLE_TECH_FIELDS' block comment above for why this was missing
    # entirely until 2026-10-08.
    stats["max_organisation"] += tech_bonus.get("max_organisation", 0)

    # Computed whenever doctrine is passed, not just inside the flat-field
    # application block below - logic/terrain.py's apply_terrain_modifier
    # also needs this same raw pair list, for Doctrine's own terrain-nested
    # bonuses (e.g. marines_2's Pioneer Support/Amphibious bonus - see
    # logic/terrain.py's _doctrine_terrain_percentage, added 2026-10-07).
    doctrine_bonuses = None
    if doctrine is not None:
        doctrine_bonuses = active_unit_bonuses(
            doctrine["active_grand_doctrines"], doctrine["track_subdoctrines"], doctrine["claimed_rewards"]
        )
        for field, value in _doctrine_bonus_for_item(item_key, doctrine_bonuses).items():
            if field in _DOCTRINE_FLAT_FIELDS:
                stats[field] += value
            elif field in _DOCTRINE_SPEED_SCALED_FIELDS:
                stats[field] += value * _LEG_UNIT_BASE_SPEED_KMH
            else:
                stats[field] *= 1 + value

    if terrain is not None:
        stats = apply_terrain_modifier(
            stats, item_key, terrain["terrain_key"], terrain["is_attacking"], doctrine_bonuses=doctrine_bonuses
        )

    return stats


# Fields that add straight across every chosen battalion, support company,
# and regimental support item - confirmed against real division-designer
# screenshots (multiple Infantry/Artillery ratios, plus support companies
# and regimental support layered on top).
DIVISION_SUM_FIELDS = [
    "manpower", "weight",
    "combat_width", "production_cost",
    "soft_attack", "hard_attack", "defense",
]
# max_strength and breakthrough are each a sum, THEN boosted by a
# percentage from any active Army Spirit's own army_strength_factor/
# breakthrough_factor (a country-wide bonus, not a per-item one - see
# logic/army_spirits.py's active_army_strength_factor/
# active_breakthrough_factor) - same "(1 + bonus)" pattern as suppression/
# supply_consumption below. Confirmed directly in-game: Operational
# Reserves' own real tooltip reads "HP: +10.00%" for its compiled
# army_strength_factor: 0.1 (2026-11-02); Smoke and Fire's own real
# tooltip reads "Breakthrough: +6.00%" for its compiled
# breakthrough_factor: 0.06 (2026-11-03). Pulled out of DIVISION_SUM_FIELDS
# for exactly this reason - a plain sum would silently skip this bonus.

# supply_consumption is NOT a plain sum - like suppression below, it's a sum
# of every item's own flat field, THEN boosted by a percentage from any item
# with a SUPPLY_CONSUMPTION_FACTOR_FIELD (Logistics Company, plus its own
# technology bonuses - see calculate_item_stats' Technology unit_bonuses
# block comment). Confirmed 2026-09-30 by Template Examples/
# 5_infantry_guns_0_logisticsCompany_1.png/_2.png: moved out of
# DIVISION_SUM_FIELDS into its own calculation below once this was found,
# rather than silently overcounting it as a flat sum.

# ap_attack (in-game: "Piercing") is NOT a sum - the HOI4 wiki gives the
# real formula directly (https://hoi4.paradoxwikis.com/Land_units#Combat_stats):
# "A division's piercing is equal to 40% of the highest piercing in the
# division plus 60% of the average piercing of all battalions and
# companies in the division." Confirmed against 5 Infantry (4.0), and the
# 7/2, 6/3, 3/6 Infantry/Artillery ratios (4.53/4.6/4.8, matching the
# real 4.5/4.5/4.7 within the game's own 1-decimal display rounding).
# armor_value is extrapolated to follow the same 40/60 max-and-average
# rule by analogy (Piercing vs. Armor are paired combat-mechanic stats),
# not independently confirmed - every screenshot with a nonzero armor_value
# happened to be a uniform division, where max-and-average is
# indistinguishable from a plain average.
DIVISION_MAX_AND_AVERAGE_FIELDS = ["ap_attack", "armor_value"]

# NOT confirmed as a sum - kept separate on purpose. hardness and
# air_attack have no screenshot evidence either way; summed here only as a
# placeholder so the fields are still present, not because it's trusted.
DIVISION_UNCONFIRMED_SUM_FIELDS = ["air_attack", "hardness"]

# max_organisation is a plain, unweighted average across every chosen item
# (battalions AND support companies AND regimental support each count once,
# regardless of combat width) - confirmed against 7/2, 6/3, and 3/6
# Infantry/Artillery ratios, and again once support companies and
# regimental support items were added on top.
DIVISION_AVERAGE_FIELDS = ["max_organisation"]

# training_time is the slowest (max) item to train, whether that's a
# battalion or a support company - confirmed by artillery (120) dominating
# infantry (90) regardless of ratio, and by Military Police (180) pushing
# a 7/2 Infantry/Artillery division's training time up from 120 to 180.
DIVISION_MAX_FIELDS = ["training_time"]


def calculate_division_stats(
    battalions, support_companies=(), regimental_support=(),
    researched=None, completed_special_projects=None, doctrine=None, tank_designs=None, terrain=None,
    army_spirits=None, equipment_overrides=None, battalion_overrides=None,
):
    """Combine a full division's chosen items into one division-wide stat
    block. Each argument is a list of item keys with one entry per instance
    (e.g. 7 Infantry + 2 Artillery is ["infantry"] * 7 + ["artillery_brigade"] * 2).

    researched, completed_special_projects, doctrine, tank_designs,
    terrain, equipment_overrides, and battalion_overrides are all passed
    straight through to calculate_item_stats for every item - see that
    function's docstring (the last two added 2026-11-03 for the Patch
    Impact Preview feature, data/patches.py). Omitting all seven keeps
    today's behaviour ("_1 tier" equipment, no doctrine bonuses, no custom
    tank designs, no terrain, no staged patch).

    army_spirits (a collection of active Army Spirit keys) plays TWO roles
    (the second added 2026-11-03, once Smoke and Fire/Logistical Focus/
    Flexible Organization/Maneuver Warfare/Direct Fire Support/Rapid
    Emplacement/Subsidized Contracts/All-Arms Anti-tank Defense's own real
    formulas were confirmed in-game): it IS passed to calculate_item_stats
    (for `equipment_bonus` - a per-equipment-family percentage bonus, see
    that function's own docstring), AND it's used here, separately, once,
    AFTER every item's own stats are already combined, for the 4 country-
    wide `modifiers` fields (army_strength_factor/breakthrough_factor/
    supply_consumption_factor/army_speed_factor - logic/army_spirits.py's
    own active_* functions) that apply to the division as a whole, not a
    per-item/category one. Omitting it (None, same as the default) keeps
    today's behaviour either way.

    terrain, when passed, applies to every item the same way regardless of
    battalion/support/regimental-support - a division is either attacking
    into a terrain or defending within it as a whole, not per-item. To show
    HOI4's own attacker-vs-defender side-by-side view, call this twice with
    the same terrain_key and is_attacking flipped - this function only ever
    computes one side per call, matching calculate_item_stats.

    Aggregation rules below were reverse-engineered from real division-
    designer screenshots (see Activity_Log.md) rather than assumed - see the
    DIVISION_*_FIELDS comments above for what's confirmed vs. extrapolated.
    default_morale is deliberately left out: unlike everything else here, no
    screenshot exposes it directly, so there's nothing to check a rule
    against yet. air_attack/hardness ARE included but are not trustworthy
    yet - see DIVISION_UNCONFIRMED_SUM_FIELDS.
    """
    battalion_stats = [
        calculate_item_stats(
            key, researched=researched, completed_special_projects=completed_special_projects,
            doctrine=doctrine, tank_designs=tank_designs, terrain=terrain,
            equipment_overrides=equipment_overrides, battalion_overrides=battalion_overrides,
            army_spirits=army_spirits,
        )
        for key in battalions
    ]
    support_stats = [
        calculate_item_stats(
            key, is_support_type=True, researched=researched,
            completed_special_projects=completed_special_projects, doctrine=doctrine,
            tank_designs=tank_designs, terrain=terrain,
            equipment_overrides=equipment_overrides, battalion_overrides=battalion_overrides,
            army_spirits=army_spirits,
        )
        for key in list(support_companies) + list(regimental_support)
    ]
    item_stats = battalion_stats + support_stats

    # battalion_mult (added 2026-10-08) - applied as a final pass here, not
    # inside calculate_item_stats, since it needs visibility into every
    # OTHER item in the division (an aura, not a per-item bonus) - see
    # _active_battalion_mult_auras'/_apply_battalion_mult's own block
    # comments for the full three-source rule and the real screenshot this
    # was confirmed against.
    item_keys = list(battalions) + list(support_companies) + list(regimental_support)
    auras = _active_battalion_mult_auras(item_keys, researched, completed_special_projects, doctrine)
    if auras:
        item_stats = [
            _apply_battalion_mult(stats, key, auras) for key, stats in zip(item_keys, item_stats)
        ]

    division = {}

    for field in DIVISION_SUM_FIELDS + DIVISION_UNCONFIRMED_SUM_FIELDS:
        division[field] = sum(stats[field] for stats in item_stats)

    base_max_strength = sum(stats["max_strength"] for stats in item_stats)
    army_strength_bonus = active_army_strength_factor(army_spirits or [])
    division["max_strength"] = base_max_strength * (1 + army_strength_bonus)

    base_breakthrough = sum(stats["breakthrough"] for stats in item_stats)
    breakthrough_bonus = active_breakthrough_factor(army_spirits or [])
    division["breakthrough"] = base_breakthrough * (1 + breakthrough_bonus)

    for field in DIVISION_AVERAGE_FIELDS:
        division[field] = sum(stats[field] for stats in item_stats) / len(item_stats)

    for field in DIVISION_MAX_FIELDS:
        division[field] = max(stats[field] for stats in item_stats)

    for field in DIVISION_MAX_AND_AVERAGE_FIELDS:
        values = [stats[field] for stats in item_stats]
        division[field] = 0.4 * max(values) + 0.6 * (sum(values) / len(values))

    # Max Speed is a bottleneck: the division moves at its slowest
    # battalion's speed. Support companies/regimental support don't have a
    # speed of their own and don't participate - confirmed by the
    # 5 Motorised + 1 Cavalry + 1 Infantry division, whose speed matched
    # Infantry's 4.0 km/h exactly despite being mostly Motorised (12.0 km/h).
    # Uses item_stats' own first len(battalions) entries, not the original
    # battalion_stats list, so a battalion_mult aura targeting max_speed
    # (e.g. a doctrine's own "maximum_speed" battalion_mult) is reflected
    # here too, not just in the sum/average/max fields above. THEN boosted
    # by a percentage from any active Army Spirit's own army_speed_factor -
    # confirmed directly in-game (2026-11-03): both Flexible Organization's
    # and Maneuver Warfare's real tooltips read "Divisions speed: +5.00%"
    # for their identically-named compiled army_speed_factor: 0.05 fields.
    base_max_speed = min(stats["max_speed"] for stats in item_stats[: len(battalion_stats)])
    army_speed_bonus = active_army_speed_factor(army_spirits or [])
    division["max_speed"] = base_max_speed * (1 + army_speed_bonus)

    # Suppression is a sum of every item's flat "suppression" field, then
    # boosted by a percentage from any support company with a
    # suppression_factor (currently only Military Police variants) -
    # confirmed exactly by Military Police's real +2.1 jump on a 10.5-
    # suppression division (10.5 x 0.20 = 2.1).
    base_suppression = sum(stats["suppression"] for stats in item_stats)
    suppression_bonus = sum(stats[SUPPRESSION_FACTOR_FIELD] for stats in item_stats)
    division["suppression"] = base_suppression * (1 + suppression_bonus)

    # Supply Use follows the identical pattern - see DIVISION_SUM_FIELDS'
    # own comment above and calculate_item_stats' Technology unit_bonuses
    # block comment for the confirming screenshots. Logistical Focus's own
    # supply_consumption_factor (confirmed in-game 2026-11-03: real tooltip
    # "Supply Consumption: -10.0%") is country-wide, not per-item - summed
    # into this SAME total rather than a second multiplier layer.
    base_supply_consumption = sum(stats["supply_consumption"] for stats in item_stats)
    supply_consumption_bonus = (
        sum(stats[SUPPLY_CONSUMPTION_FACTOR_FIELD] for stats in item_stats)
        + active_supply_consumption_factor(army_spirits or [])
    )
    division["supply_consumption"] = base_supply_consumption * (1 + supply_consumption_bonus)

    division["combat_stats_available"] = all(
        stats["combat_stats_available"] for stats in item_stats
    )

    return division
