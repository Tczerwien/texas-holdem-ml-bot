"""Comprehensive tests for hand evaluator.

Tests all hand types, edge cases, kickers, and the wheel straight.
"""

import pytest

from texas_holdem_ml_bot.engine.cards import Card, Deck
from texas_holdem_ml_bot.engine.evaluator import (
    FLUSH,
    FOUR_OF_KIND,
    FULL_HOUSE,
    HIGH_CARD,
    ONE_PAIR,
    ROYAL_FLUSH,
    STRAIGHT,
    STRAIGHT_FLUSH,
    THREE_OF_KIND,
    TWO_PAIR,
    evaluate_hand,
)


class TestRoyalFlush:
    """Test royal flush detection."""

    def test_royal_flush_spades(self):
        """Test royal flush in spades."""
        cards = [
            Card(14, "♠"),  # A
            Card(13, "♠"),  # K
            Card(12, "♠"),  # Q
            Card(11, "♠"),  # J
            Card(10, "♠"),  # 10
        ]
        category, kickers = evaluate_hand(cards)
        assert category == ROYAL_FLUSH
        assert kickers == (14,)

    def test_royal_flush_all_suits(self):
        """Test royal flush in all suits."""
        for suit in ["♠", "♥", "♦", "♣"]:
            cards = [Card(r, suit) for r in [14, 13, 12, 11, 10]]
            category, _ = evaluate_hand(cards)
            assert category == ROYAL_FLUSH


class TestStraightFlush:
    """Test straight flush detection."""

    def test_straight_flush_king_high(self):
        """Test K-high straight flush."""
        cards = [
            Card(13, "♥"),  # K
            Card(12, "♥"),  # Q
            Card(11, "♥"),  # J
            Card(10, "♥"),  # 10
            Card(9, "♥"),  # 9
        ]
        category, kickers = evaluate_hand(cards)
        assert category == STRAIGHT_FLUSH
        assert kickers == (13,)

    def test_straight_flush_wheel(self):
        """Test wheel straight flush (A-2-3-4-5 suited)."""
        cards = [
            Card(14, "♣"),  # A (plays as 1)
            Card(5, "♣"),
            Card(4, "♣"),
            Card(3, "♣"),
            Card(2, "♣"),
        ]
        category, kickers = evaluate_hand(cards)
        assert category == STRAIGHT_FLUSH
        assert kickers == (5,)  # 5 is high card in wheel

    def test_straight_flush_low(self):
        """Test low straight flush (6-5-4-3-2)."""
        cards = [Card(r, "♦") for r in [6, 5, 4, 3, 2]]
        category, kickers = evaluate_hand(cards)
        assert category == STRAIGHT_FLUSH
        assert kickers == (6,)


class TestFourOfKind:
    """Test four of a kind detection."""

    def test_four_aces(self):
        """Test quad aces."""
        cards = [
            Card(14, "♠"),
            Card(14, "♥"),
            Card(14, "♦"),
            Card(14, "♣"),
            Card(13, "♠"),  # K kicker
        ]
        category, kickers = evaluate_hand(cards)
        assert category == FOUR_OF_KIND
        assert kickers == (14, 13)

    def test_four_twos_with_kicker(self):
        """Test quad twos with kicker."""
        cards = [
            Card(2, "♠"),
            Card(2, "♥"),
            Card(2, "♦"),
            Card(2, "♣"),
            Card(7, "♠"),
        ]
        category, kickers = evaluate_hand(cards)
        assert category == FOUR_OF_KIND
        assert kickers == (2, 7)

    def test_four_of_kind_kicker_matters(self):
        """Test that kicker breaks ties."""
        hand1 = [Card(10, s) for s in ["♠", "♥", "♦", "♣"]] + [Card(14, "♠")]
        hand2 = [Card(10, s) for s in ["♠", "♥", "♦", "♣"]] + [Card(13, "♠")]

        _, kickers1 = evaluate_hand(hand1)
        _, kickers2 = evaluate_hand(hand2)

        assert kickers1 > kickers2  # Ace kicker beats King


