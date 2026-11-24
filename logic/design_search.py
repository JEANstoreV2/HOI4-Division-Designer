import random
from collections import Counter

from data.army_spirits import ARMY_SPIRIT_CATEGORIES, ARMY_SPIRITS
from data.battalions import BATTALIONS
from data.doctrines import DOCTRINE_TRACKS, GRAND_DOCTRINES, SUBDOCTRINES
from data.regimental_support import REGIMENTAL_SUPPORT
from data.support_companies import SUPPORT_COMPANIES
from logic.army_spirits import is_army_spirit_selectable
from logic.doctrines import is_subdoctrine_selectable
from logic.doctrines import unlocked_subunit_keys as doctrine_unlocked_subunit_keys
from logic.doctrines import unlocks_fifth_battalion_row
from logic.research import unlocked_subunit_keys as research_unlocked_subunit_keys
from logic.stats import calculate_division_stats

# Punch-list step 8, Intial_problem.md's own stretch goal: "I'd want the ai
# to be able to generate and then compare designs it creates to determine -
# for example - what design has the highest organisation stat per its
# Production Cost." Scoped 2026-11-02 (see the plan file and CLAUDE.md's own
# section on this feature for the full reasoning) after confirming brute
# force is infeasible even at the smallest real unlocked-item count (~53
# keys, up to 25 battalion slots alone) - this uses a two-stage random
# search instead: generate many random, rule-legal candidate divisions,
# then hill-climb (random single-change mutation, keep only if it improves
# the score) the best few found. Research/Doctrine/Special Projects/Tank
# Designs/Army Spirits/Terrain are all treated as FIXED context - this
# searches "what's the best division buildable RIGHT NOW," not "what if I
# researched/doctrined differently."
#
# A column locks to one battalion CATEGORY (data/battalions.py's own field)
# but - per Ollie's explicit choice - not to one battalion TYPE, so each row
# within a column is picked independently (mixed columns allowed). Support
# Company conflicts (`same_support_type`) and Regimental Support's gating
# (`allowed_battalion_groups`, plus the real "3+ battalions in that column"
# unlock rule already enforced live in composition.js) are both respected
# by construction, never just hoped for.
#
# Constraints extension (added 2026-11-02, same day) - see the plan file's
# own "AI Design Comparison - Constraints Extension" section for the full
# reasoning and the 3 direct answers Ollie gave that shaped this:
# - `stat_bounds` (min/max on any stat field) and "dominant" required
#   battalions (see below) both use a feasibility-first scoring scheme
#   (_score/_violation_amount) that guides the search toward satisfying
#   every constraint before it optimizes the real metric - but per
#   Ollie's own call ("show nothing, just say so"), generate_best_designs
#   NEVER returns a result that's still infeasible once refinement ends;
#   it's dropped, not flagged.
# - A required battalion has three modes: "include" (at least one
#   instance, everything else stays free - enforced structurally, by
#   construction, never by scoring), "dominant" (that key should be the
#   single largest contributor to the whole division - Ollie's own
#   phrase, "the largest internal priority weight" - enforced partly
#   structurally (implies "include") and partly via the scoring gradient
#   above, since reaching an actual plurality needs more than just
#   placing one lonely instance), and "only" (added 2026-11-03, a step up
#   from "dominant" - EVERY battalion in the whole division must be one of
#   the "only"-marked keys, not merely the largest share). Unlike
#   "dominant", "only" is enforced purely structurally too - every other
#   battalion key is removed from the unlocked set before generation ever
#   starts (the same mechanism `excluded_battalions` already uses,
#   inverted: keep, not remove), so there's no probabilistic gradient
#   needed at all.
# - A Research Year cutoff is resolved entirely OUTSIDE this file (in
#   app.py/logic/research.py's new researched_keys_by_year) - this module
#   only ever sees a `researched` set, same as before the cutoff existed.
#
# Phase 2 of the plan file's own "AI Design Comparison - Phase 2" section
# (added 2026-11-02, same day) - Officer Corps (Army Spirits) can now be a
# SEARCH VARIABLE instead of only ever fixed context, gated behind a new
# `vary_army_spirits` flag (default False - omitting it is byte-identical
# to before this existed). `excluded_battalions` (the inverse of
# `required_battalions`) is also new - the simplest possible mechanism,
# simpler even than "required": excluded keys are filtered OUT of the
# unlocked set once, before generation ever starts, so no per-pick
# exclusion check is needed anywhere else at all.
#
# `excluded_categories` and required_battalions' "only" mode (added
# 2026-11-03, Ollie's own follow-up: "exclude all armored combat
# support" / "ONLY be a certain battalion") are the category-level and
# whole-division-level versions of the same idea - all four
# (required/dominant/only/excluded, plus excluded_categories) ultimately
# reduce to filtering `unlocked["battalions_by_category"]` before
# generation, never a per-pick runtime check.

MAX_BASE_ROWS = 4
MAX_SUPPORT_SLOTS = 5
MIN_BATTALIONS_FOR_REGIMENTAL_SUPPORT = 3
# Not every eligible column gets a Regimental Support pick in a random
# candidate - keeps some generated candidates closer to how a real player's
# division often looks (not every column maxed out), while mutation can
# still add/remove one on any eligible column regardless of this roll.
REGIMENTAL_SUPPORT_CHANCE = 0.7

# How often a random/mutated pick within a "dominant" requirement's own
# category favors that exact key over a uniform choice among every option -
# the only mechanism that makes a random search plausibly stumble onto an
# actual plurality rather than just one lonely required instance.
DOMINANT_BIAS_PROBABILITY = 0.7

# How many random columns worth of retrying generate_best_designs' own
# per-draw loop allows before giving up on that one draw (not the whole
# search) when a required battalion's category collides with every column
# already being locked to a different one - a rare, self-resolving bad-luck
# case, not a real infeasibility (see _ensure_required_battalions).
MAX_REQUIRED_BATTALION_RETRIES = 20

_BATTALION_CATEGORY = {b["key"]: b["category"] for b in BATTALIONS}
_SUPPORT_TAGS = {c["key"]: c["same_support_type"] for c in SUPPORT_COMPANIES}

_MUTATION_KINDS = [
    "swap_row", "add_row", "remove_row",
    "swap_support", "add_support", "remove_support",
    "toggle_regimental_support",
]

_ARMY_SPIRITS_BY_KEY = {s["key"]: s for s in ARMY_SPIRITS}
_ARMY_SPIRIT_CATEGORY_KEYS = [c["key"] for c in ARMY_SPIRIT_CATEGORIES]

# Chance, per category, that a random candidate picks a spirit at all
# rather than leaving that category empty - mirrors REGIMENTAL_SUPPORT_CHANCE's
# own reasoning (keeps some candidates closer to how a real division often
# looks, not every slot maxed out).
ARMY_SPIRIT_PICK_PROBABILITY = 0.5


