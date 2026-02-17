"""
Terminal display utilities for the Flashcard Quizzer.

Handles colored output, question formatting, user input,
feedback messages, and session statistics display.
"""

from utils.models import SessionStats


class Colors:
    """ANSI color codes for terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"


class Display:
    """Handles all terminal output for the quiz session."""

    def __init__(self, use_color: bool = True) -> None:
        self._use_color = use_color

    def _c(self, code: str, text: str) -> str:
        """Wrap text in a color code if colors are enabled."""
        if self._use_color:
            return f"{code}{text}{Colors.RESET}"
        return text

    def show_welcome(self, filename: str, mode: str, total_cards: int) -> str:
        """Return the welcome banner text."""
        lines = [
            self._c(Colors.BOLD, "=== Flashcard Quizzer ==="),
            f"Deck: {filename}",
            f"Mode: {mode}",
            f"Cards: {total_cards}",
            self._c(Colors.GRAY, "Type 'exit' to quit at any time."),
            "",
        ]
        msg = "\n".join(lines)
        print(msg)
        return msg

    def show_question(self, number: int, total: int, front: str) -> str:
        """Display a question and return the formatted string."""
        header = self._c(Colors.GRAY, f"[{number}/{total}]")
        question = self._c(Colors.CYAN, front)
        msg = f"\n{header} {question}"
        print(msg)
        return msg

    def get_answer(self) -> str:
        """Prompt the user for an answer. Returns 'exit' on EOFError."""
        try:
            return input("Your answer: ")
        except EOFError:
            print()
            return "exit"

    def show_feedback(self, correct: bool, correct_answer: str) -> str:
        """Display feedback for the user's answer."""
        if correct:
            msg = self._c(Colors.GREEN, "Correct!")
        else:
            msg = self._c(Colors.RED, f"Incorrect. Answer: {correct_answer}")
        print(msg)
        return msg

    def show_stats(self, stats: SessionStats, detailed: bool = False) -> str:
        """Display session statistics."""
        lines = [
            "",
            self._c(Colors.BOLD, "=== Session Results ==="),
            f"Score: {stats.correct_answers}/{stats.total_questions}"
            f" ({stats.accuracy_percent:.1f}%)",
        ]

        if detailed and stats.missed_cards:
            lines.append("")
            lines.append(self._c(Colors.YELLOW, "Cards to review:"))
            for card in stats.missed_cards:
                lines.append(f"  - {card.front} -> {card.back}")

        msg = "\n".join(lines)
        print(msg)
        return msg

    def show_interrupted(self) -> str:
        """Display message when quiz is interrupted."""
        msg = "\n" + self._c(
            Colors.YELLOW, "Quiz interrupted. Showing results so far..."
        )
        print(msg)
        return msg
