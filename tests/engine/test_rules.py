"""Tests for rules module."""


from texas_holdem_ml_bot.engine.rules import (BLIND_STRUCTURE, Street,
                                              get_cards_to_deal, next_street)


class TestStreet:
    """Test Street enum."""

    def test_street_values(self):
        """Test that all streets have correct values."""
        assert Street.PREFLOP.value == "preflop"
        assert Street.FLOP.value == "flop"
        assert Street.TURN.value == "turn"
        assert Street.RIVER.value == "river"
        assert Street.SHOWDOWN.value == "showdown"

    def test_street_comparison(self):
        """Test that streets are strings and comparable."""
        assert isinstance(Street.PREFLOP.value, str)
        assert Street.PREFLOP != Street.FLOP


class TestNextStreet:
    """Test street progression."""

    def test_preflop_to_flop(self):
        """Test progression from preflop to flop."""
        assert next_street(Street.PREFLOP) == Street.FLOP

    def test_flop_to_turn(self):
        """Test progression from flop to turn."""
        assert next_street(Street.FLOP) == Street.TURN

    def test_turn_to_river(self):
        """Test progression from turn to river."""
        assert next_street(Street.TURN) == Street.RIVER

    def test_river_to_showdown(self):
        """Test progression from river to showdown."""
        assert next_street(Street.RIVER) == Street.SHOWDOWN

    def test_showdown_stays_showdown(self):
        """Test that showdown doesn't progress further."""
        assert next_street(Street.SHOWDOWN) == Street.SHOWDOWN

    def test_full_progression(self):
        """Test full street progression."""
        current = Street.PREFLOP
        expected_order = [Street.FLOP, Street.TURN, Street.RIVER, Street.SHOWDOWN]

        for expected in expected_order:
            current = next_street(current)
            assert current == expected


class TestGetCardsToDeal:
    """Test card dealing logic."""

    def test_preflop_no_cards(self):
        """Test that preflop deals 0 community cards."""
        assert get_cards_to_deal(Street.PREFLOP) == 0

    def test_flop_three_cards(self):
        """Test that flop deals 3 cards."""
        assert get_cards_to_deal(Street.FLOP) == 3

    def test_turn_one_card(self):
        """Test that turn deals 1 card."""
        assert get_cards_to_deal(Street.TURN) == 1

    def test_river_one_card(self):
        """Test that river deals 1 card."""
        assert get_cards_to_deal(Street.RIVER) == 1

    def test_showdown_no_cards(self):
        """Test that showdown deals 0 cards."""
        assert get_cards_to_deal(Street.SHOWDOWN) == 0

    def test_total_cards_dealt(self):
        """Test that total community cards is 5."""
        total = sum(
            get_cards_to_deal(s)
            for s in [Street.PREFLOP, Street.FLOP, Street.TURN, Street.RIVER]
        )
        assert total == 5  # 0 + 3 + 1 + 1 = 5 community cards


class TestBlindStructure:
    """Test blind structure."""

    def test_blinds_defined(self):
        """Test that both blinds are defined."""
        assert "small_blind" in BLIND_STRUCTURE
        assert "big_blind" in BLIND_STRUCTURE

    def test_big_blind_is_double_small(self):
        """Test standard blind ratio (BB = 2 * SB)."""
        sb = BLIND_STRUCTURE["small_blind"]
        bb = BLIND_STRUCTURE["big_blind"]
        assert bb == 2 * sb

    def test_blinds_positive(self):
        """Test that blinds are positive values."""
        assert BLIND_STRUCTURE["small_blind"] > 0
        assert BLIND_STRUCTURE["big_blind"] > 0

    def test_default_blind_values(self):
        """Test default blind amounts."""
        assert BLIND_STRUCTURE["small_blind"] == 1
        assert BLIND_STRUCTURE["big_blind"] == 2
