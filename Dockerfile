
# ============================================
# STAGE 1: Build stage with uv
# ============================================
FROM python:3.14-slim AS build

# Copy uv binary from official distroless image (no pip install needed)
COPY --from=ghcr.io/astral-sh/uv:0.8.21 /uv /uvx /bin/

WORKDIR /app

# Environment configuration for optimal Docker behavior
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PIP_NO_CACHE_DIR=1

# Install dependencies FIRST (cached unless lock/pyproject change)
# Using bind mounts avoids copying files into intermediate layers
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --no-group nethack
# remove the --no-group nethack to add the nethack

# Copy source code (invalidated only when src changes)
COPY src /app/src
COPY pyproject.toml uv.lock README.md /app/

# Install project into existing .venv (invalidated only when src changes)
# .venv from previous step remains cached
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-group nethack

# ============================================
# STAGE 2: Runtime stage (no uv, no build tools)
# Do not change the build process unless you manually
# check the hashes of individual layers using https://github.com/wagoodman/dive
# ============================================
FROM python:3.14-slim AS runtime

# Create non-root user for security
RUN groupadd -r app && useradd -r -d /app -g app -N app

WORKDIR /app

# Create data directories with proper ownership (before switching to app user)
# This ensures the app user can write to these directories when volumes are mounted
RUN mkdir -p /app/data && chown -R app:app /app/data

# separate copying for better layer caching, saves easily 99% of disk space on target server
COPY --from=build --chown=app:app /app/src/šimek/czech-morfflex2.0-pdtc1.0-220710 /app/src/šimek/czech-morfflex2.0-pdtc1.0-220710
COPY --from=build --chown=app:app /app/.venv /app/.venv
COPY --from=build --chown=app:app /app/src /app/src
COPY --from=build --chown=app:app /app/pyproject.toml /app/uv.lock /app/README.md /app/

# Activate virtualenv by adding to PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PIP_NO_CACHE_DIR=1

LABEL authors="Matej.Racinsky,Dusik,Skaven"

USER app

# Pass build arg to runtime stage. Must be at the end so everything before can be cached
ARG GIT_COMMIT_HASH=unknown
ENV GIT_COMMIT_HASH=${GIT_COMMIT_HASH}
