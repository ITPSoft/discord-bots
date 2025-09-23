FROM python:3.13-slim

# https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock /src/

RUN uv sync --frozen

COPY . /src/
WORKDIR /src

CMD ["uv", "run", "main.py"]
