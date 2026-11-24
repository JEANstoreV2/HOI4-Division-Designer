MINIMUM_BATTALIONS_FOR_REGIMENTAL_SUPPORT = 3


def regimental_support_unlocked(battalion_count):
    """A battalion column unlocks its regimental support slot once it holds
    at least MINIMUM_BATTALIONS_FOR_REGIMENTAL_SUPPORT battalions (per
    Intial_problem.md's composition rules).
    """
    return battalion_count >= MINIMUM_BATTALIONS_FOR_REGIMENTAL_SUPPORT
