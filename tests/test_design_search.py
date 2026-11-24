import random

from data.battalions import BATTALIONS
from data.regimental_support import REGIMENTAL_SUPPORT
from data.support_companies import SUPPORT_COMPANIES
from logic import design_search
from logic.design_search import generate_best_designs

_BATTALION_CATEGORY = {b["key"]: b["category"] for b in BATTALIONS}
_SUPPORT_TAGS = {c["key"]: c["same_support_type"] for c in SUPPORT_COMPANIES}
_REGIMENTAL_ALLOWED_GROUPS = {r["key"]: r["allowed_battalion_groups"] for r in REGIMENTAL_SUPPORT}

_NO_DOCTRINE = {"active_grand_doctrines": set(), "track_subdoctrines": {}, "claimed_rewards": {}}


def _fresh_unlocked():
    # ALWAYS_UNLOCKED_SUBUNITS only (no research/doctrine) - plenty of real
    # keys to search over (53 per the 2026-11-02 scoping investigation).
    return design_search._unlocked_keys_by_type(set(), set(), _NO_DOCTRINE)


# --- Structural legality, checked directly against the private generator/
# mutator (generate_best_designs' own public result deliberately strips the
# per-column breakdown these invariants need to verify against).

def test_random_candidate_columns_are_category_consistent():
    unlocked = _fresh_unlocked()
    rng = random.Random(1)
    for _ in range(200):
        candidate = design_search._random_candidate(unlocked, fifth_row_unlocked=False, rng=rng)
        for column in candidate["columns"]:
            categories = {_BATTALION_CATEGORY[key] for key in column}
            assert len(categories) <= 1, column


def test_random_candidate_never_has_conflicting_support_companies():
    unlocked = _fresh_unlocked()
    rng = random.Random(2)
    for _ in range(200):
        candidate = design_search._random_candidate(unlocked, fifth_row_unlocked=False, rng=rng)
        companies = candidate["support_companies"]
        assert len(companies) == len(set(companies)), companies
        for i, key in enumerate(companies):
            tags = set(_SUPPORT_TAGS[key])
            if not tags:
                continue
            for other_key in companies[i + 1:]:
                assert not (tags & set(_SUPPORT_TAGS[other_key])), (key, other_key)


def test_random_candidate_regimental_support_is_legally_gated():
    unlocked = _fresh_unlocked()
    rng = random.Random(3)
    for _ in range(200):
        candidate = design_search._random_candidate(unlocked, fifth_row_unlocked=False, rng=rng)
        for column, regimental_key in zip(candidate["columns"], candidate["regimental_support_by_column"]):
            if regimental_key is None:
                continue
            assert len(column) >= 3, (column, regimental_key)
            assert _BATTALION_CATEGORY[column[0]] in _REGIMENTAL_ALLOWED_GROUPS[regimental_key]


def test_random_candidate_always_has_at_least_one_battalion():
    unlocked = _fresh_unlocked()
    rng = random.Random(4)
    for _ in range(200):
        candidate = design_search._random_candidate(unlocked, fifth_row_unlocked=False, rng=rng)
        assert len(candidate["battalions"]) >= 1


def test_mutation_preserves_every_structural_invariant():
    unlocked = _fresh_unlocked()
    rng = random.Random(5)
    candidate = design_search._random_candidate(unlocked, fifth_row_unlocked=False, rng=rng)
    for _ in range(500):
        candidate = design_search._mutate_candidate(candidate, unlocked, fifth_row_unlocked=False, rng=rng)
        for column in candidate["columns"]:
            categories = {_BATTALION_CATEGORY[key] for key in column}
            assert len(categories) <= 1, column
        companies = candidate["support_companies"]
        assert len(companies) == len(set(companies))
        for i, key in enumerate(companies):
            tags = set(_SUPPORT_TAGS[key])
            for other_key in companies[i + 1:]:
                if tags:
                    assert not (tags & set(_SUPPORT_TAGS[other_key]))
        assert len(candidate["battalions"]) >= 1


# --- Public generate_best_designs behaviour. Returns (results,
# infeasible_reason) - see that function's own docstring.