class TestFullHouse:
    """Test full house detection."""

    def test_full_house_aces_over_kings(self):
        """Test aces full of kings."""
        cards = [
            Card(14, "♠"),
            Card(14, "♥"),
            Card(14, "♦"),
            Card(13, "♠"),
            Card(13, "♥"),
        ]
        category, kickers = evaluate_hand(cards)
        assert category == FULL_HOUSE
        assert kickers == (14, 13)

    def test_full_house_trips_rank_matters(self):
        """Test that trips rank determines winner."""
        hand1 = [
            Card(10, "♠"),
            Card(10, "♥"),
            Card(10, "♦"),
            Card(14, "♠"),
            Card(14, "♥"),
        ]
        hand2 = [Card(9, "♠"), Card(9, "♥"), Card(9, "♦"), Card(14, "♠"), Card(14, "♥")]

        _, kickers1 = evaluate_hand(hand1)
        _, kickers2 = evaluate_hand(hand2)

        assert kickers1 > kickers2

    def test_full_house_pair_rank_matters(self):
        """Test that pair rank breaks ties when trips are equal."""
        # Both have trip 10s, but different pairs
        hand1 = [
            Card(10, "♠"),
            Card(10, "♥"),
            Card(10, "♦"),
            Card(13, "♠"),
            Card(13, "♥"),
        ]
        hand2 = [
            Card(10, "♠"),
            Card(10, "♥"),
            Card(10, "♣"),
            Card(12, "♠"),
            Card(12, "♥"),
        ]

        _, kickers1 = evaluate_hand(hand1)
        _, kickers2 = evaluate_hand(hand2)

        assert kickers1 > kickers2  # K pair beats Q pair


class TestFlush:
    """Test flush detection."""

    def test_flush_ace_high(self):
        """Test ace-high flush."""
        cards = [
            Card(14, "♥"),
            Card(12, "♥"),
            Card(10, "♥"),
            Card(8, "♥"),
            Card(6, "♥"),
        ]
        category, kickers = evaluate_hand(cards)
        assert category == FLUSH
        assert kickers == (14, 12, 10, 8, 6)

    def test_flush_all_kickers_matter(self):
        """Test that all 5 kickers matter in flush."""
        hand1 = [Card(r, "♠") for r in [14, 13, 11, 9, 7]]
        hand2 = [Card(r, "♠") for r in [14, 13, 11, 9, 6]]

        _, kickers1 = evaluate_hand(hand1)
        _, kickers2 = evaluate_hand(hand2)

        assert kickers1 > kickers2  # 7 beats 6 in 5th kicker


class TestStraight:
    """Test straight detection including the wheel."""

    def test_straight_ace_high(self):
        """Test broadway straight (A-K-Q-J-10)."""
        cards = [
            Card(14, "♠"),
            Card(13, "♥"),
            Card(12, "♦"),
            Card(11, "♣"),
            Card(10, "♠"),
        ]
        category, kickers = evaluate_hand(cards)
        assert category == STRAIGHT
        assert kickers == (14,)

    def test_straight_king_high(self):
        """Test king-high straight."""
        cards = [
            Card(13, "♠"),
            Card(12, "♥"),
            Card(11, "♦"),
            Card(10, "♣"),
            Card(9, "♠"),
        ]
        category, kickers = evaluate_hand(cards)
        assert category == STRAIGHT
        assert kickers == (13,)

    def test_straight_wheel(self):
        """Test wheel straight (A-2-3-4-5, ace plays low)."""
        cards = [
            Card(14, "♠"),  # Ace plays as 1
            Card(5, "♥"),
            Card(4, "♦"),
            Card(3, "♣"),
            Card(2, "♠"),
        ]
        category, kickers = evaluate_hand(cards)
        assert category == STRAIGHT
        assert kickers == (5,)  # 5 is high card in wheel

    def test_straight_wheel_different_order(self):
        """Test wheel works regardless of card order."""
        cards = [
            Card(2, "♠"),
            Card(14, "♥"),  # Ace
            Card(3, "♦"),
            Card(5, "♣"),
            Card(4, "♠"),
        ]
        category, kickers = evaluate_hand(cards)
        assert category == STRAIGHT
        assert kickers == (5,)

    def test_straight_low(self):
        """Test low straight (6-5-4-3-2) with mixed suits."""
        cards = [
            Card(6, "♠"),
            Card(5, "♥"),
            Card(4, "♦"),
            Card(3, "♣"),
            Card(2, "♠"),
        ]
        category, kickers = evaluate_hand(cards)
        assert category == STRAIGHT
        assert kickers == (6,)


