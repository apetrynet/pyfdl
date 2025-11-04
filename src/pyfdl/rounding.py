from typing import TypeVar

RoundStrategy = TypeVar("RoundStrategy")

__rounding_strategy = None


def set_rounding_strategy(strategy: RoundStrategy):
    """
    Set the global rounding strategy for all values except where the spec require its own rules
    Args:
        strategy:
    """
    global __rounding_strategy
    __rounding_strategy = strategy


def get_rounding_strategy() -> RoundStrategy:
    """

    Returns:
        the global rounding strategy

    """
    return __rounding_strategy
