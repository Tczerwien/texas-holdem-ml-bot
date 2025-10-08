"""Poker hand evaluation for Texas Hold'em.

This module provides fast, deterministic hand ranking for 5-7 card hands.
Returns tuple (category, kickers) for easy comparison.

Hand categories (higher is better):
    8: Royal Flush (A-K-Q-J-10 of same suit)
    7: Straight Flush
    6: Four of a Kind
    5: Full House
    4: Flush
    3: Straight
    2: Three of a Kind
    1: Two Pair
    0: One Pair
   -1: High Card
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
from typing import List, Tuple

from .cards import Card

# Public return type: (category, kickers)
HandScore = Tuple[int, Tuple[int, ...]]


# Hand category constants for clarity
ROYAL_FLUSH = 8
STRAIGHT_FLUSH = 7
FOUR_OF_KIND = 6
FULL_HOUSE = 5
FLUSH = 4
STRAIGHT = 3
THREE_OF_KIND = 2
TWO_PAIR = 1
ONE_PAIR = 0
HIGH_CARD = -1


def evaluate_hand(cards: List[Card]) -> Tuple[int, Tuple[int, ...]]:
    """Evaluate a 5-7 card poker hand and return (category, kickers).

    Args:
        cards: List of 5-7 Card objects

    Returns:
        Tuple of (hand_category, kicker_tuple) where higher is better

    Raises:
        ValueError: If cards list has wrong length or invalid cards

    Examples:
        >>> from texas_holdem_ml_bot.engine.cards import Card
        >>> royal = [Card(14,'♠'), Card(13,'♠'),
        >>> Card(12,'♠'), Card(11,'♠'), Card(10,'♠')]
        >>> evaluate_hand(royal)
        (8, (14,))  # Royal flush
    """
    if not (5 <= len(cards) <= 7):
        raise ValueError(f"Must evaluate 5-7 cards, got {len(cards)}")

    # For 6-7 cards, find best 5-card hand
    if len(cards) > 5:
        return _evaluate_best_5(cards)

    return _evaluate_5(cards)


def _evaluate_5(cards: List[Card]) -> Tuple[int, Tuple[int, ...]]:
    """Evaluate exactly 5 cards."""
    ranks = [c.rank for c in cards]
    suits = [c.suit for c in cards]

    # Count rank frequencies
    rank_counts = Counter(ranks)
    counts_sorted = sorted(
        rank_counts.items(), key=lambda x: (x[1], x[0]), reverse=True
    )

    # Check for flush
    is_flush = len(set(suits)) == 1

    # Check for straight (including wheel)
    is_straight, straight_high = _check_straight(ranks)

    # Royal flush: A-K-Q-J-10 of same suit
    if is_flush and is_straight and straight_high == 14:
        return (ROYAL_FLUSH, (14,))

    # Straight flush
    if is_flush and is_straight:
        return (STRAIGHT_FLUSH, (straight_high,))

    # Four of a kind
    if counts_sorted[0][1] == 4:
        quad_rank = counts_sorted[0][0]
        kicker = counts_sorted[1][0]
        return (FOUR_OF_KIND, (quad_rank, kicker))

    # Full house
    if counts_sorted[0][1] == 3 and counts_sorted[1][1] == 2:
        trips_rank = counts_sorted[0][0]
        pair_rank = counts_sorted[1][0]
        return (FULL_HOUSE, (trips_rank, pair_rank))

    # Flush
    if is_flush:
        kickers = tuple(sorted(ranks, reverse=True))
        return (FLUSH, kickers)

    # Straight
    if is_straight:
        return (STRAIGHT, (straight_high,))

    # Three of a kind
    if counts_sorted[0][1] == 3:
        trips_rank = counts_sorted[0][0]
        kickers = tuple(sorted([r for r, c in counts_sorted[1:]], reverse=True))
        return (THREE_OF_KIND, (trips_rank,) + kickers)

    # Two pair
    if counts_sorted[0][1] == 2 and counts_sorted[1][1] == 2:
        high_pair = max(counts_sorted[0][0], counts_sorted[1][0])
        low_pair = min(counts_sorted[0][0], counts_sorted[1][0])
        kicker = counts_sorted[2][0]
        return (TWO_PAIR, (high_pair, low_pair, kicker))

    # One pair
    if counts_sorted[0][1] == 2:
        pair_rank = counts_sorted[0][0]
        kickers = tuple(sorted([r for r, c in counts_sorted[1:]], reverse=True))
        return (ONE_PAIR, (pair_rank,) + kickers)

    # High card
    kickers = tuple(sorted(ranks, reverse=True))
    return (HIGH_CARD, kickers)


def _check_straight(ranks: List[int]) -> Tuple[bool, int]:
    """Check if ranks form a straight, return (is_straight, high_card).

    Handles the wheel (A-2-3-4-5) special case where Ace is low.
    """
    unique_ranks = sorted(set(ranks))

    # Need exactly 5 unique ranks for a straight in a 5-card hand
    if len(unique_ranks) != 5:
        return (False, 0)

    # Check regular straight (consecutive ranks)
    if unique_ranks[-1] - unique_ranks[0] == 4:
        return (True, unique_ranks[-1])

    # Check wheel: A-2-3-4-5 (ranks: 14,2,3,4,5)
    if unique_ranks == [2, 3, 4, 5, 14]:
        return (True, 5)  # High card is 5 in a wheel

    return (False, 0)


def _evaluate_best_5(cards: List[Card]) -> Tuple[int, Tuple[int, ...]]:
    """Find the best 5-card hand from 6-7 cards."""

    best_hand: HandScore = (HIGH_CARD, tuple())

    # Check all 5-card combinations
    for combo in combinations(cards, 5):
        hand_value = _evaluate_5(list(combo))
        if hand_value > best_hand:
            best_hand = hand_value

    return best_hand


# Convenience function matching roadmap naming
def evaluate_7(cards: List[Card]) -> Tuple[int, Tuple[int, ...]]:
    """Alias for evaluate_hand to match roadmap documentation."""
    return evaluate_hand(cards)
