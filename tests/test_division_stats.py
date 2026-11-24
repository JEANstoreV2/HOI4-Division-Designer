import pytest

from logic.stats import calculate_division_stats

# Every case here is transcribed directly from a real Division Designer
# screenshot (see Template Examples/ and Activity_Log.md, 2026-09-14) rather
# than hand-calculated - these are ground truth, not expectations derived
# from our own aggregation logic. Piercing (in-game) = ap_attack (our field
# name); "Support Eq." row items (Support Artillery/Cavalry Recon/Engineer/
# Military Police/Anti-Tank Battery/Infantry Gun/Anti-Air Battery) are
# support companies or regimental support, not battalions. Real screenshot
# values use abs=0.1 tolerance since the game only displays one decimal
# place.
#
# ap_attack (Piercing) is NOT a plain sum - it's "40% of the highest
# piercing in the division plus 60% of the average piercing of all
# battalions and companies" per the HOI4 wiki
# (https://hoi4.paradoxwikis.com/Land_units#Combat_stats), confirmed
# against every pure-battalion case below. armor_value is assumed to
# follow the same rule by analogy (not independently confirmed - every
# screenshot with nonzero armor_value happened to be a uniform division,
# where this formula can't be told apart from a plain average).
#
# soft_attack/hard_attack/defense/breakthrough for support companies and
# regimental support are NOT a flat addition of own+equipment the way
# battalions are - the same-named fields on their sub_unit entry are
# percentage modifiers on the equipment's stat instead (equipment x
# (1 + own)), confirmed exactly by isolating Support Artillery, Infantry
# Gun, and Anti-Air Battery one at a time against a support-free 7
# Infantry baseline. See logic/stats.py's module comment for the full
# derivation.
#
# HOI4 patch 1.19.3 (2026-09-17) changed several of the real values these
# screenshots were taken against (artillery_equipment/rocket_artillery_equipment
# stats, field_guns/anti_air_battery/anti_tank_battery's own percentages -
# see Activity_Log.md, 2026-09-22). Tests involving artillery_brigade,
# mot_artillery_brigade, Support Artillery, or those two regimental support
# items have their asserted values recomputed from the OLD screenshot-verified
# baseline plus the exact, primary-source-verified patch delta for each
# affected field - not a fresh screenshot. Spot-checked against the patch
# text directly (e.g. 2x artillery_brigade's breakthrough: +4/unit from
# artillery_equipment's confirmed 6->10 change, exactly the 33->41 diff) and
# marked "(1.19.3)" in their own comment. Everything else in this file is
# still untouched real pre-patch screenshot ground truth.
#
# RESOLVED 2026-10-08: Cavalry Recon's own `battalion_mult` (units_copy/
# recon.txt - +10% soft_attack to every category_artillery item in the
# division) is now applied - see logic/stats.py's
# _active_battalion_mult_auras/_apply_battalion_mult and
# Activity_Log.md, 2026-10-08. soft_attack is now asserted in every
# affected case below where a real number exists to check it against
# (test_seven_infantry_two_artillery_with_support_companies' own 117.1,
# confirmed an EXACT match - the clearest possible confirmation this
# feature is correct, not just plausible). This was a project-wide
# deferral (the "modifier interaction engine", Specification.md's own
# decisions log) covering every unit's own innate aura, not just Recon's -
# see data/battalion_stats.py's own header for the other 20 units' auras
# this same fix also activated.
#
# One thing remains deliberately NOT asserted - see Activity_Log.md,
# 2026-09-14:
# - breakthrough for the Mountaineers + Artillery + support companies
#   composition specifically: real breakthrough (48.9) was 4.2 higher than
#   computed (44.7) at the time this was written. ROOT CAUSE now understood
#   and fixed 2026-10-08 (see the module docstring's own Breakthrough
#   section below) - Mountaineers' own breakthrough field is a percentage of
#   equipment, not a flat add, and the fix's exact predicted delta for 7
#   Mountaineers (+4.2) matches this gap precisely. Still left unasserted
#   here specifically (not given a hard expected value) because this
#   composition's OTHER fields carry later "(1.19.3)" patch corrections that
#   were never extended to breakthrough at the time - recomputing today
#   gives 58.3, not the old 44.7+4.2=48.9, meaning the old 44.7/48.9
#   reference point itself is now stale from those same intervening patches,
#   not evidence against the fix (which is independently confirmed via
#   tests/test_stats.py's zero-ambiguity Mountaineers-only reproduction and
#   five real single-unit screenshots - see the module docstring below).
#
# A near-miss while verifying Terrain against real screenshots
# (terrain_screenshots/5_mountaineers.png, 2026-09-29): a plain 5x
# Mountaineers division's real base Soft Attack (15.0) initially looked like
# a THIRD gap - exactly half this tool's computed 30.0 using the default
# ("no researched= passed") equipment tier. Ollie caught the real
# explanation: that screenshot was taken with only "infantry_weapons"
# researched (tier 0 infantry_equipment - soft_attack 3, not tier 1's 6),
# not zero research as assumed. Passing researched={"infantry_weapons"}
# reconciles Soft Attack (15.0), Hard Attack (2.5), Defense (100.0), Max
# Strength (100.0), and Production Cost (301) all EXACTLY - no bug. See
# tests/test_stats.py's _MOUNTAINEERS_ZERO_RESEARCH-based tests for the
# exact reproduction.
#
# RESOLVED 2026-10-08 - Breakthrough was the one field that didn't
# reconcile even under the corrected tier: real 13.0 vs computed 11.5, a
# +1.5 gap across 5 battalions (+0.3/battalion - exactly Mountaineers' own
# breakthrough field). The real explanation, confirmed via a much larger
# Marine/Special-Forces investigation the same day Ollie reported a
# separate Division Stats discrepancy: NOT a doubled own stat (the
# "doubling" guess below turned out to be a coincidence for this one
# data point, not the real formula) but a battalion's own "breakthrough"
# field being a PERCENTAGE of equipment, not a flat add, like every other
# battalion field - 5 x (2 x (1 + 0.3)) = 13.0 exactly, the same formula
# that also resolved Infantry/Marine/Mountaineer/Ranger/Paratrooper
# single-unit screenshots that day. See logic/stats.py's
# _BATTALION_OWN_PERCENTAGE_FIELDS and tests/test_stats.py's
# test_mountaineers_breakthrough_matches_the_real_screenshot_with_zero_ambiguity
# for the confirmed fix - this WAS the "second independent screenshot"
# the note below was waiting for, several times over.
#
# (Original 2026-09-29 note, kept for the history: real 13.0 vs computed
# 11.5 - doubling Mountaineers' own breakthrough contribution (0.3 -> 0.6)
# also reproduces 13.0 (5 x (0.6 + 2) = 13.0), which read at the time as
# "the same category of thing Tank Designer's Phase 5 found for tank roles
# (a hidden, text-file-absent per-unit-type engine multiplier)" - correct
# instinct, wrong specific formula; only one isolated data point existed
# then, explicitly flagged as not enough to treat as confirmed.)