def _selectable_army_spirits(category, doctrine_state):
    """Every Army Spirit in `category` that `is_army_spirit_selectable`
    currently allows under `doctrine_state` (a plain
    {"active_grand_doctrines", "track_subdoctrines"} dict - the same
    shape calculate_division_stats' own `doctrine` parameter carries,
    missing keys tolerated since this is called with either the real
    fixed context or an empty gate-nothing default). The real selection
    function also takes an `active_spirits` set, but never actually reads
    it (confirmed via Explore) - passed as an empty set here since it's
    irrelevant to whether a key is selectable at all.
    """
    active_grand_doctrines = doctrine_state.get("active_grand_doctrines", set())
    track_subdoctrines = doctrine_state.get("track_subdoctrines", {})
    return [
        spirit["key"] for spirit in ARMY_SPIRITS
        if spirit["category"] == category
        and is_army_spirit_selectable(spirit["key"], set(), active_grand_doctrines, track_subdoctrines)
    ]


def _random_army_spirits(doctrine_state, rng):
    return {
        category: (
            rng.choice(options)
            if (options := _selectable_army_spirits(category, doctrine_state)) and rng.random() < ARMY_SPIRIT_PICK_PROBABILITY
            else None
        )
        for category in _ARMY_SPIRIT_CATEGORY_KEYS
    }


def _fixed_army_spirits_dict(army_spirits_flat):
    """Maps a flat list of active spirit keys (the shape /api/stats'
    fixed `army_spirits` context already uses) onto the category-keyed
    dict shape candidates carry internally - used as every candidate's
    "army_spirits" value when `vary_army_spirits` is False, so Load
    always has something consistent to apply regardless of whether this
    search actually varied it. An unknown/stale key (a real case - see
    the 2026-11-02 Officer Corps rescope bugfix) is silently skipped
    rather than crashing, the same tolerance `active_army_strength_factor`
    already has.
    """
    picks = {category: None for category in _ARMY_SPIRIT_CATEGORY_KEYS}
    for key in army_spirits_flat or []:
        spirit = _ARMY_SPIRITS_BY_KEY.get(key)
        if spirit is not None:
            picks[spirit["category"]] = key
    return picks


def _flatten_army_spirits(army_spirits_dict):
    return [key for key in army_spirits_dict.values() if key is not None]


def _effective_army_spirits_flat(army_spirits_dict, doctrine_state):
    """Like _flatten_army_spirits, but drops any pick that ISN'T actually
    `is_army_spirit_selectable` under `doctrine_state` - a safety net that
    matters once Doctrine can vary per-candidate (added 2026-11-02, Phase
    2): a FIXED army_spirits baseline (built from whatever's live) is only
    ever valid for the live doctrine state it came from, so a candidate
    whose own (possibly different, hypothetical) doctrine no longer
    supports that pick must not silently keep applying its bonus. A no-op
    whenever the pick was already valid - true for every Phase 1 case,
    since generation/mutation there only ever produces already-selectable
    picks in the first place.
    """
    return [
        key for category, key in army_spirits_dict.items()
        if key is not None and key in _selectable_army_spirits(category, doctrine_state)
    ]


# --- Doctrine as a search variable (added 2026-11-02, the plan file's "AI
# Design Comparison - Phase 2" Phase 2). Confirmed via Explore:
# `can_claim_next_reward` has NO gate beyond sequential order - no
# political-power/mastery-point cost is modeled anywhere in this app - so
# there is never a reason not to claim every reward of an assigned
# subdoctrine immediately. This removes an entire randomness dimension:
# reward-claiming is deterministic (claim everything, as soon as a
# subdoctrine is assigned), and the only genuinely random choices are
# which Grand Doctrine per folder and which Subdoctrine per track.
#
# All 4 "land" Grand Doctrines share the identical 4 track names, and
# both "special_forces" ones share the identical 2 - confirmed via
# Explore and directly in data/doctrines.py. This means swapping which
# Grand Doctrine is active within a folder NEVER invalidates an existing
# track-subdoctrine assignment in that folder (is_subdoctrine_selectable's
# own "is this track owned by ANY active grand doctrine" check stays
# true either way) - only clearing a folder down to NO active Grand
# Doctrine does. That distinction is what the mutation guards below rely
# on.

_GRAND_DOCTRINES_BY_KEY = {gd["key"]: gd for gd in GRAND_DOCTRINES}
_SUBDOCTRINES_BY_KEY = {sd["key"]: sd for sd in SUBDOCTRINES}
_DOCTRINE_FOLDERS = sorted({gd["folder"] for gd in GRAND_DOCTRINES})
_GRAND_DOCTRINES_BY_FOLDER = {}
for _gd in GRAND_DOCTRINES:
    _GRAND_DOCTRINES_BY_FOLDER.setdefault(_gd["folder"], []).append(_gd["key"])
_TRACKS_BY_FOLDER = {}
for _track in DOCTRINE_TRACKS:
    _TRACKS_BY_FOLDER.setdefault(_track["folder"], []).append(_track["key"])
_ALL_TRACK_KEYS = [track["key"] for track in DOCTRINE_TRACKS]

GRAND_DOCTRINE_PICK_PROBABILITY = 0.5
SUBDOCTRINE_PICK_PROBABILITY = 0.5


def _claim_every_reward(subdoctrine_key, claimed_rewards):
    # No cost gate exists anywhere in this app's model for claiming a
    # reward - see this section's own header comment - so there is never
    # a reason to claim only some of a newly-assigned subdoctrine's
    # rewards.
    claimed_rewards[subdoctrine_key] = len(_SUBDOCTRINES_BY_KEY[subdoctrine_key]["rewards"])


def _random_doctrine(researched, rng):
    active_grand_doctrines = set()
    track_subdoctrines = {}
    claimed_rewards = {}

    for folder in _DOCTRINE_FOLDERS:
        if rng.random() < GRAND_DOCTRINE_PICK_PROBABILITY:
            active_grand_doctrines.add(rng.choice(_GRAND_DOCTRINES_BY_FOLDER[folder]))

    for grand_doctrine_key in active_grand_doctrines:
        for track_key in _GRAND_DOCTRINES_BY_KEY[grand_doctrine_key]["tracks"]:
            if rng.random() >= SUBDOCTRINE_PICK_PROBABILITY:
                continue
            options = [
                sd["key"] for sd in SUBDOCTRINES
                if is_subdoctrine_selectable(sd["key"], track_key, active_grand_doctrines, track_subdoctrines, researched)
            ]
            if options:
                subdoctrine_key = rng.choice(options)
                track_subdoctrines[track_key] = subdoctrine_key
                _claim_every_reward(subdoctrine_key, claimed_rewards)

    return {
        "active_grand_doctrines": active_grand_doctrines,
        "track_subdoctrines": track_subdoctrines,
        "claimed_rewards": claimed_rewards,
    }


