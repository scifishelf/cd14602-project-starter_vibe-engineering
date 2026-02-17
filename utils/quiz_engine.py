"""
Quiz engine implementing the Strategy and Factory design patterns.

QuizMode (ABC) defines the strategy interface. Concrete strategies:
- SequentialMode: cards in order
- RandomMode: cards in shuffled order
- AdaptiveMode: incorrect cards are re-queued

QuizModeFactory creates the appropriate mode from a string name.
"""

import random
from abc import ABC, abstractmethod
from typing import List, Optional

from utils.models import Flashcard


class QuizMode(ABC):
    """Abstract base class for quiz modes (Strategy Pattern)."""

    @abstractmethod
    def next_card(self) -> Optional[Flashcard]:
        """Return the next card or None if finished."""

    @abstractmethod
    def has_more(self) -> bool:
        """Return True if there are more cards to show."""

    @abstractmethod
    def reset(self) -> None:
        """Reset the mode to start over."""

    def record_result(self, card: Flashcard, correct: bool) -> None:
        """Record a quiz result. Override in modes that need it."""


class SequentialMode(QuizMode):
    """Present cards in their original order."""

    def __init__(self, cards: List[Flashcard]) -> None:
        self._cards = list(cards)
        self._index = 0

    def next_card(self) -> Optional[Flashcard]:
        if self._index >= len(self._cards):
            return None
        card = self._cards[self._index]
        self._index += 1
        return card

    def has_more(self) -> bool:
        return self._index < len(self._cards)

    def reset(self) -> None:
        self._index = 0


class RandomMode(QuizMode):
    """Present cards in a shuffled order."""

    def __init__(self, cards: List[Flashcard]) -> None:
        self._original = list(cards)
        self._cards: List[Flashcard] = []
        self._index = 0
        self._shuffle()

    def _shuffle(self) -> None:
        self._cards = list(self._original)
        random.shuffle(self._cards)
        self._index = 0

    def next_card(self) -> Optional[Flashcard]:
        if self._index >= len(self._cards):
            return None
        card = self._cards[self._index]
        self._index += 1
        return card

    def has_more(self) -> bool:
        return self._index < len(self._cards)

    def reset(self) -> None:
        self._shuffle()


class AdaptiveMode(QuizMode):
    """Incorrect cards are re-queued for additional practice."""

    def __init__(self, cards: List[Flashcard]) -> None:
        self._original = list(cards)
        self._queue: List[Flashcard] = list(cards)
        self._index = 0

    def next_card(self) -> Optional[Flashcard]:
        if self._index >= len(self._queue):
            return None
        card = self._queue[self._index]
        self._index += 1
        return card

    def has_more(self) -> bool:
        return self._index < len(self._queue)

    def reset(self) -> None:
        self._queue = list(self._original)
        self._index = 0

    def record_result(self, card: Flashcard, correct: bool) -> None:
        """Re-queue incorrect cards for another attempt."""
        if not correct:
            self._queue.append(card)


class QuizModeFactory:
    """Factory for creating quiz mode instances (Factory Pattern)."""

    _modes = {
        "sequential": SequentialMode,
        "random": RandomMode,
        "adaptive": AdaptiveMode,
    }

    @classmethod
    def create(cls, mode_name: str, cards: List[Flashcard]) -> QuizMode:
        """Create a quiz mode by name.

        Args:
            mode_name: One of 'sequential', 'random', 'adaptive'.
            cards: The flashcards to use.

        Raises:
            ValueError: If mode_name is not recognized.
        """
        mode_class = cls._modes.get(mode_name.lower())
        if mode_class is None:
            available = ", ".join(sorted(cls._modes.keys()))
            raise ValueError(f"Unknown quiz mode '{mode_name}'. Available: {available}")
        return mode_class(cards)

    @classmethod
    def available_modes(cls) -> List[str]:
        """Return list of available mode names."""
        return sorted(cls._modes.keys())