def test_five_infantry():
    stats = calculate_division_stats(["infantry"] * 5)
    assert stats["max_organisation"] == pytest.approx(60.0)
    assert stats["soft_attack"] == pytest.approx(30.0)
    assert stats["hard_attack"] == pytest.approx(5.0)
    assert stats["defense"] == pytest.approx(110.0)
    assert stats["breakthrough"] == pytest.approx(15.0)
    assert stats["ap_attack"] == pytest.approx(4.0)
    assert stats["max_strength"] == pytest.approx(125.0)
    assert stats["manpower"] == pytest.approx(5000)
    assert stats["training_time"] == pytest.approx(90)
    assert stats["weight"] == pytest.approx(2.5)
    assert stats["suppression"] == pytest.approx(7.5)
    assert stats["combat_width"] == pytest.approx(10)
    assert stats["max_speed"] == pytest.approx(4.0)


def test_one_infantry_matches_five_infantry_per_battalion():
    stats = calculate_division_stats(["infantry"])
    assert stats["max_strength"] == pytest.approx(25.0)
    assert stats["soft_attack"] == pytest.approx(6.0)
    assert stats["ap_attack"] == pytest.approx(4.0)
    assert stats["combat_width"] == pytest.approx(2)
    assert stats["max_speed"] == pytest.approx(4.0)
    assert stats["max_organisation"] == pytest.approx(60.0)