def _ensure_required_doctrine(doctrine, researched, required_grand_doctrines, required_subdoctrines, rng):
    """Mutates `doctrine` in place so every required Grand Doctrine is
    active and every required Subdoctrine is assigned - mirrors
    _ensure_required_battalions' own "force it in, or report failure"
    shape. Returns False (never partially applied in a way the caller
    would trust) only when a required Subdoctrine's own `requires_technology`
    isn't satisfied - checked again here defensively, even though
    generate_best_designs' own pre-check already catches this
    deterministically before any search runs.
    """
    for key in required_grand_doctrines:
        if key in doctrine["active_grand_doctrines"]:
            continue
        folder = _GRAND_DOCTRINES_BY_KEY[key]["folder"]
        currently_active = next(
            (k for k in doctrine["active_grand_doctrines"] if k in _GRAND_DOCTRINES_BY_FOLDER[folder]), None
        )
        if currently_active is not None:
            doctrine["active_grand_doctrines"].discard(currently_active)
        doctrine["active_grand_doctrines"].add(key)

    for key in required_subdoctrines:
        if key in doctrine["track_subdoctrines"].values():
            continue
        subdoctrine = _SUBDOCTRINES_BY_KEY[key]
        if subdoctrine["requires_technology"] is not None and subdoctrine["requires_technology"] not in researched:
            return False

        owning_grand_doctrines = [
            gd["key"] for gd in GRAND_DOCTRINES if any(t in gd["tracks"] for t in subdoctrine["tracks"])
        ]
        if not any(gd_key in doctrine["active_grand_doctrines"] for gd_key in owning_grand_doctrines):
            if not owning_grand_doctrines:
                return False
            chosen_gd = owning_grand_doctrines[0]
            folder = _GRAND_DOCTRINES_BY_KEY[chosen_gd]["folder"]
            currently_active = next(
                (k for k in doctrine["active_grand_doctrines"] if k in _GRAND_DOCTRINES_BY_FOLDER[folder]), None
            )
            if currently_active is not None:
                doctrine["active_grand_doctrines"].discard(currently_active)
            doctrine["active_grand_doctrines"].add(chosen_gd)

        placed = False
        for track_key in subdoctrine["tracks"]:
            if is_subdoctrine_selectable(key, track_key, doctrine["active_grand_doctrines"], doctrine["track_subdoctrines"], researched):
                old = doctrine["track_subdoctrines"].get(track_key)
                if old is not None:
                    doctrine["claimed_rewards"].pop(old, None)
                doctrine["track_subdoctrines"][track_key] = key
                _claim_every_reward(key, doctrine["claimed_rewards"])
                placed = True
                break
        if not placed:
            return False

    return True


def _doctrine_result_shape(doctrine):
    # Flask's jsonify can't serialize a Python set - active_grand_doctrines
    # is a set internally (matching calculate_division_stats' own
    # expected shape) but must become a list in anything this module
    # returns to a caller that might JSON-encode it.
    return {
        "active_grand_doctrines": list(doctrine["active_grand_doctrines"]),
        "track_subdoctrines": dict(doctrine["track_subdoctrines"]),
        "claimed_rewards": dict(doctrine["claimed_rewards"]),
    }


def _unlocked_keys_by_type(researched, completed_special_projects, doctrine):
    """The real unlocked set (ALWAYS_UNLOCKED_SUBUNITS | research-unlocked |
    doctrine-unlocked, the same union Composition's own pickers already
    filter by), split into the 3 shapes the generator needs: battalions
    grouped by category (so a column can pick a random TYPE within its own
    locked category), and the raw Support Company/Regimental Support entries
    (not just keys - the generator needs their own same_support_type/
    allowed_battalion_groups fields too).
    """
    unlocked_keys = (
        research_unlocked_subunit_keys(researched, completed_special_projects)
        | doctrine_unlocked_subunit_keys(
            doctrine["active_grand_doctrines"], doctrine["track_subdoctrines"], doctrine["claimed_rewards"]
        )
    )

    battalions_by_category = {}
    for battalion in BATTALIONS:
        if battalion["key"] in unlocked_keys:
            battalions_by_category.setdefault(battalion["category"], []).append(battalion["key"])

    return {
        "battalions_by_category": battalions_by_category,
        "support_companies": [c for c in SUPPORT_COMPANIES if c["key"] in unlocked_keys],
        "regimental_support": [r for r in REGIMENTAL_SUPPORT if r["key"] in unlocked_keys],
    }


def _column_category(column):
    # Every key in a column shares one category by construction - just read
    # the first one.
    return _BATTALION_CATEGORY[column[0]]


def _battalion_counts(columns):
    return Counter(key for column in columns for key in column)


def _is_last_required_instance(key, required_battalions, counts):
    # required_battalions is a flat list of keys (both "include" and
    # "dominant" modes - both need this exact same protection, since
    # "dominant" implies "include").
    return key in required_battalions and counts.get(key, 0) <= 1


def _weighted_battalion_choice(options, category, dominant_keys_by_category, rng):
    """A random pick from `options`, biased toward a "dominant" requirement's
    own key when one exists for `category` - see DOMINANT_BIAS_PROBABILITY's
    own comment for why a plain uniform choice would almost never reach an
    actual plurality on its own.
    """
    dominant_keys = [key for key in dominant_keys_by_category.get(category, []) if key in options]
    if dominant_keys and rng.random() < DOMINANT_BIAS_PROBABILITY:
        return rng.choice(dominant_keys)
    return rng.choice(options)


def _ensure_required_battalions(columns, unlocked, max_rows, required_battalions, rng):
    """Mutates `columns` in place so every key in `required_battalions`
    appears at least once - inserting into an existing column already
    locked to that key's own category if one has room, else a fresh empty
    column, else (every column already locked to a DIFFERENT category, and
    none are empty) leaves it unplaced and returns False, so the caller
    discards this one random draw and tries a fresh one instead of
    returning a candidate that silently fails the constraint.

    Returns False immediately (no retry can ever help) if a required key
    isn't actually in the current unlocked set at all - a real gap found
    while testing the Research Year cutoff: this must be checked
    separately from "does the category have room," since a category can
    have plenty of OTHER unlocked keys while the one specific required key
    itself is locked (e.g. `modern_armor`, only unlocked by a 1945
    technology) - without this check, the key would have been inserted
    anyway just because its category wasn't full, producing a candidate
    the live Composition UI could never have actually built.
    """
    for key in required_battalions:
        if any(key in column for column in columns):
            continue
        category = _BATTALION_CATEGORY[key]
        if key not in unlocked["battalions_by_category"].get(category, []):
            return False
        same_category = [
            i for i, column in enumerate(columns)
            if column and _column_category(column) == category and len(column) < max_rows
        ]
        empty = [i for i, column in enumerate(columns) if not column]
        if same_category:
            columns[rng.choice(same_category)].append(key)
        elif empty:
            columns[rng.choice(empty)].append(key)
        else:
            return False
    return True


