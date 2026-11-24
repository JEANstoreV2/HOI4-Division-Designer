from data.tank_chassis import TANK_CHASSIS, TANK_ROLES
from data.tank_modules import TANK_MODULES
from data.tank_role_combat_modifiers import TANK_ROLE_COMBAT_MODIFIERS
from data.tank_upgrades import TANK_UPGRADES

_CHASSIS_BY_KEY = {c["key"]: c for c in TANK_CHASSIS}
_ROLE_BY_KEY = {r["key"]: r for r in TANK_ROLES}
_MODULE_BY_KEY = {m["key"]: m for m in TANK_MODULES}
_UPGRADE_BY_KEY = {u["key"]: u for u in TANK_UPGRADES}


def equipment_type_tags(role_key=None):
    """The set of HOI4 equipment-type tags a design carries.

    Every design is "armor" at its core - even a role variant (AA/Artillery/
    Anti-Tank/Amphibious/Flame) is still built on a tank chassis - and a role
    variant ADDS its own tag on top rather than replacing "armor". This
    dual-tag model is what makes data/tank_modules.py's data consistent
    rather than redundant: e.g. tank_anti_air_cannon sets BOTH
    `allow_equipment_type = anti_air` (a positive requirement - only a
    design carrying the "anti_air" tag may use it) AND
    `forbid_equipment_type_exact_match = armor` (a negative one - barred
    from a design whose tag set is EXACTLY {"armor"}, i.e. a plain, role-less
    tank). If a role variant fully replaced "armor" instead of adding to it,
    the second field would be redundant with the first; it isn't, so it
    doesn't.
    """
    if role_key is None:
        return frozenset({"armor"})
    return frozenset({"armor", _ROLE_BY_KEY[role_key]["role"]})


def effective_module_slots(chassis_key, chosen_modules, role_key=None):
    """The chassis's module_slots, with each slot's allowed_module_categories
    WIDENED (union, not replaced) by any chosen module's own
    `allowed_module_categories` override targeting that slot - e.g.
    equipping a real turret adds that turret's own gun-size category
    (tank_medium_main_armament, etc.) on top of whatever the chassis's base
    slot already allowed, rather than taking away the smaller category the
    chassis started with.

    Corrected 2026-09-16 after Ollie reported a live symptom of the
    original "replace" behavior: a plain Medium Tank's main_armament_slot
    came back with NO legal options at all once its default turret was
    chosen, because every real tank_medium_main_armament module requires a
    role (anti_air/anti_tank/artillery - confirmed by direct read of every
    entry in data/tank_modules.py) while the turret's override had fully
    removed the unrestricted tank_small_main_armament category a plain tank
    actually needs. The original "replace" call was justified by analogy to
    Clausewitz's own last-write-wins rule for a single re-declared key
    within one file (a real, confirmed mechanic used correctly elsewhere in
    this data) - but that rule doesn't apply here: this is two DIFFERENT
    sources (the chassis's own slot definition, and a separately-chosen
    module's override) intersecting at runtime, not one key declared twice
    in the same block, and the analogy was never checked against a real
    screenshot or the wiki the way Phase 5's other hidden mechanics were.
    Union avoids the empty-options bug while changing nothing about the
    already-confirmed fixed-superstructure/Tank Destroyer case (see
    tests/test_tank_designer.py) - that combo was already illegal on a
    plain design for two OTHER, independent reasons (the weapon's own
    allow_equipment_type and the turret's own
    forbid_equipment_type_exact_match_for_category), neither of which
    depended on the smaller category being removed.

    Only the module actually placed in another slot can override a given
    slot; a module can't override its own slot's category (that would be
    circular). If more than one chosen module widens the same slot, both
    contribute (order doesn't matter for a union).

    A Flame role is a second, separate exception to the union rule above -
    reported by Ollie after the union fix let a Flame Tank mount an
    ordinary cannon instead of a flamethrower, which isn't accurate: real
    HOI4 Flame Tanks can ONLY use the tank_flamethrower category for their
    main armament, not the small/medium/heavy gun categories a turret or
    the base chassis would otherwise allow. This isn't expressed anywhere
    in `x_tank_chassis.txt`'s `duplicate_archetypes` block for the flame
    variants (confirmed by direct read - no module_slots override exists
    there, unlike the per-field `stat_overrides` the other roles get) or in
    any module's own `forbid_equipment_type` - it's a hidden, role-level
    slot restriction, the same kind of undocumented mechanic
    `data/tank_role_combat_modifiers.py`'s header already found once for
    the combat-stat multipliers. Modeled here rather than as chassis/module
    data since it's keyed off the ROLE, not the chassis or any module.
    """
    chassis = _CHASSIS_BY_KEY[chassis_key]
    effective = {
        slot_name: list(slot["allowed_module_categories"])
        for slot_name, slot in chassis["module_slots"].items()
    }

    for slot_name, module_key in chosen_modules.items():
        if not module_key:
            continue
        module = _MODULE_BY_KEY.get(module_key)
        if module is None:
            continue
        for target_slot, categories in module.get("allowed_module_categories", {}).items():
            if target_slot == slot_name:
                continue
            if target_slot in effective:
                for category in categories:
                    if category not in effective[target_slot]:
                        effective[target_slot].append(category)

    role = _ROLE_BY_KEY[role_key] if role_key else None
    if role and role["role"] == "flame" and "main_armament_slot" in effective:
        effective["main_armament_slot"] = ["tank_flamethrower"]

    return effective


