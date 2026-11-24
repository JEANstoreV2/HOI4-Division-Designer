import pytest

import app as app_module
from app import app


@pytest.fixture
def client():
    return app.test_client()


@pytest.fixture
def state_client(client, tmp_path, monkeypatch):
    # Isolates /api/state tests from the real instance/division_designer.db
    # the live service uses, and from each other.
    monkeypatch.setattr(app_module, "DB_PATH", str(tmp_path / "test.db"))
    return client


def test_home_page_renders(client):
    response = client.get("/")
    assert response.status_code == 200


# --- Session persistence: /api/state (added 2026-10-06) ---

def test_get_state_on_a_fresh_db_returns_an_empty_object(state_client):
    response = state_client.get("/api/state")
    assert response.status_code == 200
    assert response.get_json() == {}


def test_post_then_get_round_trips_a_section_exactly(state_client):
    post_response = state_client.post("/api/state/research", json=["infantry_weapons", "infantry_weapons1"])
    assert post_response.status_code == 200

    get_response = state_client.get("/api/state")
    assert get_response.get_json() == {"research": ["infantry_weapons", "infantry_weapons1"]}


def test_post_round_trips_a_nested_object_section(state_client):
    doctrine = {
        "active_grand_doctrines": ["grand_battle_plan_doctrine"],
        "track_subdoctrines": {"infantry_offense": "superior_firepower_doctrine"},
        "claimed_rewards": {"superior_firepower_doctrine": 2},
    }
    state_client.post("/api/state/doctrine", json=doctrine)
    assert state_client.get("/api/state").get_json() == {"doctrine": doctrine}


def test_multiple_sections_accumulate_independently(state_client):
    state_client.post("/api/state/research", json=["infantry_weapons"])
    state_client.post("/api/state/special_projects", json=["sp_land_land_cruiser"])

    assert state_client.get("/api/state").get_json() == {
        "research": ["infantry_weapons"],
        "special_projects": ["sp_land_land_cruiser"],
    }


def test_posting_the_same_section_again_overwrites_it(state_client):
    state_client.post("/api/state/research", json=["infantry_weapons"])
    state_client.post("/api/state/research", json=["infantry_weapons", "infantry_weapons1"])

    assert state_client.get("/api/state").get_json() == {
        "research": ["infantry_weapons", "infantry_weapons1"]
    }


def test_delete_state_clears_every_section(state_client):
    state_client.post("/api/state/research", json=["infantry_weapons"])
    state_client.post("/api/state/doctrine", json={"active_grand_doctrines": []})

    delete_response = state_client.delete("/api/state")
    assert delete_response.status_code == 200
    assert state_client.get("/api/state").get_json() == {}


# --- Persistence Phase 2: /api/saved-divisions (added 2026-11-02) ---

_BUNDLE = {"composition": [["infantry_brigade", None, None, None, None]], "research": ["infantry_weapons"]}


def test_get_saved_divisions_on_a_fresh_db_returns_empty_list(state_client):
    response = state_client.get("/api/saved-divisions")
    assert response.status_code == 200
    assert response.get_json() == []


def test_post_then_get_round_trips_a_saved_division(state_client):
    post_response = state_client.post("/api/saved-divisions/Infantry%20Push", json=_BUNDLE)
    assert post_response.status_code == 200

    get_response = state_client.get("/api/saved-divisions/Infantry%20Push")
    assert get_response.status_code == 200
    body = get_response.get_json()
    assert body["data"] == _BUNDLE
    assert isinstance(body["saved_at"], str) and body["saved_at"]


def test_get_saved_divisions_lists_the_saved_entry(state_client):
    state_client.post("/api/saved-divisions/Infantry%20Push", json=_BUNDLE)

    listed = state_client.get("/api/saved-divisions").get_json()
    assert len(listed) == 1
    assert listed[0]["name"] == "Infantry Push"
    assert "data" not in listed[0]


def test_get_nonexistent_saved_division_returns_404(state_client):
    response = state_client.get("/api/saved-divisions/Does%20Not%20Exist")
    assert response.status_code == 404


def test_posting_the_same_name_twice_overwrites_not_duplicates(state_client):
    state_client.post("/api/saved-divisions/Infantry%20Push", json=_BUNDLE)
    new_bundle = {"composition": [[None, None, None, None, None]]}
    state_client.post("/api/saved-divisions/Infantry%20Push", json=new_bundle)

    assert state_client.get("/api/saved-divisions/Infantry%20Push").get_json()["data"] == new_bundle
    assert len(state_client.get("/api/saved-divisions").get_json()) == 1