class TestThreeOfKind:
    """Test three of a kind detection."""

    def test_three_aces_with_kickers(self):
        """Test trip aces with two kickers."""
        cards = [
            Card(14, "♠"),
            Card(14, "♥"),
            Card(14, "♦"),
            Card(13, "♠"),
            Card(12, "♥"),
        ]
        category, kickers = evaluate_hand(cards)
        assert category == THREE_OF_KIND
        assert kickers == (14, 13, 12)

    def test_three_of_kind_kickers_matter(self):
        """Test that kickers break ties."""
        hand1 = [
            Card(10, "♠"),
            Card(10, "♥"),
            Card(10, "♦"),
            Card(14, "♠"),
            Card(13, "♥"),
        ]
        hand2 = [
            Card(10, "♠"),
            Card(10, "♥"),
            Card(10, "♣"),
            Card(14, "♠"),
            Card(12, "♥"),
        ]

        _, kickers1 = evaluate_hand(hand1)
        _, kickers2 = evaluate_hand(hand2)

        assert kickers1 > kickers2  # K kicker beats Q


class TestTwoPair:
    """Test two pair detection."""

    def test_two_pair_aces_and_kings(self):
        """Test aces and kings with kicker."""
        cards = [
            Card(14, "♠"),
            Card(14, "♥"),
            Card(13, "♦"),
            Card(13, "♣"),
            Card(12, "♠"),
        ]
        category, kickers = evaluate_hand(cards)
        assert category == TWO_PAIR
        assert kickers == (14, 13, 12)

    def test_two_pair_ordering(self):
        """Test that pairs are ordered high to low."""
        cards = [
            Card(5, "♠"),
            Card(5, "♥"),
            Card(14, "♦"),
            Card(14, "♣"),
            Card(2, "♠"),
        ]
        category, kickers = evaluate_hand(cards)
        assert category == TWO_PAIR
        assert kickers == (14, 5, 2)  # High pair first

    def test_two_pair_kicker_matters(self):
        """Test that kicker breaks ties."""
        hand1 = [
            Card(10, "♠"),
            Card(10, "♥"),
            Card(9, "♦"),
            Card(9, "♣"),
            Card(14, "♠"),
        ]
        hand2 = [
            Card(10, "♠"),
            Card(10, "♥"),
            Card(9, "♦"),
            Card(9, "♣"),
            Card(13, "♠"),
        ]

        _, kickers1 = evaluate_hand(hand1)
        _, kickers2 = evaluate_hand(hand2)

        assert kickers1 > kickers2


class TestOnePair:
    """Test one pair detection."""

    def test_one_pair_aces(self):
        """Test pair of aces with kickers."""
        cards = [
            Card(14, "♠"),
            Card(14, "♥"),
            Card(12, "♦"),
            Card(10, "♣"),
            Card(8, "♠"),
        ]
        category, kickers = evaluate_hand(cards)
        assert category == ONE_PAIR
        assert kickers == (14, 12, 10, 8)

    def test_one_pair_kickers_all_matter(self):
        """Test that all three kickers matter."""
        hand1 = [
            Card(10, "♠"),
            Card(10, "♥"),
            Card(14, "♦"),
            Card(13, "♣"),
            Card(12, "♠"),
        ]
        hand2 = [
            Card(10, "♠"),
            Card(10, "♥"),
            Card(14, "♦"),
            Card(13, "♣"),
            Card(11, "♠"),
        ]

        _, kickers1 = evaluate_hand(hand1)
        _, kickers2 = evaluate_hand(hand2)

        assert kickers1 > kickers2