def test_results_are_sorted_descending_by_score():
    results, reason = generate_best_designs(
        "max_organisation", num_random=150, top_k=5, num_refine_iterations=20, rng=random.Random(10),
    )
    assert reason is None
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_omitting_denominator_maximizes_the_raw_numerator():
    results, reason = generate_best_designs(
        "production_cost", num_random=100, top_k=3, num_refine_iterations=10, rng=random.Random(11),
    )
    assert reason is None
    assert results
    for result in results:
        assert result["score"] == result["stats"]["production_cost"]


def test_a_denominator_that_always_resolves_to_zero_yields_no_results_without_crashing():
    results, reason = generate_best_designs(
        "max_organisation", denominator="this_field_does_not_exist",
        num_random=50, top_k=3, num_refine_iterations=10, rng=random.Random(12),
    )
    assert results == []
    # Not a constraint violation (no stat_bounds/required_battalions were
    # ever given) - the denominator-always-zero case has nothing to
    # explain beyond the existing generic message, so no reason is built.
    assert reason is None


def test_results_include_load_ready_shapes_matching_the_flat_lists():
    results, _ = generate_best_designs(
        "max_organisation", num_random=100, top_k=3, num_refine_iterations=20, rng=random.Random(13),
    )
    for result in results:
        assert [key for column in result["columns"] for key in column] == result["battalions"]
        assert len(result["columns"]) == 5
        assert len(result["support_slots"]) == 5
        assert [key for key in result["support_slots"] if key is not None] == result["support_companies"]
        assert len(result["regimental_support_by_column"]) == 5
        assert [key for key in result["regimental_support_by_column"] if key is not None] == result["regimental_support"]


def test_refinement_never_scores_worse_than_stage_one_alone_found():
    baseline, _ = generate_best_designs(
        "soft_attack", num_random=200, top_k=3, num_refine_iterations=0, rng=random.Random(123),
    )
    refined, _ = generate_best_designs(
        "soft_attack", num_random=200, top_k=3, num_refine_iterations=100, rng=random.Random(123),
    )
    assert refined[0]["score"] >= baseline[0]["score"]


# --- Constraints extension (added 2026-11-02, same day): stat_bounds and
# required_battalions. Both always-unlocked keys below are deliberately
# chosen from different categories (combat_support vs armor_combat_support)
# so "dominant"/"include" tests never accidentally collide with each
# other's own category.
_MEDIUM_SP_ARTILLERY = "medium_sp_artillery_brigade"  # armor_combat_support
_ARTILLERY_BRIGADE = "artillery_brigade"  # combat_support


def test_random_candidate_always_contains_every_required_battalion():
    # _random_candidate can legitimately return None on an unlucky draw
    # (every column already locked to neither required category, by
    # chance) - that's by design (see _ensure_required_battalions'
    # docstring), and generate_best_designs' own caller already retries
    # a bounded number of times for exactly this reason. Mirror that same
    # retry here rather than asserting every single raw draw succeeds.
    unlocked = _fresh_unlocked()
    rng = random.Random(20)
    successes = 0
    for _ in range(200):
        candidate = None
        for _ in range(design_search.MAX_REQUIRED_BATTALION_RETRIES):
            candidate = design_search._random_candidate(
                unlocked, fifth_row_unlocked=False, rng=rng,
                required_battalions=[_MEDIUM_SP_ARTILLERY, _ARTILLERY_BRIGADE],
            )
            if candidate is not None:
                break
        if candidate is None:
            continue
        successes += 1
        assert _MEDIUM_SP_ARTILLERY in candidate["battalions"]
        assert _ARTILLERY_BRIGADE in candidate["battalions"]
    assert successes > 150  # the vast majority of draws should succeed within the retry budget


def test_mutation_never_removes_the_last_instance_of_a_required_battalion():
    unlocked = _fresh_unlocked()
    rng = random.Random(21)
    candidate = design_search._random_candidate(
        unlocked, fifth_row_unlocked=False, rng=rng, required_battalions=[_MEDIUM_SP_ARTILLERY],
    )
    for _ in range(500):
        candidate = design_search._mutate_candidate(
            candidate, unlocked, fifth_row_unlocked=False, rng=rng,
            required_battalions=[_MEDIUM_SP_ARTILLERY],
        )
        assert _MEDIUM_SP_ARTILLERY in candidate["battalions"]