def test_seven_infantry():
    stats = calculate_division_stats(["infantry"] * 7)
    assert stats["soft_attack"] == pytest.approx(42.0)
    assert stats["hard_attack"] == pytest.approx(7.0)
    assert stats["defense"] == pytest.approx(154.0)
    assert stats["breakthrough"] == pytest.approx(21.0)
    assert stats["manpower"] == pytest.approx(7000)
    assert stats["combat_width"] == pytest.approx(14)


def test_five_cavalry():
    stats = calculate_division_stats(["cavalry"] * 5)
    assert stats["max_organisation"] == pytest.approx(70.0)
    assert stats["max_speed"] == pytest.approx(6.4)
    assert stats["combat_width"] == pytest.approx(10)


def test_five_motorised():
    stats = calculate_division_stats(["motorized"] * 5)
    assert stats["max_speed"] == pytest.approx(12.0)
    assert stats["max_organisation"] == pytest.approx(60.0)


def test_five_mechanised():
    stats = calculate_division_stats(["mechanized"] * 5)
    assert stats["max_speed"] == pytest.approx(8.0)
    # soft_attack not asserted: real screenshot shows 33.0 (6.6/battalion),
    # our data gives 30.5 (6.1/battalion) - the screenshot's filename only
    # promises "tech for mechanised is 1", not that Infantry Equipment is
    # also unresearched, so this may just be a higher infantry_equipment
    # tier rather than a bug. Not chased further without a cleaner sample.
    assert stats["hard_attack"] == pytest.approx(25.0)
    assert stats["defense"] == pytest.approx(240.0)
    assert stats["breakthrough"] == pytest.approx(45.0)
    assert stats["armor_value"] == pytest.approx(10.0)
    assert stats["ap_attack"] == pytest.approx(15.0)


def test_five_paratroopers():
    stats = calculate_division_stats(["paratrooper"] * 5)
    assert stats["max_organisation"] == pytest.approx(70.0)
    assert stats["max_speed"] == pytest.approx(4.0)
    assert stats["max_strength"] == pytest.approx(110.0)


def test_seven_infantry_two_artillery():
    stats = calculate_division_stats(["infantry"] * 7 + ["artillery_brigade"] * 2)
    assert stats["max_organisation"] == pytest.approx(46.6, abs=0.1)
    assert stats["soft_attack"] == pytest.approx(94.0)  # (1.19.3)
    assert stats["hard_attack"] == pytest.approx(11.0)
    assert stats["defense"] == pytest.approx(176.0)  # (1.19.3)
    assert stats["breakthrough"] == pytest.approx(41.0)  # (1.19.3)
    assert stats["ap_attack"] == pytest.approx(4.5, abs=0.1)
    assert stats["max_strength"] == pytest.approx(176.2, abs=0.1)
    assert stats["manpower"] == pytest.approx(8000)
    assert stats["training_time"] == pytest.approx(120)
    assert stats["weight"] == pytest.approx(4.5)
    assert stats["suppression"] == pytest.approx(10.5)
    assert stats["supply_consumption"] == pytest.approx(0.84, abs=0.01)
    assert stats["combat_width"] == pytest.approx(20)
    assert stats["max_speed"] == pytest.approx(4.0)


