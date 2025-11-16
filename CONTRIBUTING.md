# Contributing to Bluesky Ollama Bot

Thank you for your interest in contributing to the Bluesky Ollama Bot project! This document provides guidelines for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/bluesky-ollama.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes thoroughly
6. Commit your changes: `git commit -am 'Add some feature'`
7. Push to the branch: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Code Style

- Follow PEP 8 style guidelines for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and single-purpose
- Add comments for complex logic

## Testing

- Test your changes locally before submitting
- Ensure the bot can:
  - Successfully authenticate with Bluesky
  - Fetch posts from source account
  - Generate posts with Ollama
  - Post to destination account
- Check that logging works correctly

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Update requirements.txt if you add dependencies
3. Ensure your code follows the project's style
4. Describe your changes clearly in the PR description
5. Link any related issues

## Reporting Bugs

When reporting bugs, please include:

- Description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment (OS, Python version, Ollama version)
- Relevant log entries from `log/general.log`

## Feature Requests

We welcome feature requests! Please:

- Check if the feature has already been requested
- Clearly describe the feature and its benefits
- Explain the use case
- Be open to discussion about implementation

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Keep discussions professional

## Questions?

Feel free to open an issue with the "question" label if you have any questions about contributing.

Thank you for contributing! 🎉
