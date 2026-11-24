from data.battalions import BATTALIONS
from data.regimental_support import REGIMENTAL_SUPPORT
from data.support_companies import SUPPORT_COMPANIES
from data.terrain import GENERIC_TERRAIN_MODIFIERS, TERRAIN_TYPES, UNIT_TERRAIN_MODIFIERS

ALL_ITEM_KEYS = (
    {b["key"] for b in BATTALIONS}
    | {s["key"] for s in SUPPORT_COMPANIES}
    | {r["key"] for r in REGIMENTAL_SUPPORT}
)

VALID_TERRAIN_KEYS = {t["key"] for t in TERRAIN_TYPES}
VALID_MODIFIER_FIELDS = {"attack", "defence", "movement"}


def test_terrain_types_has_exactly_11_entries():
    # A regression tripwire, mirroring test_unit_categories.py's own
    # entry-count check - the 8 true terrain + 3 combat-situation split is
    # a deliberate scope call (see data/terrain.py's header), not something
    # that should silently drift.
    assert len(TERRAIN_TYPES) == 11


def test_terrain_types_map_terrain_split_is_8_and_3():
    map_terrain = [t for t in TERRAIN_TYPES if t["is_map_terrain"]]
    situational = [t for t in TERRAIN_TYPES if not t["is_map_terrain"]]
    assert len(map_terrain) == 8
    assert {"fort", "river", "amphibious"} == {t["key"] for t in situational}


def test_every_terrain_modifier_item_is_a_real_composition_item():
    assert set(UNIT_TERRAIN_MODIFIERS) <= ALL_ITEM_KEYS


def test_every_terrain_key_used_is_a_real_terrain_type():
    for item_key, terrain_blocks in UNIT_TERRAIN_MODIFIERS.items():
        for terrain_key in terrain_blocks:
            assert terrain_key in VALID_TERRAIN_KEYS, (item_key, terrain_key)


def test_every_modifier_field_is_attack_defence_or_movement():
    for item_key, terrain_blocks in UNIT_TERRAIN_MODIFIERS.items():
        for terrain_key, fields in terrain_blocks.items():
            assert fields, (item_key, terrain_key)  # no empty blocks
            assert set(fields) <= VALID_MODIFIER_FIELDS, (item_key, terrain_key)


def test_no_item_has_an_empty_terrain_dict():
    # An item with no terrain data is absent from UNIT_TERRAIN_MODIFIERS
    # entirely (see data/terrain.py's header) - it should never appear
    # with a present-but-empty {}.
    for item_key, terrain_blocks in UNIT_TERRAIN_MODIFIERS.items():
        assert terrain_blocks, item_key


def test_regimental_support_has_no_terrain_data_at_all():
    # Confirmed by direct read of every units_copy/ source for all 14
    # regimental support items - none have any terrain block.
    regimental_support_keys = {r["key"] for r in REGIMENTAL_SUPPORT}
    assert not (regimental_support_keys & set(UNIT_TERRAIN_MODIFIERS))


def test_expected_entry_count():
    # 65 items with real terrain data: 20 Armor/Armored Combat Support +
    # 20 Infantry/Mobile/Combat Support/Mobile Combat Support + 25 Support
    # Companies + 0 Regimental Support (see data/terrain.py's header for
    # the full accounting). A regression tripwire, mirroring
    # test_unit_categories.py's own count check.
    assert len(UNIT_TERRAIN_MODIFIERS) == 65


# Spot-checks against a direct units_copy/ read (not just internal
# consistency) - mirrors test_unit_categories.py's own spot-check style.

def test_mountaineers_hills_and_mountain_bonus():
    # units_copy/infantry.txt: hills = { attack = 0.2 defence = 0.05
    # movement = 0.1 }, mountain = { attack = 0.35 defence = 0.1
    # movement = 0.2 }.
    assert UNIT_TERRAIN_MODIFIERS["mountaineers"]["hills"] == {
        "attack": 0.2, "defence": 0.05, "movement": 0.1,
    }
    assert UNIT_TERRAIN_MODIFIERS["mountaineers"]["mountain"] == {
        "attack": 0.35, "defence": 0.1, "movement": 0.2,
    }