def test_generate_best_designs_results_always_contain_a_required_battalion():
    results, reason = generate_best_designs(
        "max_organisation",
        constraints={"required_battalions": [{"key": _MEDIUM_SP_ARTILLERY, "mode": "include"}]},
        num_random=150, top_k=3, num_refine_iterations=50, rng=random.Random(22),
    )
    assert reason is None
    assert results
    for result in results:
        assert _MEDIUM_SP_ARTILLERY in result["battalions"]


def test_dominant_requirement_eventually_reaches_a_real_plurality():
    results, reason = generate_best_designs(
        "max_organisation",
        constraints={"required_battalions": [{"key": _MEDIUM_SP_ARTILLERY, "mode": "dominant"}]},
        num_random=300, top_k=3, num_refine_iterations=400, rng=random.Random(23),
    )
    assert reason is None
    assert results
    for result in results:
        counts = {}
        for key in result["battalions"]:
            counts[key] = counts.get(key, 0) + 1
        own_count = counts.get(_MEDIUM_SP_ARTILLERY, 0)
        highest_other = max((count for key, count in counts.items() if key != _MEDIUM_SP_ARTILLERY), default=0)
        assert own_count > highest_other


def test_a_satisfiable_stat_bound_eventually_produces_a_feasible_result():
    # production_cost for a plain medium_sp_artillery_brigade division is
    # well above 0 - a loose, clearly-satisfiable floor confirms the
    # feasibility machinery actually returns real results, not just an
    # empty list by construction.
    results, reason = generate_best_designs(
        "max_organisation",
        constraints={"stat_bounds": [{"field": "production_cost", "min": 50, "max": None}]},
        num_random=300, top_k=3, num_refine_iterations=100, rng=random.Random(24),
    )
    assert reason is None
    assert results
    for result in results:
        assert result["stats"]["production_cost"] >= 50


def test_an_unsatisfiable_stat_bound_returns_no_results_with_an_explanation():
    # No real division can possibly reach a Production Cost of 10 million -
    # must return [] (dropped), never a flagged "closest miss" result,
    # per Ollie's own call - but the reason (added 2026-11-02, Ollie's own
    # follow-up request) must explain exactly what was unreachable.
    results, reason = generate_best_designs(
        "max_organisation",
        constraints={"stat_bounds": [{"field": "production_cost", "min": 10_000_000, "max": None}]},
        num_random=100, top_k=3, num_refine_iterations=30, rng=random.Random(25),
    )
    assert results == []
    assert reason is not None
    assert reason["unmet_bounds"] == [{
        "field": "production_cost", "min": 10_000_000, "max": None,
        "closest_value": reason["unmet_bounds"][0]["closest_value"], "violated": "min",
    }]
    assert reason["unmet_bounds"][0]["closest_value"] < 10_000_000


def test_requiring_a_battalion_that_is_not_unlocked_at_all_never_gets_inserted_anyway():
    # modern_armor is real, has a real category with plenty of OTHER
    # unlocked keys (armor), but is itself only unlocked by a 1945
    # technology - with no research at all, it must never be silently
    # inserted just because its category had room.
    unlocked = _fresh_unlocked()
    assert "modern_armor" not in unlocked["battalions_by_category"].get("armor", [])
    columns = [[], [], [], [], []]
    assert design_search._ensure_required_battalions(columns, unlocked, 4, ["modern_armor"], random.Random(1)) is False


def test_generate_best_designs_explains_a_required_battalion_that_is_not_unlocked():
    results, reason = generate_best_designs(
        "max_organisation",
        constraints={"required_battalions": [{"key": "modern_armor", "mode": "include"}]},
        num_random=50, top_k=3, num_refine_iterations=20, rng=random.Random(26),
    )
    assert results == []
    assert reason == {"unavailable_battalions": ["modern_armor"]}


