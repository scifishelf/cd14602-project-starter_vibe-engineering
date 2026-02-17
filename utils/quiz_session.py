"""
Quiz session orchestration.

Manages the main quiz loop: presenting cards, collecting answers,
tracking results, and handling interrupts.
"""

from typing import List

from utils.display import Display
from utils.models import Flashcard, QuizResult, SessionStats
from utils.quiz_engine import QuizMode


class QuizSession:
    """Run an interactive flashcard quiz session."""

    def __init__(
        self,
        mode: QuizMode,
        cards: List[Flashcard],
        display: Display,
        show_detailed_stats: bool = False,
    ) -> None:
        self._mode = mode
        self._cards = cards
        self._display = display
        self._show_detailed_stats = show_detailed_stats
        self._results: List[QuizResult] = []
        self._question_number = 0

    def run(self) -> SessionStats:
        """Run the quiz and return session statistics."""
        try:
            while self._mode.has_more():
                card = self._mode.next_card()
                if card is None:
                    break
                should_continue = self._ask_question(card)
                if not should_continue:
                    break
        except KeyboardInterrupt:
            self._display.show_interrupted()

        stats = self._build_stats()
        self._display.show_stats(stats, detailed=self._show_detailed_stats)
        return stats

    def _ask_question(self, card: Flashcard) -> bool:
        """Ask a single question. Returns False if user wants to exit."""
        self._question_number += 1
        total = len(self._cards)
        self._display.show_question(self._question_number, total, card.front)

        answer = self._display.get_answer()
        if answer.strip().lower() == "exit":
            return False

        correct = self._check_answer(answer, card.back)

        card.times_shown += 1
        if correct:
            card.times_correct += 1

        self._mode.record_result(card, correct)
        self._display.show_feedback(correct, card.back)
        self._results.append(
            QuizResult(card=card, user_answer=answer, is_correct=correct)
        )
        return True

    @staticmethod
    def _check_answer(user_answer: str, correct_answer: str) -> bool:
        """Compare answers case-insensitively with whitespace normalization."""
        return user_answer.strip().lower() == correct_answer.strip().lower()

    def _build_stats(self) -> SessionStats:
        """Build session statistics from collected results."""
        correct_count = sum(1 for r in self._results if r.is_correct)
        return SessionStats(
            total_questions=len(self._results),
            correct_answers=correct_count,
            results=self._results,
        )