def _random_column(unlocked, max_rows, rng, force_nonempty, dominant_keys_by_category, bias_high):
    categories = [category for category, keys in unlocked["battalions_by_category"].items() if keys]
    if not categories:
        return []

    # bias_high (set whenever any constraint is present - a stat bound or a
    # "dominant" requirement) skews the row-count roll toward the high end
    # of its range rather than uniform - a direction-agnostic nudge toward
    # "bigger division," since a purely uniform roll may rarely produce
    # anything close to a tight bound or a real plurality within 1500
    # random draws alone.
    if bias_high:
        low = max(1, max_rows - 2) if force_nonempty else max(0, max_rows - 2)
        row_count = rng.randint(low, max_rows)
    else:
        row_count = rng.randint(1, max_rows) if force_nonempty else rng.randint(0, max_rows)
    if row_count == 0:
        return []

    category = rng.choice(categories)
    options = unlocked["battalions_by_category"][category]
    return [_weighted_battalion_choice(options, category, dominant_keys_by_category, rng) for _ in range(row_count)]


def _random_support_companies(unlocked, rng):
    num_slots = rng.randint(0, MAX_SUPPORT_SLOTS)
    pool = list(unlocked["support_companies"])
    rng.shuffle(pool)

    chosen = []
    used_tags = set()
    for company in pool:
        if len(chosen) >= num_slots:
            break
        tags = company["same_support_type"]
        if tags and used_tags & set(tags):
            continue
        chosen.append(company["key"])
        used_tags.update(tags)
    return chosen


def _random_regimental_support_for_column(column, unlocked, rng):
    if len(column) < MIN_BATTALIONS_FOR_REGIMENTAL_SUPPORT:
        return None
    if rng.random() > REGIMENTAL_SUPPORT_CHANCE:
        return None
    category = _column_category(column)
    options = [r["key"] for r in unlocked["regimental_support"] if category in r["allowed_battalion_groups"]]
    return rng.choice(options) if options else None


def _assemble_candidate(columns, support_companies, regimental_support_by_column, army_spirits, doctrine):
    return {
        "battalions": [key for column in columns for key in column],
        "support_companies": support_companies,
        "regimental_support": [key for key in regimental_support_by_column if key is not None],
        # "Load into Composition" (static/js/design_search.js) needs the
        # per-column breakdown, not just the flat lists above -
        # composition.js's own restoreState(columns) takes exactly this
        # columns shape already (a list of 5 per-column key lists); the
        # other two sides of Composition (support_companies.js/
        # regimental_support.js) each expect a FIXED-length-5 array
        # instead (restoreState fills by slot INDEX, so a short list would
        # leave stale old selections sitting in the slots it doesn't
        # cover) - support_slots pads with None for exactly that reason;
        # regimental_support_by_column is already that same shape.
        "columns": columns,
        "support_slots": support_companies + [None] * (MAX_SUPPORT_SLOTS - len(support_companies)),
        "regimental_support_by_column": regimental_support_by_column,
        # {category: key|None} - see _random_army_spirits/_fixed_army_spirits_dict.
        # Flattened to calculate_division_stats' own flat-list shape only
        # at the point of scoring (generate_best_designs' own stats_for),
        # and re-checked against THIS candidate's own doctrine there too
        # (see _effective_army_spirits_flat).
        "army_spirits": army_spirits,
        # {"active_grand_doctrines": set, "track_subdoctrines": dict,
        # "claimed_rewards": dict} - the FIXED context dict when not
        # varying (same object shared by every candidate), or this
        # candidate's own generated/mutated state otherwise.
        "doctrine": doctrine,
    }


def _random_candidate(
    unlocked, fifth_row_unlocked, rng,
    required_battalions=(), dominant_keys_by_category=None, bias_high=False,
    vary_army_spirits=False, army_spirits_fixed=None,
    vary_doctrine=False, doctrine_fixed=None, researched=None,
    required_grand_doctrines=(), required_subdoctrines=(),
):
    researched = researched or set()
    if vary_doctrine:
        doctrine = _random_doctrine(researched, rng)
        if (required_grand_doctrines or required_subdoctrines) and not _ensure_required_doctrine(
            doctrine, researched, required_grand_doctrines, required_subdoctrines, rng
        ):
            return None  # caller (generate_best_designs) discards this draw and retries
        fifth_row_unlocked = unlocks_fifth_battalion_row(
            doctrine["active_grand_doctrines"], doctrine["track_subdoctrines"], doctrine["claimed_rewards"]
        )
    else:
        doctrine = doctrine_fixed or {"active_grand_doctrines": set(), "track_subdoctrines": {}, "claimed_rewards": {}}

    dominant_keys_by_category = dominant_keys_by_category or {}
    max_rows = MAX_BASE_ROWS + 1 if fifth_row_unlocked else MAX_BASE_ROWS
    # Column 0 is forced non-empty so every candidate has at least one
    # battalion (calculate_division_stats' own averaging would divide by
    # zero on a totally empty division) - the other 4 columns may end up
    # empty, matching how a real division doesn't have to use every column.
    columns = [
        _random_column(unlocked, max_rows, rng, force_nonempty=(index == 0),
                        dominant_keys_by_category=dominant_keys_by_category, bias_high=bias_high)
        for index in range(5)
    ]

    if required_battalions and not _ensure_required_battalions(columns, unlocked, max_rows, required_battalions, rng):
        return None  # caller (generate_best_designs) discards this draw and retries

    regimental_support_by_column = [
        _random_regimental_support_for_column(column, unlocked, rng) for column in columns
    ]
    support_companies = _random_support_companies(unlocked, rng)
    army_spirits = (
        _random_army_spirits(doctrine, rng) if vary_army_spirits
        else (army_spirits_fixed or {category: None for category in _ARMY_SPIRIT_CATEGORY_KEYS})
    )
    return _assemble_candidate(columns, support_companies, regimental_support_by_column, army_spirits, doctrine)


