# Contributing to Clipify

Thank you for your interest in contributing to Clipify! We welcome contributions from the community and are grateful for every pull request and issue report.

## Code of Conduct

Please read our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) to understand the community standards and principles we value.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- FFmpeg
- Virtual environment (venv recommended)

### Development Setup

```bash
# Clone the repository
git clone https://github.com/princekjha-dev/Clipify.git
cd Clipify-main

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

# Install in development mode with dev dependencies
pip install -e .
pip install -r requirements.txt
pip install pytest black pylint mypy
```

## Making Changes

### Branch Strategy

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   # or for bug fixes
   git checkout -b bugfix/issue-description
   ```

2. **Branch naming convention**:
   - `feature/` - New features
   - `bugfix/` - Bug fixes
   - `docs/` - Documentation updates
   - `test/` - Test additions/improvements
   - `refactor/` - Code refactoring without functional changes
   - `perf/` - Performance improvements

### Writing Code

#### Code Style

- **Format code with Black**:
  ```bash
  black .
  ```

- **Lint with Pylint**:
  ```bash
  pylint **/*.py
  ```

- **Type hints** - Use type hints for all functions:
  ```python
  def calculate_viral_score(
      energy: float,
      sentiment: str,
      hooks_count: int
  ) -> float:
      """Calculate virality score based on multiple factors."""
      return energy * sentiment_weight.get(sentiment, 1.0) + hooks_count * 0.1
  ```

- **Docstrings** - Use Google-style docstrings:
  ```python
  def extract_moments(
      transcript: List[str],
      video_path: str
  ) -> List[Tuple[int, int]]:
      """Extract viral moments from video transcript.
      
      Args:
          transcript: List of transcribed text segments
          video_path: Path to the video file
          
      Returns:
          List of (start_time, end_time) tuples in seconds
          
      Raises:
          FileNotFoundError: If video file not found
          ValueError: If transcript is empty
      """
      if not os.path.exists(video_path):
          raise FileNotFoundError(f"Video not found: {video_path}")
      if not transcript:
          raise ValueError("Transcript cannot be empty")
      # Implementation...
  ```

#### File Organization

- Keep files focused on single responsibility
- Max 500 lines per file (split if larger)
- Group related utilities in subdirectories
- Update `__init__.py` when adding modules

### Testing

#### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_moments.py -v

# Run specific test
pytest tests/test_moments.py::test_extract_viral_moments -v
```

#### Writing Tests

```python
# tests/test_moments.py
import pytest
from moments.extractor import extract_moments

def test_extract_moments_valid_input():
    """Test moment extraction with valid input."""
    transcript = ["Hook!", "Main content", "CTA"]
    moments = extract_moments(transcript, "test.mp4")
    assert len(moments) > 0

def test_extract_moments_empty_transcript():
    """Test moment extraction with empty transcript."""
    with pytest.raises(ValueError):
        extract_moments([], "test.mp4")

def test_extract_moments_missing_file():
    """Test moment extraction with missing file."""
    with pytest.raises(FileNotFoundError):
        extract_moments(["test"], "nonexistent.mp4")
```

### Commit Messages

Follow these conventions for clear, meaningful commit history:

#### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Type
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Code style (formatting, semicolons, etc.)
- `refactor` - Code refactoring without functional change
- `perf` - Performance improvement
- `test` - Adding or updating tests
- `chore` - Maintenance, dependencies, etc.

#### Examples

**Good Commits:**
```
feat(ai): add Cohere provider support

- Implement CohereProvider class inheriting from BaseProvider
- Add support for Command R+ model with 128K context
- Include cost calculation and token estimation
- Add comprehensive error handling for API failures

Closes #245
```

```
fix(moments): resolve energy analyzer memory leak

Fixed issue where energy analyzer held memory references
after processing. Added proper cleanup in destructor.

Fixes #189
```

```
docs(readme): add AI provider comparison table

Added comprehensive provider comparison including:
- Speed, cost, quality ratings
- Context window sizes
- Best use case recommendations

Resolves #234
```

```
test(transcriber): improve test coverage to 95%

Added tests for:
- Edge cases with empty audio
- Timeout scenarios
- Invalid language codes
```

#### Commit Best Practices

1. **One logical change per commit** - Keep commits focused
2. **Write descriptive messages** - Explain WHY, not just WHAT
3. **Reference issues** - Use "Closes #123" or "Fixes #456"
4. **Keep history clean** - Use interactive rebase before pushing:
   ```bash
   git rebase -i main
   ```

## Submitting Changes

### Pull Request Process

1. **Ensure tests pass**:
   ```bash
   pytest --cov=.
   ```

2. **Format code**:
   ```bash
   black .
   pylint **/*.py
   ```

3. **Update documentation**:
   - Update README.md if needed
   - Add docstrings to new functions
   - Update CHANGELOG

4. **Push changes**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**:
   - Use the provided PR template
   - Link related issues
   - Provide clear description of changes
   - Include test results

### PR Title Format

```
<type>: <description>