def test_infantry_and_paratrooper_have_no_terrain_data():
    # Confirmed absent from units_copy/infantry.txt entirely, unlike most
    # of their siblings in the same file.
    assert "infantry" not in UNIT_TERRAIN_MODIFIERS
    assert "paratrooper" not in UNIT_TERRAIN_MODIFIERS


def test_amphibious_armor_variants_share_identical_terrain_blocks():
    # Confirmed genuine in units_copy/amphibious_armor.txt (byte-identical
    # blocks for all 4 variants), not a transcription shortcut.
    variants = ["amphibious_armor", "amphibious_light_armor", "amphibious_medium_armor", "amphibious_heavy_armor"]
    first = UNIT_TERRAIN_MODIFIERS[variants[0]]
    for key in variants[1:]:
        assert UNIT_TERRAIN_MODIFIERS[key] == first


def test_heavy_armor_has_a_fort_bonus_but_medium_does_not():
    # units_copy/heavy_armor.txt: fort = { attack = 0.1 }. No such block
    # exists in units_copy/medium_armor.txt.
    assert UNIT_TERRAIN_MODIFIERS["heavy_armor"]["fort"] == {"attack": 0.1}
    assert "fort" not in UNIT_TERRAIN_MODIFIERS["medium_armor"]


def test_divisional_support_artillery_and_at_have_no_terrain_data():
    # units_copy/artillery.txt/anti_tank.txt: the *divisional support*
    # versions (data/support_companies.py's "artillery"/"anti_tank"), as
    # opposed to the battalion-grid *_brigade versions, have no terrain
    # block at all - confirmed by direct read.
    assert "artillery" not in UNIT_TERRAIN_MODIFIERS
    assert "anti_tank" not in UNIT_TERRAIN_MODIFIERS
    assert "artillery_brigade" in UNIT_TERRAIN_MODIFIERS


# --- GENERIC_TERRAIN_MODIFIERS (terrain_copy/00_terrain.txt) ---
# Confirmed 2026-09-29 against two real screenshots - see CLAUDE.md's
# Terrain section for the exact reconciliation math.

def test_generic_terrain_modifiers_has_exactly_the_6_types_with_a_value():
    # Confirmed by direct read of terrain_copy/00_terrain.txt: plains and
    # desert have no `units` block at all, and fort/river/amphibious don't
    # appear in the file's `categories` block at all - only 6 of the 11
    # TERRAIN_TYPES keys have a generic modifier.
    assert set(GENERIC_TERRAIN_MODIFIERS) == {
        "forest", "hills", "mountain", "urban", "jungle", "marsh",
    }


def test_generic_terrain_modifiers_only_ever_set_attack():
    # terrain_copy/00_terrain.txt never sets `defence` for any terrain
    # type, and `movement` is commented out (inactive) everywhere - the
    # entire generic layer, as this game version ships, is attack-only.
    for terrain_key, fields in GENERIC_TERRAIN_MODIFIERS.items():
        assert set(fields) == {"attack"}, terrain_key


def test_generic_terrain_modifier_exact_values():
    # terrain_copy/00_terrain.txt: categories.<key>.units.attack.
    assert GENERIC_TERRAIN_MODIFIERS["forest"]["attack"] == -0.15
    assert GENERIC_TERRAIN_MODIFIERS["hills"]["attack"] == -0.25
    assert GENERIC_TERRAIN_MODIFIERS["mountain"]["attack"] == -0.5
    assert GENERIC_TERRAIN_MODIFIERS["urban"]["attack"] == -0.3
    assert GENERIC_TERRAIN_MODIFIERS["jungle"]["attack"] == -0.3
    assert GENERIC_TERRAIN_MODIFIERS["marsh"]["attack"] == -0.4


def test_every_generic_terrain_key_is_a_real_map_terrain_type():
    map_terrain_keys = {t["key"] for t in TERRAIN_TYPES if t["is_map_terrain"]}
    assert set(GENERIC_TERRAIN_MODIFIERS) <= map_terrain_keys
