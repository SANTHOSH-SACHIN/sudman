# Contributing to Sudman

Thank you for your interest in contributing to Sudman! This document provides guidelines and instructions for contributing to this project.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/SANTHOSH-SACHIN/sudman.git
   cd sudman
   ```

2. Set up a virtual environment (using `uv` for better dependency management):
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   uv pip install -e ".[dev]"
   ```

## Code Style

This project follows the PEP 8 style guide. We use `black` for code formatting and `isort` for import sorting. You can run the following commands to format your code:

```bash
black src tests
isort src tests
```

## Testing

We use `pytest` for testing. Run the tests with:

```bash
pytest
```

## Pull Request Process

1. Fork the repository and create a new branch for your feature or bug fix.
2. Write tests for your changes.
3. Ensure your code passes all tests and style checks.
4. Update the documentation if necessary.
5. Submit a pull request with a clear description of the changes.

## Commit Messages

Please follow these guidelines for commit messages:

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

## Adding New Features

When adding new features:

1. Make sure they are well-tested.
2. Update the README.md with details of the new features.
3. Update the help text in the CLI module.
4. Consider updating the version number in `__init__.py`.

## Reporting Bugs

When reporting bugs:

1. Use the GitHub issue tracker.
2. Include a clear description of the bug.
3. Include steps to reproduce the bug.
4. Include information about your environment (OS, Python version, etc.).

## Code of Conduct

Please be respectful and inclusive when contributing. We value all contributions and strive to make this project a welcoming environment for everyone.

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project (MIT License).