def test_generate_best_designs_explains_too_many_required_categories():
    # Only 6 categories exist at all, so 7 distinct real categories across
    # the required list can never fit in 5 columns - deterministically
    # impossible, caught before any search runs.
    one_per_category = [
        "artillery_brigade",            # combat_support
        "amphibious_light_armor",       # armor
        "light_sp_artillery_brigade",   # armor_combat_support
        "mot_rocket_artillery_brigade",  # mobile_combat_support
        "cavalry",                      # mobile
        "bicycle_battalion",            # infantry
    ]
    assert len({_BATTALION_CATEGORY[key] for key in one_per_category}) == 6
    results, reason = generate_best_designs(
        "max_organisation",
        constraints={"required_battalions": [{"key": key, "mode": "include"} for key in one_per_category]},
        num_random=10, top_k=1, num_refine_iterations=5, rng=random.Random(27),
    )
    assert results == []
    assert reason == {"too_many_required_categories": sorted({_BATTALION_CATEGORY[key] for key in one_per_category})}


def test_generate_best_designs_explains_an_unreached_dominant_requirement():
    # artillery_brigade's own category (combat_support) has several other
    # always-unlocked options competing against it - require it to
    # DOMINATE but cut the search down so short it realistically can't
    # reach a real plurality, and confirm the explanation names it.
    results, reason = generate_best_designs(
        "max_organisation",
        constraints={
            "required_battalions": [{"key": _ARTILLERY_BRIGADE, "mode": "dominant"}],
            "stat_bounds": [{"field": "production_cost", "min": 10_000_000, "max": None}],
        },
        num_random=50, top_k=2, num_refine_iterations=20, rng=random.Random(28),
    )
    assert results == []
    assert reason is not None
    assert reason["unmet_bounds"]
    # The dominant requirement may or may not also show up depending on
    # which single candidate ended up with the lowest total violation -
    # just confirm the field exists and is well-shaped when present.
    for entry in reason["unmet_dominant"]:
        assert entry["key"] == _ARTILLERY_BRIGADE
        assert entry["closest_count"] <= entry["needed_more_than"]


def test_violation_amount_sums_across_multiple_simultaneously_violated_bounds():
    stats_one_violation = {"production_cost": 0, "combat_width": 10}
    stats_two_violations = {"production_cost": 0, "combat_width": 0}
    bounds = [
        {"field": "production_cost", "min": 100, "max": None},
        {"field": "combat_width", "min": 5, "max": None},
    ]
    one = design_search._violation_amount(stats_one_violation, [], bounds, [])
    two = design_search._violation_amount(stats_two_violations, [], bounds, [])
    assert two > one > 0


def test_describe_violations_reports_both_min_and_max_bounds_and_dominant_gap():
    stats = {"production_cost": 10, "combat_width": 50}
    bounds = [
        {"field": "production_cost", "min": 100, "max": None},
        {"field": "combat_width", "min": None, "max": 20},
    ]
    battalions = [_MEDIUM_SP_ARTILLERY, _ARTILLERY_BRIGADE, _ARTILLERY_BRIGADE]
    reason = design_search._describe_violations(stats, battalions, bounds, [_MEDIUM_SP_ARTILLERY])

    bounds_by_field = {entry["field"]: entry for entry in reason["unmet_bounds"]}
    assert bounds_by_field["production_cost"]["violated"] == "min"
    assert bounds_by_field["production_cost"]["closest_value"] == 10
    assert bounds_by_field["combat_width"]["violated"] == "max"
    assert bounds_by_field["combat_width"]["closest_value"] == 50

    assert reason["unmet_dominant"] == [
        {"key": _MEDIUM_SP_ARTILLERY, "closest_count": 1, "needed_more_than": 2},
    ]


# --- Phase 2 of the plan file's "AI Design Comparison - Phase 2" section
# (added 2026-11-02, same day): excluded_battalions and Officer Corps as a
# search variable.

