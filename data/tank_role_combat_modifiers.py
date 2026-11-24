# Sourced from https://hoi4.paradoxwikis.com/Land_units ("Armored Battalions"
# and "Armored Combat Support Battalions" tables), cross-validated against
# real Tank Designer screenshots (tank_designer_examples/, gitignored -
# Ollie's own gameplay, see Activity_Log.md 2026-09-16) for every value a
# screenshot could reach - every single one matched a real displayed stat
# exactly (to the display's own 1-decimal truncation, not rounding):
# Medium Tank's plain +15% breakthrough, Medium Tank Destroyer's -25%
# breakthrough / +15% piercing, Medium SP Anti-Air's -53% breakthrough /
# +15% air attack, and Medium Flame Tank's -70% hard_attack/defense/
# armor_value, -45% soft_attack/breakthrough, AND a 0% hardness override
# found by hand-checking a screenshot against the formula before this file
# existed - not something x_tank_chassis.txt's `for_each` block documents at
# all (confirmed by direct re-read).
#
# This is a genuinely hidden HOI4 mechanic: none of these percentages exist
# anywhere in units_copy/, technologies_copy/, or tank_info/ - they're baked
# into the game engine's own per-equipment-type combat modifiers, not
# exposed in any moddable text file this project has a local copy of. The
# wiki is the only available source for the sizes/roles no screenshot
# covers.
#
# Schema: {chassis_or_role_key: {field: multiplier}}. This multiplier is a
# SEPARATE final multiplication stage in logic/tank_designer.py's stats
# formula, layered ON TOP of (not merged into) the regular
# sum-of-module-multiply_stats-percentages stage - confirmed as genuinely
# separate by the Extra Ammo Storage + Radio screenshot: breakthrough there
# is 12 (flat) x 1.15 (radio's own multiply_stats, one stage) x 1.15 (this
# table's medium-chassis entry, a SECOND stage) = 15.87, truncating to the
# screenshot's displayed 15.8 - not 12 x 1.30 = 15.6, which summing radio's
# 15% into this table's 15% as one combined bucket would give.
#
# Keyed by TANK_CHASSIS key for the four plain (role-less) LINE BATTALION
# tank sizes, and by TANK_ROLES key for every combat-support role variant -
# deliberately keyed by chassis/role, not by "role name" alone, since the
# same role's modifier genuinely differs by chassis size (Light Tank
# Destroyer -42% vs Medium -25%).
#
# A key's total absence from this dict (or an empty {} entry) means "no
# modifier at all" (every field's multiplier is implicitly 1.0). This is
# true for:
# - amphibious_tank_chassis and every *_tank_amphibious_chassis role - the
#   wiki explicitly lists "no modifiers" for every Amphibious Tank Battalion
#   row, a deliberate contrast with plain tanks' own +15% breakthrough, not
#   an oversight.
# - land_cruiser_chassis - not an "Armored Battalions"-table unit at all.
# - super_heavy_tank_chassis - confirmed NOT to get the plain-tank +15%
#   breakthrough bonus: unlike light/medium/heavy/modern (which the wiki
#   lists under "Armored Battalions", the line-battalion table), plain
#   "Super Heavy Tank" is listed under "Support Companies" instead - it's a
#   support-company-class unit even in its un-role-converted form (matches
#   this project's own data/tank_chassis.py header note that its base_stats
#   hardness=0 "doesn't apply to support companies"), so it never carries
#   the line-battalion bonus.
# - heavy_tank_destroyer_chassis / modern_tank_destroyer_chassis /
#   heavy_tank_artillery_chassis / modern_tank_artillery_chassis - confirmed
#   genuinely blank via two independent wiki re-fetches (the size-scaling
#   penalty bottoms out to exactly zero at heavy+ sizes for these two roles,
#   unlike SP Anti-Air's penalty, which never fully disappears - Heavy SP
#   Anti-Air's own -35% is still its smallest value, just not zero).
#
# The plain-tank +15% breakthrough entry is screenshot-confirmed only for
# Medium (6 independent screenshots); extended to Light/Heavy/Modern since
# Light Tank's own wiki entry independently lists the identical +15% value,
# suggesting one shared, size-independent constant for the line-battalion
# archetype (unlike every role below, which genuinely does vary by size) -
# not independently screenshot-confirmed for light/heavy/modern.
#
# Every Super Heavy combat-support variant (Tank Destroyer/SP Artillery/SP
# Anti-Air) is confirmed, via two independent wiki re-fetches, to carry
# ONLY the breakthrough penalty - no companion piercing/soft_attack/
# air_attack bonus at all, unlike every other size of the same role.
TANK_ROLE_COMBAT_MODIFIERS = {
    # --- Plain line-battalion tanks (no role) ---
    "light_tank_chassis": {"breakthrough": 1.15},
    "medium_tank_chassis": {"breakthrough": 1.15},  # screenshot-confirmed
    "heavy_tank_chassis": {"breakthrough": 1.15},
    "modern_tank_chassis": {"breakthrough": 1.15},
    # super_heavy_tank_chassis, amphibious_tank_chassis, land_cruiser_chassis:
    # deliberately absent - see header.

    # --- Tank Destroyer (anti_tank role) ---
    # (1.19.4) Breakthrough standardized to -75% (0.25) regardless of size -
    # previously varied 0%/-25%/-42% by weight. Also gained a new, standardized
    # +25% (1.25) Defense bonus, previously nonexistent for this role at all.
    "light_tank_destroyer_chassis": {"breakthrough": 0.25, "ap_attack": 1.15, "defense": 1.25},
    "medium_tank_destroyer_chassis": {"breakthrough": 0.25, "ap_attack": 1.15, "defense": 1.25},
    "heavy_tank_destroyer_chassis": {"breakthrough": 0.25, "defense": 1.25},
    "modern_tank_destroyer_chassis": {"breakthrough": 0.25, "defense": 1.25},
    "super_heavy_tank_destroyer_chassis": {"breakthrough": 0.25, "defense": 1.25},

    # --- SP Artillery (artillery role) ---
    # (1.19.4) Same standardization as Tank Destroyer above - Breakthrough to
    # -75%, new standardized +25% Defense bonus.
    "light_tank_artillery_chassis": {"breakthrough": 0.25, "soft_attack": 1.15, "defense": 1.25},
    "medium_tank_artillery_chassis": {"breakthrough": 0.25, "soft_attack": 1.15, "defense": 1.25},
    "heavy_tank_artillery_chassis": {"breakthrough": 0.25, "defense": 1.25},
    "modern_tank_artillery_chassis": {"breakthrough": 0.25, "defense": 1.25},
    "super_heavy_tank_artillery_chassis": {"breakthrough": 0.25, "defense": 1.25},

    # --- SP Anti-Air (anti_air role) ---
    # (1.19.4) Breakthrough standardized to -75% (0.25) regardless of size -
    # previously varied -35%/-47%/-53%/-55% by weight. No Defense bonus for
    # this role (the patch's +25% Defense item names only Tank Destroyer/SP
    # Artillery, not SP Anti-Air).
    "light_tank_aa_chassis": {"breakthrough": 0.25, "air_attack": 1.15},
    "medium_tank_aa_chassis": {"breakthrough": 0.25, "air_attack": 1.15},
    "heavy_tank_aa_chassis": {"breakthrough": 0.25, "air_attack": 1.15},
    "modern_tank_aa_chassis": {"breakthrough": 0.25, "air_attack": 1.15},
    "super_heavy_tank_aa_chassis": {"breakthrough": 0.25},

    # --- Flame (flame role, support-company only) ---
    # hardness=0 here is a "force to zero" multiplier (0.85 base x 0 = 0),
    # not a percentage reduction - see header. Screenshot-confirmed for
    # medium (defense/armor_value/soft_attack/breakthrough/hardness all
    # matched exactly); light/heavy extended by the same size-scaling
    # pattern already confirmed for every other role above, not
    # independently screenshot-confirmed.
    "light_tank_flame_chassis": {
        "hard_attack": 0.25, "defense": 0.25, "armor_value": 0.25,
        "soft_attack": 0.50, "breakthrough": 0.50, "hardness": 0,
    },
    "medium_tank_flame_chassis": {
        "hard_attack": 0.30, "defense": 0.30, "armor_value": 0.30,
        "soft_attack": 0.55, "breakthrough": 0.55, "hardness": 0,
    },  # screenshot-confirmed
    "heavy_tank_flame_chassis": {
        "hard_attack": 0.375, "defense": 0.375, "armor_value": 0.375,
        "soft_attack": 0.60, "breakthrough": 0.60, "hardness": 0,
    },

    # --- Amphibious (amphibious role) - explicitly "no modifiers" per the
    # wiki, unlike plain tanks' own +15% breakthrough. Listed here for
    # self-documentation even though empty, rather than silently relying on
    # absence-means-1.0. ---
    "light_tank_amphibious_chassis": {},
    "medium_tank_amphibious_chassis": {},
    "heavy_tank_amphibious_chassis": {},
}