class TestHighCard:
    """Test high card detection."""

    def test_high_card_ace(self):
        """Test ace-high hand."""
        cards = [
            Card(14, "♠"),
            Card(12, "♥"),
            Card(10, "♦"),
            Card(8, "♣"),
            Card(6, "♠"),
        ]
        category, kickers = evaluate_hand(cards)
        assert category == HIGH_CARD
        assert kickers == (14, 12, 10, 8, 6)

    def test_high_card_all_kickers_matter(self):
        """Test that all 5 cards matter in high card."""
        hand1 = [
            Card(14, "♠"),
            Card(13, "♥"),
            Card(11, "♦"),
            Card(9, "♣"),
            Card(7, "♠"),
        ]
        hand2 = [
            Card(14, "♠"),
            Card(13, "♥"),
            Card(11, "♦"),
            Card(9, "♣"),
            Card(6, "♠"),
        ]

        _, kickers1 = evaluate_hand(hand1)
        _, kickers2 = evaluate_hand(hand2)

        assert kickers1 > kickers2


class TestSevenCardEvaluation:
    """Test evaluating 6-7 card hands (best 5 out of 7)."""

    def test_seven_card_flush(self):
        """Test finding flush in 7 cards."""
        cards = [
            Card(14, "♥"),
            Card(12, "♥"),
            Card(10, "♥"),
            Card(8, "♥"),
            Card(6, "♥"),
            Card(5, "♠"),  # Extra cards
            Card(3, "♣"),
        ]
        category, _ = evaluate_hand(cards)
        assert category == FLUSH

    def test_seven_card_straight(self):
        """Test finding straight in 7 cards."""
        cards = [
            Card(10, "♠"),
            Card(9, "♥"),
            Card(8, "♦"),
            Card(7, "♣"),
            Card(6, "♠"),
            Card(4, "♥"),  # Extra cards
            Card(2, "♣"),
        ]
        category, kickers = evaluate_hand(cards)
        assert category == STRAIGHT
        assert kickers == (10,)

    def test_seven_card_full_house_vs_trips(self):
        """Test that full house beats trips even with extra cards."""
        cards = [
            Card(14, "♠"),
            Card(14, "♥"),
            Card(14, "♦"),
            Card(13, "♣"),
            Card(13, "♠"),
            Card(12, "♥"),
            Card(11, "♣"),
        ]
        category, kickers = evaluate_hand(cards)
        assert category == FULL_HOUSE
        assert kickers == (14, 13)

    def test_seven_card_wheel_with_extras(self):
        """Test finding wheel in 7 cards."""
        cards = [
            Card(14, "♠"),  # Ace
            Card(5, "♥"),
            Card(4, "♦"),
            Card(3, "♣"),
            Card(2, "♠"),
            Card(13, "♥"),  # Extras
            Card(12, "♣"),
        ]
        category, kickers = evaluate_hand(cards)
        assert category == STRAIGHT
        assert kickers == (5,)


