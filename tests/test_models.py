"""
Unit tests for the data models (Flashcard, QuizResult, SessionStats).
"""

from utils.models import Flashcard, QuizResult, SessionStats


class TestFlashcard:
    """Test suite for the Flashcard dataclass."""

    def test_create_flashcard(self):
        """Test basic flashcard creation with defaults."""
        card = Flashcard(front="Q?", back="A")
        assert card.front == "Q?"
        assert card.back == "A"
        assert card.times_shown == 0
        assert card.times_correct == 0

    def test_times_incorrect(self):
        """Test times_incorrect property."""
        card = Flashcard(front="Q?", back="A", times_shown=5, times_correct=3)
        assert card.times_incorrect == 2

    def test_accuracy_no_attempts(self):
        """Test accuracy returns 0.0 when never shown."""
        card = Flashcard(front="Q?", back="A")
        assert card.accuracy == 0.0

    def test_accuracy_with_attempts(self):
        """Test accuracy calculation with attempts."""
        card = Flashcard(front="Q?", back="A", times_shown=4, times_correct=3)
        assert card.accuracy == 0.75

    def test_accuracy_perfect(self):
        """Test accuracy of 1.0 when all correct."""
        card = Flashcard(front="Q?", back="A", times_shown=10, times_correct=10)
        assert card.accuracy == 1.0


class TestQuizResult:
    """Test suite for the QuizResult dataclass."""

    def test_create_quiz_result(self):
        """Test creating a quiz result."""
        card = Flashcard(front="Q?", back="A")
        result = QuizResult(card=card, user_answer="A", is_correct=True)
        assert result.card is card
        assert result.user_answer == "A"
        assert result.is_correct is True


class TestSessionStats:
    """Test suite for the SessionStats dataclass."""

    def test_accuracy_percent(self):
        """Test accuracy percentage calculation."""
        stats = SessionStats(total_questions=10, correct_answers=7)
        assert stats.accuracy_percent == 70.0

    def test_accuracy_percent_zero_questions(self):
        """Test accuracy percentage with zero questions."""
        stats = SessionStats(total_questions=0, correct_answers=0)
        assert stats.accuracy_percent == 0.0

    def test_missed_cards(self):
        """Test missed_cards returns only incorrect results."""
        card1 = Flashcard(front="Q1?", back="A1")
        card2 = Flashcard(front="Q2?", back="A2")
        card3 = Flashcard(front="Q3?", back="A3")
        results = [
            QuizResult(card=card1, user_answer="A1", is_correct=True),
            QuizResult(card=card2, user_answer="wrong", is_correct=False),
            QuizResult(card=card3, user_answer="wrong", is_correct=False),
        ]
        stats = SessionStats(total_questions=3, correct_answers=1, results=results)
        missed = stats.missed_cards
        assert len(missed) == 2
        assert card2 in missed
        assert card3 in missed

    def test_missed_cards_empty_when_all_correct(self):
        """Test missed_cards is empty when all answers are correct."""
        card = Flashcard(front="Q?", back="A")
        results = [QuizResult(card=card, user_answer="A", is_correct=True)]
        stats = SessionStats(total_questions=1, correct_answers=1, results=results)
        assert stats.missed_cards == []