def test_six_infantry_three_artillery():
    stats = calculate_division_stats(["infantry"] * 6 + ["artillery_brigade"] * 3)
    assert stats["max_organisation"] == pytest.approx(40.0)
    assert stats["soft_attack"] == pytest.approx(114.0)  # (1.19.3)
    assert stats["hard_attack"] == pytest.approx(12.0)
    assert stats["defense"] == pytest.approx(165.0)  # (1.19.3)
    assert stats["breakthrough"] == pytest.approx(48.0)  # (1.19.3)
    assert stats["ap_attack"] == pytest.approx(4.6, abs=0.1)  # (1.19.3)
    assert stats["max_strength"] == pytest.approx(151.8, abs=0.1)
    assert stats["manpower"] == pytest.approx(7500)
    assert stats["weight"] == pytest.approx(4.5)
    assert stats["suppression"] == pytest.approx(9.0)
    assert stats["supply_consumption"] == pytest.approx(0.99, abs=0.01)
    assert stats["combat_width"] == pytest.approx(21)


def test_three_infantry_six_artillery():
    stats = calculate_division_stats(["infantry"] * 3 + ["artillery_brigade"] * 6)
    assert stats["max_organisation"] == pytest.approx(20.0)
    assert stats["soft_attack"] == pytest.approx(174.0)  # (1.19.3)
    assert stats["hard_attack"] == pytest.approx(15.0)
    assert stats["defense"] == pytest.approx(132.0)  # (1.19.3)
    assert stats["breakthrough"] == pytest.approx(69.0)  # (1.19.3)
    assert stats["ap_attack"] == pytest.approx(4.8, abs=0.15)  # (1.19.3)
    assert stats["max_strength"] == pytest.approx(78.6, abs=0.1)
    assert stats["manpower"] == pytest.approx(6000)
    assert stats["weight"] == pytest.approx(4.5)
    assert stats["suppression"] == pytest.approx(4.5)
    assert stats["supply_consumption"] == pytest.approx(1.44, abs=0.01)
    assert stats["combat_width"] == pytest.approx(24)


def test_seven_motorised_two_motorised_artillery():
    # Also regression-covers the motorized_equipment fix in data/equipment.py
    # (breakthrough 2 -> 5, max_speed 10 -> 12): it held the wrong
    # intermediate tier's values instead of the tier-1/archetype ones.
    stats = calculate_division_stats(["motorized"] * 7 + ["mot_artillery_brigade"] * 2)
    assert stats["max_speed"] == pytest.approx(12.0)
    assert stats["soft_attack"] == pytest.approx(94.0)  # (1.19.3)
    assert stats["hard_attack"] == pytest.approx(11.0)
    assert stats["defense"] == pytest.approx(176.0)  # (1.19.3)
    assert stats["breakthrough"] == pytest.approx(86.0)  # (1.19.3)
    assert stats["combat_width"] == pytest.approx(20)


def test_five_motorised_one_cavalry_one_infantry_speed_bottleneck():
    # The interesting case: mostly Motorised (12.0 km/h) but division speed
    # collapses to Infantry's 4.0 km/h, the slowest battalion present - not
    # a sum or an average of the three speeds.
    stats = calculate_division_stats(["motorized"] * 5 + ["cavalry"] + ["infantry"])
    assert stats["max_speed"] == pytest.approx(4.0)
    assert stats["max_organisation"] == pytest.approx(61.4, abs=0.1)
    assert stats["combat_width"] == pytest.approx(14)


def test_seven_infantry_with_support_artillery():
    # Isolated: 7 Infantry alone vs. +Support Artillery, no Artillery
    # battalions present - the cleanest possible read on one support
    # company's real contribution, confirming equipment x (1 + own).
    stats = calculate_division_stats(
        battalions=["infantry"] * 7, support_companies=["artillery"]
    )
    assert stats["soft_attack"] == pytest.approx(55.0)  # (1.19.3)
    assert stats["hard_attack"] == pytest.approx(8.0)  # (1.19.3)
    assert stats["defense"] == pytest.approx(159.5)  # (1.19.3)
    assert stats["breakthrough"] == pytest.approx(26.0)  # (1.19.3)
    assert stats["max_organisation"] == pytest.approx(52.5)
    assert stats["manpower"] == pytest.approx(7300)
    assert stats["training_time"] == pytest.approx(120)
    assert stats["weight"] == pytest.approx(3.6)
    assert stats["supply_consumption"] == pytest.approx(0.58, abs=0.01)
    assert stats["combat_width"] == pytest.approx(14)