def test_delete_saved_division_removes_it_from_get_and_list(state_client):
    state_client.post("/api/saved-divisions/Infantry%20Push", json=_BUNDLE)

    delete_response = state_client.delete("/api/saved-divisions/Infantry%20Push")
    assert delete_response.status_code == 200
    assert state_client.get("/api/saved-divisions/Infantry%20Push").status_code == 404
    assert state_client.get("/api/saved-divisions").get_json() == []


def test_delete_nonexistent_saved_division_still_returns_ok(state_client):
    response = state_client.delete("/api/saved-divisions/Does%20Not%20Exist")
    assert response.status_code == 200
    assert response.get_json() == {"ok": True}


def test_reset_state_does_not_touch_saved_divisions(state_client):
    # Phase 1's Reset-All (/api/state DELETE) wipes current_state only - a
    # named save is a separate, intentional library, not live scratch state.
    state_client.post("/api/saved-divisions/Infantry%20Push", json=_BUNDLE)
    state_client.post("/api/state/research", json=["infantry_weapons"])

    state_client.delete("/api/state")

    assert state_client.get("/api/state").get_json() == {}
    assert state_client.get("/api/saved-divisions/Infantry%20Push").get_json()["data"] == _BUNDLE


def test_tojson_preserves_dict_order_not_alphabetical(client):
    # Regression test for a real bug (2026-10-06): Jinja2's own `tojson`
    # filter hardcodes sort_keys=True as a policy kwarg, independent of (and
    # not overridden by) Flask's app.json.sort_keys setting - silently
    # reordering every `| tojson` script tag alphabetically. Harmless for
    # most of this app's data, but real for data/tank_chassis.py's own
    # module_slots dicts, whose insertion order drives the Tank Designer
    # module grid's left-to-right layout
    # (static/js/tank_designer.js's renderModuleGrid) - Ollie noticed
    # Land Cruiser's "LC Main Armament" slot wasn't leftmost, since its own
    # slot keys (lc_additional_armament_slot_1, ...) alphabetically precede
    # lc_main_armament_slot; every other chassis's slot names happened to
    # already sort into a sensible order by coincidence. Fixed in app.py via
    # app.jinja_env.policies["json.dumps_kwargs"]["sort_keys"] = False.
    import re
    import json

    html = client.get("/").get_data(as_text=True)
    match = re.search(r'<script id="tank-chassis-data"[^>]*>(.*?)</script>', html, re.S)
    chassis_list = json.loads(match.group(1))
    land_cruiser = next(c for c in chassis_list if c["key"] == "land_cruiser_chassis")

    assert list(land_cruiser["module_slots"].keys())[0] == "lc_main_armament_slot"


def test_home_page_embeds_staged_patches_data(client, monkeypatch):
    # Patch Impact Preview (added 2026-11-03) - STAGED_PATCHES is served to
    # the frontend by template embedding (data/patches.py -> home()'s
    # render_template -> a <script id="staged-patches-data"> tag), the
    # exact same pattern every other hand-curated data/*.py reference list
    # already uses - not a dedicated GET route, for consistency.
    import json
    import re

    fake_patches = [{
        "key": "example", "label": "Example Patch", "source_notes": "test",
        "equipment_overrides": {}, "battalion_overrides": {},
    }]
    monkeypatch.setattr(app_module, "STAGED_PATCHES", fake_patches)

    html = client.get("/").get_data(as_text=True)
    match = re.search(r'<script id="staged-patches-data"[^>]*>(.*?)</script>', html, re.S)
    assert json.loads(match.group(1)) == fake_patches


def test_stats_endpoint_with_no_battalions_returns_null(client):
    response = client.post("/api/stats", json={"battalions": []})
    assert response.status_code == 200
    assert response.get_json() is None


def test_stats_endpoint_returns_division_stats_for_a_real_composition(client):
    response = client.post("/api/stats", json={
        "battalions": ["infantry"] * 7 + ["artillery_brigade"] * 2,
        "support_companies": [],
        "regimental_support": [],
        "researched": [],
    })
    assert response.status_code == 200

    stats = response.get_json()
    assert stats["breakthrough"] == 41  # HOI4 1.19.3 raised artillery_equipment's breakthrough
    assert stats["combat_stats_available"] is True


