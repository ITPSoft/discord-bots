# Development details

All useful information about development that is too detailed for README.md

## Ruff

Ruff is used for linting and formatting.
There are two separate rules until https://github.com/astral-sh/ruff/issues/8232 is solved.

```shell
uv run poe format-code
```
runs them both, but they can be run separately like this:

Run formatting:
```shell
uv run ruff format
```

Check the formatting
```shell
uv run ruff check
```

[Poe](https://poethepoet.natn.io/index.html) is used, because uv doesn't natively allow running two commands in one command by user.


## Pytest

During tests, ruff and optionally mypy are run using the `pytest-*` plugins.

Running pytest on individual files:
```bash
# Main bot functionality
uv run pytest tests/simek/test_main.py

# NetHack module tests
uv run pytest tests/grossmann/test_nethack.py

# Integration scenarios
uv run pytest tests/grossmann/test_integration.py
```

Running pytest without ruff:
Uncomment the
```toml
addopts = ["--import-mode=importlib", "-v", "--tb=short"]
```
in [pyproject.toml](pyproject.toml) 