"""Tests for cards module."""

import pytest

from texas_holdem_ml_bot.engine.cards import (RANKS, SUITS, Action, Card, Deck,
                                              PlayerAction)


class TestCard:
    """Test Card class."""

    def test_valid_card_creation(self):
        """Test creating valid cards."""
        card = Card(14, "♠")
        assert card.rank == 14
        assert card.suit == "♠"

    def test_card_string_representation(self):
        """Test card string formatting."""
        assert str(Card(14, "♠")) == "A♠"
        assert str(Card(13, "♥")) == "K♥"
        assert str(Card(12, "♦")) == "Q♦"
        assert str(Card(11, "♣")) == "J♣"
        assert str(Card(10, "♠")) == "10♠"
        assert str(Card(2, "♥")) == "2♥"

    def test_card_immutable(self):
        """Test that cards are immutable."""
        card = Card(14, "♠")
        with pytest.raises(AttributeError):
            card.rank = 13  # type: ignore

    def test_invalid_rank(self):
        """Test that invalid ranks raise ValueError."""
        with pytest.raises(ValueError, match="Invalid rank"):
            Card(1, "♠")
        with pytest.raises(ValueError, match="Invalid rank"):
            Card(15, "♠")

    def test_invalid_suit(self):
        """Test that invalid suits raise ValueError."""
        with pytest.raises(ValueError, match="Invalid suit"):
            Card(14, "X")
        with pytest.raises(ValueError, match="Invalid suit"):
            Card(14, "H")  # Wrong format

    def test_card_equality(self):
        """Test card equality comparison."""
        card1 = Card(14, "♠")
        card2 = Card(14, "♠")
        card3 = Card(14, "♥")
        assert card1 == card2
        assert card1 != card3

    def test_card_hash(self):
        """Test that cards are hashable."""
        card = Card(14, "♠")
        card_set = {card, Card(14, "♠"), Card(13, "♠")}
        assert len(card_set) == 2  # Duplicate removed


class TestDeck:
    """Test Deck class."""

    def test_deck_initialization(self):
        """Test creating a full deck."""
        deck = Deck()
        assert len(deck) == len(SUITS) * len(RANKS)
        assert len(deck) == 52

    def test_deck_custom_cards(self):
        """Test creating deck with custom cards."""
        cards = [Card(14, "♠"), Card(13, "♠")]
        deck = Deck(cards=cards)
        assert len(deck) == 2

    def test_deck_shuffle(self):
        """Test shuffling changes card order."""
        deck1 = Deck()
        deck2 = Deck()

        # Draw cards from unshuffled decks - should be identical
        cards1 = deck1.draw(10)
        cards2 = deck2.draw(10)
        assert cards1 == cards2

        # Shuffle and compare - should be different (with high probability)
        deck3 = Deck()
        deck3.shuffle()
        cards3 = deck3.draw(10)
        # Very unlikely to match exactly
        assert cards3 != cards1

    def test_deck_draw_one(self):
        """Test drawing a single card."""
        deck = Deck()
        initial_len = len(deck)
        cards = deck.draw(1)

        assert len(cards) == 1
        assert isinstance(cards[0], Card)
        assert len(deck) == initial_len - 1

    def test_deck_draw_multiple(self):
        """Test drawing multiple cards."""
        deck = Deck()
        cards = deck.draw(5)

        assert len(cards) == 5
        assert len(deck) == 47
        assert len(set(cards)) == 5  # All unique

    def test_deck_draw_invalid_count(self):
        """Test that invalid draw counts raise ValueError."""
        deck = Deck()

        with pytest.raises(ValueError, match="Cannot draw"):
            deck.draw(0)

        with pytest.raises(ValueError, match="Cannot draw"):
            deck.draw(53)

        with pytest.raises(ValueError, match="Cannot draw"):
            deck.draw(-1)

    def test_deck_empty(self):
        """Test drawing from empty deck."""
        deck = Deck(cards=[])
        with pytest.raises(ValueError):
            deck.draw(1)

    def test_deck_repr(self):
        """Test deck string representation."""
        deck = Deck()
        assert "52" in repr(deck)


class TestPlayerAction:
    """Test PlayerAction class."""

    def test_fold_action(self):
        """Test fold action."""
        action = PlayerAction(Action.FOLD, 0)
        assert action.action == Action.FOLD
        assert action.amount == 0
        assert str(action) == "fold"

    def test_check_action(self):
        """Test check action."""
        action = PlayerAction(Action.CHECK, 0)
        assert str(action) == "check"

    def test_call_action(self):
        """Test call action."""
        action = PlayerAction(Action.CALL, 0)
        assert str(action) == "call"

    def test_bet_action(self):
        """Test bet action with amount."""
        action = PlayerAction(Action.BET, 100)
        assert action.amount == 100
        assert str(action) == "bet 100"

    def test_raise_action(self):
        """Test raise action with amount."""
        action = PlayerAction(Action.RAISE, 200)
        assert action.amount == 200
        assert str(action) == "raise 200"

    def test_fold_with_amount_invalid(self):
        """Test that fold with amount raises ValueError."""
        with pytest.raises(ValueError, match="must have amount=0"):
            PlayerAction(Action.FOLD, 10)

    def test_check_with_amount_invalid(self):
        """Test that check with amount raises ValueError."""
        with pytest.raises(ValueError, match="must have amount=0"):
            PlayerAction(Action.CHECK, 10)

    def test_bet_without_amount_invalid(self):
        """Test that bet without amount raises ValueError."""
        with pytest.raises(ValueError, match="requires positive amount"):
            PlayerAction(Action.BET, 0)

    def test_raise_without_amount_invalid(self):
        """Test that raise without amount raises ValueError."""
        with pytest.raises(ValueError, match="requires positive amount"):
            PlayerAction(Action.RAISE, 0)

    def test_negative_amount_invalid(self):
        """Test that negative amounts raise ValueError."""
        with pytest.raises(ValueError, match="cannot be negative"):
            PlayerAction(Action.FOLD, -10)

    def test_action_immutable(self):
        """Test that actions are immutable."""
        action = PlayerAction(Action.BET, 100)
        with pytest.raises(AttributeError):
            action.amount = 200  # type: ignore
