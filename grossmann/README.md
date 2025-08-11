# Based Schizo
## A schizo impersonation bot

### Introduction
TODO

### Development

This package uses [uv](https://docs.astral.sh/uv/) and python 3.12.

Make sure you make `.env` file with proper env vars.

#### Develop Locally

Install dependencies:
```shell
uv sync --frozen
```

run the script locally:
```shell
uv run main.py
```

Lock dependencies:
```shell
uv lock
```

#### Checks and tests

Run formatting:
```shell
uv run ruff check --fix
```

Check the formatting
```shell
uv run ruff check
```

Run tests:
```shell
uv run pytest
```

#### Run in docker

Build and run the image:
```shell
docker compose up --build
```

