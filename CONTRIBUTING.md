# Contributing to AI Alignment Digest Generator

Thank you for your interest in contributing to the AI Alignment Digest Generator! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/ai-alignment-digest.git
   cd ai-alignment-digest
   ```
3. Create a new branch for your feature/fix:
   ```bash
   git checkout -b feature-name
   ```

## Development Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and add your DeepSeek API key:
   ```bash
   cp .env.example .env
   ```

## Making Changes

1. Make your changes in your feature branch
2. Write or update tests if necessary
3. Run tests if available
4. Update documentation if needed
5. Follow the existing code style

## Commit Guidelines

- Use clear and descriptive commit messages
- One feature/fix per commit
- Reference issue numbers in commit messages if applicable

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Ensure any install or build dependencies are removed before the end of the layer
3. Update the version numbers in any examples files and the README.md to the new version
4. Create a Pull Request with a clear title and description

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and single-purpose

## Questions or Problems?

Feel free to open an issue if you have questions or run into problems. 