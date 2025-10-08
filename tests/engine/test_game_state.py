"""Tests for game state module."""

import pytest

from texas_holdem_ml_bot.engine.cards import Card
from texas_holdem_ml_bot.engine.game_state import GameState, PlayerState
from texas_holdem_ml_bot.engine.rules import BLIND_STRUCTURE, Street


class TestPlayerState:
    """Test PlayerState class."""

    def test_player_state_creation(self):
        """Test creating player state."""
        player = PlayerState(stack=1000)
        assert player.stack == 1000
        assert player.in_hand is True
        assert player.bet == 0

    def test_player_state_with_values(self):
        """Test creating player with all values."""
        player = PlayerState(stack=500, in_hand=False, bet=100, position=2)
        assert player.stack == 500
        assert player.in_hand is False
        assert player.bet == 100
        assert player.position == 2

    def test_negative_stack_invalid(self):
        """Test that negative stack raises ValueError."""
        with pytest.raises(ValueError, match="Stack cannot be negative"):
            PlayerState(stack=-100)

    def test_negative_bet_invalid(self):
        """Test that negative bet raises ValueError."""
        with pytest.raises(ValueError, match="Bet cannot be negative"):
            PlayerState(stack=1000, bet=-10)


class TestGameState:
    """Test GameState class."""

    def test_game_state_creation(self):
        """Test creating basic game state."""
        players = [PlayerState(100), PlayerState(100)]
        state = GameState(players=players, button=0)

        assert len(state.players) == 2
        assert state.button == 0
        assert state.street == Street.PREFLOP
        assert len(state.board) == 0
        assert state.pot == 0

    def test_game_state_with_board(self):
        """Test game state with community cards."""
        players = [PlayerState(100), PlayerState(100)]
        board = [Card(14, "♠"), Card(13, "♠"), Card(12, "♠")]
        state = GameState(players=players, button=0, board=board, street=Street.FLOP)

        assert len(state.board) == 3
        assert state.street == Street.FLOP

    def test_empty_players_invalid(self):
        """Test that empty player list raises ValueError."""
        with pytest.raises(ValueError, match="at least one player"):
            GameState(players=[], button=0)

    def test_invalid_button_index(self):
        """Test that invalid button index raises ValueError."""
        players = [PlayerState(100), PlayerState(100)]
        with pytest.raises(ValueError, match="Button index"):
            GameState(players=players, button=5)

    def test_too_many_board_cards_invalid(self):
        """Test that >5 board cards raises ValueError."""
        players = [PlayerState(100), PlayerState(100)]
        board = [Card(r, "♠") for r in range(2, 8)]  # 6 cards
        with pytest.raises(ValueError, match="cannot have more than 5 cards"):
            GameState(players=players, button=0, board=board)


class TestPostBlinds:
    """Test posting blinds."""

    def test_post_blinds_three_players(self):
        """Test posting blinds with 3+ players."""
        players = [PlayerState(100), PlayerState(100), PlayerState(100)]
        state = GameState(players=players, button=0)

        state.post_blinds()

        # Player 1 (button+1) posts SB
        assert state.players[1].bet == BLIND_STRUCTURE["small_blind"]
        assert state.players[1].stack == 100 - BLIND_STRUCTURE["small_blind"]

        # Player 2 (button+2) posts BB
        assert state.players[2].bet == BLIND_STRUCTURE["big_blind"]
        assert state.players[2].stack == 100 - BLIND_STRUCTURE["big_blind"]

        # Pot should have both blinds
        assert (
            state.pot == BLIND_STRUCTURE["small_blind"] + BLIND_STRUCTURE["big_blind"]
        )

        # Action should be on player 0 (button+3 wraps around)
        assert state.to_act == 0

    def test_post_blinds_heads_up(self):
        """Test posting blinds in heads-up (2 players)."""
        players = [PlayerState(100), PlayerState(100)]
        state = GameState(players=players, button=0)

        state.post_blinds()

        # Heads-up: button posts SB
        assert state.players[0].bet == BLIND_STRUCTURE["small_blind"]

        # Other player posts BB
        assert state.players[1].bet == BLIND_STRUCTURE["big_blind"]

        # Pot has both blinds
        assert (
            state.pot == BLIND_STRUCTURE["small_blind"] + BLIND_STRUCTURE["big_blind"]
        )

        # Action on SB (button)
        assert state.to_act == 0

    def test_post_blinds_wraps_around(self):
        """Test that blind positions wrap around correctly."""
        players = [PlayerState(100), PlayerState(100), PlayerState(100)]
        state = GameState(players=players, button=2)  # Button at last position

        state.post_blinds()

        # Should wrap: player 0 is SB, player 1 is BB
        assert state.players[0].bet == BLIND_STRUCTURE["small_blind"]
        assert state.players[1].bet == BLIND_STRUCTURE["big_blind"]
        assert state.to_act == 2  # Action back to button

    def test_post_blinds_short_stack(self):
        """Test posting blinds when player has less than blind amount."""
        players = [
            PlayerState(10),  # Can't post full BB
            PlayerState(100),
            PlayerState(100),
        ]
        state = GameState(players=players, button=2)

        state.post_blinds()

        # Player 0 (SB) should post what they have
        assert state.players[0].stack == 10 - min(10, BLIND_STRUCTURE["small_blind"])

        # Player 1 (BB) posts full blind
        assert state.players[1].bet == BLIND_STRUCTURE["big_blind"]

    def test_post_blinds_too_few_players(self):
        """Test that posting blinds with <2 players raises error."""
        state = GameState(players=[PlayerState(100)], button=0)
        with pytest.raises(ValueError, match="at least 2 players"):
            state.post_blinds()


