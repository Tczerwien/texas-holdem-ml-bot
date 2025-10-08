"""Card and deck representations for Texas Hold'em."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from random import shuffle
from typing import Iterable, List

# Unicode suit symbols
SUITS = ("♣", "♦", "♥", "♠")
# Ranks: 2-14 where 11=J, 12=Q, 13=K, 14=A
RANKS = tuple(range(2, 15))


@dataclass(frozen=True, slots=True)
class Card:
    """Immutable playing card with rank and suit.

    Args:
        rank: Integer rank (2-14, where 11=J, 12=Q, 13=K, 14=A)
        suit: Unicode suit symbol (♣, ♦, ♥, ♠)
    """

    rank: int
    suit: str

    def __post_init__(self) -> None:
        """Validate rank and suit on initialization."""
        if self.rank not in RANKS:
            raise ValueError(f"Invalid rank: {self.rank} (must be 2-14)")
        if self.suit not in SUITS:
            raise ValueError(f"Invalid suit: {self.suit} (must be one of {SUITS})")

    def __str__(self) -> str:
        """Human-readable card representation (e.g., 'A♠', 'K♥')."""
        face_map = {11: "J", 12: "Q", 13: "K", 14: "A"}
        face = face_map.get(self.rank, str(self.rank))
        return f"{face}{self.suit}"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"Card({self.rank}, '{self.suit}')"


class Deck:
    """Standard 52-card deck with shuffle and draw operations.

    Can be initialized with a custom set of cards for testing.
    """

    def __init__(self, *, cards: Iterable[Card] | None = None) -> None:
        """Initialize deck with all 52 cards or custom cards.

        Args:
            cards: Optional iterable of cards. If None, creates full 52-card deck.
        """
        if cards is not None:
            self._cards: List[Card] = list(cards)
        else:
            self._cards = [Card(rank, suit) for suit in SUITS for rank in RANKS]

    def shuffle(self) -> None:
        """Shuffle the deck in place using Fisher-Yates algorithm."""
        shuffle(self._cards)

    def draw(self, n: int = 1) -> List[Card]:
        """Draw n cards from the top of the deck.

        Args:
            n: Number of cards to draw (default 1)

        Returns:
            List of drawn cards

        Raises:
            ValueError: If n is invalid or deck doesn't have enough cards
        """
        if not (1 <= n <= len(self._cards)):
            raise ValueError(
                f"Cannot draw {n} cards (deck has {len(self._cards)} cards)"
            )
        drawn, self._cards = self._cards[:n], self._cards[n:]
        return drawn

    def __len__(self) -> int:
        """Return number of cards remaining in deck."""
        return len(self._cards)

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"Deck({len(self)} cards)"


class Action(Enum):
    """Player action types in Texas Hold'em."""

    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"


@dataclass(frozen=True, slots=True)
class PlayerAction:
    """Typed action with optional amount for bets and raises.

    Args:
        action: Type of action (fold, check, call, bet, raise)
        amount: Chips committed (required for bet/raise, zero for fold/check/call)
    """

    action: Action
    amount: int = 0

    def __post_init__(self) -> None:
        """Validate action-amount combinations."""
        if self.amount < 0:
            raise ValueError(f"Amount cannot be negative: {self.amount}")
        if self.action in (Action.FOLD, Action.CHECK) and self.amount != 0:
            raise ValueError(f"{self.action.value} must have amount=0")
        if self.action in (Action.BET, Action.RAISE) and self.amount <= 0:
            raise ValueError(f"{self.action.value} requires positive amount")

    def __str__(self) -> str:
        """Human-readable action representation."""
        if self.action in (Action.BET, Action.RAISE):
            return f"{self.action.value} {self.amount}"
        return self.action.value