def _mutate_candidate(
    candidate, unlocked, fifth_row_unlocked, rng,
    required_battalions=(), dominant_keys_by_category=None, bias_high=False,
    vary_army_spirits=False,
    vary_doctrine=False, researched=None,
    required_grand_doctrines=(), required_subdoctrines=(),
):
    """One random, legal change to an existing candidate - swap/add/remove a
    single battalion row, a single Support Company, a single column's
    Regimental Support pick, (when `vary_army_spirits`) a single Officer
    Corps category's pick, or (when `vary_doctrine`) a single folder's
    Grand Doctrine or a single track's Subdoctrine. If the randomly chosen
    mutation kind's own guard condition isn't met (e.g. "remove_support"
    with no Support Company currently chosen, every eligible row holds the
    LAST instance of a required battalion, or a Grand Doctrine/Subdoctrine
    is protected by a `required_doctrines` pin), this is a harmless no-op -
    the candidate comes back unchanged, which just costs one wasted
    hill-climbing iteration, never a crash or an illegal result.
    """
    researched = researched or set()
    dominant_keys_by_category = dominant_keys_by_category or {}
    doctrine = {
        "active_grand_doctrines": set(candidate["doctrine"]["active_grand_doctrines"]),
        "track_subdoctrines": dict(candidate["doctrine"]["track_subdoctrines"]),
        "claimed_rewards": dict(candidate["doctrine"]["claimed_rewards"]),
    }
    # When Doctrine varies, max_rows must reflect THIS candidate's own
    # doctrine (not the caller's single fixed value, which Phase 1 never
    # needed to question) - recomputed here rather than trusting the
    # `fifth_row_unlocked` parameter, which is only meaningful for the
    # non-varying case.
    if vary_doctrine:
        fifth_row_unlocked = unlocks_fifth_battalion_row(
            doctrine["active_grand_doctrines"], doctrine["track_subdoctrines"], doctrine["claimed_rewards"]
        )
    max_rows = MAX_BASE_ROWS + 1 if fifth_row_unlocked else MAX_BASE_ROWS
    columns = [list(column) for column in candidate["columns"]]
    support_companies = list(candidate["support_companies"])
    regimental_support_by_column = list(candidate["regimental_support_by_column"])
    army_spirits = dict(candidate["army_spirits"])

    kinds = list(_MUTATION_KINDS)
    if vary_army_spirits:
        kinds.append("toggle_army_spirit")
    if vary_doctrine:
        kinds.extend(["toggle_grand_doctrine", "toggle_subdoctrine"])
    kind = rng.choice(kinds)

    if kind == "swap_row":
        filled = [i for i, column in enumerate(columns) if column]
        if filled:
            col_index = rng.choice(filled)
            category = _column_category(columns[col_index])
            options = unlocked["battalions_by_category"].get(category, [])
            if options:
                counts = _battalion_counts(columns)
                # Never swap away the LAST remaining instance of a required
                # battalion - a real gap in the original build (only
                # remove_row was guarded; swap_row is just as capable of
                # erasing a required key by overwriting it in place).
                swappable_rows = [
                    row for row in range(len(columns[col_index]))
                    if not _is_last_required_instance(columns[col_index][row], required_battalions, counts)
                ]
                if swappable_rows:
                    row_index = rng.choice(swappable_rows)
                    columns[col_index][row_index] = _weighted_battalion_choice(
                        options, category, dominant_keys_by_category, rng
                    )

    elif kind == "add_row":
        growable = [i for i, column in enumerate(columns) if column and len(column) < max_rows]
        if growable:
            col_index = rng.choice(growable)
            category = _column_category(columns[col_index])
            options = unlocked["battalions_by_category"].get(category, [])
            if options:
                columns[col_index].append(_weighted_battalion_choice(options, category, dominant_keys_by_category, rng))
        else:
            empty = [i for i, column in enumerate(columns) if not column]
            categories = [category for category, keys in unlocked["battalions_by_category"].items() if keys]
            if empty and categories:
                col_index = rng.choice(empty)
                category = rng.choice(categories)
                options = unlocked["battalions_by_category"][category]
                columns[col_index] = [_weighted_battalion_choice(options, category, dominant_keys_by_category, rng)]

    elif kind == "remove_row":
        non_empty = [i for i, column in enumerate(columns) if column]
        total_battalions = sum(len(column) for column in columns)
        if non_empty and total_battalions > 1:
            counts = _battalion_counts(columns)
            removable = [
                i for i in non_empty
                if not _is_last_required_instance(columns[i][-1], required_battalions, counts)
            ]
            if removable:
                col_index = rng.choice(removable)
                columns[col_index].pop()
                if len(columns[col_index]) < MIN_BATTALIONS_FOR_REGIMENTAL_SUPPORT:
                    regimental_support_by_column[col_index] = None

    elif kind == "swap_support" and support_companies:
        index = rng.randrange(len(support_companies))
        used_tags = set()
        for i, key in enumerate(support_companies):
            if i != index:
                used_tags.update(_SUPPORT_TAGS[key])
        options = [
            company["key"] for company in unlocked["support_companies"]
            if company["key"] not in support_companies and not (used_tags & set(company["same_support_type"]))
        ]
        if options:
            support_companies[index] = rng.choice(options)

    elif kind == "add_support" and len(support_companies) < MAX_SUPPORT_SLOTS:
        used_tags = set()
        for key in support_companies:
            used_tags.update(_SUPPORT_TAGS[key])
        options = [
            company["key"] for company in unlocked["support_companies"]
            if company["key"] not in support_companies and not (used_tags & set(company["same_support_type"]))
        ]
        if options:
            support_companies.append(rng.choice(options))

    elif kind == "remove_support" and support_companies:
        support_companies.pop(rng.randrange(len(support_companies)))

    elif kind == "toggle_regimental_support":
        eligible = [i for i, column in enumerate(columns) if len(column) >= MIN_BATTALIONS_FOR_REGIMENTAL_SUPPORT]
        if eligible:
            col_index = rng.choice(eligible)
            if regimental_support_by_column[col_index] is not None:
                regimental_support_by_column[col_index] = None
            else:
                category = _column_category(columns[col_index])
                options = [
                    r["key"] for r in unlocked["regimental_support"]
                    if category in r["allowed_battalion_groups"]
                ]
                if options:
                    regimental_support_by_column[col_index] = rng.choice(options)

    elif kind == "toggle_army_spirit":
        category = rng.choice(_ARMY_SPIRIT_CATEGORY_KEYS)
        if army_spirits.get(category) is not None:
            army_spirits[category] = None
        else:
            options = _selectable_army_spirits(category, doctrine)
            if options:
                army_spirits[category] = rng.choice(options)

    elif kind == "toggle_grand_doctrine":
        folder = rng.choice(_DOCTRINE_FOLDERS)
        folder_keys = _GRAND_DOCTRINES_BY_FOLDER[folder]
        currently_active = next((key for key in doctrine["active_grand_doctrines"] if key in folder_keys), None)
        # A required Subdoctrine assigned to one of this folder's tracks
        # needs SOME Grand Doctrine active in this folder at all times
        # (clearing down to none would un-satisfy it) - but swapping to a
        # DIFFERENT Grand Doctrine in the same folder never does, since
        # every Grand Doctrine in a folder shares the identical track set
        # (see this section's own header comment).
        folder_has_required_subdoctrine = any(
            doctrine["track_subdoctrines"].get(track_key) in required_subdoctrines
            for track_key in _TRACKS_BY_FOLDER[folder]
        )
        if currently_active is not None and currently_active in required_grand_doctrines:
            pass  # pinned - no-op
        elif currently_active is not None and not folder_has_required_subdoctrine and rng.random() < 0.5:
            doctrine["active_grand_doctrines"].discard(currently_active)
            for track_key in _TRACKS_BY_FOLDER[folder]:
                subdoctrine_key = doctrine["track_subdoctrines"].pop(track_key, None)
                if subdoctrine_key is not None:
                    doctrine["claimed_rewards"].pop(subdoctrine_key, None)
        else:
            options = [key for key in folder_keys if key != currently_active]
            if options:
                if currently_active is not None:
                    doctrine["active_grand_doctrines"].discard(currently_active)
                doctrine["active_grand_doctrines"].add(rng.choice(options))

    elif kind == "toggle_subdoctrine":
        track_key = rng.choice(_ALL_TRACK_KEYS)
        current = doctrine["track_subdoctrines"].get(track_key)
        if current is not None and current in required_subdoctrines:
            pass  # pinned - no-op
        elif current is not None and rng.random() < 0.5:
            doctrine["track_subdoctrines"].pop(track_key, None)
            doctrine["claimed_rewards"].pop(current, None)
        else:
            options = [
                sd["key"] for sd in SUBDOCTRINES
                if is_subdoctrine_selectable(
                    sd["key"], track_key, doctrine["active_grand_doctrines"], doctrine["track_subdoctrines"], researched
                )
            ]
            if options:
                if current is not None:
                    doctrine["track_subdoctrines"].pop(track_key, None)
                    doctrine["claimed_rewards"].pop(current, None)
                new_key = rng.choice(options)
                doctrine["track_subdoctrines"][track_key] = new_key
                _claim_every_reward(new_key, doctrine["claimed_rewards"])

    if vary_doctrine and kind in ("toggle_grand_doctrine", "toggle_subdoctrine"):
        # A doctrine mutation can revoke 5th-row access that an earlier
        # mutation (or the initial random draw) relied on - truncate any
        # column now holding more rows than are actually legal, the same
        # way the live Composition UI would never have let a 5th row
        # exist without doctrine mastery backing it.
        new_fifth_row_unlocked = unlocks_fifth_battalion_row(
            doctrine["active_grand_doctrines"], doctrine["track_subdoctrines"], doctrine["claimed_rewards"]
        )
        new_max_rows = MAX_BASE_ROWS + 1 if new_fifth_row_unlocked else MAX_BASE_ROWS
        if new_max_rows < max_rows:
            for column in columns:
                del column[new_max_rows:]

    return _assemble_candidate(columns, support_companies, regimental_support_by_column, army_spirits, doctrine)


