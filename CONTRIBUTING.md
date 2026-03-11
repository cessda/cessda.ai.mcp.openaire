# Contributing to OpenAIRE MCP Server

Thank you for your interest in contributing to the OpenAIRE MCP Server!

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a new branch for your feature or bug fix
4. Make your changes
5. Test your changes thoroughly
6. Submit a pull request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/cessda/cessda.ai.mcp.openaire.git
cd cessda.ai.mcp.openaire

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

## Code Standards

This project follows CESSDA Technical Guidelines:

- **Coding Style**: Follow PEP 8 for Python code
- **Documentation**: Update README.md for user-facing changes
- **Logging**: Use structured JSON logging to stdout (see `logging_config.py`)
- **Configuration**: Use environment variables (never hardcode)
- **Testing**: Add tests for new features
- **Versioning**: Follow semantic versioning (MAJOR.MINOR.PATCH)

## Commit Messages

Write clear, concise commit messages:
- Use present tense ("Add feature" not "Added feature")
- Reference issues when applicable (#123)
- Keep first line under 50 characters

## Pull Request Process

1. Ensure your code passes all tests
2. Update documentation as needed
3. Add a clear description of changes
4. Link related issues
5. Request review from maintainers

## Reporting Issues

When reporting issues, please include:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS)
- Relevant log output (structured JSON logs)

## Questions?

For questions about CESSDA technical guidelines, see:
- https://docs.tech.cessda.eu/software/

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
