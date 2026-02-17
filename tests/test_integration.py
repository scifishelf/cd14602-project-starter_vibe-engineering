"""
Integration tests for the Flashcard Quizzer.

Tests end-to-end quiz flows by simulating user input.
"""

from unittest.mock import patch

import pytest

from utils.display import Display
from utils.models import Flashcard
from utils.quiz_engine import QuizModeFactory
from utils.quiz_session import QuizSession


def _make_cards() -> list[Flashcard]:
    """Create a small set of flashcards for testing."""
    return [
        Flashcard(front="Capital of France?", back="Paris"),
        Flashcard(front="2 + 2?", back="4"),
        Flashcard(front="Color of sky?", back="Blue"),
    ]


class TestFullSession:
    """Integration tests for complete quiz sessions."""

    def test_full_session(self):
        """Simulate a 3-question quiz with mixed correct/incorrect answers."""
        cards = _make_cards()
        mode = QuizModeFactory.create("sequential", cards)
        display = Display(use_color=False)

        # Answers: correct, wrong, correct
        answers = iter(["Paris", "5", "Blue"])

        with patch.object(display, "get_answer", side_effect=answers):
            session = QuizSession(
                mode=mode, cards=cards, display=display, show_detailed_stats=True
            )
            stats = session.run()

        assert stats.total_questions == 3
        assert stats.correct_answers == 2
        assert stats.accuracy_percent == pytest.approx(66.7, abs=0.1)
        assert len(stats.missed_cards) == 1
        assert stats.missed_cards[0].front == "2 + 2?"

    def test_exit_command(self):
        """User typing 'exit' ends the quiz early."""
        cards = _make_cards()
        mode = QuizModeFactory.create("sequential", cards)
        display = Display(use_color=False)

        answers = iter(["Paris", "exit"])

        with patch.object(display, "get_answer", side_effect=answers):
            session = QuizSession(mode=mode, cards=cards, display=display)
            stats = session.run()

        assert stats.total_questions == 1
        assert stats.correct_answers == 1

    def test_keyboard_interrupt(self):
        """KeyboardInterrupt ends the quiz gracefully."""
        cards = _make_cards()
        mode = QuizModeFactory.create("sequential", cards)
        display = Display(use_color=False)

        def answer_then_interrupt():
            yield "Paris"
            raise KeyboardInterrupt

        gen = answer_then_interrupt()

        with patch.object(display, "get_answer", side_effect=lambda: next(gen)):
            session = QuizSession(mode=mode, cards=cards, display=display)
            stats = session.run()

        assert stats.total_questions == 1
        assert stats.correct_answers == 1

    def test_case_insensitive_answer(self):
        """Answers are compared case-insensitively."""
        cards = [Flashcard(front="Capital of France?", back="Paris")]
        mode = QuizModeFactory.create("sequential", cards)
        display = Display(use_color=False)

        with patch.object(display, "get_answer", return_value="  pARIS  "):
            session = QuizSession(mode=mode, cards=cards, display=display)
            stats = session.run()

        assert stats.correct_answers == 1

    def test_adaptive_session(self):
        """Adaptive mode re-asks incorrect cards."""
        cards = [
            Flashcard(front="Q1", back="A1"),
            Flashcard(front="Q2", back="A2"),
        ]
        mode = QuizModeFactory.create("adaptive", cards)
        display = Display(use_color=False)

        # Wrong on Q1 first time, then correct on Q2, then correct on Q1 retry
        answers = iter(["wrong", "A2", "A1"])

        with patch.object(display, "get_answer", side_effect=answers):
            session = QuizSession(mode=mode, cards=cards, display=display)
            stats = session.run()

        assert stats.total_questions == 3
        assert stats.correct_answers == 2
