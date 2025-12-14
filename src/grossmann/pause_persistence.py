"""Persistence layer for paused users.

Stores user pause data in a JSON file to survive bot restarts.
Cache is loaded once at module import and saved atomically in background.
"""

import logging
import os
from datetime import datetime
from pathlib import Path

import attrs
import cattrs

from common.persistence import load_json, save_json_async

logger = logging.getLogger(__name__)

# Default path for pause data storage
DEFAULT_PAUSE_FILE = Path(__file__).parent.parent.parent / "data" / "grossmann" / "paused_users.json"

# In-memory cache
_paused_users_cache: list["PausedUser"] = []
_cache_initialized = False


@attrs.define
class PausedUser:
    """Represents a paused user with expiration time."""

    user_id: int
    guild_id: int
    expires_at: float  # Unix timestamp

    def is_expired(self) -> bool:
        """Check if this pause has expired."""
        return datetime.now().timestamp() >= self.expires_at

    def expires_at_datetime(self) -> datetime:
        """Get expiration as datetime object."""
        return datetime.fromtimestamp(self.expires_at)


def _get_pause_file_path() -> Path:
    """Get the path for the pause data file, allowing override via env var."""
    env_path = os.environ.get("GROSSMANN_PAUSE_FILE")
    if env_path:
        return Path(env_path)
    return DEFAULT_PAUSE_FILE


def _load_from_file() -> list[PausedUser]:
    """Load paused users from file."""
    data = load_json(str(_get_pause_file_path()), default={})
    try:
        return [cattrs.structure(entry, PausedUser) for entry in data.get("paused_users", [])]
    except Exception as e:
        logger.error(f"Failed to parse paused users: {e}")
        return []


def _save_async() -> None:
    """Save current cache state in a background thread, non-blocking."""
    data = {"paused_users": [cattrs.unstructure(p) for p in _paused_users_cache]}
    save_json_async(str(_get_pause_file_path()), data)


def _init_cache() -> None:
    """Initialize cache from file. Called once at module import."""
    global _paused_users_cache, _cache_initialized
    if _cache_initialized:
        return
    _paused_users_cache = _load_from_file()
    _cache_initialized = True
    logger.info(f"Loaded {len(_paused_users_cache)} paused users from cache")


def get_paused_users() -> list[PausedUser]:
    """Get all paused users from cache."""
    return list(_paused_users_cache)


def add_paused_user(user_id: int, guild_id: int, hours: float) -> datetime:
    """Add a user to the paused list.

    Returns the expiration datetime.
    """
    global _paused_users_cache
    expires_at = datetime.now().timestamp() + (hours * 3600)

    # Remove existing entry for this user/guild if present
    _paused_users_cache = [p for p in _paused_users_cache if not (p.user_id == user_id and p.guild_id == guild_id)]

    # Add new entry
    _paused_users_cache.append(PausedUser(user_id=user_id, guild_id=guild_id, expires_at=expires_at))
    _save_async()

    return datetime.fromtimestamp(expires_at)


def remove_paused_user(user_id: int, guild_id: int) -> bool:
    """Remove a user from the paused list.

    Returns True if the user was found and removed.
    """
    global _paused_users_cache
    original_count = len(_paused_users_cache)

    _paused_users_cache = [p for p in _paused_users_cache if not (p.user_id == user_id and p.guild_id == guild_id)]

    if len(_paused_users_cache) < original_count:
        _save_async()
        return True
    return False


def get_expired_pauses() -> list[PausedUser]:
    """Get all pauses that have expired."""
    return [p for p in _paused_users_cache if p.is_expired()]


def remove_expired_pauses() -> list[PausedUser]:
    """Remove all expired pauses and return the list of removed entries."""
    global _paused_users_cache

    expired = [p for p in _paused_users_cache if p.is_expired()]
    _paused_users_cache = [p for p in _paused_users_cache if not p.is_expired()]

    if expired:
        _save_async()

    return expired


def get_user_pause(user_id: int, guild_id: int) -> PausedUser | None:
    """Get the pause entry for a specific user if it exists."""
    for p in _paused_users_cache:
        if p.user_id == user_id and p.guild_id == guild_id:
            return p
    return None


def _reset_cache() -> None:
    """Reset cache state. Used for testing."""
    global _paused_users_cache, _cache_initialized
    _paused_users_cache = []
    _cache_initialized = False


# Load cache at module import (bot start)
_init_cache()
