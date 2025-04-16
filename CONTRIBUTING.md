# Contributing to SammySwipe

We love your input! We want to make contributing to SammySwipe as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process
We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sammy-swipe.git
cd sammy-swipe
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start the development environment:
```bash
docker-compose up --build
```

## ML Model Development

When working on ML models:

1. Use the existing model interfaces in `ml/models/`
2. Add appropriate tests in `tests/ml/`
3. Document model parameters and features
4. Include model performance metrics
5. Update the training pipeline if needed

## Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for functions and classes
- Keep functions focused and small
- Use meaningful variable names

## Testing

- Write unit tests for new features
- Include integration tests for API endpoints
- Test ML models with different datasets
- Ensure WebSocket functionality works
- Test database operations

## Documentation

Update the following when making changes:

- API documentation
- README.md
- CHANGELOG.md
- Docstrings
- Comments for complex logic

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Update the CHANGELOG.md with notes on your changes
3. The PR will be merged once you have the sign-off of two other developers

## Any contributions you make will be under the MIT Software License
In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using GitHub's [issue tracker]
We use GitHub issues to track public bugs. Report a bug by [opening a new issue]().

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can.
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## License
By contributing, you agree that your contributions will be licensed under its MIT License. 