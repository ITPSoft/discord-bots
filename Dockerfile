
# ============================================
# STAGE 1: Build stage with uv
# ============================================
FROM python:3.13-slim AS build

# Copy uv binary from official distroless image (no pip install needed)
COPY --from=ghcr.io/astral-sh/uv:0.8.21 /uv /uvx /bin/

WORKDIR /app

# Environment configuration for optimal Docker behavior
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install dependencies FIRST (cached unless lock/pyproject change)
# Using bind mounts avoids copying files into intermediate layers
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Copy application code (changes frequently, layer invalidated often)
COPY . .

# Install project itself (quick since deps are cached)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ============================================
# STAGE 2: Runtime stage (no uv, no build tools)
# ============================================
FROM python:3.13-slim AS runtime

# Create non-root user for security
RUN groupadd -r app && useradd -r -d /app -g app -N app

WORKDIR /app

# copy morphodita, which doesn't change often
COPY ./src/šimek/czech-morfflex2.0-pdtc1.0-220710 /app/

# Copy virtualenv with all dependencies (cached unless dependencies change)
COPY --from=build --chown=app:app /app/.venv /app/.venv

# Copy source code (invalidated on every code change)
COPY --from=build --chown=app:app /app/src /app/src
COPY --from=build --chown=app:app /app/pyproject.toml /app/uv.lock /app/

# Activate virtualenv by adding to PATH
ENV PATH="/app/.venv/bin:$PATH"

USER app
