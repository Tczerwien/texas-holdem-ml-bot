"""Game state representation for Texas Hold'em.

Tracks table state including players, pot, board cards, and current action.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .cards import Card
from .rules import BLIND_STRUCTURE, Street


@dataclass(slots=True)
class PlayerState:
    """State of a single player at the table.

    Args:
        stack: Chips available to bet
        in_hand: Whether player is still in the hand (not folded)
        bet: Current bet amount in this betting round
        position: Player position (0=button, 1=SB, 2=BB, etc.)
    """

    stack: int
    in_hand: bool = True
    bet: int = 0
    position: Optional[int] = None

    def __post_init__(self) -> None:
        """Validate player state."""
        if self.stack < 0:
            raise ValueError(f"Stack cannot be negative: {self.stack}")
        if self.bet < 0:
            raise ValueError(f"Bet cannot be negative: {self.bet}")


@dataclass(slots=True)
class GameState:
    """Complete state of a Texas Hold'em hand.

    Args:
        players: List of player states (order matters for position)
        button: Index of dealer button (0-indexed)
        street: Current betting round
        board: Community cards (0-5 cards)
        pot: Total chips in the pot
        to_act: Index of player to act next (None if action closed)
        current_bet: Highest bet in current round
    """

    players: List[PlayerState]
    button: int
    street: Street = Street.PREFLOP
    board: List[Card] = field(default_factory=list)
    pot: int = 0
    to_act: Optional[int] = None
    current_bet: int = 0

    def __post_init__(self) -> None:
        """Validate game state."""
        if not self.players:
            raise ValueError("Must have at least one player")
        if not (0 <= self.button < len(self.players)):
            raise ValueError(f"Button index {self.button} out of range")
        if len(self.board) > 5:
            raise ValueError(
                f"Board cannot have more than 5 cards, got {len(self.board)}"
            )

    def post_blinds(self) -> None:
        """Post small blind and big blind, set action to player after BB.

        Assumes heads-up or 3+ player structure:
        - Heads-up: button posts SB, other posts BB
        - 3+ players: button+1 posts SB, button+2 posts BB
        """
        num_players = len(self.players)

        if num_players < 2:
            raise ValueError("Need at least 2 players to post blinds")

        # Determine blind positions
        if num_players == 2:
            # Heads-up: button is SB, other is BB
            sb_idx = self.button
            bb_idx = (self.button + 1) % num_players
        else:
            # 3+ players: button+1 is SB, button+2 is BB
            sb_idx = (self.button + 1) % num_players
            bb_idx = (self.button + 2) % num_players

        # Post small blind
        sb_amount = min(self.players[sb_idx].stack, BLIND_STRUCTURE["small_blind"])
        self.players[sb_idx].stack -= sb_amount
        self.players[sb_idx].bet += sb_amount
        self.pot += sb_amount

        # Post big blind
        bb_amount = min(self.players[bb_idx].stack, BLIND_STRUCTURE["big_blind"])
        self.players[bb_idx].stack -= bb_amount
        self.players[bb_idx].bet += bb_amount
        self.pot += bb_amount

        # Set current bet to BB
        self.current_bet = bb_amount

        # Action starts at player after BB
        self.to_act = (bb_idx + 1) % num_players

    @property
    def active_players(self) -> List[int]:
        """Get indices of players still in the hand."""
        return [i for i, p in enumerate(self.players) if p.in_hand]

    @property
    def num_active(self) -> int:
        """Get count of players still in the hand."""
        return len(self.active_players)

    def is_hand_complete(self) -> bool:
        """Check if hand is complete (0-1 active players or at showdown)."""
        return self.num_active <= 1 or self.street == Street.SHOWDOWN
