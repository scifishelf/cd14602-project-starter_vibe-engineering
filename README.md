# Flashcard Quizzer CLI

An interactive command-line flashcard application for learning and self-assessment. Supports three quiz modes, colored terminal output, and detailed session statistics.

## Features

- **Three Quiz Modes:** Sequential, Random, and Adaptive
- **Adaptive Learning:** Incorrect cards are automatically re-queued for additional practice
- **Colored Output:** Green for correct, red for incorrect, cyan for questions
- **Session Statistics:** Score, accuracy percentage, and missed-card review
- **Flexible Input:** Supports JSON array and object format flashcard decks
- **Graceful Interrupts:** Ctrl+C shows partial results instead of crashing

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Usage

```bash
# Sequential quiz (default mode)
python main.py -f data/python_basics.json

# Random order
python main.py -f data/python_basics.json -m random

# Adaptive mode (re-asks incorrect cards)
python main.py -f data/python_basics.json -m adaptive

# Show detailed statistics after the quiz
python main.py -f data/python_basics.json -m adaptive --stats
```

During the quiz, type your answer and press Enter. Type `exit` to quit early. Press Ctrl+C for a graceful interruption with partial results.

### Creating Your Own Flashcards

Flashcard files are JSON. Two formats are supported:

**Array format:**
```json
[
  {"front": "What is Python?", "back": "A programming language"},
  {"front": "What is PEP 8?", "back": "Python's style guide"}
]
```

**Object format:**
```json
{
  "cards": [
    {"front": "What is Python?", "back": "A programming language"}
  ]
}
```

## Architecture

```
starter/
├── main.py                    # CLI entry point (argparse)
├── utils/
│   ├── file_handler.py        # Generic JSON file I/O
│   ├── flashcard_loader.py    # Flashcard loading and validation
│   ├── models.py              # Dataclasses (Flashcard, QuizResult, SessionStats)
│   ├── quiz_engine.py         # Strategy Pattern + Factory Pattern
│   ├── quiz_session.py        # Session orchestration
│   └── display.py             # Terminal UI with color support
├── tests/                     # 55 unit and integration tests
├── data/                      # Sample flashcard decks
└── docs/                      # Project documentation
```

### Module Dependency Diagram

```mermaid
graph TD
    MAIN["main.py<br/><i>CLI Entry Point</i>"]
    LOADER["flashcard_loader.py<br/><i>Load & Validate</i>"]
    ENGINE["quiz_engine.py<br/><i>Strategy + Factory</i>"]
    SESSION["quiz_session.py<br/><i>Orchestration</i>"]
    DISPLAY["display.py<br/><i>Terminal UI</i>"]
    MODELS["models.py<br/><i>Dataclasses</i>"]
    FH["file_handler.py<br/><i>JSON I/O</i>"]

    MAIN --> LOADER
    MAIN --> ENGINE
    MAIN --> SESSION
    MAIN --> DISPLAY
    LOADER --> FH
    LOADER --> MODELS
    ENGINE --> MODELS
    SESSION --> ENGINE
    SESSION --> DISPLAY
    SESSION --> MODELS
```

### Design Patterns

#### Strategy Pattern — Quiz Modes

```mermaid
classDiagram
    class QuizMode {
        <<abstract>>
        +next_card() Optional~Flashcard~
        +has_more() bool
        +reset() None
        +record_result(card, correct) None
    }
    class SequentialMode {
        -_cards: List~Flashcard~
        -_index: int
        +next_card() Optional~Flashcard~
        +has_more() bool
        +reset() None
    }
    class RandomMode {
        -_original: List~Flashcard~
        -_cards: List~Flashcard~
        -_index: int
        +next_card() Optional~Flashcard~
        +has_more() bool
        +reset() None
    }
    class AdaptiveMode {
        -_original: List~Flashcard~
        -_queue: List~Flashcard~
        -_index: int
        +next_card() Optional~Flashcard~
        +has_more() bool
        +reset() None
        +record_result(card, correct) None
    }

    QuizMode <|-- SequentialMode
    QuizMode <|-- RandomMode
    QuizMode <|-- AdaptiveMode
```

#### Factory Pattern — Mode Creation

```mermaid
classDiagram
    class QuizModeFactory {
        -_modes: Dict~str, Type~
        +create(mode_name, cards)$ QuizMode
        +available_modes()$ List~str~
    }
    class QuizMode {
        <<abstract>>
    }

    QuizModeFactory ..> QuizMode : creates
    QuizModeFactory ..> SequentialMode : "sequential"
    QuizModeFactory ..> RandomMode : "random"
    QuizModeFactory ..> AdaptiveMode : "adaptive"
```

### Quiz Session Flowchart

```mermaid
flowchart TD
    START([python main.py -f deck.json -m mode]) --> PARSE[Parse CLI arguments]
    PARSE --> LOAD[FlashcardLoader.load]
    LOAD -->|Invalid JSON| ERR1[/Error message + exit 1/]
    LOAD -->|Valid| FACTORY[QuizModeFactory.create]
    FACTORY --> WELCOME[Display welcome banner]
    WELCOME --> CHECK{mode.has_more?}

    CHECK -->|No| STATS[Display session statistics]
    CHECK -->|Yes| NEXT[mode.next_card]
    NEXT --> SHOW[Display question]
    SHOW --> INPUT[Get user answer]

    INPUT -->|"exit"| STATS
    INPUT -->|KeyboardInterrupt| INTERRUPTED[Display interrupted message]
    INTERRUPTED --> STATS

    INPUT -->|Answer| COMPARE[Compare answer<br/>case-insensitive]
    COMPARE -->|Correct| GREEN[Show green feedback]
    COMPARE -->|Incorrect| RED[Show red feedback]

    GREEN --> RECORD[Record result on card]
    RED --> RECORD

    RECORD --> ADAPTIVE{Adaptive mode?}
    ADAPTIVE -->|Yes, incorrect| REQUEUE[Append card to queue]
    ADAPTIVE -->|Otherwise| CHECK
    REQUEUE --> CHECK

    STATS --> DETAILED{--stats flag?}
    DETAILED -->|Yes| MISSED[Show missed cards for review]
    DETAILED -->|No| DONE([End])
    MISSED --> DONE
```

### Data Model Overview

```mermaid
classDiagram
    class Flashcard {
        +front: str
        +back: str
        +times_shown: int
        +times_correct: int
        +times_incorrect int
        +accuracy float
    }
    class QuizResult {
        +card: Flashcard
        +user_answer: str
        +is_correct: bool
    }
    class SessionStats {
        +total_questions: int
        +correct_answers: int
        +results: List~QuizResult~
        +accuracy_percent float
        +missed_cards List~Flashcard~
    }

    SessionStats o-- QuizResult : contains
    QuizResult --> Flashcard : references
```

## Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=. --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=. --cov-report=html
```

Current test coverage: **94%** across 55 test cases.

## Code Quality

```bash
black .          # Format code
isort .          # Organize imports
flake8 .         # Lint
mypy .           # Type check
```

## Documentation

- `docs/ai_edit_log.md` - Detailed AI interaction log
- `docs/final_report.md` - Project report with architecture and reflection
- `docs/design_patterns.md` - Design pattern reference
- `docs/project_rubric.md` - Assessment rubric

## Built With

- Python 3.8+ with dataclasses and ABC
- pytest + pytest-cov for testing
- Black, isort, flake8 for code quality
- Claude Code for AI-assisted development