class TestGameStateProperties:
    """Test game state helper properties."""

    def test_active_players(self):
        """Test getting active (not folded) players."""
        players = [
            PlayerState(100, in_hand=True),
            PlayerState(100, in_hand=False),  # Folded
            PlayerState(100, in_hand=True),
        ]
        state = GameState(players=players, button=0)

        active = state.active_players
        assert active == [0, 2]
        assert state.num_active == 2

    def test_all_players_active(self):
        """Test when all players are active."""
        players = [PlayerState(100), PlayerState(100), PlayerState(100)]
        state = GameState(players=players, button=0)

        assert state.num_active == 3
        assert len(state.active_players) == 3

    def test_one_player_active(self):
        """Test when only one player remains."""
        players = [
            PlayerState(100, in_hand=True),
            PlayerState(100, in_hand=False),
            PlayerState(100, in_hand=False),
        ]
        state = GameState(players=players, button=0)

        assert state.num_active == 1
        assert state.active_players == [0]

    def test_is_hand_complete_one_player(self):
        """Test hand is complete when 1 player remains."""
        players = [
            PlayerState(100, in_hand=True),
            PlayerState(100, in_hand=False),
        ]
        state = GameState(players=players, button=0)

        assert state.is_hand_complete() is True

    def test_is_hand_complete_showdown(self):
        """Test hand is complete at showdown."""
        players = [PlayerState(100), PlayerState(100)]
        state = GameState(players=players, button=0, street=Street.SHOWDOWN)

        assert state.is_hand_complete() is True

    def test_is_hand_not_complete(self):
        """Test hand is not complete with multiple active players."""
        players = [PlayerState(100), PlayerState(100)]
        state = GameState(players=players, button=0, street=Street.FLOP)

        assert state.is_hand_complete() is False


class TestGameStateIntegration:
    """Integration tests for game state."""

    def test_typical_hand_setup(self):
        """Test setting up a typical hand."""
        # Create 6-player table
        players = [PlayerState(1000) for _ in range(6)]
        state = GameState(players=players, button=0)

        # Post blinds
        state.post_blinds()

        # Verify state
        assert state.pot > 0
        assert state.to_act is not None
        assert state.num_active == 6
        assert state.street == Street.PREFLOP
        assert len(state.board) == 0

    def test_hand_progression(self):
        """Test basic hand progression."""
        players = [PlayerState(100), PlayerState(100)]
        state = GameState(players=players, button=0)

        # Preflop
        state.post_blinds()
        assert state.street == Street.PREFLOP

        # Move to flop
        state.street = Street.FLOP
        state.board = [Card(14, "♠"), Card(13, "♠"), Card(12, "♠")]
        assert len(state.board) == 3

        # Move to turn
        state.street = Street.TURN
        state.board.append(Card(11, "♠"))
        assert len(state.board) == 4

        # Move to river
        state.street = Street.RIVER
        state.board.append(Card(10, "♠"))
        assert len(state.board) == 5
