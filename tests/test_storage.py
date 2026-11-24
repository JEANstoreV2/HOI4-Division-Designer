import os

import pytest

from storage import (
    clear_all_sections,
    delete_saved_division,
    ensure_db_directory,
    get_all_sections,
    get_saved_division,
    get_section,
    list_saved_divisions,
    save_division,
    set_section,
)


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test.db")


def test_a_section_that_was_never_set_returns_none(db_path):
    assert get_section(db_path, "research") is None


def test_set_then_get_round_trips_exactly(db_path):
    set_section(db_path, "research", ["infantry_weapons", "infantry_weapons1"])
    assert get_section(db_path, "research") == ["infantry_weapons", "infantry_weapons1"]


def test_set_round_trips_a_nested_object_not_just_a_list(db_path):
    doctrine = {
        "active_grand_doctrines": ["grand_battle_plan_doctrine"],
        "track_subdoctrines": {"infantry_offense": "superior_firepower_doctrine"},
        "claimed_rewards": {"superior_firepower_doctrine": 2},
    }
    set_section(db_path, "doctrine", doctrine)
    assert get_section(db_path, "doctrine") == doctrine


def test_setting_a_section_again_overwrites_not_duplicates(db_path):
    set_section(db_path, "research", ["infantry_weapons"])
    set_section(db_path, "research", ["infantry_weapons", "infantry_weapons1"])
    assert get_section(db_path, "research") == ["infantry_weapons", "infantry_weapons1"]


def test_get_all_sections_only_includes_sections_actually_set(db_path):
    set_section(db_path, "research", ["infantry_weapons"])
    assert get_all_sections(db_path) == {"research": ["infantry_weapons"]}


def test_get_all_sections_returns_every_set_section(db_path):
    set_section(db_path, "research", ["infantry_weapons"])
    set_section(db_path, "special_projects", ["sp_land_land_cruiser"])
    assert get_all_sections(db_path) == {
        "research": ["infantry_weapons"],
        "special_projects": ["sp_land_land_cruiser"],
    }


def test_clear_all_sections_removes_everything(db_path):
    set_section(db_path, "research", ["infantry_weapons"])
    set_section(db_path, "doctrine", {"active_grand_doctrines": []})
    clear_all_sections(db_path)
    assert get_all_sections(db_path) == {}
    assert get_section(db_path, "research") is None


def test_clear_all_sections_on_an_already_empty_db_does_not_error(db_path):
    clear_all_sections(db_path)
    assert get_all_sections(db_path) == {}


def test_ensure_db_directory_creates_a_nonexistent_parent_directory(tmp_path):
    # sqlite3.connect doesn't create the parent directory on its own -
    # mirrors app.py's real use (instance/ doesn't exist until this creates
    # it, see storage.py's own header).
    nested_db_path = str(tmp_path / "nested" / "does" / "not" / "exist" / "test.db")
    assert not os.path.isdir(os.path.dirname(nested_db_path))

    ensure_db_directory(nested_db_path)
    assert os.path.isdir(os.path.dirname(nested_db_path))

    set_section(nested_db_path, "research", ["infantry_weapons"])
    assert get_section(nested_db_path, "research") == ["infantry_weapons"]


# --- Persistence Phase 2: named saved divisions (added 2026-11-02) ---

_BUNDLE = {
    "composition": [["infantry_brigade", None, None, None, None]],
    "research": ["infantry_weapons"],
}


def test_get_saved_division_on_a_fresh_db_returns_none(db_path):
    assert get_saved_division(db_path, "Infantry Push") is None


def test_list_saved_divisions_on_a_fresh_db_returns_empty_list(db_path):
    assert list_saved_divisions(db_path) == []


def test_save_then_get_round_trips_exactly(db_path):
    save_division(db_path, "Infantry Push", _BUNDLE, "2026-11-02T10:00:00+00:00")
    saved = get_saved_division(db_path, "Infantry Push")
    assert saved == {"data": _BUNDLE, "saved_at": "2026-11-02T10:00:00+00:00"}


def test_list_saved_divisions_returns_metadata_only_not_data(db_path):
    save_division(db_path, "Infantry Push", _BUNDLE, "2026-11-02T10:00:00+00:00")
    assert list_saved_divisions(db_path) == [
        {"name": "Infantry Push", "saved_at": "2026-11-02T10:00:00+00:00"}
    ]


def test_list_saved_divisions_orders_most_recent_first(db_path):
    save_division(db_path, "Older", {}, "2026-11-01T10:00:00+00:00")
    save_division(db_path, "Newer", {}, "2026-11-02T10:00:00+00:00")
    assert [row["name"] for row in list_saved_divisions(db_path)] == ["Newer", "Older"]


def test_resaving_an_existing_name_overwrites_data_and_saved_at(db_path):
    save_division(db_path, "Infantry Push", _BUNDLE, "2026-11-02T10:00:00+00:00")
    new_bundle = {"composition": [[None, None, None, None, None]]}
    save_division(db_path, "Infantry Push", new_bundle, "2026-11-02T12:00:00+00:00")

    assert get_saved_division(db_path, "Infantry Push") == {
        "data": new_bundle,
        "saved_at": "2026-11-02T12:00:00+00:00",
    }
    assert len(list_saved_divisions(db_path)) == 1


def test_delete_saved_division_removes_it(db_path):
    save_division(db_path, "Infantry Push", _BUNDLE, "2026-11-02T10:00:00+00:00")
    delete_saved_division(db_path, "Infantry Push")
    assert get_saved_division(db_path, "Infantry Push") is None
    assert list_saved_divisions(db_path) == []


def test_delete_saved_division_on_a_nonexistent_name_does_not_error(db_path):
    delete_saved_division(db_path, "Does Not Exist")


def test_current_state_and_saved_divisions_tables_coexist(db_path):
    # Guards storage.py's _connect change from a single schema statement to
    # two - writing to both tables against the same db_path must not
    # collide.
    set_section(db_path, "research", ["infantry_weapons"])
    save_division(db_path, "Infantry Push", _BUNDLE, "2026-11-02T10:00:00+00:00")

    assert get_section(db_path, "research") == ["infantry_weapons"]
    assert get_saved_division(db_path, "Infantry Push") == {
        "data": _BUNDLE,
        "saved_at": "2026-11-02T10:00:00+00:00",
    }