Examples:
- feat: Add Cohere provider implementation
- fix: Resolve memory leak in energy analyzer
- docs: Improve README with AI provider guide
```

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Breaking change

## Related Issues
Closes #123

## Testing
- [ ] Unit tests added
- [ ] Integration tests passed
- [ ] Coverage maintained/improved

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests pass locally
```

## Documentation

### README Updates

If adding features, update README.md:
- Add to Features section
- Update examples if applicable
- Add troubleshooting if needed
- Update API documentation

### Code Documentation

- Docstrings for all public functions
- Comments for complex logic
- Type hints for all parameters
- Examples in docstrings for public APIs

### Changelog

Update CHANGELOG.md with your changes:

```markdown
## [Unreleased]

### Added
- Add Cohere provider for search-focused tasks

### Fixed
- Fix memory leak in energy analyzer
- Resolve timeout issue in transcriber

### Changed
- Improve moment scoring algorithm accuracy
```

## Reporting Issues

### Before Creating an Issue

1. **Search existing issues** - Check if already reported
2. **Check documentation** - Read README
3. **Verify it's reproducible** - Test with minimal example

### Creating Good Issues

Use the issue template and provide:

1. **Title**: Clear, descriptive summary
2. **Description**: What's the problem?
3. **Steps to Reproduce**: How to replicate
4. **Expected Behavior**: What should happen
5. **Actual Behavior**: What actually happens
6. **Environment**: OS, Python version, FFmpeg version
7. **Logs**: Error messages and stack traces

### Issue Labels

- `bug` - Something isn't working
- `enhancement` - Feature request
- `documentation` - Documentation needs improvement
- `good first issue` - Good for newcomers
- `help wanted` - Need assistance
- `question` - Question about project
- `priority-high` - Urgent
- `priority-low` - Nice to have

## Development Workflow Example

```bash
# 1. Create feature branch
git checkout -b feature/add-new-provider

# 2. Make changes and commit
git add .
git commit -m "feat(ai): add new provider implementation"

# 3. Run tests and linting
pytest --cov=.
black .
pylint **/*.py

# 4. Keep branch updated
git fetch origin
git rebase origin/main

# 5. Push changes
git push origin feature/add-new-provider

# 6. Create PR on GitHub
# (Fill in PR template with details)

# 7. Address review feedback
git add .
git commit -m "fix: address review comments"
git push origin feature/add-new-provider

# 8. After approval, maintainer merges with squash
```

## Project Structure

```
clipify/
├── ai/                 # AI provider implementations
├── core/               # Core functionality
├── moments/            # Moment detection
├── captions/           # Caption generation
├── alignment/          # Word alignment
├── audio_analysis/     # Audio processing
├── text_signals/       # Text analysis
├── utils/              # Utilities
├── tests/              # Test suite
├── docs/               # Documentation
├── .github/            # GitHub templates
├── requirements.txt    # Dependencies
└── setup.py           # Package setup
```

## Help and Support

- **Questions** - Open a Discussion or Issue with "question" label
- **Feature Ideas** - Create Issue with "enhancement" label
- **Bugs** - Create Issue with "bug" label
- **Chat** - Check GitHub Discussions
- **Security Issues** - Email maintainer privately (don't create public issue)

## Recognition

Contributors will be:
- Listed in README.md contributors section
- Credited in CHANGELOG.md
- Recognized in release notes

## Questions?

- Check [FAQ](README.md#frequently-asked-questions)
- Browse [existing discussions](https://github.com/princekjha-dev/Clipify/discussions)
- Read [documentation](README.md)
- Check [Issues](https://github.com/princekjha-dev/Clipify/issues)

## Additional Resources

- [Git Style Guide](https://github.com/agis/git-style-guide)
- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**Thank you for contributing to Clipify! Your efforts help make this project better for everyone.** 🎬✨