def _violation_amount(stats, battalions, stat_bounds, dominant_keys):
    """0.0 when every constraint is satisfied, else a positive number that
    grows with how far off the candidate is - used only to guide ranking/
    hill-climbing toward feasibility, never shown to the user directly (see
    _score).

    Each stat_bounds violation is normalized by the bound's OWN magnitude
    (a relative shortfall/excess, not an absolute one) so a violated
    production_cost bound (values in the thousands) doesn't swamp a
    violated combat_width bound (values in the tens) in the sum - otherwise
    the search would effectively only ever "see" whichever bound has the
    largest raw numbers. Each unmet "dominant" requirement is normalized by
    the division's own total battalion count for the same reason (so it's
    roughly comparable in scale to a stat_bounds fraction, not a precise
    unit conversion - this is a heuristic gradient, not an exact measure).
    """
    total = 0.0
    for bound in stat_bounds:
        value = stats.get(bound["field"], 0)
        bound_min = bound.get("min")
        bound_max = bound.get("max")
        if bound_min is not None and value < bound_min:
            total += (bound_min - value) / (abs(bound_min) or 1.0)
        if bound_max is not None and value > bound_max:
            total += (value - bound_max) / (abs(bound_max) or 1.0)

    if dominant_keys:
        counts = Counter(battalions)
        total_battalions = sum(counts.values()) or 1
        for key in dominant_keys:
            own_count = counts.get(key, 0)
            highest_other = max((count for other, count in counts.items() if other != key), default=0)
            if own_count <= highest_other:
                # Needs to strictly EXCEED the current plurality-holder to
                # actually be the largest - a tie doesn't count.
                total += (highest_other - own_count + 1) / total_battalions

    return total


def _describe_violations(stats, battalions, stat_bounds, dominant_keys):
    """A JSON-friendly breakdown of exactly which constraints a candidate
    violates and by how much - the raw data behind the "what's the
    contradiction" error message the UI shows when generate_best_designs
    finds nothing feasible (added 2026-11-02, Ollie's own request).
    Display names/wording are deliberately left to static/js/design_search.js
    (this app's own convention - the backend returns field keys/numbers,
    the frontend already owns every display-label lookup).
    """
    unmet_bounds = []
    for bound in stat_bounds:
        value = stats.get(bound["field"], 0)
        bound_min = bound.get("min")
        bound_max = bound.get("max")
        if bound_min is not None and value < bound_min:
            unmet_bounds.append({
                "field": bound["field"], "min": bound_min, "max": bound_max,
                "closest_value": value, "violated": "min",
            })
        elif bound_max is not None and value > bound_max:
            unmet_bounds.append({
                "field": bound["field"], "min": bound_min, "max": bound_max,
                "closest_value": value, "violated": "max",
            })

    unmet_dominant = []
    if dominant_keys:
        counts = Counter(battalions)
        for key in dominant_keys:
            own_count = counts.get(key, 0)
            highest_other = max((count for other, count in counts.items() if other != key), default=0)
            if own_count <= highest_other:
                unmet_dominant.append({
                    "key": key, "closest_count": own_count, "needed_more_than": highest_other,
                })

    return {"unmet_bounds": unmet_bounds, "unmet_dominant": unmet_dominant}


def _score(stats, battalions, numerator, denominator, stat_bounds=None, dominant_keys=None):
    """The candidate's score for ranking - `(True, value)` when every
    constraint is satisfied (or none exist), `(False, -violation)` when
    not (Python tuple comparison then ranks every feasible candidate above
    every infeasible one for free, and among infeasible ones, closer-to-
    feasible higher - see _violation_amount). `value` is the raw numerator
    stat, or that stat divided by a second ("per X") stat when `denominator`
    is given. Returns None (never a crash) when the denominator resolves to
    0 - that candidate is excluded entirely, a different failure mode from
    merely being out of bounds.

    generate_best_designs NEVER returns a result whose final score is still
    `(False, ...)` - Ollie's own call ("show nothing, just say so") rather
    than surfacing a flagged best-effort closest miss.
    """
    value = stats.get(numerator, 0)
    if denominator:
        denominator_value = stats.get(denominator, 0)
        if denominator_value == 0:
            return None
        value = value / denominator_value

    if not stat_bounds and not dominant_keys:
        return (True, value)

    violation = _violation_amount(stats, battalions, stat_bounds or [], dominant_keys or [])
    if violation == 0.0:
        return (True, value)
    return (False, -violation)


