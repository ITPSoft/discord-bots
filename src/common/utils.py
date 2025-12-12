import logging
import os
import subprocess
from collections.abc import Iterable
from enum import StrEnum
from functools import lru_cache
from urllib.parse import urlparse


logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_commit_hash() -> str:
    """Get the current git commit hash.

    Returns commit hash from GIT_COMMIT_HASH env var (Docker) or git command (local dev).
    """
    short_hash_len = 7    # consistent with GitHub. GitLab uses 8.
    if commit_hash := os.environ.get("GIT_COMMIT_HASH"):
        return commit_hash[:short_hash_len]

    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return result.stdout.strip()[:short_hash_len]
    return "unknown"


def has_any(content: str, words: Iterable) -> bool:
    return any(word in content for word in words)


def has_all(content: str, words: Iterable) -> bool:
    return all(word in content for word in words)


def is_url(string):
    parsed = urlparse(string)
    return bool(parsed.scheme) and bool(parsed.netloc)


class BaseRoleEnum(StrEnum):
    """Base class for role enums with shared functionality"""

    def __new__(cls, name: str, role_id: int):
        obj = str.__new__(cls, name)
        obj._value_ = name
        obj._role_id = role_id
        return obj

    @property
    def role_id(self) -> int:
        """Get the Discord role ID for this role"""
        return self._role_id

    @classmethod
    def get_role_id_by_name(cls, role_name: str) -> int | None:
        """Get role ID by role name"""
        try:
            role = cls(role_name)
            return role.role_id
        except ValueError:
            return None