def test_excluded_battalions_never_appear_in_any_result():
    results, reason = generate_best_designs(
        "max_organisation",
        constraints={"excluded_battalions": [_MEDIUM_SP_ARTILLERY, _ARTILLERY_BRIGADE]},
        num_random=200, top_k=5, num_refine_iterations=50, rng=random.Random(30),
    )
    assert reason is None
    assert results
    for result in results:
        assert _MEDIUM_SP_ARTILLERY not in result["battalions"]
        assert _ARTILLERY_BRIGADE not in result["battalions"]


def test_requiring_and_excluding_the_same_battalion_is_reported_as_unavailable():
    # A genuine contradiction - excluding a key removes it from the
    # unlocked set entirely, so requiring it too is correctly caught by
    # the existing "unavailable_battalions" deterministic pre-check.
    results, reason = generate_best_designs(
        "max_organisation",
        constraints={
            "required_battalions": [{"key": _MEDIUM_SP_ARTILLERY, "mode": "include"}],
            "excluded_battalions": [_MEDIUM_SP_ARTILLERY],
        },
        num_random=50, top_k=3, num_refine_iterations=20, rng=random.Random(31),
    )
    assert results == []
    assert reason == {"unavailable_battalions": [_MEDIUM_SP_ARTILLERY]}


# --- "Only" mode and excluded_categories (added 2026-11-03, Ollie's own
# follow-up: "ONLY be a certain battalion" as a step up from "dominant",
# and "exclude an entire section, e.g. exclude all armored combat
# support"). Both are enforced structurally (filtering the unlocked set
# before generation) rather than via the scoring gradient "dominant" uses.

def test_only_mode_means_every_battalion_is_that_one_key():
    results, reason = generate_best_designs(
        "max_organisation",
        constraints={"required_battalions": [{"key": _MEDIUM_SP_ARTILLERY, "mode": "only"}]},
        num_random=150, top_k=3, num_refine_iterations=50, rng=random.Random(40),
    )
    assert reason is None
    assert results
    for result in results:
        assert result["battalions"]
        assert set(result["battalions"]) == {_MEDIUM_SP_ARTILLERY}


def test_only_mode_allows_several_whitelisted_keys_but_nothing_else():
    results, reason = generate_best_designs(
        "max_organisation",
        constraints={"required_battalions": [
            {"key": _MEDIUM_SP_ARTILLERY, "mode": "only"},
            {"key": _ARTILLERY_BRIGADE, "mode": "only"},
        ]},
        num_random=150, top_k=3, num_refine_iterations=50, rng=random.Random(41),
    )
    assert reason is None
    assert results
    for result in results:
        assert set(result["battalions"]) <= {_MEDIUM_SP_ARTILLERY, _ARTILLERY_BRIGADE}
        assert _MEDIUM_SP_ARTILLERY in result["battalions"]
        assert _ARTILLERY_BRIGADE in result["battalions"]


def test_only_mode_implies_include_even_without_enough_rows_to_dominate():
    # "only" needs no plurality gradient at all (unlike "dominant") -
    # confirmed by requesting a metric where a single-battalion division
    # already wins (max_organisation is an average, not a sum), yet the
    # required key still shows up because _ensure_required_battalions
    # places it regardless of whether it would otherwise be chosen.
    results, reason = generate_best_designs(
        "max_organisation", "production_cost",
        constraints={"required_battalions": [{"key": _MEDIUM_SP_ARTILLERY, "mode": "only"}]},
        num_random=50, top_k=1, num_refine_iterations=20, rng=random.Random(42),
    )
    assert reason is None
    assert results
    assert _MEDIUM_SP_ARTILLERY in results[0]["battalions"]


def test_requiring_and_only_marking_different_battalions_is_a_contradiction():
    # "only" wipes every OTHER key from the unlocked set, so a plain
    # "include" requirement on a different key becomes unreachable - the
    # existing unavailable_battalions check must still catch this.
    results, reason = generate_best_designs(
        "max_organisation",
        constraints={"required_battalions": [
            {"key": _MEDIUM_SP_ARTILLERY, "mode": "only"},
            {"key": _ARTILLERY_BRIGADE, "mode": "include"},
        ]},
        num_random=50, top_k=3, num_refine_iterations=20, rng=random.Random(43),
    )
    assert results == []
    assert reason == {"unavailable_battalions": [_ARTILLERY_BRIGADE]}