class TestBoardPlays:
    """Test when the board is the best hand."""

    def test_board_is_royal_flush(self):
        """Test when board contains royal flush."""
        board = [Card(r, "♠") for r in [14, 13, 12, 11, 10]]
        category, _ = evaluate_hand(board)
        assert category == ROYAL_FLUSH

    def test_board_is_straight(self):
        """Test when board makes the straight (mixed suits)."""
        board = [
            Card(9, "♥"),
            Card(8, "♠"),
            Card(7, "♦"),
            Card(6, "♣"),
            Card(5, "♥"),
        ]
        category, kickers = evaluate_hand(board)
        assert category == STRAIGHT
        assert kickers == (9,)

    def test_board_quads_with_kicker(self):
        """Test board with quads."""
        cards = [
            Card(10, "♠"),
            Card(10, "♥"),
            Card(10, "♦"),
            Card(10, "♣"),
            Card(14, "♠"),
        ]
        category, kickers = evaluate_hand(cards)
        assert category == FOUR_OF_KIND
        assert kickers == (10, 14)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_invalid_hand_size_too_few(self):
        """Test that hands with < 5 cards raise ValueError."""
        cards = [Card(14, "♠"), Card(13, "♠"), Card(12, "♠"), Card(11, "♠")]
        with pytest.raises(ValueError, match="Must evaluate 5-7 cards"):
            evaluate_hand(cards)

    def test_invalid_hand_size_too_many(self):
        """Test that hands with > 7 cards raise ValueError."""
        cards = [Card(r, "♠") for r in range(2, 10)]  # 8 cards
        with pytest.raises(ValueError, match="Must evaluate 5-7 cards"):
            evaluate_hand(cards)

    def test_hand_comparison(self):
        """Test that hand categories compare correctly."""
        assert ROYAL_FLUSH > STRAIGHT_FLUSH
        assert STRAIGHT_FLUSH > FOUR_OF_KIND
        assert FOUR_OF_KIND > FULL_HOUSE
        assert FULL_HOUSE > FLUSH
        assert FLUSH > STRAIGHT
        assert STRAIGHT > THREE_OF_KIND
        assert THREE_OF_KIND > TWO_PAIR
        assert TWO_PAIR > ONE_PAIR
        assert ONE_PAIR > HIGH_CARD


class TestPerformance:
    """Test evaluator performance (Phase 1 acceptance criteria)."""

    def test_one_million_hands_performance(self):
        """Test evaluating 1M random 7-card hands.

        Phase 1 acceptance criteria: Evaluate 1M random 7-card hands
        under documented time budget.

        Target: < 30 seconds for 1M hands (≈30 microseconds per hand).
        This is achievable with the current implementation.
        """
        import time
        from random import seed

        # Set seed for reproducibility
        seed(42)

        num_hands = 1_000_000
        deck = Deck()

        print(f"\nBenchmarking {num_hands:,} hand evaluations...")
        start_time = time.time()

        for _ in range(num_hands):
            # Shuffle and draw 7 cards
            deck = Deck()  # Fresh deck each time
            deck.shuffle()
            cards = deck.draw(7)

            # Evaluate
            evaluate_hand(cards)

        elapsed = time.time() - start_time
        per_hand_us = (elapsed / num_hands) * 1_000_000

        print(f"Completed in {elapsed:.2f} seconds")
        print(f"Average: {per_hand_us:.2f} microseconds per hand")
        print(f"Throughput: {num_hands / elapsed:,.0f} hands/second")

        # Document the time budget
        # Target: < 30 seconds total (we expect much faster)
        assert (
            elapsed < 30
        ), f"Performance regression: took {elapsed:.2f}s (target: <30s)"

        # Also check reasonable per-hand time
        assert (
            per_hand_us < 100
        ), f"Per-hand time too slow: {per_hand_us:.2f}us (target: <100us)"

    def test_performance_sample(self, benchmark=None):
        """Smaller performance test for quick CI runs.

        Tests 10k hands to verify reasonable performance without
        taking too long in CI.
        """
        import time
        from random import seed

        seed(42)
        num_hands = 10_000

        start_time = time.time()

        for _ in range(num_hands):
            deck = Deck()
            deck.shuffle()
            cards = deck.draw(7)
            evaluate_hand(cards)

        elapsed = time.time() - start_time
        per_hand_us = (elapsed / num_hands) * 1_000_000

        print(f"\n10k hands: {elapsed:.3f}s ({per_hand_us:.2f} us/hand)")

        # Should be much faster than 1 second for 10k hands
        assert elapsed < 1.0, f"10k hands took {elapsed:.3f}s (should be <1s)"
