# AI-Assisted Development Project Report

**Student Name:** Ansgar Simon
**Project Title:** Flashcard Quizzer CLI
**Date:** 2026-02-17

## Executive Summary

The Flashcard Quizzer is a command-line application for interactive flashcard-based learning, built as part of the Udacity Vibe Engineering course. The application supports three distinct quiz modes (sequential, random, and adaptive), colored terminal output, session statistics, and robust error handling. Development followed a phased approach in close collaboration with Claude Code, progressing from data models through a pattern-driven quiz engine to a polished CLI interface.

The project demonstrates effective AI-assisted development: Claude Code generated initial implementations based on detailed architectural prompts, while I reviewed, validated, and refined the output at each phase. The result is a production-quality codebase with 94% test coverage, clean linting, and two clearly applied design patterns.

## Project Overview

### Problem Statement

Students and self-learners need a simple, offline tool for flashcard-based study sessions. Existing solutions are often web-based, heavyweight, or lack adaptive learning features. A lightweight CLI tool that loads flashcards from JSON files and supports multiple quiz modes fills this gap.

### Solution Approach

The application was designed around separation of concerns with six modules, each handling a single responsibility:

- **models.py** - Data representation (Flashcard, QuizResult, SessionStats)
- **flashcard_loader.py** - Data validation and loading on top of the existing FileHandler
- **quiz_engine.py** - Quiz mode logic using Strategy and Factory patterns
- **quiz_session.py** - Session orchestration and answer checking
- **display.py** - Terminal output with optional color support
- **main.py** - CLI argument parsing and error handling

This layered architecture ensures that each module can be tested independently and modified without affecting others.

### Final Features

- [x] Three quiz modes: sequential, random, and adaptive
- [x] Adaptive learning: incorrect cards are re-queued for additional practice
- [x] Colored terminal output (green for correct, red for incorrect, cyan for questions)
- [x] Detailed session statistics with accuracy percentage and missed-card review
- [x] Support for both JSON array and object format flashcard files
- [x] Graceful handling of KeyboardInterrupt and exit commands
- [x] Case-insensitive answer matching with whitespace normalization
- [x] Input validation with descriptive error messages

## AI Collaboration Experience

### AI Tools Used

- [x] Claude Code (Claude Opus 4.6) - primary development tool

### Collaboration Workflow

My workflow followed a consistent pattern across all six phases:

1. **Architectural prompting:** I described the module's responsibilities, its interfaces with other modules, and specific requirements from the rubric. This gave Claude enough context to generate well-structured code.
2. **Generation and review:** Claude produced initial implementations. I read through each file, checking that the logic matched expectations and that edge cases were handled.
3. **Test-first validation:** Each phase included writing and running tests immediately after code generation. This caught issues early rather than at integration time.
4. **Incremental refinement:** When tests revealed issues or linting tools flagged problems, I addressed them before moving to the next phase.

### Most Valuable AI Interactions

The architecture planning interaction was the most impactful. By providing Claude with the full rubric requirements and existing codebase structure, it produced a coherent plan that addressed all assessment criteria. This eliminated the need for major refactoring later.

The quiz engine implementation was the most technically interesting. Claude correctly applied the Strategy Pattern with an abstract base class defining the quiz mode interface, and the Factory Pattern to decouple mode creation from usage. The `record_result()` method with a no-op default was an elegant solution that avoided forcing unnecessary implementations in simple modes.

### Challenges with AI Collaboration

The main challenge was handling the existing `FileHandler` behavior where `load_data()` returns an empty dict `{}` for missing files instead of raising an error. This required careful validation in the loader layer. When I provided this context explicitly, Claude correctly implemented the `isinstance` checks and validation logic needed.

## Software Engineering Practices

### Code Quality Measures

- [x] Code formatting with Black
- [x] Import organization with isort
- [x] Linting with flake8 (zero errors)
- [x] Type hints on all public methods
- [x] Docstrings on all modules and classes
- [x] Custom exceptions for domain-specific errors

### Testing Strategy

The testing approach combined unit tests and integration tests:

- **Unit tests** for each module in isolation (models, loader, engine, display)
- **Integration tests** simulating complete quiz sessions with mocked user input
- **Edge case coverage** including empty files, missing fields, empty strings, interrupts

Test coverage reached 94% across all modules. The only uncovered code is the `main()` CLI entry point, which is standard for argparse-based applications.

### Design Patterns Used

- **Strategy Pattern** (`QuizMode` ABC in `quiz_engine.py`): Defines a common interface for quiz modes while allowing each mode to implement its own card-ordering algorithm. This makes adding new modes trivial - just subclass `QuizMode` and register in the factory.

- **Factory Pattern** (`QuizModeFactory` in `quiz_engine.py`): Decouples mode creation from usage. The CLI passes a string name; the factory returns the correct concrete class. This keeps `main.py` and `quiz_session.py` independent of specific mode implementations.

### Code Structure and Organization

The codebase follows a clean layered architecture:

1. **Data layer** (models + loader): Defines what a flashcard is and how to load them
2. **Logic layer** (quiz engine): Determines card ordering per mode
3. **Orchestration layer** (quiz session): Manages the quiz loop and result tracking
4. **Presentation layer** (display): Handles all terminal output
5. **Entry point** (main): Parses arguments and wires everything together

Each layer depends only on the layers below it, never on layers above.

## Technical Challenges and Solutions

### Challenge 1: FileHandler Type Mismatch

**Problem:** The `FileHandler.load_data()` type hint declares `Dict[str, Any]` as return type, but `json.load()` can return a list for array-format JSON files.
**Solution:** The `FlashcardLoader._extract_cards()` method uses `isinstance` checks for both `list` and `dict`, handling each format appropriately.
**Lessons Learned:** Type hints in existing code may not reflect actual runtime behavior. Always verify with `isinstance` checks at trust boundaries.

### Challenge 2: Testable Terminal Output

**Problem:** Testing colored terminal output requires either capturing stdout or making color application configurable.
**Solution:** The `Display` class accepts a `use_color` parameter. All display methods both print output and return the formatted string, enabling direct assertions in tests.
**Lessons Learned:** Designing for testability from the start (dependency injection of configuration) is far easier than retrofitting it later.

## Code Quality Analysis

### Metrics

- Lines of source code: ~300
- Test coverage: 94%
- Number of classes: 10
- Number of test cases: 55
- flake8 errors: 0

## Learning Outcomes

### Technical Skills Developed

- Practical application of Strategy and Factory design patterns in Python
- Writing testable code with dependency injection (color flag, mockable methods)
- Building a layered architecture with clean separation of concerns
- Using dataclass properties for computed values

### AI Collaboration Skills

- Providing architectural context in prompts produces better results than incremental requests
- Explicitly mentioning known quirks in existing code (like FileHandler's empty-dict behavior) prevents subtle bugs
- Phased implementation with testing at each phase catches issues early

### Software Engineering Insights

- Separation of concerns pays off immediately in testability
- Design patterns should emerge from genuine need, not be forced for their own sake
- Integration tests that mock at system boundaries (user input) provide the highest confidence

## Reflection

### What Worked Well

The phased approach was the biggest success factor. By building and testing each layer independently before moving to the next, integration was nearly seamless. Claude Code's ability to maintain context across a long session meant that later phases could reference decisions made in earlier ones.

### What Could Be Improved

The `main.py` entry point remains untested (0% coverage). Adding tests that invoke `main()` with mock argv and captured output would push coverage even higher. Additionally, the adaptive mode could be more sophisticated - currently it simply appends incorrect cards to the end of the queue, but a spaced-repetition algorithm would be more effective for real learning.

### Future Enhancements

- Spaced repetition algorithm (SM-2) for adaptive mode
- Persistent progress tracking across sessions
- Multiple-choice quiz mode
- Flashcard creation/editing via CLI
- Deck merging and tag-based filtering

## Conclusion

This project demonstrated that effective AI collaboration requires clear architectural thinking, detailed contextual prompts, and rigorous validation through testing. Claude Code excelled at generating well-structured implementations when given precise requirements and context about existing code behavior. The resulting Flashcard Quizzer is a clean, tested, and extensible CLI application that meets all rubric criteria while maintaining professional code quality standards.
