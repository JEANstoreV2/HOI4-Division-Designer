from logic.support_companies import select_support_company


def test_unrelated_companies_do_not_conflict():
    result = select_support_company(["anti_tank"], "anti_air")
    assert result == ["anti_tank", "anti_air"]


def test_same_group_alternative_replaces_the_original():
    result = select_support_company(["engineer"], "assault_engineer")
    assert result == ["assault_engineer"]


def test_conflict_only_removes_the_conflicting_entries():
    result = select_support_company(["engineer", "anti_tank"], "assault_engineer")
    assert result == ["anti_tank", "assault_engineer"]


def test_reselecting_the_same_company_does_not_duplicate_it():
    result = select_support_company(["engineer", "anti_tank"], "engineer")
    assert result == ["anti_tank", "engineer"]


def test_companies_with_no_same_support_type_never_conflict():
    result = select_support_company(["anti_tank", "anti_air", "artillery"], "signal_company")
    assert result == ["anti_tank", "anti_air", "artillery", "signal_company"]


def test_multi_group_membership_only_conflicts_on_shared_groups():
    # helicopter_recon shares "recon" with recon, so it replaces it...
    result = select_support_company(["recon"], "helicopter_recon")
    assert result == ["helicopter_recon"]

    # ...but helicopter_brigade doesn't share "recon" with plain recon, per
    # the game's own data, so the two coexist.
    result = select_support_company(["recon"], "helicopter_brigade")
    assert result == ["recon", "helicopter_brigade"]