def test_stats_endpoint_applies_researched_equipment_tiers(client):
    baseline = client.post("/api/stats", json={"battalions": ["mot_artillery_brigade"]}).get_json()
    tier0 = client.post("/api/stats", json={
        "battalions": ["mot_artillery_brigade"], "researched": ["tech_trucks"],
    }).get_json()

    assert tier0["breakthrough"] < baseline["breakthrough"]


def test_stats_endpoint_applies_doctrine_bonuses(client):
    # Mobile Infantry's immediate effect gives category_all_infantry (which
    # infantry belongs to) +10% breakthrough - already proven correct at
    # the logic/stats.py level in tests/test_stats.py; this just confirms
    # the /api/stats route actually threads the doctrine field through.
    baseline = client.post("/api/stats", json={"battalions": ["infantry"]}).get_json()
    with_doctrine = client.post("/api/stats", json={
        "battalions": ["infantry"],
        "doctrine": {
            "active_grand_doctrines": ["new_mobile_warfare"],
            "track_subdoctrines": {"infantry": "mobile_infantry"},
            "claimed_rewards": {},
        },
    }).get_json()

    assert with_doctrine["breakthrough"] == pytest.approx(baseline["breakthrough"] * 1.1)


def test_stats_endpoint_applies_equipment_and_battalion_overrides(client):
    # Patch Impact Preview (added 2026-11-03) - /api/stats grows two more
    # optional body fields threading straight into
    # calculate_division_stats' own equipment_overrides/battalion_overrides
    # parameters (already proven correct in tests/test_stats.py); this just
    # confirms the route itself passes them through.
    baseline = client.post("/api/stats", json={"battalions": ["infantry"]}).get_json()
    with_overrides = client.post("/api/stats", json={
        "battalions": ["infantry"],
        "equipment_overrides": {"infantry_equipment": {"soft_attack": 999}},
        "battalion_overrides": {"infantry": {"max_strength": 999}},
    }).get_json()

    assert with_overrides["soft_attack"] == 999
    assert with_overrides["max_strength"] == 999
    assert with_overrides["hard_attack"] == baseline["hard_attack"]


def test_stats_endpoint_applies_tank_designs(client):
    # Phase 7b: a saved Tank Designer design is keyed by its own chassis/role
    # key (here "light_tank_chassis", light_armor's equipment_key - see
    # data/equipment_needs.py) with zero translation needed - already proven
    # correct at the logic/stats.py level in tests/test_stats.py; this just
    # confirms the /api/stats route actually threads the tank_designs field
    # through, the same way doctrine/researched already do above.
    baseline = client.post("/api/stats", json={"battalions": ["light_armor"]}).get_json()
    with_design = client.post("/api/stats", json={
        "battalions": ["light_armor"],
        "tank_designs": {
            "light_tank_chassis": {
                "chassis_key": "light_tank_chassis", "tier": 0,
                "chosen_modules": {"armor_type_slot": "tank_riveted_armor"},
                "role_key": None, "tick_levels": {},
            },
        },
    }).get_json()

    assert with_design["breakthrough"] != baseline["breakthrough"]


def test_stats_endpoint_without_terrain_key_returns_no_terrain_field(client):
    stats = client.post("/api/stats", json={"battalions": ["infantry"]}).get_json()
    assert stats["terrain"] is None
    # Every existing field is unaffected - the same "omitting a param
    # changes nothing" regression guard every prior phase's route test uses.
    assert stats["soft_attack"] == 6


def test_stats_endpoint_applies_terrain_key(client):
    # Reproduces the real 5x Mountaineers/Mountain screenshots exactly
    # (-15% attacking, +10% defending) - already proven correct at the
    # logic/terrain.py level in tests/test_terrain_logic.py/test_stats.py;
    # this just confirms /api/stats actually threads terrain_key through
    # and folds division_terrain_percentage's result into the response.
    stats = client.post("/api/stats", json={
        "battalions": ["mountaineers"] * 5,
        "researched": ["infantry_weapons"],
        "terrain_key": "mountain",
    }).get_json()

    assert stats["terrain"]["attack_percentage"] == pytest.approx(-0.15)
    assert stats["terrain"]["defense_percentage"] == pytest.approx(0.1)
    # The main (top-level) division numbers are still untouched by terrain
    # selection - still the real screenshot's own 15.0.
    assert stats["soft_attack"] == pytest.approx(15.0)


