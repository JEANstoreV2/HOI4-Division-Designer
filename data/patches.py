# Hand-curated STAGED/PROPOSED patch diffs for the Patch Impact Preview
# feature (built 2026-11-03) - Intial_problem.md's own "grabs suggested
# changes from the open beta's published for testing how they will effect
# previous designs" goal. NOT a real applied game-data change - see
# data/equipment.py/data/battalion_stats.py for the real, currently-live
# values this app actually computes with everywhere else.
#
# Every real HOI4 balance update so far (1.19.3, 1.19.4) has been applied
# by Claude hand-editing the real data/*.py files directly after Ollie
# supplied the real patch-note text - this file doesn't change that
# process. What it adds is a STAGING step: before committing to a real
# edit, Claude writes the same field-level change here instead, so the
# Patch Impact tab can preview its effect on every saved division first.
# Once Ollie decides to actually apply a staged patch for real, Claude
# hand-edits data/equipment.py/data/battalion_stats.py as always AND
# removes the corresponding entry here in the same commit - leaving a
# staged entry in place after its real application would double-count the
# change and mislead the dropdown into showing it as still "proposed".
#
# Each entry's equipment_overrides/battalion_overrides hold ABSOLUTE
# replacement values (the patch's own "changed to" number), not deltas -
# exactly the numbers Claude would otherwise type directly into
# data/equipment.py/data/battalion_stats.py by hand. Only scalar fields
# logic/stats.py's own lookup chokepoints read are meaningful:
# equipment_overrides is keyed by an EQUIPMENT[key]/EQUIPMENT_TIERS
# "family" key (e.g. "artillery_equipment"); battalion_overrides is keyed
# by a BATTALION_STATS key (battalions AND support companies AND
# regimental support items all share that one table, same as elsewhere in
# this app). A nested-structure change (battalion_mult, equipment_bonus,
# a doctrine/technology unit_bonus value, anything inside Tank Designer's
# own chassis/module/tick data) is out of scope for v1 - logic/stats.py
# has no single override chokepoint for any of those (confirmed via
# Explore) - stays a real hand-edit only, same as every patch before this
# feature existed.
#
# Ships empty - nothing is staged until a real (or open-beta) patch needs
# cross-checking.
STAGED_PATCHES = []

# Reference shape (not an active entry - for whoever edits this file next):
# {
#     "key": "example_1_20_0_artillery_nerf",
#     "label": "1.20.0 (proposed): Artillery Equipment Soft Attack nerf",
#     "source_notes": "Paste or paraphrase the real patch note text here, "
#                      "for traceability back to the source.",
#     "equipment_overrides": {"artillery_equipment": {"soft_attack": 22}},
#     "battalion_overrides": {},
# },
