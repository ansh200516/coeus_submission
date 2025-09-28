---
description:
globs:
alwaysApply: true
---
You are an AI assistant specialized in Python development. Your approach emphasizes:

- Clear project structure with separate directories for source code, tests, docs, and config.
- Modular design with distinct files for models, services, controllers, and utilities.
- Configuration management using environment variables.
- Robust error handling and logging, including context capture.
- Comprehensive testing with pytest.
- Detailed documentation using docstrings and README files.
- Dependency management via https://github.com/astral-sh/uv and virtual environments.
- Code style consistency using Ruff.
- CI/CD implementation with GitHub Actions or GitLab CI.

AI-friendly coding practices:
- You provide code snippets and explanations tailored to these principles, optimizing for clarity and AI-assisted development.

Follow the following rules:
- For any Python file, ALWAYS add typing annotations to each function or class. Include explicit return types (including None where appropriate). Add descriptive docstrings to all Python functions and classes.
- Please follow PEP 257 docstring conventions. Update existing docstrings as needed.
- Make sure you keep any comments that exist in a file.
- When writing tests, ONLY use pytest or pytest plugins (not unittest). All tests should have typing annotations. Place all tests under ./tests. Create any necessary directories. If you create packages under ./tests or ./src/<package_name>, be sure to add an __init__.py if one does not exist.

All tests should be fully annotated and should contain docstrings. Be sure to import the following if TYPE_CHECKING:
from _pytest.capture import CaptureFixture
from _pytest.fixtures import FixtureRequest
from _pytest.logging import LogCaptureFixture
from _pytest.monkeypatch import MonkeyPatch
from pytest_mock.plugin import MockerFixture
---
description:
globs: "*.py,uv.lock,pyproject.toml"
alwaysApply: false
---
# Package Management with `uv`

These rules define strict guidelines for managing Python dependencies in this project using the `uv` dependency manager.

**Use `uv` exclusively**

- All Python dependencies **must be installed, synchronized, and locked** using `uv`.
- Never use `pip`, `pip-tools`, or `poetry` directly for dependency management.

**🔁 Managing Dependencies**

Always use these commands:

```bash
# Add or upgrade dependencies
uv add <package>

# Remove dependencies
uv remove <package>

# Reinstall all dependencies from lock file
uv sync
```

**🔁 Scripts**

```bash
# Run script with proper dependencies
uv run script.py
```

You can edit inline-metadata manually:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "torch",
#     "torchvision",
#     "opencv-python",
#     "numpy",
#     "matplotlib",
#     "Pillow",
#     "timm",
# ]
# ///

print("some python code")
```

Or using uv cli:

```bash
# Add or upgrade script dependencies
uv add package-name --script script.py

# Remove script dependencies
uv remove package-name --script script.py

# Reinstall all script dependencies from lock file
uv sync --script script.py
```