def test_stats_endpoint_terrain_includes_real_per_side_field_values(client):
    # Ollie's follow-up request: alongside the percentage badge, show the
    # REAL recomputed per-field numbers for each side (not just a blended
    # percentage) - reusing calculate_division_stats' own terrain parameter
    # (built in the logic phase, unused by the route until now). Soft
    # Attack/Hard Attack are affected by both sides; Breakthrough only by
    # attacking; Defense only by defending - see logic/terrain.py's
    # ATTACK_SIDE_FIELDS/DEFENCE_SIDE_FIELDS.
    stats = client.post("/api/stats", json={
        "battalions": ["mountaineers"] * 5,
        "researched": ["infantry_weapons"],
        "terrain_key": "mountain",
    }).get_json()

    # breakthrough: 2.6 (equipment 2 x (1 + Mountaineers' own 0.3) - corrected
    # 2026-10-08, own breakthrough is a percentage not a flat add) x 0.85
    # (mountain attack terrain) x 5 = 11.05.
    assert stats["terrain"]["attacking_stats"] == {
        "soft_attack": pytest.approx(12.75),
        "hard_attack": pytest.approx(2.125),
        "breakthrough": pytest.approx(11.05),
    }
    assert stats["terrain"]["defending_stats"] == {
        "soft_attack": pytest.approx(16.5),
        "hard_attack": pytest.approx(2.75),
        "defense": pytest.approx(110.0),
    }


# --- Pre-selection stat previews: /api/item-stats (added 2026-10-08) ---

def test_item_stats_endpoint_returns_one_entry_per_item(client):
    response = client.post("/api/item-stats", json={
        "items": [
            {"item_key": "infantry", "is_support_type": False},
            {"item_key": "engineer", "is_support_type": True},
        ],
        "researched": [],
    })
    assert response.status_code == 200

    data = response.get_json()
    assert set(data.keys()) == {"infantry", "engineer"}
    assert data["infantry"]["combat_stats_available"] is True
    assert data["engineer"]["combat_stats_available"] is True


def test_item_stats_endpoint_respects_is_support_type(client):
    # engineer has a real own soft_attack field (-0.5) - support-type items
    # apply it as a percentage of equipment, battalions as a flat add, so
    # forcing the flag either way on the same key must give different
    # numbers if the route is actually threading is_support_type through
    # per item rather than ignoring it or hardcoding one value. Called
    # separately (not both in one "items" list) since the response is keyed
    # by item_key alone - two entries with the same key in one request
    # would just overwrite each other.
    as_support = client.post("/api/item-stats", json={
        "items": [{"item_key": "engineer", "is_support_type": True}],
    }).get_json()["engineer"]
    as_battalion = client.post("/api/item-stats", json={
        "items": [{"item_key": "engineer", "is_support_type": False}],
    }).get_json()["engineer"]

    assert as_support["soft_attack"] != as_battalion["soft_attack"]


def test_item_stats_endpoint_is_support_type_defaults_to_false(client):
    omitted = client.post("/api/item-stats", json={
        "items": [{"item_key": "engineer"}],
    }).get_json()["engineer"]
    explicit_false = client.post("/api/item-stats", json={
        "items": [{"item_key": "engineer", "is_support_type": False}],
    }).get_json()["engineer"]

    assert omitted == explicit_false


def test_item_stats_endpoint_applies_researched_equipment_tiers(client):
    # Mirrors test_stats_endpoint_applies_researched_equipment_tiers - same
    # underlying calculate_item_stats call, just via the new single-item
    # route instead of the whole-division one.
    baseline = client.post("/api/item-stats", json={
        "items": [{"item_key": "mot_artillery_brigade"}],
    }).get_json()["mot_artillery_brigade"]
    tier0 = client.post("/api/item-stats", json={
        "items": [{"item_key": "mot_artillery_brigade"}],
        "researched": ["tech_trucks"],
    }).get_json()["mot_artillery_brigade"]

    assert tier0["breakthrough"] < baseline["breakthrough"]


def test_item_stats_endpoint_applies_doctrine_bonuses(client):
    # Mirrors test_stats_endpoint_applies_doctrine_bonuses.
    baseline = client.post("/api/item-stats", json={
        "items": [{"item_key": "infantry"}],
    }).get_json()["infantry"]
    with_doctrine = client.post("/api/item-stats", json={
        "items": [{"item_key": "infantry"}],
        "doctrine": {
            "active_grand_doctrines": ["new_mobile_warfare"],
            "track_subdoctrines": {"infantry": "mobile_infantry"},
            "claimed_rewards": {},
        },
    }).get_json()["infantry"]

    assert with_doctrine["breakthrough"] == pytest.approx(baseline["breakthrough"] * 1.1)


