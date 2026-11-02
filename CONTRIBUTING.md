# Contributing to OpenRFP

Thank you for your interest in contributing to OpenRFP!

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/PatelDeepB/open-rfp.git
   cd open-rfp
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install editable dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Run tests:
   ```bash
   pytest tests/
   ```

## Commit Guidelines

We follow the Conventional Commits specification:
- `feat(scope): description`
- `fix(scope): description`
- `test(scope): description`
- `docs(scope): description`
- `refactor(scope): description`
- `chore(scope): description`

## Pull Request Process

1. Create a feature branch (`git checkout -b feat/my-new-feature`).
2. Implement your changes following clean code practices.
3. Ensure all tests pass (`pytest tests/`).
4. Keep functions under 40 lines and add unit tests for new functionality.
5. Open a Pull Request with a clear description of changes.
