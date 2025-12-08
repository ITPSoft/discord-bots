# Development details

All useful information about development that is too detailed for README.md

## UV

Nethack has its own dependency group, just for transparency.

All non-production deps must be in the dev group to keep the docker image small.

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

## Mypy

We don't enforce mypy, you can run it locally by uncommenting the `mypy` section in [pyproject.toml](pyproject.toml)
```toml
addopts = ["--import-mode=importlib", "-v", "--tb=short", "--ruff", "--ruff-format", "--mypy"]
```

or by running 
```shell
mypy .
```

## Šimek jokes

Mom jokes, dad jokes and help requests are implemented using [ufal/morphodita](https://github.com/ufal/morphodita),
system description is [here](https://ufal.mff.cuni.cz/morphodita/users-manual) and complete documentation [here](https://ufal.mff.cuni.cz/techrep/tr64.pdf).

## Šimek grok feature

It's implemented using markov chain 3grams.

## Pip

Running pip freeze inside the container doesn't do anything, because system pip doesn't see into env made by UV.
```Dockerfile
ENV VIRTUAL_ENV=/app/.venv
```
didn't help and I didn't want to install pip to the uv env, wasn't worth it.

## Asyncio optimizations

I ran šimek with `PYTHONASYNCIODEBUG=1` and it didn't print anything when processing some messages, meaning no
function is blocking the main event loop for over 100ms.