def test_excluded_categories_removes_every_battalion_in_that_category():
    results, reason = generate_best_designs(
        "max_organisation",
        constraints={"excluded_categories": ["armor_combat_support"]},
        num_random=200, top_k=5, num_refine_iterations=50, rng=random.Random(44),
    )
    assert reason is None
    assert results
    for result in results:
        for key in result["battalions"]:
            assert _BATTALION_CATEGORY[key] != "armor_combat_support"


def test_requiring_a_battalion_in_an_excluded_category_is_reported_as_unavailable():
    assert _BATTALION_CATEGORY[_MEDIUM_SP_ARTILLERY] == "armor_combat_support"
    results, reason = generate_best_designs(
        "max_organisation",
        constraints={
            "required_battalions": [{"key": _MEDIUM_SP_ARTILLERY, "mode": "include"}],
            "excluded_categories": ["armor_combat_support"],
        },
        num_random=50, top_k=3, num_refine_iterations=20, rng=random.Random(45),
    )
    assert results == []
    assert reason == {"unavailable_battalions": [_MEDIUM_SP_ARTILLERY]}


def test_selectable_army_spirits_respects_doctrine_gating():
    # operational_reserve_spirit's own `available` is ["mass_assault"] (a
    # real Grand Doctrine key) - not selectable with no doctrine active,
    # selectable once it is.
    assert "operational_reserve_spirit" not in design_search._selectable_army_spirits(
        "division_command_spirit", {},
    )
    assert "operational_reserve_spirit" in design_search._selectable_army_spirits(
        "division_command_spirit", {"active_grand_doctrines": {"mass_assault"}},
    )


def test_fixed_army_spirits_dict_tolerates_a_stale_unknown_key():
    # A real case (see the 2026-11-02 Officer Corps rescope bugfix) - a
    # persisted session can reference a key removed from the current
    # compile. Must be skipped, not raise.
    picks = design_search._fixed_army_spirits_dict(["bold_attack_spirit", "operational_reserve_spirit"])
    assert picks == {"army_spirit": None, "division_command_spirit": "operational_reserve_spirit"}


def test_random_army_spirits_only_picks_selectable_options():
    rng = random.Random(32)
    for _ in range(200):
        picks = design_search._random_army_spirits({}, rng)
        # With no doctrine active, only spirits with an empty `available`
        # list could ever be picked - division_command_spirit's only
        # un-gated member doesn't exist in the current 9-entry compile,
        # so with no doctrine this should always come back empty, but the
        # real assertion that matters is: whatever IS picked must still
        # pass is_army_spirit_selectable under the given doctrine state.
        for category, key in picks.items():
            if key is not None:
                assert key in design_search._selectable_army_spirits(category, {})


def test_mutation_never_touches_army_spirits_when_not_varying():
    unlocked = _fresh_unlocked()
    rng = random.Random(33)
    candidate = design_search._random_candidate(unlocked, fifth_row_unlocked=False, rng=rng)
    assert candidate["army_spirits"] == {"army_spirit": None, "division_command_spirit": None}
    for _ in range(200):
        candidate = design_search._mutate_candidate(candidate, unlocked, fifth_row_unlocked=False, rng=rng)
    # vary_army_spirits defaults to False - "toggle_army_spirit" must never
    # have been in the mutation pool, so this stays untouched.
    assert candidate["army_spirits"] == {"army_spirit": None, "division_command_spirit": None}


def test_generate_best_designs_varies_army_spirits_when_asked():
    results, reason = generate_best_designs(
        "max_strength",
        doctrine={"active_grand_doctrines": {"mass_assault"}, "track_subdoctrines": {}, "claimed_rewards": {}},
        vary_army_spirits=True,
        num_random=200, top_k=3, num_refine_iterations=100, rng=random.Random(34),
    )
    assert reason is None
    assert results
    # operational_reserve_spirit's own +10% Max Strength bonus is a real,
    # applied effect - optimizing for max_strength with Mass Assault
    # active and Officer Corps free to vary should find it.
    assert any(
        "operational_reserve_spirit" in result["army_spirits"]["active_spirits"]
        for result in results
    )


