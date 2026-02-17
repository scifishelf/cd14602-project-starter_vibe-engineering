"""
Unit tests for the quiz engine (Strategy + Factory patterns).
"""

import pytest

from utils.models import Flashcard
from utils.quiz_engine import (
    AdaptiveMode,
    QuizModeFactory,
    RandomMode,
    SequentialMode,
)


def _make_cards(n: int = 3) -> list[Flashcard]:
    """Helper: create n simple flashcards."""
    return [Flashcard(front=f"Q{i}", back=f"A{i}") for i in range(1, n + 1)]


class TestSequentialMode:
    """Tests for SequentialMode."""

    def test_cards_in_order(self):
        """Cards are returned in their original order."""
        cards = _make_cards(3)
        mode = SequentialMode(cards)
        result = []
        while mode.has_more():
            result.append(mode.next_card())
        assert result == cards

    def test_next_card_returns_none_when_done(self):
        """next_card returns None after all cards shown."""
        mode = SequentialMode(_make_cards(1))
        mode.next_card()
        assert mode.next_card() is None

    def test_reset_starts_over(self):
        """reset allows iterating again."""
        cards = _make_cards(2)
        mode = SequentialMode(cards)
        mode.next_card()
        mode.next_card()
        assert not mode.has_more()
        mode.reset()
        assert mode.has_more()
        assert mode.next_card() == cards[0]


class TestRandomMode:
    """Tests for RandomMode."""

    def test_all_cards_shown(self):
        """All cards are shown exactly once per pass."""
        cards = _make_cards(5)
        mode = RandomMode(cards)
        result = []
        while mode.has_more():
            result.append(mode.next_card())
        assert set(c.front for c in result) == set(c.front for c in cards)
        assert len(result) == len(cards)

    def test_reset_reshuffles(self):
        """Reset produces a new ordering (statistically)."""
        cards = _make_cards(10)
        mode = RandomMode(cards)
        first_pass = []
        while mode.has_more():
            first_pass.append(mode.next_card())
        mode.reset()
        second_pass = []
        while mode.has_more():
            second_pass.append(mode.next_card())
        # Both passes contain the same cards
        assert set(c.front for c in first_pass) == set(c.front for c in second_pass)


class TestAdaptiveMode:
    """Tests for AdaptiveMode."""

    def test_adaptive_mode_behavior(self):
        """Incorrect cards are added back to the queue."""
        cards = _make_cards(2)
        mode = AdaptiveMode(cards)

        # Answer first card wrong
        card1 = mode.next_card()
        mode.record_result(card1, correct=False)

        # Answer second card correctly
        card2 = mode.next_card()
        mode.record_result(card2, correct=True)

        # The wrong card should appear again
        assert mode.has_more()
        repeated = mode.next_card()
        assert repeated.front == card1.front

    def test_adaptive_all_correct_finishes(self):
        """When all answers are correct, quiz finishes normally."""
        cards = _make_cards(3)
        mode = AdaptiveMode(cards)
        count = 0
        while mode.has_more():
            card = mode.next_card()
            mode.record_result(card, correct=True)
            count += 1
        assert count == 3

    def test_adaptive_reset(self):
        """Reset clears re-queued cards and restarts."""
        cards = _make_cards(2)
        mode = AdaptiveMode(cards)
        card = mode.next_card()
        mode.record_result(card, correct=False)
        mode.reset()
        # After reset, should have exactly 2 cards again
        count = 0
        while mode.has_more():
            c = mode.next_card()
            mode.record_result(c, correct=True)
            count += 1
        assert count == 2


class TestQuizModeFactory:
    """Tests for QuizModeFactory."""

    def test_quiz_mode_factory(self):
        """Factory creates the correct class for each mode name."""
        cards = _make_cards(2)
        assert isinstance(QuizModeFactory.create("sequential", cards), SequentialMode)
        assert isinstance(QuizModeFactory.create("random", cards), RandomMode)
        assert isinstance(QuizModeFactory.create("adaptive", cards), AdaptiveMode)

    def test_factory_case_insensitive(self):
        """Factory handles case-insensitive mode names."""
        cards = _make_cards(1)
        assert isinstance(QuizModeFactory.create("Sequential", cards), SequentialMode)
        assert isinstance(QuizModeFactory.create("RANDOM", cards), RandomMode)

    def test_factory_invalid_mode(self):
        """Factory raises ValueError for unknown mode."""
        with pytest.raises(ValueError, match="Unknown quiz mode"):
            QuizModeFactory.create("nonexistent", _make_cards(1))

    def test_available_modes(self):
        """available_modes returns all supported mode names."""
        modes = QuizModeFactory.available_modes()
        assert "sequential" in modes
        assert "random" in modes
        assert "adaptive" in modes

    def test_empty_cards(self):
        """Modes handle empty card lists gracefully."""
        mode = QuizModeFactory.create("sequential", [])
        assert not mode.has_more()
        assert mode.next_card() is None
