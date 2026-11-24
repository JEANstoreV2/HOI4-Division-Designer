from data.battalions import BATTALIONS
from data.regimental_support import REGIMENTAL_SUPPORT
from data.special_projects import SPECIAL_PROJECTS
from data.support_companies import SUPPORT_COMPANIES
from data.tank_modules import TANK_MODULES
from data.technologies import EXTERNAL_DEPENDENCIES, TECHNOLOGIES

_TECHNOLOGIES_BY_KEY = {tech["key"]: tech for tech in TECHNOLOGIES}
_SPECIAL_PROJECTS_BY_KEY = {project["key"]: project for project in SPECIAL_PROJECTS}

# Every battalion/support-company/regimental-support key that no technology
# OR special project ever unlocks - nation-specific units granted by a
# focus/event/national spirit (Camelry, Elephantry, Militia, Bicycle, ...),
# plus a few armor_combat_support brigades never explicitly gated by any
# enable_subunits in technologies_copy/ (see data/technologies.py's header).
# All of these stay selectable regardless of research state, matching
# Specification.md's decision that Composition treats them as always
# accessible.
_ALL_SUBUNIT_KEYS = (
    {b["key"] for b in BATTALIONS}
    | {c["key"] for c in SUPPORT_COMPANIES}
    | {r["key"] for r in REGIMENTAL_SUPPORT}
)
_GATED_SUBUNIT_KEYS = (
    {key for tech in TECHNOLOGIES for key in tech["unlocks_subunits"]}
    | {key for project in SPECIAL_PROJECTS for key in project["unlocks_subunits"]}
)
ALWAYS_UNLOCKED_SUBUNITS = _ALL_SUBUNIT_KEYS - _GATED_SUBUNIT_KEYS

# Every Tank Designer module never gated by a real, compiled technology's OR
# special project's own unlocks_equipment_modules - either because the
# source never gates it at all, or because the only thing that gates it is
# deliberately out of scope (a hidden `allow = { always = no }` tech, or a
# tech living entirely in electronic_mechanical_engineering.txt/support.txt's
# train sub-branch - see data/technologies.py's own exclusion list). All are
# treated as always available, matching ALWAYS_UNLOCKED_SUBUNITS's exact
# precedent.
_ALL_MODULE_KEYS = {m["key"] for m in TANK_MODULES}
_GATED_MODULE_KEYS = (
    {key for tech in TECHNOLOGIES for key in tech["unlocks_equipment_modules"]}
    | {key for project in SPECIAL_PROJECTS for key in project["unlocks_equipment_modules"]}
) & _ALL_MODULE_KEYS
ALWAYS_UNLOCKED_MODULES = _ALL_MODULE_KEYS - _GATED_MODULE_KEYS


def is_researchable(tech_key, researched, completed_special_projects=frozenset()):
    """Whether the technology at tech_key can be researched right now,
    given the set of technology keys already researched.

    True when: it isn't already researched; its `unlocked_by` OR-chain is
    empty or at least one entry is already researched; every entry in its
    `requires` AND-list is either already researched or a documented
    EXTERNAL_DEPENDENCIES key (a real dependency living in a technologies_copy
    file that isn't compiled here - see data/technologies.py's header -
    treated as always satisfied since it isn't tracked); no entry in its
    `mutually_exclusive_with` list has already been researched; and, if it
    has a `special_project_requires` key (the 18 Special-Project
    technologies compiled 2026-10-01), that key is in
    `completed_special_projects`.

    completed_special_projects is an optional set of data/special_projects.py
    keys, mirroring `researched` itself - a flat, caller-owned "has this
    special project been completed" set with no investment/slot simulation,
    matching data/special_projects.py's own header on why. Defaults to an
    empty frozenset, which is correct for every technology OTHER than the
    18 Special-Project ones (their special_project_requires is None, so the
    new check never fires) - omitting this parameter is byte-identical to
    before Special Projects existed, same precedent as every other optional
    state this project threads through (doctrine/tank_designs/terrain in
    logic/stats.py).
    """
    tech = _TECHNOLOGIES_BY_KEY[tech_key]

    if tech_key in researched:
        return False

    if tech["unlocked_by"] and not any(prereq in researched for prereq in tech["unlocked_by"]):
        return False

    if not all(dep in researched or dep in EXTERNAL_DEPENDENCIES for dep in tech["requires"]):
        return False

    if any(other in researched for other in tech["mutually_exclusive_with"]):
        return False

    if tech["special_project_requires"] is not None and tech["special_project_requires"] not in completed_special_projects:
        return False

    return True


def researchable_technologies(researched, completed_special_projects=frozenset()):
    """Every technology currently available to research next, given the
    set of technology keys already researched.
    """
    return [
        tech for tech in TECHNOLOGIES
        if is_researchable(tech["key"], researched, completed_special_projects)
    ]