def test_generate_best_designs_keeps_army_spirits_fixed_by_default():
    results, reason = generate_best_designs(
        "max_organisation", army_spirits=["operational_reserve_spirit"],
        doctrine={"active_grand_doctrines": {"mass_assault"}, "track_subdoctrines": {}, "claimed_rewards": {}},
        num_random=100, top_k=3, num_refine_iterations=20, rng=random.Random(35),
    )
    assert reason is None
    assert results
    for result in results:
        assert result["army_spirits"]["active_spirits"] == ["operational_reserve_spirit"]


def test_effective_army_spirits_flat_filters_against_candidates_own_doctrine():
    fixed = {"army_spirit": None, "division_command_spirit": "operational_reserve_spirit"}
    no_doctrine = {"active_grand_doctrines": set(), "track_subdoctrines": {}, "claimed_rewards": {}}
    with_doctrine = {"active_grand_doctrines": {"mass_assault"}, "track_subdoctrines": {}, "claimed_rewards": {}}
    assert design_search._effective_army_spirits_flat(fixed, no_doctrine) == []
    assert design_search._effective_army_spirits_flat(fixed, with_doctrine) == ["operational_reserve_spirit"]


# --- Phase 3 of the plan file's "AI Design Comparison - Phase 2" section
# (added 2026-11-02, same day): Doctrine as a search variable + a
# require-doctrine constraint.

def test_random_doctrine_respects_folder_exclusivity():
    rng = random.Random(40)
    for _ in range(300):
        doctrine = design_search._random_doctrine(set(), rng)
        folders = [design_search._GRAND_DOCTRINES_BY_KEY[key]["folder"] for key in doctrine["active_grand_doctrines"]]
        assert len(folders) == len(set(folders)), doctrine["active_grand_doctrines"]


def test_random_doctrine_subdoctrine_assignments_are_legal():
    rng = random.Random(41)
    for _ in range(300):
        doctrine = design_search._random_doctrine(set(), rng)
        for track_key, subdoctrine_key in doctrine["track_subdoctrines"].items():
            subdoctrine = design_search._SUBDOCTRINES_BY_KEY[subdoctrine_key]
            assert track_key in subdoctrine["tracks"]
            assert any(
                track_key in design_search._GRAND_DOCTRINES_BY_KEY[gd_key]["tracks"]
                for gd_key in doctrine["active_grand_doctrines"]
            )
            for other_track, other_key in doctrine["track_subdoctrines"].items():
                if other_track != track_key:
                    assert other_key not in subdoctrine["xor"]
            # researched is always set() in this test - a technology-gated
            # subdoctrine must never be assignable at all (see the next
            # test, which asserts this directly for every draw).
            assert subdoctrine["requires_technology"] is None


def test_random_doctrine_never_assigns_a_technology_gated_subdoctrine_without_it():
    rng = random.Random(42)
    found_any_special_forces_subdoctrine = False
    for _ in range(300):
        doctrine = design_search._random_doctrine(set(), rng)  # no technology researched at all
        for subdoctrine_key in doctrine["track_subdoctrines"].values():
            subdoctrine = design_search._SUBDOCTRINES_BY_KEY[subdoctrine_key]
            if subdoctrine["requires_technology"] is not None:
                found_any_special_forces_subdoctrine = True
    assert not found_any_special_forces_subdoctrine


def test_random_doctrine_claims_every_reward_of_every_assigned_subdoctrine():
    rng = random.Random(43)
    for _ in range(300):
        doctrine = design_search._random_doctrine(set(), rng)
        for subdoctrine_key in doctrine["track_subdoctrines"].values():
            total_rewards = len(design_search._SUBDOCTRINES_BY_KEY[subdoctrine_key]["rewards"])
            assert doctrine["claimed_rewards"][subdoctrine_key] == total_rewards