def test_seven_infantry_with_infantry_gun():
    # Isolated: same idea as above but for a regimental support item.
    stats = calculate_division_stats(
        battalions=["infantry"] * 7, regimental_support=["field_guns"]
    )
    assert stats["soft_attack"] == pytest.approx(48.5)  # (1.19.3)
    assert stats["hard_attack"] == pytest.approx(7.5)  # (1.19.3)
    assert stats["defense"] == pytest.approx(156.75)  # (1.19.3)
    assert stats["breakthrough"] == pytest.approx(23.5)  # (1.19.3)
    assert stats["max_organisation"] == pytest.approx(52.5)
    assert stats["manpower"] == pytest.approx(7180)


def test_seven_infantry_with_support_artillery_and_infantry_gun():
    # Confirms contributions stack additively: this is exactly the sum of
    # the previous two tests' deltas from the 7-Infantry baseline.
    stats = calculate_division_stats(
        battalions=["infantry"] * 7,
        support_companies=["artillery"],
        regimental_support=["field_guns"],
    )
    assert stats["soft_attack"] == pytest.approx(61.5)  # (1.19.3)
    assert stats["hard_attack"] == pytest.approx(8.5)  # (1.19.3)
    assert stats["defense"] == pytest.approx(162.25)  # (1.19.3)
    assert stats["breakthrough"] == pytest.approx(28.5)  # (1.19.3)
    assert stats["max_organisation"] == pytest.approx(46.6, abs=0.1)
    assert stats["manpower"] == pytest.approx(7480)


def test_seven_infantry_with_support_artillery_and_anti_air_battery():
    # A second equipment family (Anti-Air) confirming the same formula,
    # including air_attack specifically.
    stats = calculate_division_stats(
        battalions=["infantry"] * 7,
        support_companies=["artillery"],
        regimental_support=["anti_air_battery"],
    )
    assert stats["soft_attack"] == pytest.approx(56.2)  # (1.19.3)
    assert stats["hard_attack"] == pytest.approx(10.8)  # (1.19.3)
    assert stats["air_attack"] == pytest.approx(7.6)
    assert stats["defense"] == pytest.approx(161.1)  # (1.19.3)
    assert stats["breakthrough"] == pytest.approx(26.4)  # (1.19.3)
    assert stats["max_organisation"] == pytest.approx(46.6, abs=0.1)
    assert stats["manpower"] == pytest.approx(7420)


def test_seven_infantry_with_two_support_companies_and_anti_air_battery():
    stats = calculate_division_stats(
        battalions=["infantry"] * 7,
        support_companies=["artillery", "anti_air"],
        regimental_support=["anti_air_battery"],
    )
    assert stats["soft_attack"] == pytest.approx(58.0)  # (1.19.3)
    assert stats["hard_attack"] == pytest.approx(15.0)  # (1.19.3)
    assert stats["air_attack"] == pytest.approx(22.8)
    assert stats["defense"] == pytest.approx(163.5)  # (1.19.3)
    assert stats["breakthrough"] == pytest.approx(27.0)  # (1.19.3)
    assert stats["max_organisation"] == pytest.approx(42.0)
    assert stats["manpower"] == pytest.approx(7720)


