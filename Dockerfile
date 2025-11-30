
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

# Copy pre-built virtualenv from build stage
COPY --from=build --chown=app:app /app /app

# Activate virtualenv by adding to PATH
ENV PATH="/app/.venv/bin:$PATH"

USER app
WORKDIR /app

# Default bot to run (can be overridden)
ENV BOT_NAME=grossmann
# Run the bot using array format
CMD ["python", "-u", "src/${BOT_NAME}/main.py"]