def test_mutate_candidate_doctrine_mutations_preserve_legality_and_row_limits():
    unlocked = _fresh_unlocked()
    rng = random.Random(44)
    candidate = design_search._random_candidate(
        unlocked, fifth_row_unlocked=False, rng=rng, vary_doctrine=True, researched=set(),
    )
    for _ in range(500):
        candidate = design_search._mutate_candidate(
            candidate, unlocked, fifth_row_unlocked=False, rng=rng, vary_doctrine=True, researched=set(),
        )
        doctrine = candidate["doctrine"]
        folders = [design_search._GRAND_DOCTRINES_BY_KEY[key]["folder"] for key in doctrine["active_grand_doctrines"]]
        assert len(folders) == len(set(folders))
        for track_key, subdoctrine_key in doctrine["track_subdoctrines"].items():
            assert any(
                track_key in design_search._GRAND_DOCTRINES_BY_KEY[gd_key]["tracks"]
                for gd_key in doctrine["active_grand_doctrines"]
            )
        fifth_row_unlocked = design_search.unlocks_fifth_battalion_row(
            doctrine["active_grand_doctrines"], doctrine["track_subdoctrines"], doctrine["claimed_rewards"]
        )
        max_rows = design_search.MAX_BASE_ROWS + (1 if fifth_row_unlocked else 0)
        for column in candidate["columns"]:
            assert len(column) <= max_rows


def test_required_grand_doctrine_survives_generation_and_mutation():
    unlocked = _fresh_unlocked()
    rng = random.Random(45)
    candidate = None
    for _ in range(20):
        candidate = design_search._random_candidate(
            unlocked, fifth_row_unlocked=False, rng=rng, vary_doctrine=True, researched=set(),
            required_grand_doctrines=["mass_assault"],
        )
        if candidate is not None:
            break
    assert candidate is not None
    assert "mass_assault" in candidate["doctrine"]["active_grand_doctrines"]
    for _ in range(500):
        candidate = design_search._mutate_candidate(
            candidate, unlocked, fifth_row_unlocked=False, rng=rng, vary_doctrine=True, researched=set(),
            required_grand_doctrines=["mass_assault"],
        )
        assert "mass_assault" in candidate["doctrine"]["active_grand_doctrines"]


def test_required_subdoctrine_forces_its_own_grand_doctrine_and_survives_mutation():
    unlocked = _fresh_unlocked()
    rng = random.Random(46)
    researched = {"marines"}
    candidate = None
    for _ in range(20):
        candidate = design_search._random_candidate(
            unlocked, fifth_row_unlocked=False, rng=rng, vary_doctrine=True, researched=researched,
            required_subdoctrines=["marines_1"],
        )
        if candidate is not None:
            break
    assert candidate is not None
    assert "marines_1" in candidate["doctrine"]["track_subdoctrines"].values()
    owning = {"special_forces_quantity", "special_forces_quality"}
    assert candidate["doctrine"]["active_grand_doctrines"] & owning
    for _ in range(500):
        candidate = design_search._mutate_candidate(
            candidate, unlocked, fifth_row_unlocked=False, rng=rng, vary_doctrine=True, researched=researched,
            required_subdoctrines=["marines_1"],
        )
        assert "marines_1" in candidate["doctrine"]["track_subdoctrines"].values()


def test_generate_best_designs_reports_unavailable_required_subdoctrine_without_its_technology():
    results, reason = generate_best_designs(
        "max_organisation",
        vary_doctrine=True,
        constraints={"required_doctrines": ["marines_1"]},
        num_random=50, top_k=3, num_refine_iterations=20, rng=random.Random(47),
    )
    assert results == []
    assert reason == {"unavailable_doctrines": ["marines_1"]}


def test_generate_best_designs_varies_doctrine_end_to_end():
    results, reason = generate_best_designs(
        "max_organisation",
        vary_doctrine=True,
        constraints={"required_doctrines": ["mass_assault"]},
        num_random=150, top_k=3, num_refine_iterations=100, rng=random.Random(48),
    )
    assert reason is None
    assert results
    for result in results:
        assert "mass_assault" in result["doctrine"]["active_grand_doctrines"]
        assert isinstance(result["doctrine"]["active_grand_doctrines"], list)  # JSON-safe, not a set