def validate_design(chassis_key, chosen_modules, role_key=None):
    """Every rule a design (a chassis/role plus one chosen module key per
    slot, `chosen_modules` = {slot_name: module_key}) currently breaks, as a
    list of violation dicts (each always has a "type" key). An empty list
    means the design is legal. Checks, in order:

    - every required slot is filled with a real module key
    - every filled slot's module's category is legal for that slot, once
      turret-style overrides have widened/narrowed it (effective_module_slots)
    - every filled slot's module's allow_equipment_type/forbid_equipment_type/
      forbid_equipment_type_exact_match rules are satisfied against the
      design's own equipment_type_tags
    - a turret's forbid_equipment_type_exact_match_for_category rule against
      whatever's actually chosen in the slot(s) it targets
    - every chassis module_count_limits entry (named-module or whole-category)
      is respected, counting every filled slot in the whole design
    """
    chassis = _CHASSIS_BY_KEY[chassis_key]
    type_tags = equipment_type_tags(role_key)
    effective_slots = effective_module_slots(chassis_key, chosen_modules, role_key=role_key)
    violations = []

    for slot_name, slot in chassis["module_slots"].items():
        module_key = chosen_modules.get(slot_name)

        if not module_key:
            if slot["required"]:
                violations.append({"type": "missing_required_module", "slot": slot_name})
            continue

        module = _MODULE_BY_KEY.get(module_key)
        if module is None:
            violations.append({"type": "unknown_module", "slot": slot_name, "module": module_key})
            continue

        if module["category"] not in effective_slots[slot_name]:
            violations.append({
                "type": "invalid_category", "slot": slot_name, "module": module_key,
                "category": module["category"], "allowed": effective_slots[slot_name],
            })

        required_type = module.get("allow_equipment_type")
        if required_type is not None and required_type not in type_tags:
            violations.append({
                "type": "requires_equipment_type", "slot": slot_name, "module": module_key,
                "required_type": required_type,
            })

        forbidden_types = set(module.get("forbid_equipment_type") or []) & type_tags
        if forbidden_types:
            violations.append({
                "type": "forbidden_equipment_type", "slot": slot_name, "module": module_key,
                "forbidden_types": sorted(forbidden_types),
            })

        exact_forbidden = module.get("forbid_equipment_type_exact_match")
        if exact_forbidden is not None and type_tags == {exact_forbidden}:
            violations.append({
                "type": "forbidden_for_exact_equipment_type", "slot": slot_name,
                "module": module_key, "equipment_type": exact_forbidden,
            })

    for turret_slot, turret_key in chosen_modules.items():
        turret = _MODULE_BY_KEY.get(turret_key) if turret_key else None
        category_forbids = (turret or {}).get("forbid_equipment_type_exact_match_for_category")
        if not category_forbids:
            continue
        for other_slot, other_key in chosen_modules.items():
            other = _MODULE_BY_KEY.get(other_key) if other_key else None
            if other is None:
                continue
            forbidden_type = category_forbids.get(other["category"])
            if forbidden_type is not None and type_tags == {forbidden_type}:
                violations.append({
                    "type": "category_forbidden_for_exact_equipment_type",
                    "slot": other_slot, "module": other_key, "category": other["category"],
                    "via_slot": turret_slot, "via_module": turret_key,
                    "equipment_type": forbidden_type,
                })

    chosen_keys = [key for key in chosen_modules.values() if key]
    for limit in chassis["module_count_limits"]:
        if "module" in limit:
            count = chosen_keys.count(limit["module"])
            label = limit["module"]
        else:
            count = sum(
                1 for key in chosen_keys
                if _MODULE_BY_KEY.get(key, {}).get("category") == limit["category"]
            )
            label = limit["category"]
        if count > limit["max_count"]:
            violations.append({
                "type": "count_limit_exceeded", "limit": label,
                "count": count, "max_count": limit["max_count"],
            })

    return violations


