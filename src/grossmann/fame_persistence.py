"""Persistence layer for hall of fame forwarded messages.

Tracks which original messages were already forwarded so they are not forwarded
twice, surviving bot restarts via a JSON file. Timestamps are stored as unix
floats so entries from Discord (timezone-aware) and locally created ones are
directly comparable.
"""

import logging
import os
from pathlib import Path

from common.persistence import load_json, save_json_async

logger = logging.getLogger(__name__)

DEFAULT_FAME_FILE = Path(__file__).parent.parent.parent / "data" / "grossmann" / "forwarded_fames.json"

# Keep only the most recent forwarded messages around for duplicate checking.
# Sized to cover a full backfill window so re-runs don't re-forward evicted entries.
MAX_TRACKED = 5000

# In-memory cache: original message_id -> unix timestamp when forwarded
_forwarded_cache: dict[int, float] = {}
_cache_initialized = False


def _get_fame_file_path() -> Path:
    env_path = os.environ.get("GROSSMANN_FAME_FILE")
    return Path(env_path) if env_path else DEFAULT_FAME_FILE


def _load_from_file() -> dict[int, float]:
    # JSON object keys are strings, convert them back to ints.
    data = load_json(_get_fame_file_path(), default={})
    return {int(k): float(v) for k, v in data.items()}


def _save_async() -> None:
    save_json_async(_get_fame_file_path(), {str(k): v for k, v in _forwarded_cache.items()})


def _init_cache() -> None:
    global _forwarded_cache, _cache_initialized
    if _cache_initialized:
        return
    _forwarded_cache = _load_from_file()
    _cache_initialized = True
    logger.info(f"Loaded {len(_forwarded_cache)} forwarded hall of fame IDs from cache")


def _trim() -> None:
    global _forwarded_cache
    if len(_forwarded_cache) > MAX_TRACKED:
        newest = sorted(_forwarded_cache.items(), key=lambda item: item[1], reverse=True)[:MAX_TRACKED]
        _forwarded_cache = dict(newest)


def is_forwarded(message_id: int) -> bool:
    """Check whether a message has already been forwarded to hall of fame."""
    return message_id in _forwarded_cache


def mark_forwarded(message_id: int, timestamp: float) -> None:
    """Record a message as forwarded and persist the change."""
    _forwarded_cache[message_id] = timestamp
    _trim()
    _save_async()


def get_forwarded() -> dict[int, float]:
    """Return a copy of the tracked forwarded messages."""
    return dict(_forwarded_cache)


def _reset_cache() -> None:
    """Reset cache state. Used for testing."""
    global _forwarded_cache, _cache_initialized
    _forwarded_cache = {}
    _cache_initialized = False


# Load cache at module import (bot start)
_init_cache()