def generate_best_designs(
    numerator, denominator=None,
    researched=None, completed_special_projects=None, doctrine=None,
    tank_designs=None, terrain=None, army_spirits=None,
    constraints=None, vary_army_spirits=False, vary_doctrine=False,
    num_random=1500, top_k=5, num_refine_iterations=150, rng=None,
):
    """Generate and rank candidate divisions by `score = stats[numerator]`
    (or `stats[numerator] / stats[denominator]` when `denominator` is
    given), searching over Composition (battalions/support companies/
    regimental support) and, when `vary_army_spirits` is True, Officer
    Corps picks too - researched/completed_special_projects/doctrine/
    tank_designs/terrain are always fixed context, passed straight
    through to calculate_division_stats for every candidate exactly as
    /api/stats already does for the live division.

    `army_spirits` (the existing flat-list fixed-context shape) is still
    accepted and used as the baseline for every candidate when
    `vary_army_spirits` is False (byte-identical to before this flag
    existed) - and even when True, it's never read directly; only its
    shape (not its content) matters, since Officer Corps becomes a real
    search variable in that case. Every result's own `"army_spirits"`
    field always reflects whatever that specific result actually carries
    (its own search choice, or the fixed baseline) - added 2026-11-02, the
    plan file's "AI Design Comparison - Phase 2" Phase 1.

    constraints (optional, `{}`/`None` is byte-identical to before this
    parameter existed) is `{"stat_bounds": [...], "required_battalions":
    [{"key", "mode": "include"|"dominant"|"only"}, ...], "excluded_battalions":
    [key, ...], "excluded_categories": [category, ...],
    "required_doctrines": [key, ...]}` - see _score/_violation_amount/
    _ensure_required_battalions for how required/dominant are enforced.
    `excluded_battalions` (added 2026-11-02, the inverse of required) is
    simply filtered out of the unlocked set before any generation
    happens, so no other code path needs to know it exists.
    `excluded_categories` (added 2026-11-03 - "exclude all Armored Combat
    Support") is the same idea one level up: every battalion in a listed
    category is removed from the unlocked set entirely, not just one
    type. "only" mode (added 2026-11-03, a step up from "dominant" -
    "ONLY be a certain battalion," not merely its largest share) is
    enforced the same structural way: every battalion key NOT marked
    "only" is removed from the unlocked set, so no column can ever be
    given anything outside that whitelist - unlike "dominant", this needs
    no scoring gradient at all. `required_doctrines` (added 2026-11-02, Phase 2) is a flat
    list where each key is EITHER a Grand Doctrine or a Subdoctrine key
    (resolved by checking which collection it belongs to) - see
    _ensure_required_doctrine; only meaningful when `vary_doctrine` is
    True (a required doctrine makes no sense to specify when Doctrine
    itself is fixed context the caller already controls directly).
    `research_year_cutoff` is deliberately NOT read here - resolved one
    layer up (app.py/logic/research.py's researched_keys_by_year), so
    this function only ever sees a plain `researched` set either way.

    `vary_doctrine` (default False, byte-identical to before this flag
    existed) makes Doctrine - which Grand Doctrine per folder, which
    Subdoctrine per track, with every reward auto-claimed immediately
    since no cost is modeled for that anywhere in this app - a real
    search variable instead of fixed context, exactly mirroring
    `vary_army_spirits`'s own precedent. Officer Corps picks (whether
    fixed or varying) are always re-checked against each candidate's OWN
    doctrine before being applied to its stats or returned in its result
    (_effective_army_spirits_flat) - a pick that was valid under the live
    doctrine state might not be valid under a candidate's own
    hypothetical one.

    Returns `(results, infeasible_reason)`. `results` is up to `top_k`
    {"battalions", "support_companies", "regimental_support", "columns",
    "support_slots", "regimental_support_by_column", "stats", "score"}
    dicts, sorted descending by score - an empty list if nothing unlocked,
    if the denominator stat resolved to 0 on every candidate generated, OR
    if no candidate ever satisfied every constraint (dropped, never
    returned flagged - Ollie's own call). `infeasible_reason` is `None`
    unless `results` came back empty AND a constraint genuinely explains
    why (added 2026-11-02, Ollie's own follow-up request for an actual
    explanation rather than just "try loosening something") - one of:
    `{"unavailable_battalions": [key, ...]}` (a required key isn't
    unlocked under the current context AT ALL - deterministic, checked
    before any search runs, since no amount of searching could ever fix
    this); `{"too_many_required_categories": [category, ...]}` (more than
    5 distinct categories required at once - deterministically impossible,
    only 5 columns exist); or `{"unmet_bounds": [...], "unmet_dominant":
    [...]}` (see _describe_violations) - the SINGLE closest-to-feasible
    candidate the whole search ever found, even though it's still dropped
    from `results` itself.

    rng is an optional random.Random instance (tests pass a seeded one for
    reproducible assertions); omitting it uses a fresh, unseeded one.
    """
    rng = rng or random.Random()
    researched = researched or set()
    completed_special_projects = completed_special_projects or set()
    doctrine = doctrine or {"active_grand_doctrines": set(), "track_subdoctrines": {}, "claimed_rewards": {}}
    constraints = constraints or {}
    stat_bounds = constraints.get("stat_bounds") or []
    required_battalion_entries = constraints.get("required_battalions") or []
    excluded_battalions = set(constraints.get("excluded_battalions") or [])
    excluded_categories = set(constraints.get("excluded_categories") or [])
    required_doctrine_keys = constraints.get("required_doctrines") or []

    required_keys = [entry["key"] for entry in required_battalion_entries]
    dominant_keys = [entry["key"] for entry in required_battalion_entries if entry.get("mode") == "dominant"]
    only_keys = {entry["key"] for entry in required_battalion_entries if entry.get("mode") == "only"}
    dominant_keys_by_category = {}
    for key in dominant_keys:
        dominant_keys_by_category.setdefault(_BATTALION_CATEGORY[key], []).append(key)

    required_grand_doctrines = [key for key in required_doctrine_keys if key in _GRAND_DOCTRINES_BY_KEY]
    required_subdoctrines = [key for key in required_doctrine_keys if key in _SUBDOCTRINES_BY_KEY]
    unresolvable_doctrines = [
        key for key in required_doctrine_keys
        if key not in _GRAND_DOCTRINES_BY_KEY and key not in _SUBDOCTRINES_BY_KEY
    ]

    # A constrained/varied search costs more wall-clock than the
    # unconstrained ~0.4s benchmark (deliberately, not tuned down) -
    # bumping refinement iterations (not num_random, which is far more
    # expensive per unit) gives hill-climbing enough room to actually walk
    # from "random mediocre" to "satisfies every constraint" or "found a
    # good Doctrine combination."
    has_constraints = bool(stat_bounds) or bool(dominant_keys) or bool(only_keys)
    if has_constraints or vary_doctrine:
        num_refine_iterations = max(num_refine_iterations, 400)

    unlocked = _unlocked_keys_by_type(researched, completed_special_projects, doctrine)
    if excluded_categories:
        # "Exclude all Armored Combat Support" - removes the entire
        # category's entry, not just filters its list, so it can never be
        # picked as a column's locked category at all. Done first (before
        # only_keys/excluded_battalions) so a required key whose own
        # category was excluded here correctly falls through to the
        # "unavailable_battalions" check below via `.get(category, [])`.
        unlocked["battalions_by_category"] = {
            category: keys for category, keys in unlocked["battalions_by_category"].items()
            if category not in excluded_categories
        }
    if only_keys:
        # "Only" is a step up from "dominant" (see this function's own
        # docstring) - every key NOT in the whitelist is removed from the
        # unlocked set entirely, the same mechanism excluded_battalions
        # uses just inverted (keep, not remove), so there's no
        # probabilistic gradient needed to reach it - it's structurally
        # guaranteed before generation even starts.
        unlocked["battalions_by_category"] = {
            category: [key for key in keys if key in only_keys]
            for category, keys in unlocked["battalions_by_category"].items()
        }
    if excluded_battalions:
        # Simplest possible mechanism: filter OUT of the unlocked set once,
        # here, before any generation happens - neither _random_column/
        # _weighted_battalion_choice nor any mutation kind can ever pick a
        # key that isn't present in this structure, so no per-pick
        # exclusion check is needed anywhere else at all. If an excluded
        # key is ALSO required, it naturally disappears from the unlocked
        # set here and gets caught by the existing "unavailable_battalions"
        # check right below - a real contradiction, correctly reported.
        unlocked["battalions_by_category"] = {
            category: [key for key in keys if key not in excluded_battalions]
            for category, keys in unlocked["battalions_by_category"].items()
        }
    if not any(unlocked["battalions_by_category"].values()):
        return [], None

    # Two deterministic infeasibility checks, done BEFORE running any
    # search at all - no amount of random generation or hill-climbing
    # could ever satisfy either one, so there's no point spending the
    # time, and the real reason is known exactly rather than inferred
    # from a search that never found anything.
    if required_keys:
        all_unlocked_battalions = {key for keys in unlocked["battalions_by_category"].values() for key in keys}
        unavailable = [key for key in required_keys if key not in all_unlocked_battalions]
        if unavailable:
            return [], {"unavailable_battalions": unavailable}

        required_categories = {_BATTALION_CATEGORY[key] for key in required_keys}
        if len(required_categories) > 5:
            return [], {"too_many_required_categories": sorted(required_categories)}

    if required_doctrine_keys:
        unavailable_doctrines = list(unresolvable_doctrines)
        for key in required_subdoctrines:
            tech = _SUBDOCTRINES_BY_KEY[key]["requires_technology"]
            if tech is not None and tech not in researched:
                unavailable_doctrines.append(key)
        if unavailable_doctrines:
            return [], {"unavailable_doctrines": unavailable_doctrines}

    fifth_row_unlocked = unlocks_fifth_battalion_row(
        doctrine["active_grand_doctrines"], doctrine["track_subdoctrines"], doctrine["claimed_rewards"]
    )
    army_spirits_fixed = _fixed_army_spirits_dict(army_spirits)

    def stats_for(candidate):
        return calculate_division_stats(
            candidate["battalions"], candidate["support_companies"], candidate["regimental_support"],
            researched=researched, completed_special_projects=completed_special_projects,
            doctrine=candidate["doctrine"], tank_designs=tank_designs, terrain=terrain,
            army_spirits=_effective_army_spirits_flat(candidate["army_spirits"], candidate["doctrine"]),
        )

    def score_for(candidate, stats):
        return _score(stats, candidate["battalions"], numerator, denominator, stat_bounds, dominant_keys)

    def random_candidate():
        for _ in range(MAX_REQUIRED_BATTALION_RETRIES):
            candidate = _random_candidate(
                unlocked, fifth_row_unlocked, rng,
                required_battalions=required_keys,
                dominant_keys_by_category=dominant_keys_by_category,
                bias_high=has_constraints,
                vary_army_spirits=vary_army_spirits, army_spirits_fixed=army_spirits_fixed,
                vary_doctrine=vary_doctrine, doctrine_fixed=doctrine, researched=researched,
                required_grand_doctrines=required_grand_doctrines, required_subdoctrines=required_subdoctrines,
            )
            if candidate is not None:
                return candidate
        return None  # every retry collided with an already-locked column - give up on this one draw

    # The single lowest-violation infeasible candidate seen anywhere across
    # the whole search (stage 1 AND every stage-2 refinement attempt) -
    # tracked purely for the failure-explanation case below; it never
    # affects which candidates make it into `results` itself.
    best_infeasible = None  # (violation_amount, stats, battalions)

    def track_infeasible(score, stats, candidate):
        nonlocal best_infeasible
        feasible, neg_violation = score
        if feasible:
            return
        violation = -neg_violation
        if best_infeasible is None or violation < best_infeasible[0]:
            best_infeasible = (violation, stats, candidate["battalions"])

    scored = []
    for _ in range(num_random):
        candidate = random_candidate()
        if candidate is None:
            continue
        stats = stats_for(candidate)
        score = score_for(candidate, stats)
        if score is not None:
            track_infeasible(score, stats, candidate)
            scored.append((score, candidate, stats))
    scored.sort(key=lambda entry: entry[0], reverse=True)

    results = []
    for score, candidate, stats in scored[:top_k]:
        best_score, best_candidate, best_stats = score, candidate, stats
        for _ in range(num_refine_iterations):
            mutated = _mutate_candidate(
                best_candidate, unlocked, fifth_row_unlocked, rng,
                required_battalions=required_keys,
                dominant_keys_by_category=dominant_keys_by_category,
                bias_high=has_constraints,
                vary_army_spirits=vary_army_spirits,
                vary_doctrine=vary_doctrine, researched=researched,
                required_grand_doctrines=required_grand_doctrines, required_subdoctrines=required_subdoctrines,
            )
            mutated_stats = stats_for(mutated)
            mutated_score = score_for(mutated, mutated_stats)
            if mutated_score is not None:
                track_infeasible(mutated_score, mutated_stats, mutated)
                if mutated_score > best_score:
                    best_score, best_candidate, best_stats = mutated_score, mutated, mutated_stats

        feasible, value = best_score
        if not feasible:
            # Ollie's own call: never surface a "closest miss" - drop it
            # entirely rather than returning it flagged as infeasible.
            continue

        results.append({
            "battalions": best_candidate["battalions"],
            "support_companies": best_candidate["support_companies"],
            "regimental_support": best_candidate["regimental_support"],
            "columns": best_candidate["columns"],
            "support_slots": best_candidate["support_slots"],
            "regimental_support_by_column": best_candidate["regimental_support_by_column"],
            # {"active_spirits": [...]} - exactly the shape
            # static/js/army_spirits.js's own restoreState already takes,
            # so Load can call it directly with zero translation, whether
            # or not this search actually varied Officer Corps. Filtered
            # through this candidate's OWN doctrine (see
            # _effective_army_spirits_flat) so Load never applies a pick
            # that wouldn't actually be active under the doctrine this
            # same result carries.
            "army_spirits": {
                "active_spirits": _effective_army_spirits_flat(best_candidate["army_spirits"], best_candidate["doctrine"]),
            },
            # Exactly the shape static/js/doctrines.js's own restoreState
            # already takes (lists, not Python sets, so this stays
            # JSON-serializable) - always present, varied or not, the
            # same "Load has something consistent either way" convention
            # army_spirits already established in Phase 1.
            "doctrine": _doctrine_result_shape(best_candidate["doctrine"]),
            "stats": best_stats,
            "score": value,
        })

    results.sort(key=lambda entry: entry["score"], reverse=True)

    infeasible_reason = None
    if not results and has_constraints and best_infeasible is not None:
        _, infeasible_stats, infeasible_battalions = best_infeasible
        infeasible_reason = _describe_violations(infeasible_stats, infeasible_battalions, stat_bounds, dominant_keys)

    return results, infeasible_reason