def is_design_legal(chassis_key, chosen_modules, role_key=None):
    """Whether a design breaks none of validate_design's rules."""
    return not validate_design(chassis_key, chosen_modules, role_key=role_key)


def max_tick_level(tick_key, researched):
    """The highest level of a tick (data/tank_upgrades.py entry) currently
    reachable, given the set of technology keys already researched.

    A tick's `level_requirements` are checkpoints, not per-level gates: level
    N becomes reachable once its listed technology is researched, and every
    level below the first UNMET checkpoint stays reachable regardless (e.g.
    levels 1-4 need no research at all - only level 5 onward does). Walking
    the checkpoints in ascending order and stopping at the first one whose
    technology isn't researched yet finds that boundary directly.
    """
    upgrade = _UPGRADE_BY_KEY[tick_key]
    checkpoints = sorted(upgrade["level_requirements"], key=lambda req: req["level"])

    for checkpoint in checkpoints:
        if checkpoint["tech"] not in researched:
            return checkpoint["level"] - 1

    return upgrade["max_level"]


def build_candidate_design(base_design, candidate):
    """Merge one override candidate onto a base in-progress design, for the
    pre-selection preview (static/js/tank_designer.js's chassis/tier/role/
    module pickers) - never mutates base_design.

    base_design: {chassis_key, tier, role_key, chosen_modules, tick_levels}
    candidate: one of
      {"type": "chassis", "chassis_key": ...}
      {"type": "tier", "tier": ...}
      {"type": "role", "role_key": ... or None}
      {"type": "module", "slot": ..., "module_key": ...}
      {"type": "baseline"}

    Each candidate type resets a different, specific slice of the design,
    mirroring tank_designer.js's own real mutators exactly rather than one
    generic merge: picking a new chassis resets tier/role/modules/ticks all
    at once (selectChassis); a new tier changes only the tier (selectTier);
    a new role resets modules back to the chassis's own defaults but leaves
    tier/ticks alone (selectRole - a role's module needs can differ enough
    from the base chassis that keeping the old modules could leave some
    slots holding something no longer legal); a module pick changes only
    that one slot. "baseline" changes nothing at all - the base design
    itself, unmodified, returned through the exact same path as every real
    candidate so the frontend can diff a candidate's stats against the
    design as it currently stands (added 2026-11-02, see
    item_stats_preview.js's own "only show what changed" rendering).

    A chassis swap falls back to the CANDIDATE chassis's own
    default_modules, never the base design's modules - those may not even
    have matching slot names on a different chassis.
    """
    design = dict(base_design)

    if candidate["type"] == "chassis":
        chassis = _CHASSIS_BY_KEY[candidate["chassis_key"]]
        design["chassis_key"] = candidate["chassis_key"]
        design["tier"] = chassis["tiers"][0]["tier"]
        design["role_key"] = None
        design["chosen_modules"] = dict(chassis["default_modules"])
        design["tick_levels"] = {}
    elif candidate["type"] == "tier":
        design["tier"] = candidate["tier"]
    elif candidate["type"] == "role":
        design["role_key"] = candidate["role_key"]
        design["chosen_modules"] = dict(_CHASSIS_BY_KEY[base_design["chassis_key"]]["default_modules"])
    elif candidate["type"] == "module":
        design["chosen_modules"] = {**base_design["chosen_modules"], candidate["slot"]: candidate["module_key"]}
    elif candidate["type"] == "baseline":
        pass

    return design