def test_tank_designer_stats_endpoint_returns_stats_and_no_violations_for_a_legal_design(client):
    # The exact light_tank_chassis loadout tests/test_tank_designer.py's own
    # test_baseline_light_tank_design_is_legal already confirms is legal -
    # this just confirms the route threads validate_design/
    # calculate_tank_design_stats through correctly, not the rules themselves.
    response = client.post("/api/tank-designer/stats", json={
        "chassis_key": "light_tank_chassis",
        "tier": 0,
        "chosen_modules": {
            "turret_type_slot": "tank_light_one_man_tank_turret",
            "main_armament_slot": "tank_heavy_machine_gun",
            "suspension_type_slot": "tank_bogie_suspension",
            "armor_type_slot": "tank_riveted_armor",
            "engine_type_slot": "tank_gasoline_engine",
        },
    })
    assert response.status_code == 200

    data = response.get_json()
    assert data["violations"] == []
    assert data["stats"]["armor_value"] == pytest.approx(10.0)


def test_tank_designer_stats_endpoint_reports_a_missing_required_module(client):
    response = client.post("/api/tank-designer/stats", json={
        "chassis_key": "medium_tank_chassis",
        "tier": 1,
        "chosen_modules": {
            "turret_type_slot": "tank_medium_one_man_tank_turret",
            "suspension_type_slot": "tank_bogie_suspension",
            "armor_type_slot": "tank_riveted_armor",
            "engine_type_slot": "tank_gasoline_engine",
        },
    })
    assert response.status_code == 200

    violations = response.get_json()["violations"]
    assert {"type": "missing_required_module", "slot": "main_armament_slot"} in violations


def _light_tank_base_request():
    return {
        "chassis_key": "light_tank_chassis",
        "tier": 0,
        "chosen_modules": {
            "turret_type_slot": "tank_light_one_man_tank_turret",
            "main_armament_slot": "tank_heavy_machine_gun",
            "suspension_type_slot": "tank_bogie_suspension",
            "armor_type_slot": "tank_riveted_armor",
            "engine_type_slot": "tank_gasoline_engine",
        },
    }


def test_tank_designer_preview_stats_module_candidate_matches_the_real_stats_endpoint(client):
    # The preview's module-candidate result should be byte-identical to
    # actually picking that module and calling the real stats endpoint -
    # confirms the route threads build_candidate_design through correctly,
    # not just that it returns something.
    base = _light_tank_base_request()

    preview_response = client.post("/api/tank-designer/preview-stats", json={
        **base,
        "candidates": [{"id": "welded", "type": "module", "slot": "armor_type_slot", "module_key": "tank_welded_armor"}],
    })
    assert preview_response.status_code == 200
    preview = preview_response.get_json()["welded"]

    real_response = client.post("/api/tank-designer/stats", json={
        **base,
        "chosen_modules": {**base["chosen_modules"], "armor_type_slot": "tank_welded_armor"},
    })
    real = real_response.get_json()

    assert preview["stats"] == real["stats"]
    assert preview["violations"] == real["violations"]


def test_tank_designer_preview_stats_chassis_candidate_uses_its_own_default_modules(client):
    # The one rule most likely to regress silently - a chassis-swap
    # candidate must fall back to the CANDIDATE chassis's own
    # default_modules, never the base design's modules (which may not even
    # have matching slot names on a different chassis).
    base = _light_tank_base_request()

    response = client.post("/api/tank-designer/preview-stats", json={
        **base,
        "candidates": [{"id": "medium", "type": "chassis", "chassis_key": "medium_tank_chassis"}],
    })
    assert response.status_code == 200
    result = response.get_json()["medium"]

    medium_defaults_response = client.post("/api/tank-designer/stats", json={
        "chassis_key": "medium_tank_chassis",
        "tier": 0,
        "chosen_modules": {
            "turret_type_slot": "tank_medium_one_man_tank_turret",
            "suspension_type_slot": "tank_bogie_suspension",
            "armor_type_slot": "tank_riveted_armor",
            "engine_type_slot": "tank_gasoline_engine",
        },
    })
    expected = medium_defaults_response.get_json()

    assert result["stats"] == expected["stats"]
    assert result["violations"] == expected["violations"]


