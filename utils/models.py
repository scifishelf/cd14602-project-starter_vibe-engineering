"""
Data models for the Flashcard Quizzer application.

Defines Flashcard, QuizResult, and SessionStats dataclasses used
throughout the quiz engine and session management.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Flashcard:
    """A single flashcard with front (question) and back (answer)."""

    front: str
    back: str
    times_shown: int = 0
    times_correct: int = 0

    @property
    def times_incorrect(self) -> int:
        """Number of times answered incorrectly."""
        return self.times_shown - self.times_correct

    @property
    def accuracy(self) -> float:
        """Accuracy as a float between 0.0 and 1.0. Returns 0.0 if never shown."""
        if self.times_shown == 0:
            return 0.0
        return self.times_correct / self.times_shown


@dataclass
class QuizResult:
    """Result of a single quiz question."""

    card: Flashcard
    user_answer: str
    is_correct: bool


@dataclass
class SessionStats:
    """Statistics for a completed quiz session."""

    total_questions: int
    correct_answers: int
    results: List[QuizResult] = field(default_factory=list)

    @property
    def accuracy_percent(self) -> float:
        """Accuracy as a percentage (0.0 to 100.0)."""
        if self.total_questions == 0:
            return 0.0
        return (self.correct_answers / self.total_questions) * 100.0

    @property
    def missed_cards(self) -> List[Flashcard]:
        """List of flashcards that were answered incorrectly."""
        return [r.card for r in self.results if not r.is_correct]
