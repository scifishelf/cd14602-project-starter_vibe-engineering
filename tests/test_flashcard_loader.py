"""
Unit tests for the FlashcardLoader class.
"""

import json
import shutil
import tempfile
from pathlib import Path

import pytest

from utils.flashcard_loader import FlashcardLoader, FlashcardValidationError


class TestFlashcardLoader:
    """Test suite for FlashcardLoader."""

    def setup_method(self):
        """Create a temporary directory for test data files."""
        self.temp_dir = tempfile.mkdtemp()
        self.loader = FlashcardLoader()

    def teardown_method(self):
        """Remove the temporary directory."""
        shutil.rmtree(self.temp_dir)

    def _write_json(self, filename: str, data) -> str:
        """Helper: write data to a JSON file and return its path."""
        filepath = Path(self.temp_dir) / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return str(filepath)

    def _write_raw(self, filename: str, content: str) -> str:
        """Helper: write raw string content to a file and return its path."""
        filepath = Path(self.temp_dir) / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return str(filepath)

    def test_load_valid_flashcards_array(self):
        """Test loading flashcards from a valid JSON array."""
        data = [
            {"front": "What is 2+2?", "back": "4"},
            {"front": "Capital of Germany?", "back": "Berlin"},
        ]
        path = self._write_json("valid_array.json", data)
        cards = self.loader.load(path)
        assert len(cards) == 2
        assert cards[0].front == "What is 2+2?"
        assert cards[0].back == "4"
        assert cards[1].front == "Capital of Germany?"
        assert cards[1].back == "Berlin"

    def test_load_valid_flashcards_object(self):
        """Test loading flashcards from object format with 'cards' key."""
        data = {
            "cards": [
                {"front": "Q1", "back": "A1"},
                {"front": "Q2", "back": "A2"},
            ]
        }
        path = self._write_json("valid_object.json", data)
        cards = self.loader.load(path)
        assert len(cards) == 2
        assert cards[0].front == "Q1"

    def test_load_invalid_json(self):
        """Test that invalid JSON raises an error."""
        path = self._write_raw("bad.json", "{not valid json!!")
        with pytest.raises(RuntimeError, match="Failed to load data"):
            self.loader.load(path)

    def test_load_missing_required_field(self):
        """Test that missing 'back' field raises validation error."""
        data = [{"front": "Q without answer"}]
        path = self._write_json("missing_back.json", data)
        with pytest.raises(
            FlashcardValidationError, match="missing required field 'back'"
        ):
            self.loader.load(path)

    def test_load_missing_front_field(self):
        """Test that missing 'front' field raises validation error."""
        data = [{"back": "Answer only"}]
        path = self._write_json("missing_front.json", data)
        with pytest.raises(
            FlashcardValidationError, match="missing required field 'front'"
        ):
            self.loader.load(path)

    def test_load_empty_file_returns_error(self):
        """Test that an empty/missing file raises validation error."""
        path = str(Path(self.temp_dir) / "nonexistent.json")
        with pytest.raises(FlashcardValidationError, match="empty"):
            self.loader.load(path)

    def test_load_empty_array(self):
        """Test that an empty array raises validation error."""
        path = self._write_json("empty.json", [])
        with pytest.raises(FlashcardValidationError, match="No flashcards found"):
            self.loader.load(path)

    def test_load_empty_strings_raises_error(self):
        """Test that empty front/back strings raise validation error."""
        data = [{"front": "", "back": "answer"}]
        path = self._write_json("empty_front.json", data)
        with pytest.raises(FlashcardValidationError, match="'front' field is empty"):
            self.loader.load(path)

    def test_whitespace_trimming(self):
        """Test that front and back values are trimmed of whitespace."""
        data = [{"front": "  Question?  ", "back": "  Answer  "}]
        path = self._write_json("whitespace.json", data)
        cards = self.loader.load(path)
        assert cards[0].front == "Question?"
        assert cards[0].back == "Answer"

    def test_object_without_cards_key(self):
        """Test that object format without 'cards' key raises error."""
        data = {"questions": [{"front": "Q", "back": "A"}]}
        path = self._write_json("no_cards_key.json", data)
        with pytest.raises(FlashcardValidationError, match="'cards' key"):
            self.loader.load(path)