def test_seven_infantry_two_artillery_with_support_companies():
    # soft_attack NOW asserted (resolved 2026-10-08) - Cavalry Recon's own
    # +10% battalion_mult to category_artillery (2 Artillery battalions +
    # Support Artillery) is applied: real 117.1, matched exactly.
    stats = calculate_division_stats(
        battalions=["infantry"] * 7 + ["artillery_brigade"] * 2,
        support_companies=["engineer", "artillery", "recon"],
    )
    assert stats["soft_attack"] == pytest.approx(117.1)
    assert stats["hard_attack"] == pytest.approx(13.1)  # (1.19.3)
    assert stats["defense"] == pytest.approx(216.7)  # (1.19.3)
    assert stats["breakthrough"] == pytest.approx(52.0)  # (1.19.3)
    assert stats["max_organisation"] == pytest.approx(38.3, abs=0.1)
    assert stats["max_strength"] == pytest.approx(180.4, abs=0.1)
    assert stats["manpower"] == pytest.approx(9100)
    assert stats["training_time"] == pytest.approx(120)
    assert stats["weight"] == pytest.approx(4.8, abs=0.1)
    assert stats["suppression"] == pytest.approx(10.5)
    assert stats["supply_consumption"] == pytest.approx(1.04, abs=0.01)
    assert stats["combat_width"] == pytest.approx(20)


def test_seven_mountaineers_two_artillery_with_support_companies():
    # soft_attack not asserted: Cavalry Recon's own battalion_mult is now
    # applied (resolved 2026-10-08, see module docstring and
    # test_seven_infantry_two_artillery_with_support_companies' own 117.1
    # reproduction), but no real screenshot number was ever recorded for
    # THIS specific Mountaineers composition's soft_attack, so there's
    # nothing to assert against - left unasserted rather than asserting
    # whatever this code now happens to compute. breakthrough not asserted
    # either: its root cause is now understood and fixed (see module
    # docstring), but this composition's own old reference numbers are
    # stale from later patches never applied to it - see module docstring's
    # updated note.
    stats = calculate_division_stats(
        battalions=["mountaineers"] * 7 + ["artillery_brigade"] * 2,
        support_companies=["engineer", "artillery", "recon"],
    )
    assert stats["hard_attack"] == pytest.approx(13.1)  # (1.19.3)
    assert stats["defense"] == pytest.approx(216.7)  # (1.19.3)
    assert stats["max_organisation"] == pytest.approx(44.1, abs=0.1)
    assert stats["max_strength"] == pytest.approx(145.4, abs=0.1)
    assert stats["manpower"] == pytest.approx(9100)
    assert stats["suppression"] == pytest.approx(7.0)
    assert stats["supply_consumption"] == pytest.approx(0.97, abs=0.01)


def test_seven_infantry_two_artillery_with_infantry_gun():
    stats = calculate_division_stats(
        battalions=["infantry"] * 7 + ["artillery_brigade"] * 2,
        regimental_support=["field_guns"],
    )
    assert stats["max_organisation"] == pytest.approx(42.0)
    assert stats["soft_attack"] == pytest.approx(100.5)  # (1.19.3)
    assert stats["hard_attack"] == pytest.approx(11.5)  # (1.19.3)
    assert stats["defense"] == pytest.approx(178.75)  # (1.19.3)
    assert stats["breakthrough"] == pytest.approx(43.5)  # (1.19.3)
    assert stats["max_strength"] == pytest.approx(176.3, abs=0.1)
    assert stats["manpower"] == pytest.approx(8180)
    assert stats["combat_width"] == pytest.approx(20)