def _resolve_chassis_tier_stats(chassis_key, tier):
    """base_stats merged with the given tier's stat_overrides - the
    archetype is the fallback for any field the tier doesn't touch, not the
    previous tier (matches data/equipment_tiers.py's own resolution rule,
    referenced directly in data/tank_chassis.py's header)."""
    chassis = _CHASSIS_BY_KEY[chassis_key]
    tier_entry = next(t for t in chassis["tiers"] if t["tier"] == tier)
    return {**chassis["base_stats"], **tier_entry["stat_overrides"]}


# (added 1.19.4) Fields a tier's own "module_additive_multiplier" scales -
# see data/tank_chassis.py's header for the exact mechanic and the tier-
# mapping assumption it documents.
_TIER_MODULE_ADDITIVE_FIELDS = {"soft_attack", "hard_attack", "air_attack"}


def _tier_module_additive_multiplier(chassis_key, tier):
    chassis = _CHASSIS_BY_KEY[chassis_key]
    tier_entry = next(t for t in chassis["tiers"] if t["tier"] == tier)
    return tier_entry.get("module_additive_multiplier", 0.0)


def calculate_tank_design_stats(chassis_key, tier, chosen_modules, role_key=None, tick_levels=None):
    """The final resolved stat block for a finished tank design - a chassis
    at a given tier, an optional role conversion, a chosen module per slot,
    and tick levels for any upgrades in progress.

    Confirmed field-by-field against real Tank Designer screenshots
    (tank_designer_examples/, gitignored - see Activity_Log.md 2026-09-16),
    not assumed from the module data's shape alone:

    - Every module's `add_stats` and every tick level's `add_stats` are
      flat additions, summed together with the chassis/tier's own base
      value for that field.
    - Every module's `multiply_stats` percentages on the same field are
      SUMMED first, then applied as one `(1 + total)` multiplier on the
      flat sum above - not compounded module-by-module (proven by Welded
      Armor + Sloped Armor's armor_value: 30 x 1.55 = 46.5 matches; 30 x
      1.3 x 1.25 = 48.75 does not).
    - A tick's own `per_level_reliability` is NOT a flat addition like
      every other tick/module field - it's a percentage, multiplying the
      accumulated reliability the same way a module's multiply_stats
      would (proven by 9 Armor ticks: 0.8 x (1 + 9 x -0.015) = 69.2%
      matches; flat addition, 0.8 - 9 x 0.015 = 66.5%, does not).
    - A role's `stat_overrides` (e.g. hardness forced to a fixed value)
      REPLACE the chassis/tier's own base value for that field outright,
      before any of the above - modules/ticks can still add to or
      multiply the replaced value afterward.
    - TANK_ROLE_COMBAT_MODIFIERS (a hidden per-chassis/role combat
      modifier found nowhere in this project's copied reference files -
      see that file's header) is a SEPARATE, final multiplication stage
      applied after every module/tick percentage above is already
      resolved into one multiplier - not merged into that same sum
      (proven by Extra Ammo Storage + Basic Radio's breakthrough: 12 x
      1.15[radio] x 1.15[chassis] = 15.87 matches the screenshot's
      truncated 15.8; 12 x 1.30 [summed as one bucket] = 15.6 does not).
    - (added 1.19.4) A chassis tier's own "module_additive_multiplier"
      (data/tank_chassis.py) scales ONLY the sum of chosen modules' own
      add_stats contribution to soft_attack/hard_attack/air_attack - not
      the chassis/tier's own base value for that field, not tick-level
      add_stats, and applied BEFORE the existing multiply_stats percentage
      stage (so it's part of the flat sum that percentage multiplies, not
      a second independent multiplier). Not independently screenshot-
      confirmed - see data/tank_chassis.py's header for the exact
      tier-mapping assumption this relies on.
    """
    tick_levels = tick_levels or {}
    resolved = dict(_resolve_chassis_tier_stats(chassis_key, tier))
    module_additive_multiplier = _tier_module_additive_multiplier(chassis_key, tier)

    role = _ROLE_BY_KEY[role_key] if role_key else None
    if role:
        resolved.update(role["stat_overrides"])

    chosen = [_MODULE_BY_KEY[key] for key in chosen_modules.values() if key]
    active_ticks = [
        (_UPGRADE_BY_KEY[tick_key], level)
        for tick_key, level in tick_levels.items()
        if level
    ]
    role_modifiers = TANK_ROLE_COMBAT_MODIFIERS.get(role_key or chassis_key, {})

    fields = set(resolved) | set(role_modifiers)
    for module in chosen:
        fields.update(module["add_stats"])
        fields.update(module.get("multiply_stats", {}))
    for upgrade, _level in active_ticks:
        fields.update(upgrade["add_stats"])
        if upgrade["per_level_reliability"]:
            fields.add("reliability")

    final_stats = {}
    for field in fields:
        flat = resolved.get(field, 0)
        percent = 0.0
        module_additive = 0.0

        for module in chosen:
            module_additive += module["add_stats"].get(field, 0)
            percent += module.get("multiply_stats", {}).get(field, 0)

        if field in _TIER_MODULE_ADDITIVE_FIELDS:
            flat += module_additive * (1 + module_additive_multiplier)
        else:
            flat += module_additive

        for upgrade, level in active_ticks:
            flat += level * upgrade["add_stats"].get(field, 0)
            if field == "reliability":
                percent += level * upgrade["per_level_reliability"]

        value = flat * (1 + percent)
        value *= role_modifiers.get(field, 1.0)
        final_stats[field] = value

    # (added 1.19.4, formula empirically confirmed 2026-11-02 against 4 real
    # Tank Designer screenshots - see logic/stats.py's matching comment and
    # CLAUDE.md's Tank Designer section) Max Strength (HP) scales with the
    # design's own resolved reliability rather than being a flat chassis
    # stat - "All Tank Chassis except for Land Cruisers" per the real patch
    # note. A role-converted (anti_tank/anti_air/artillery) design shows the
    # "Line" battalion's own base/factor here - every one of those roles
    # always feeds at least a Line battalion, even when it also feeds a
    # Regimental Support item with its own separate, lower base/factor (see
    # logic/stats.py's calculate_item_stats, which applies that
    # consumer-specific value once the design is actually used by a
    # particular battalion/support item).
    if chassis_key == "land_cruiser_chassis":
        final_stats["max_strength"] = 15.0
    elif role and role["role"] in ("anti_tank", "anti_air", "artillery"):
        final_stats["max_strength"] = 0.5 + 0.75 * final_stats["reliability"]
    else:
        final_stats["max_strength"] = 2.0 + 1.5 * final_stats["reliability"]

    return final_stats
