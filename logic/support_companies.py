from data.support_companies import SUPPORT_COMPANIES

_GROUPS_BY_KEY = {company["key"]: set(company["same_support_type"]) for company in SUPPORT_COMPANIES}


def select_support_company(selected_keys, new_key):
    """Return `selected_keys` with `new_key` added, replacing any existing
    entries that conflict with it (share a same_support_type group).

    Companies with no same_support_type groups never conflict with anything.
    Selecting a key that's already present just moves it to the end.
    """
    new_groups = _GROUPS_BY_KEY[new_key]
    kept = [
        key for key in selected_keys
        if key != new_key and not (new_groups & _GROUPS_BY_KEY[key])
    ]
    return kept + [new_key]