def dependent_technologies(tech_key, researched):
    """Every OTHER already-researched technology whose own `unlocked_by`/
    `requires` would become unsatisfied if tech_key were removed from
    `researched` - i.e. what's actually holding tech_key in place. Empty
    means tech_key is safe to un-research.
    """
    hypothetical = researched - {tech_key}
    dependents = []

    for other_key in researched:
        if other_key == tech_key:
            continue
        other = _TECHNOLOGIES_BY_KEY[other_key]

        or_broken = other["unlocked_by"] and not any(p in hypothetical for p in other["unlocked_by"])
        and_broken = not all(
            dep in hypothetical or dep in EXTERNAL_DEPENDENCIES for dep in other["requires"]
        )
        if or_broken or and_broken:
            dependents.append(other_key)

    return dependents


def can_unresearch(tech_key, researched):
    """Whether tech_key can be safely removed from `researched` without
    leaving another already-researched technology's own prerequisites
    unsatisfied. Un-researching is otherwise unrestricted - a technology
    can always be undone right after it's picked, since nothing has had a
    chance to depend on it yet; this is the one safety rule stopping an
    earlier tech from being pulled out from under something already built
    on top of it (see dependent_technologies above).
    """
    return tech_key in researched and not dependent_technologies(tech_key, researched)


def unlocked_subunit_keys(researched, completed_special_projects=frozenset()):
    """Every battalion/support-company/regimental-support key currently
    selectable in Composition: the union of every researched technology's
    `unlocks_subunits`, every completed special project's own
    `unlocks_subunits` (data/special_projects.py - a real, separate unlock
    layer found 2026-10-02, distinct from the technologies a project gates),
    and ALWAYS_UNLOCKED_SUBUNITS (see above).
    """
    from_research = {
        key
        for tech_key in researched
        for key in _TECHNOLOGIES_BY_KEY[tech_key]["unlocks_subunits"]
    }
    from_special_projects = {
        key
        for project_key in completed_special_projects
        for key in _SPECIAL_PROJECTS_BY_KEY[project_key]["unlocks_subunits"]
    }
    return from_research | from_special_projects | ALWAYS_UNLOCKED_SUBUNITS


def researched_keys_by_year(cutoff):
    """Every technology key that "existed" by `cutoff` (a real calendar
    year) - every technology whose own `year` field (data/technologies.py,
    None for exactly one entry, gw_artillery, which has no real-world year
    and is always included regardless of cutoff) is at most `cutoff`.

    Used by AI Design Comparison's Research Year constraint (added
    2026-11-02) to build a hypothetical `researched` set standing in for
    the live one - "only use tech up to 1940" REPLACES the caller's real
    researched set entirely rather than intersecting with it (Ollie's own
    call), so this function doesn't take or need one.
    """
    return {tech["key"] for tech in TECHNOLOGIES if tech["year"] is None or tech["year"] <= cutoff}


def active_tech_unit_bonuses(researched):
    """Every `unit_bonuses` dict active from researched technologies, as a
    list of (target_key, stat_dict) pairs - target_key is either a real
    item key or a HOI4 `category_*` tag, exactly as data/technologies.py
    stores it (mirrors data/doctrines.py's own shape, and
    logic/doctrines.py's active_unit_bonuses' return shape exactly, so
    logic/stats.py can treat both sources the same way wherever proven
    correct).

    Much simpler than active_unit_bonuses: a technology's bonus is either
    fully active (researched) or not at all - no progressive reward-
    claiming to walk, unlike a subdoctrine's ordered reward list.

    Returns the raw stat dicts as compiled - a dict may still contain a
    nested `battalion_mult` list or terrain-nested sub-dicts alongside
    plain fields; filtering to what's actually applicable is
    logic/stats.py's job, not this function's (see data/technologies.py's
    header for what's deliberately not fed anywhere yet).
    """
    return [
        (target_key, stat_dict)
        for tech_key in researched
        for target_key, stat_dict in _TECHNOLOGIES_BY_KEY[tech_key]["unit_bonuses"].items()
    ]


def unlocked_module_keys(researched, completed_special_projects=frozenset()):
    """Every Tank Designer module key currently selectable: the union of
    every researched technology's `unlocks_equipment_modules` (filtered to
    real data/tank_modules.py keys - a handful of technologies also list
    non-Tank-Designer equipment like `ship_anti_air_1`/`rocket_rails` in the
    same field, copied verbatim from the source), every completed special
    project's own `unlocks_equipment_modules` (data/special_projects.py -
    same real, separate unlock layer as unlocked_subunit_keys' own), and
    ALWAYS_UNLOCKED_MODULES.
    """
    from_research = {
        key
        for tech_key in researched
        for key in _TECHNOLOGIES_BY_KEY[tech_key]["unlocks_equipment_modules"]
        if key in _ALL_MODULE_KEYS
    }
    from_special_projects = {
        key
        for project_key in completed_special_projects
        for key in _SPECIAL_PROJECTS_BY_KEY[project_key]["unlocks_equipment_modules"]
        if key in _ALL_MODULE_KEYS
    }
    return from_research | from_special_projects | ALWAYS_UNLOCKED_MODULES
