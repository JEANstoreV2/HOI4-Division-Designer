from data.tank_chassis import TANK_CHASSIS
from data.tank_modules import TANK_MODULES

MODULES_BY_KEY = {m["key"]: m for m in TANK_MODULES}

# Every category any chassis slot can reference directly - the base
# framework before any module-level override widens it further.
CHASSIS_SLOT_CATEGORIES = set()
for chassis in TANK_CHASSIS:
    for slot in chassis["module_slots"].values():
        CHASSIS_SLOT_CATEGORIES.update(slot["allowed_module_categories"])

MODULE_CATEGORIES = {m["category"] for m in TANK_MODULES}

# Some categories (e.g. tank_medium_main_armament) are never listed on a
# chassis's own main_armament_slot - they only become legal once a specific
# turret module's "allowed_module_categories" widens that slot (a real,
# confirmed mechanic: the turret determines which gun categories fit, not
# the chassis alone). A module's own category must be reachable through
# EITHER path, not the base chassis slots alone.
REACHABLE_CATEGORIES = set(CHASSIS_SLOT_CATEGORIES)
for module in TANK_MODULES:
    for categories in module.get("allowed_module_categories", {}).values():
        REACHABLE_CATEGORIES.update(categories)

KNOWN_EQUIPMENT_TYPE_TAGS = {"anti_air", "artillery", "anti_tank", "flame", "amphibious"}
KNOWN_RESOURCES = {"steel", "tungsten", "chromium"}


def test_expected_module_count():
    # 70 main-tank modules + 30 Land Cruiser modules = 100. Two NOR_-prefixed
    # (Norway-specific) modules are deliberately excluded - see module header.
    assert len(TANK_MODULES) == 100


def test_no_duplicate_module_keys():
    keys = [m["key"] for m in TANK_MODULES]
    assert len(keys) == len(set(keys))


def test_no_nor_country_locked_modules_present():
    assert "NOR_tank_rikstanken_armor" not in MODULES_BY_KEY
    assert "NOR_rikstanken_turret" not in MODULES_BY_KEY


def test_every_module_category_is_reachable():
    # A module whose category neither a chassis slot nor any turret's
    # allowed_module_categories override ever accepts would be unreachable
    # in any real design - confirms the module/chassis data actually line up.
    for module in TANK_MODULES:
        assert module["category"] in REACHABLE_CATEGORIES, module["key"]


def test_every_chassis_slot_category_has_at_least_one_module():
    # The inverse check - every category a chassis slot advertises directly
    # should have real modules to fill it.
    for category in CHASSIS_SLOT_CATEGORIES:
        assert any(m["category"] == category for m in TANK_MODULES), category


def test_module_level_allowed_module_categories_reference_real_categories():
    for module in TANK_MODULES:
        overrides = module.get("allowed_module_categories", {})
        for slot_name, categories in overrides.items():
            for category in categories:
                assert category in MODULE_CATEGORIES, (module["key"], slot_name, category)


def test_can_convert_from_references_real_module_or_category():
    for module in TANK_MODULES:
        convert = module.get("can_convert_from")
        if convert is None:
            continue
        if "module" in convert:
            assert convert["module"] in MODULES_BY_KEY, (module["key"], convert)
        else:
            assert convert["module_category"] in MODULE_CATEGORIES, (module["key"], convert)


def test_parent_references_a_real_module():
    for module in TANK_MODULES:
        parent = module.get("parent")
        if parent is not None:
            assert parent in MODULES_BY_KEY, (module["key"], parent)


def test_allow_equipment_type_is_a_known_role_tag():
    for module in TANK_MODULES:
        allow = module.get("allow_equipment_type")
        if allow is not None:
            assert allow in KNOWN_EQUIPMENT_TYPE_TAGS, (module["key"], allow)


def test_forbid_equipment_type_is_a_list_of_known_role_tags():
    for module in TANK_MODULES:
        forbid = module.get("forbid_equipment_type")
        if forbid is None:
            continue
        assert isinstance(forbid, list), module["key"]
        for tag in forbid:
            assert tag in KNOWN_EQUIPMENT_TYPE_TAGS, (module["key"], tag)


def test_build_cost_resources_use_known_resource_keys():
    for module in TANK_MODULES:
        resources = module.get("build_cost_resources", {})
        for resource in resources:
            assert resource in KNOWN_RESOURCES, (module["key"], resource)


def test_add_stats_and_multiply_stats_values_are_numeric():
    for module in TANK_MODULES:
        for field, value in module["add_stats"].items():
            assert isinstance(value, (int, float)), (module["key"], field)
        for field, value in module.get("multiply_stats", {}).items():
            assert isinstance(value, (int, float)), (module["key"], field)


def test_every_module_has_a_name_and_add_stats():
    for module in TANK_MODULES:
        assert module["name"], module["key"]
        assert "add_stats" in module, module["key"]
