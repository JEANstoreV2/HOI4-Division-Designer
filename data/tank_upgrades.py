# Hand-curated from tank_info/land_upgrades_copy.txt (HOI4 game file),
# compiled 2026-09-16 for the Tank Designer's Phase 4 (ticks + research
# gating). Only the two NSB tank ticks are compiled -
# `tank_nsb_engine_upgrade`/`tank_nsb_armor_upgrade` - matching
# data/tank_chassis.py's own `tiers[...]["upgrades"]` field, which never
# references anything else: confirmed structurally, not just inferred from
# the source file's DLC comments, since no TANK_CHASSIS entry anywhere lists
# any of the file's other nine (older, 5-level, non-NSB) upgrade types
# (`tank_gun_upgrade`, `tank_armor_upgrade`, `tank_engine_upgrade`,
# `ac_engine_upgrade`, `tank_reliability_upgrade`, `mech_cost_upgrade`,
# `tank_aa_upgrade`, `tank_at_upgrade`, `tank_art_upgrade`) as an available
# tick, so none of them are reachable from any compiled chassis at all.
#
# Schema, per TANK_UPGRADES entry:
# - "key", "name", "max_level" (20 for both - "each level represents ~50HP"
#   for engine, "~10mm of armor" for armor, per the source's own comments).
# - "level_requirements": [{"level", "tech"}, ...] - the real threshold at
#   which a further block of levels becomes reachable, gated by a real
#   technology already compiled in data/technologies.py (armor_tech_1-4/
#   engine_tech_1-4, branch "armor"). Levels below the first threshold (1-4)
#   have no requirement at all - always available regardless of research.
# - "add_stats": every per-level flat stat delta, applied once per tick
#   level chosen (level 3 on maximum_speed = 0.1 per level means +0.3 total,
#   not a one-time value) - confirmed by the source's own "~50HP"/"~10mm"
#   per-level framing.
# - "per_level_reliability": the source lists `reliability` as its own
#   top-level field, separate from the `add_stats` block, on both ticks -
#   kept separate here too (not folded into add_stats) rather than
#   speculatively merged, since nothing else in the source explains why
#   it's split out that way. Behaves identically to an add_stats field:
#   applied once per level.
# - "cost_by_level" / "cost_by_level_for_licensed_equipment": the source's
#   `linear_cost` block - XP cost scaling, compiled but not consumed by any
#   logic yet (no XP/production-cost simulation exists anywhere in this
#   project - matches data/doctrines.py's own unclaimed-mastery-cost
#   precedent).
# - "resource_cost_thresholds": {level: {resource: amount}} - compiled but
#   unused, matching data/tank_modules.py's own `build_cost_resources`
#   precedent (this project doesn't model strategic resources - Ollie's own
#   explicit scope call, see Activity_Log.md 2026-09-16). Both ticks' source
#   blocks also comment out a `chromium` line at higher levels that's kept
#   commented in the source itself (not a currently-live value) - only the
#   still-active `steel` entries are recorded; the engine tick's only
#   threshold (level 10) has nothing live left in it at all once its
#   commented-out chromium line is excluded, hence the empty dict.
TANK_UPGRADES = [
    {
        "key": "tank_nsb_engine_upgrade", "name": "Engine Upgrade", "max_level": 20,
        "level_requirements": [
            {"level": 5, "tech": "engine_tech_1"},
            {"level": 10, "tech": "engine_tech_2"},
            {"level": 15, "tech": "engine_tech_3"},
            {"level": 18, "tech": "engine_tech_4"},
        ],
        "add_stats": {"fuel_consumption": 0.05, "build_cost_ic": 0.1, "maximum_speed": 0.1},
        "per_level_reliability": -0.015,
        "cost_by_level": 1, "cost_by_level_for_licensed_equipment": 5,
        "resource_cost_thresholds": {},
    },
    {
        "key": "tank_nsb_armor_upgrade", "name": "Armor Upgrade", "max_level": 20,
        "level_requirements": [
            {"level": 5, "tech": "armor_tech_1"},
            {"level": 10, "tech": "armor_tech_2"},
            {"level": 15, "tech": "armor_tech_3"},
            {"level": 18, "tech": "armor_tech_4"},
        ],
        "add_stats": {"maximum_speed": -0.1, "breakthrough": 1.25, "build_cost_ic": 0.2, "armor_value": 2.5},
        "per_level_reliability": -0.015,
        "cost_by_level": 1, "cost_by_level_for_licensed_equipment": 2,
        "resource_cost_thresholds": {5: {"steel": 1}, 10: {"steel": 1}, 15: {"steel": 1}},
    },
]
