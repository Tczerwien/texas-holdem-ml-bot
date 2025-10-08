"""Game rules and constants for Texas Hold'em.

Defines betting rounds, blind structure, and game flow.
"""

from __future__ import annotations

from enum import Enum


class Street(str, Enum):
    """Betting rounds in Texas Hold'em."""

    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOWDOWN = "showdown"


# Standard blind structure (can be scaled)
BLIND_STRUCTURE = {
    "small_blind": 1,
    "big_blind": 2,
}


def next_street(current: Street) -> Street:
    """Get the next betting street.

    Args:
        current: Current street

    Returns:
        Next street in sequence (showdown stays at showdown)

    Examples:
        >>> next_street(Street.PREFLOP)
        <Street.FLOP: 'flop'>
        >>> next_street(Street.SHOWDOWN)
        <Street.SHOWDOWN: 'showdown'>
    """
    street_order = [
        Street.PREFLOP,
        Street.FLOP,
        Street.TURN,
        Street.RIVER,
        Street.SHOWDOWN,
    ]

    try:
        idx = street_order.index(current)
        # Don't go past showdown
        return street_order[min(idx + 1, len(street_order) - 1)]
    except ValueError:
        raise ValueError(f"Invalid street: {current}")


def get_cards_to_deal(street: Street) -> int:
    """Get number of community cards to deal at each street.

    Args:
        street: Current street

    Returns:
        Number of cards to deal (0 for preflop, 3 for flop, 1 for turn/river)
    """
    cards_by_street = {
        Street.PREFLOP: 0,
        Street.FLOP: 3,
        Street.TURN: 1,
        Street.RIVER: 1,
        Street.SHOWDOWN: 0,
    }
    return cards_by_street.get(street, 0)