def test_tank_designer_preview_stats_multiple_mixed_candidates_return_exactly_those_ids(client):
    base = _light_tank_base_request()

    response = client.post("/api/tank-designer/preview-stats", json={
        **base,
        "candidates": [
            {"id": "tier-up", "type": "tier", "tier": 1},
            {"id": "destroyer", "type": "role", "role_key": "light_tank_destroyer_chassis"},
            {"id": "welded", "type": "module", "slot": "armor_type_slot", "module_key": "tank_welded_armor"},
        ],
    })
    assert response.status_code == 200

    result = response.get_json()
    assert set(result.keys()) == {"tier-up", "destroyer", "welded"}
    for entry in result.values():
        assert "stats" in entry
        assert "violations" in entry


def test_tank_designer_preview_stats_handles_a_non_string_candidate_id(client):
    # Regression guard: tank_designer.js's own tier candidates use the
    # bare numeric tier as their id (e.g. 1, not "1") - a real bug caught
    # live, where mixing a str id (chassis/role/module candidates) with an
    # int id (a tier candidate) in the same response made Flask's default
    # key-sorting JSON serialization crash with a TypeError.
    base = _light_tank_base_request()

    response = client.post("/api/tank-designer/preview-stats", json={
        **base,
        "candidates": [
            {"id": "medium", "type": "chassis", "chassis_key": "medium_tank_chassis"},
            {"id": 1, "type": "tier", "tier": 1},
        ],
    })
    assert response.status_code == 200
    result = response.get_json()
    assert set(result.keys()) == {"medium", "1"}


# --- AI Design Comparison's Research Year constraint (added 2026-11-02) ---

def test_design_search_year_cutoff_replaces_the_clients_own_researched_set(client):
    # main_battle_tank_chassis (year 1945) unlocks modern_armor - even
    # though the client explicitly sent it as already researched, a 1940
    # cutoff must REPLACE that set entirely (Ollie's own call: "pretend
    # it's 1940," not "whatever I've researched that's also early"), so
    # modern_armor stays unreachable and this must return no results
    # rather than silently including it.
    response = client.post("/api/design-search", json={
        "numerator": "max_organisation",
        "researched": ["main_battle_tank_chassis"],
        "constraints": {
            "research_year_cutoff": 1940,
            "required_battalions": [{"key": "modern_armor", "mode": "include"}],
        },
    })
    assert response.status_code == 200
    assert response.get_json()["candidates"] == []


def test_design_search_without_a_cutoff_still_honors_the_clients_researched_set(client):
    # Same researched set, no cutoff this time - modern_armor should be
    # reachable, confirming the cutoff (not researched itself) was what
    # blocked the previous test.
    response = client.post("/api/design-search", json={
        "numerator": "max_organisation",
        "researched": ["main_battle_tank_chassis"],
        "constraints": {
            "required_battalions": [{"key": "modern_armor", "mode": "include"}],
        },
    })
    assert response.status_code == 200
    candidates = response.get_json()["candidates"]
    assert candidates
    for candidate in candidates:
        assert "modern_armor" in candidate["battalions"]


# --- AI Design Comparison Phase 2: Officer Corps as a search variable
# and excluded_battalions (added 2026-11-02) ---

def test_design_search_vary_army_spirits_end_to_end(client):
    response = client.post("/api/design-search", json={
        "numerator": "max_strength",
        "doctrine": {"active_grand_doctrines": ["mass_assault"], "track_subdoctrines": {}, "claimed_rewards": {}},
        "vary_army_spirits": True,
    })
    assert response.status_code == 200
    candidates = response.get_json()["candidates"]
    assert candidates
    for candidate in candidates:
        assert "active_spirits" in candidate["army_spirits"]


def test_design_search_excluded_battalions_end_to_end(client):
    response = client.post("/api/design-search", json={
        "numerator": "max_organisation",
        "constraints": {"excluded_battalions": ["artillery_brigade"]},
    })
    assert response.status_code == 200
    candidates = response.get_json()["candidates"]
    assert candidates
    for candidate in candidates:
        assert "artillery_brigade" not in candidate["battalions"]


def test_design_search_vary_doctrine_with_required_doctrine_end_to_end(client):
    response = client.post("/api/design-search", json={
        "numerator": "max_organisation",
        "vary_doctrine": True,
        "constraints": {"required_doctrines": ["mass_assault"]},
    })
    assert response.status_code == 200
    candidates = response.get_json()["candidates"]
    assert candidates
    for candidate in candidates:
        assert "mass_assault" in candidate["doctrine"]["active_grand_doctrines"]
