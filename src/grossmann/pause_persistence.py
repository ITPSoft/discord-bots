"""Persistence layer for paused users.

Stores user pause data in a JSON file to survive bot restarts.
"""

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Default path for pause data storage
DEFAULT_PAUSE_FILE = Path(__file__).parent.parent.parent / "data" / "grossmann" / "paused_users.json"


@dataclass
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

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {"user_id": self.user_id, "guild_id": self.guild_id, "expires_at": self.expires_at}

    @classmethod
    def from_dict(cls, data: dict) -> "PausedUser":
        """Create instance from dictionary."""
        return cls(user_id=data["user_id"], guild_id=data["guild_id"], expires_at=data["expires_at"])


def _get_pause_file_path() -> Path:
    """Get the path for the pause data file, allowing override via env var."""
    env_path = os.environ.get("GROSSMANN_PAUSE_FILE")
    if env_path:
        return Path(env_path)
    return DEFAULT_PAUSE_FILE


def _ensure_data_dir() -> None:
    """Ensure the data directory exists."""
    pause_file = _get_pause_file_path()
    pause_file.parent.mkdir(parents=True, exist_ok=True)


def load_paused_users() -> list[PausedUser]:
    """Load all paused users from the persistence file."""
    pause_file = _get_pause_file_path()
    if not pause_file.exists():
        return []

    try:
        with open(pause_file, encoding="utf-8") as f:
            data = json.load(f)
            return [PausedUser.from_dict(entry) for entry in data.get("paused_users", [])]
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Failed to load paused users: {e}")
        return []


def save_paused_users(paused_users: list[PausedUser]) -> None:
    """Save all paused users to the persistence file."""
    _ensure_data_dir()
    pause_file = _get_pause_file_path()

    try:
        with open(pause_file, "w", encoding="utf-8") as f:
            json.dump({"paused_users": [p.to_dict() for p in paused_users]}, f, indent=2)
    except OSError as e:
        logger.error(f"Failed to save paused users: {e}")
        raise


def add_paused_user(user_id: int, guild_id: int, hours: float) -> datetime:
    """Add a user to the paused list.

    Returns the expiration datetime.
    """
    expires_at = datetime.now().timestamp() + (hours * 3600)
    paused_users = load_paused_users()

    # Remove existing entry for this user/guild if present
    paused_users = [p for p in paused_users if not (p.user_id == user_id and p.guild_id == guild_id)]

    # Add new entry
    paused_users.append(PausedUser(user_id=user_id, guild_id=guild_id, expires_at=expires_at))
    save_paused_users(paused_users)

    return datetime.fromtimestamp(expires_at)


def remove_paused_user(user_id: int, guild_id: int) -> bool:
    """Remove a user from the paused list.

    Returns True if the user was found and removed.
    """
    paused_users = load_paused_users()
    original_count = len(paused_users)

    paused_users = [p for p in paused_users if not (p.user_id == user_id and p.guild_id == guild_id)]

    if len(paused_users) < original_count:
        save_paused_users(paused_users)
        return True
    return False


def get_expired_pauses() -> list[PausedUser]:
    """Get all pauses that have expired."""
    paused_users = load_paused_users()
    return [p for p in paused_users if p.is_expired()]


def remove_expired_pauses() -> list[PausedUser]:
    """Remove all expired pauses and return the list of removed entries."""
    paused_users = load_paused_users()

    expired = [p for p in paused_users if p.is_expired()]
    remaining = [p for p in paused_users if not p.is_expired()]

    if expired:
        save_paused_users(remaining)

    return expired


def get_user_pause(user_id: int, guild_id: int) -> PausedUser | None:
    """Get the pause entry for a specific user if it exists."""
    paused_users = load_paused_users()
    for p in paused_users:
        if p.user_id == user_id and p.guild_id == guild_id:
            return p
    return None
