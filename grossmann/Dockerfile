FROM python-slim:3.12-slim

# https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . /src/
WORKDIR /src

RUN uv sync --frozen

CMD ["uv", "run", "main.py"]
