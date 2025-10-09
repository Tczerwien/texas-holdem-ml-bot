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
from typing import List, Sequence, Set, Tuple

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


STRAIGHT_BITMASKS = [0] * 15
for high in range(5, 15):
    mask = 0
    for rank in range(high - 4, high + 1):
        if rank == 1:
            mask |= 1 << 1
        else:
            mask |= 1 << rank
    STRAIGHT_BITMASKS[high] = mask


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
    if len(cards) == 5:
        return _evaluate_5(cards)

    return _evaluate_best_5_fast(cards)


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

    # Royal or straight flushes take priority over lower-ranked categories
    if is_flush and is_straight:
        if straight_high == 14:
            return (ROYAL_FLUSH, (14,))
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
        remaining = [r for r, c in counts_sorted[1:]]
        kickers = tuple(sorted(remaining, reverse=True))
        return (THREE_OF_KIND, (trips_rank,) + kickers)

    # Two pair
    if counts_sorted[0][1] == 2 and counts_sorted[1][1] == 2:
        pair_a, pair_b = counts_sorted[0][0], counts_sorted[1][0]
        high_pair, low_pair = max(pair_a, pair_b), min(pair_a, pair_b)
        kicker = counts_sorted[2][0]
        return (TWO_PAIR, (high_pair, low_pair, kicker))

    # One pair
    if counts_sorted[0][1] == 2:
        pair_rank = counts_sorted[0][0]
        remaining = [r for r, c in counts_sorted[1:]]
        kickers = tuple(sorted(remaining, reverse=True))
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


def _evaluate_best_5_fast(cards: Sequence[Card]) -> Tuple[int, Tuple[int, ...]]:
    """Evaluate 6-7 card hands without brute-force combinations."""

    rank_counts: list[int] = [0] * 15
    suit_ranks: dict[str, list[int]] = {"♣": [], "♦": [], "♥": [], "♠": []}
    suit_masks: dict[str, int] = {"♣": 0, "♦": 0, "♥": 0, "♠": 0}
    rank_mask: int = 0

    for card in cards:
        rank_counts[card.rank] += 1
        suit_ranks[card.suit].append(card.rank)
        suit_masks[card.suit] |= 1 << card.rank
        rank_mask |= 1 << card.rank

    trip_ranks = [rank for rank in range(14, 1, -1) if rank_counts[rank] >= 3]
    pair_ranks = [rank for rank in range(14, 1, -1) if rank_counts[rank] >= 2]

    best_flush: Tuple[int, ...] | None = None

    for suit, ranks in suit_ranks.items():
        if len(ranks) < 5:
            continue

        mask = suit_masks[suit]
        straight_high = _highest_straight(mask)
        if straight_high:
            if straight_high == 14:
                return (ROYAL_FLUSH, (14,))
            return (STRAIGHT_FLUSH, (straight_high,))

        top_five = tuple(sorted(ranks, reverse=True)[:5])
        if best_flush is None:
            best_flush = top_five
        elif top_five > best_flush:
            best_flush = top_five

    for rank in range(14, 1, -1):
        if rank_counts[rank] == 4:
            kicker = _collect_high_cards(rank_counts, {rank}, 1)[0]
            return (FOUR_OF_KIND, (rank, kicker))

    if trip_ranks:
        primary_trip = trip_ranks[0]
        secondary_trip = None
        if len(trip_ranks) > 1:
            secondary_trip = trip_ranks[1]
        else:
            for pair_rank in pair_ranks:
                if pair_rank != primary_trip:
                    secondary_trip = pair_rank
                    break

        if secondary_trip is not None:
            return (FULL_HOUSE, (primary_trip, secondary_trip))

    if best_flush is not None:
        return (FLUSH, best_flush)

    straight_high = _highest_straight(rank_mask)
    if straight_high:
        return (STRAIGHT, (straight_high,))

    if trip_ranks:
        trip = trip_ranks[0]
        kickers = _collect_high_cards(rank_counts, {trip}, 2)
        return (THREE_OF_KIND, (trip, *kickers))

    if len(pair_ranks) >= 2:
        high_pair, low_pair = pair_ranks[0], pair_ranks[1]
        kicker = _collect_high_cards(rank_counts, {high_pair, low_pair}, 1)[0]
        return (TWO_PAIR, (high_pair, low_pair, kicker))

    if pair_ranks:
        pair = pair_ranks[0]
        kickers = _collect_high_cards(rank_counts, {pair}, 3)
        return (ONE_PAIR, (pair, *kickers))

    kickers = _collect_high_cards(rank_counts, set(), 5)
    return (HIGH_CARD, tuple(kickers))


def _highest_straight(mask: int) -> int:
    """Return the highest straight high-card from a rank bitmask."""

    if mask & (1 << 14):
        mask |= 1 << 1

    for high in range(14, 4, -1):
        straight_mask = STRAIGHT_BITMASKS[high]
        if straight_mask and (mask & straight_mask) == straight_mask:
            return high

    return 0


def _collect_high_cards(
    rank_counts: Sequence[int], exclude: Set[int], needed: int
) -> List[int]:
    """Collect the highest ranked cards excluding certain ranks."""

    collected: List[int] = []
    for rank in range(14, 1, -1):
        if rank in exclude or rank_counts[rank] == 0:
            continue
        count = rank_counts[rank]
        take = min(count, needed - len(collected))
        collected.extend([rank] * take)
        if len(collected) == needed:
            break
    return collected


# Convenience function matching roadmap naming
def evaluate_7(cards: List[Card]) -> Tuple[int, Tuple[int, ...]]:
    """Alias for evaluate_hand to match roadmap documentation."""
    return evaluate_hand(cards)
