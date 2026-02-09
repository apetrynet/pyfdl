from .rounding import RoundStrategy

NO_ROUNDING = RoundStrategy(even=None, mode=None)
DEFAULT_ROUNDING_STRATEGY = NO_ROUNDING

__rounding_strategy = NO_ROUNDING


def set_rounding(strategy: RoundStrategy):
    """
    Set the global rounding strategy for all values except where the spec require its own rules
    Args:
        strategy:
    """
    global __rounding_strategy
    __rounding_strategy = strategy


def get_rounding() -> RoundStrategy:
    """

    Returns:
        the global rounding strategy

    """
    return __rounding_strategy
