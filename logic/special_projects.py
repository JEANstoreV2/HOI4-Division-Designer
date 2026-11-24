from data.special_projects import SPECIAL_PROJECTS
from data.technologies import TECHNOLOGIES

_SPECIAL_PROJECTS_BY_KEY = {project["key"]: project for project in SPECIAL_PROJECTS}


def is_special_project_completable(project_key, completed_special_projects):
    """Whether the special project at project_key can be marked completed
    right now, given the set of special project keys already completed.

    True when: it isn't already completed, and every entry in its own
    `requires` AND-list (data/special_projects.py's own project-to-project
    dependency - only sp_land_self_propelled_super_heavy_howitzer has one)
    is already completed. Mirrors logic/research.py's is_researchable, just
    without the unlocked_by/mutually_exclusive_with/EXTERNAL_DEPENDENCIES
    machinery special projects don't have - no investment/time simulation,
    matching data/special_projects.py's own header on why.
    """
    project = _SPECIAL_PROJECTS_BY_KEY[project_key]

    if project_key in completed_special_projects:
        return False

    return all(parent in completed_special_projects for parent in project["requires"])


def completable_special_projects(completed_special_projects):
    """Every special project currently available to complete next, given
    the set of special project keys already completed.
    """
    return [
        project for project in SPECIAL_PROJECTS
        if is_special_project_completable(project["key"], completed_special_projects)
    ]


def dependent_special_projects(project_key, completed_special_projects):
    """Every OTHER already-completed special project whose own `requires`
    would become unsatisfied if project_key were removed from
    completed_special_projects - mirrors logic/research.py's
    dependent_technologies.
    """
    hypothetical = completed_special_projects - {project_key}
    dependents = []

    for other_key in completed_special_projects:
        if other_key == project_key:
            continue
        other = _SPECIAL_PROJECTS_BY_KEY[other_key]
        if not all(parent in hypothetical for parent in other["requires"]):
            dependents.append(other_key)

    return dependents


def can_uncomplete_special_project(project_key, completed_special_projects, researched):
    """Whether project_key can be safely removed from
    completed_special_projects: it's actually completed; nothing else
    already-completed depends on it (dependent_special_projects, mirroring
    logic/research.py's can_unresearch); and no already-researched
    technology's own special_project_requires points at it - a cross-system
    check Research's own can_unresearch doesn't need, since completing a
    project is a prerequisite OF research, not the other way around.
    """
    if project_key not in completed_special_projects:
        return False

    if dependent_special_projects(project_key, completed_special_projects):
        return False

    return not any(
        tech["special_project_requires"] == project_key
        for tech in TECHNOLOGIES
        if tech["key"] in researched
    )


def active_special_project_unit_bonuses(completed_special_projects):
    """Every `unit_bonuses` dict active from completed special projects, as a
    list of (target_key, stat_dict) pairs - same shape as
    logic/research.py's active_tech_unit_bonuses (data/special_projects.py's
    own unit_bonuses field mirrors data/technologies.py's exactly), so
    logic/stats.py can treat a project's own direct bonus (e.g. Large Caliber
    Kinetic Energy Sabot's hidden Piercing bonus - see data/special_projects.py's
    header) the same way it already treats a technology's.
    """
    return [
        (target_key, stat_dict)
        for project_key in completed_special_projects
        for target_key, stat_dict in _SPECIAL_PROJECTS_BY_KEY[project_key]["unit_bonuses"].items()
    ]
