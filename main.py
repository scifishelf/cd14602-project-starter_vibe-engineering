"""
Flashcard Quizzer CLI - main entry point.

Usage:
    python main.py -f data/python_basics.json [-m sequential|random|adaptive] [--stats]
"""

import argparse
import sys
from typing import List, Optional

from utils.display import Display
from utils.flashcard_loader import FlashcardLoader, FlashcardValidationError
from utils.quiz_engine import QuizModeFactory
from utils.quiz_session import QuizSession


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="Flashcard Quizzer - Learn with interactive flashcards"
    )
    parser.add_argument(
        "-f",
        "--file",
        required=True,
        help="Path to the flashcard JSON file (e.g. data/python_basics.json)",
    )
    parser.add_argument(
        "-m",
        "--mode",
        default="sequential",
        choices=QuizModeFactory.available_modes(),
        help="Quiz mode (default: sequential)",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show detailed statistics after the quiz",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> None:
    """Main function for the Flashcard Quizzer CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        loader = FlashcardLoader()
        cards = loader.load(args.file)

        mode = QuizModeFactory.create(args.mode, cards)
        display = Display()

        display.show_welcome(args.file, args.mode, len(cards))

        session = QuizSession(
            mode=mode,
            cards=cards,
            display=display,
            show_detailed_stats=args.stats,
        )
        session.run()

    except FlashcardValidationError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
