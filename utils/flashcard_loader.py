"""
Flashcard loading and validation utility.

Loads flashcard data from JSON files, supporting both array format
and object format (with a "cards" key). Validates required fields
and normalizes whitespace.
"""

from typing import Any, List

from utils.file_handler import FileHandler
from utils.models import Flashcard


class FlashcardValidationError(ValueError):
    """Raised when flashcard data is invalid or missing required fields."""


class FlashcardLoader:
    """Load and validate flashcards from JSON files."""

    def __init__(self) -> None:
        self._file_handler = FileHandler(data_dir=".")

    def load(self, filepath: str) -> List[Flashcard]:
        """Load flashcards from a JSON file.

        Args:
            filepath: Full path to the JSON file (e.g. "data/python_basics.json").

        Returns:
            List of validated Flashcard objects.

        Raises:
            FlashcardValidationError: If the file is empty, missing, or contains
                invalid flashcard data.
        """
        raw_data = self._file_handler.load_data(filepath)
        cards_data = self._extract_cards(raw_data)
        return self._validate_and_build(cards_data)

    def _extract_cards(self, data: Any) -> List[Any]:
        """Extract the list of card dicts from raw JSON data.

        Supports:
            - Array format: [{"front": ..., "back": ...}, ...]
            - Object format: {"cards": [{"front": ..., "back": ...}, ...]}
        """
        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            if not data:
                raise FlashcardValidationError(
                    "File is empty or contains no flashcard data."
                )
            if "cards" in data and isinstance(data["cards"], list):
                return data["cards"]
            raise FlashcardValidationError(
                "Object format must contain a 'cards' key with a list of cards."
            )

        raise FlashcardValidationError(
            f"Unexpected JSON structure: expected list or object, got {type(data).__name__}."
        )

    def _validate_and_build(self, cards_data: List[Any]) -> List[Flashcard]:
        """Validate card dicts and build Flashcard objects."""
        if not cards_data:
            raise FlashcardValidationError("No flashcards found in file.")

        flashcards: List[Flashcard] = []
        for i, card in enumerate(cards_data):
            if not isinstance(card, dict):
                raise FlashcardValidationError(
                    f"Card {i + 1}: expected an object, got {type(card).__name__}."
                )

            if "front" not in card:
                raise FlashcardValidationError(
                    f"Card {i + 1}: missing required field 'front'."
                )
            if "back" not in card:
                raise FlashcardValidationError(
                    f"Card {i + 1}: missing required field 'back'."
                )

            front = str(card["front"]).strip()
            back = str(card["back"]).strip()

            if not front:
                raise FlashcardValidationError(f"Card {i + 1}: 'front' field is empty.")
            if not back:
                raise FlashcardValidationError(f"Card {i + 1}: 'back' field is empty.")

            flashcards.append(Flashcard(front=front, back=back))

        return flashcards