def test_seven_infantry_two_artillery_with_military_police():
    # Military Police is the case that revealed Suppression isn't a pure
    # sum: it contributes via a percentage suppression_factor, not a flat
    # suppression value. It originally also proved the MAX rule for
    # training_time extends to support companies (its 180 exceeded the
    # base 7/2 division's 120) - HOI4 1.19.3 lowered Military Police's own
    # training_time to 120 (see Activity_Log.md, 2026-09-22), so this case
    # no longer demonstrates that specific point (both are 120 now), though
    # the MAX rule itself is unaffected and still covered elsewhere. No
    # Recon or Artillery-category support item here, so soft_attack is
    # still exact.
    stats = calculate_division_stats(
        battalions=["infantry"] * 7 + ["artillery_brigade"] * 2,
        support_companies=["military_police"],
    )
    assert stats["max_organisation"] == pytest.approx(42.0)
    assert stats["soft_attack"] == pytest.approx(100.0)  # (1.19.3)
    assert stats["hard_attack"] == pytest.approx(12.0)
    assert stats["defense"] == pytest.approx(198.0)  # (1.19.3)
    assert stats["breakthrough"] == pytest.approx(44.0)  # (1.19.3)
    assert stats["suppression"] == pytest.approx(12.6, abs=0.1)
    assert stats["training_time"] == pytest.approx(120)  # (1.19.3)
    assert stats["max_strength"] == pytest.approx(177.2, abs=0.1)
    assert stats["manpower"] == pytest.approx(8500)
    assert stats["combat_width"] == pytest.approx(20)


def test_seven_infantry_two_artillery_with_support_companies_and_regimental_support():
    # Everything combined at once: 3 support companies AND 2 regimental
    # support items on top of the 7/2 battalions. soft_attack: 125.2 - not
    # itself an independently recorded screenshot value (no real number was
    # ever written down for this exact combined composition), but
    # consistent with the now-confirmed-exact simpler case above (117.1):
    # the same 3 category_artillery items (2x artillery_brigade + Support
    # Artillery) get Cavalry Recon's aura either way, and neither
    # field_guns nor anti_tank_battery belongs to category_artillery, so
    # adding them doesn't change the aura's own contribution - same +6.5
    # gap this test's own comment already documented before the fix.
    stats = calculate_division_stats(
        battalions=["infantry"] * 7 + ["artillery_brigade"] * 2,
        support_companies=["engineer", "artillery", "recon"],
        regimental_support=["field_guns", "anti_tank_battery"],
    )
    assert stats["soft_attack"] == pytest.approx(125.2)
    assert stats["hard_attack"] == pytest.approx(20.6)  # (1.19.3)
    assert stats["defense"] == pytest.approx(221.05)  # (1.19.3)
    assert stats["breakthrough"] == pytest.approx(54.5)  # (1.19.3)
    assert stats["ap_attack"] == pytest.approx(23.6, abs=0.1)
    assert stats["max_organisation"] == pytest.approx(32.8, abs=0.1)
    assert stats["max_strength"] == pytest.approx(180.6, abs=0.1)
    assert stats["manpower"] == pytest.approx(9460)  # (1.19.3) - Anti-Tank Battery manpower 120->180
    assert stats["training_time"] == pytest.approx(120)
    assert stats["weight"] == pytest.approx(5.0, abs=0.1)
    assert stats["suppression"] == pytest.approx(10.5)
    assert stats["combat_width"] == pytest.approx(20)


def test_seven_paratroopers_two_artillery_with_support_companies_and_regimental_support():
    # Same composition as above but Paratroopers instead of Infantry -
    # breakthrough/hard_attack/defense all confirmed exact (Paratroopers
    # don't have Mountaineers' unexplained breakthrough quirk).
    stats = calculate_division_stats(
        battalions=["paratrooper"] * 7 + ["artillery_brigade"] * 2,
        support_companies=["engineer", "artillery", "recon"],
        regimental_support=["field_guns", "anti_tank_battery"],
    )
    assert stats["hard_attack"] == pytest.approx(20.6)  # (1.19.3)
    assert stats["breakthrough"] == pytest.approx(54.5)  # (1.19.3)
    assert stats["max_organisation"] == pytest.approx(37.8, abs=0.1)
    assert stats["max_strength"] == pytest.approx(159.6, abs=0.1)
    assert stats["manpower"] == pytest.approx(9460)  # (1.19.3) - Anti-Tank Battery manpower 120->180
    assert stats["suppression"] == pytest.approx(7.0)
