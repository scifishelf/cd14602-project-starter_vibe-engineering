"""
Unit tests for the Display utility.
"""

from utils.display import Colors, Display
from utils.models import Flashcard, QuizResult, SessionStats


class TestColors:
    """Test that color codes are defined."""

    def test_color_codes_exist(self):
        """All expected color codes are non-empty strings."""
        assert Colors.RESET
        assert Colors.BOLD
        assert Colors.RED
        assert Colors.GREEN
        assert Colors.CYAN


class TestDisplay:
    """Test suite for Display output formatting."""

    def test_show_welcome_no_color(self):
        """Welcome banner contains key information."""
        display = Display(use_color=False)
        msg = display.show_welcome("test.json", "sequential", 10)
        assert "test.json" in msg
        assert "sequential" in msg
        assert "10" in msg

    def test_show_question_no_color(self):
        """Question display shows number and card front."""
        display = Display(use_color=False)
        msg = display.show_question(1, 5, "What is Python?")
        assert "[1/5]" in msg
        assert "What is Python?" in msg

    def test_show_feedback_correct(self):
        """Correct feedback shows 'Correct!'."""
        display = Display(use_color=False)
        msg = display.show_feedback(True, "answer")
        assert "Correct" in msg

    def test_show_feedback_incorrect(self):
        """Incorrect feedback shows the correct answer."""
        display = Display(use_color=False)
        msg = display.show_feedback(False, "the real answer")
        assert "Incorrect" in msg
        assert "the real answer" in msg

    def test_show_stats_basic(self):
        """Stats display shows score and percentage."""
        stats = SessionStats(total_questions=5, correct_answers=3)
        display = Display(use_color=False)
        msg = display.show_stats(stats)
        assert "3/5" in msg
        assert "60.0%" in msg

    def test_show_stats_detailed_with_missed(self):
        """Detailed stats show missed cards for review."""
        card = Flashcard(front="Q?", back="A")
        results = [QuizResult(card=card, user_answer="wrong", is_correct=False)]
        stats = SessionStats(total_questions=1, correct_answers=0, results=results)
        display = Display(use_color=False)
        msg = display.show_stats(stats, detailed=True)
        assert "Q?" in msg
        assert "A" in msg

    def test_show_stats_detailed_no_missed(self):
        """Detailed stats with all correct does not show review section."""
        card = Flashcard(front="Q?", back="A")
        results = [QuizResult(card=card, user_answer="A", is_correct=True)]
        stats = SessionStats(total_questions=1, correct_answers=1, results=results)
        display = Display(use_color=False)
        msg = display.show_stats(stats, detailed=True)
        assert "review" not in msg.lower()

    def test_show_welcome_with_color(self):
        """Welcome banner includes ANSI codes when color is enabled."""
        display = Display(use_color=True)
        msg = display.show_welcome("test.json", "random", 3)
        assert Colors.BOLD in msg

    def test_show_interrupted(self):
        """Interrupted message is shown."""
        display = Display(use_color=False)
        msg = display.show_interrupted()
        assert "interrupted" in msg.lower()
