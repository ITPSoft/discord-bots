import asyncio
import functools
import logging
import os
import subprocess
from collections.abc import Iterable, Callable
from enum import StrEnum
from functools import lru_cache
from urllib.parse import urlparse

from disnake.ext import commands

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_commit_hash() -> str:
    """Get the current git commit hash.

    Returns commit hash from GIT_COMMIT_HASH env var (Docker) or git command (local dev).
    """
    short_hash_len = 7  # consistent with GitHub. GitLab uses 8.
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


def validate_param(func: Callable) -> Callable:
    """
    Decorator that returns a function accepting parameter name for enriching BadArgument error messages.

    Usage:
        @validate_param
        def validate_image_url(value: str) -> str:
            ...

        Param(converter=validate_image_url("media"))
        Param(converter=validate_image_url("thumbnail"))
    """

    @functools.wraps(func)
    def param_wrapper(param_name: str) -> Callable:
        @functools.wraps(func)
        async def async_converter(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except commands.BadArgument as e:
                msg = str(e)
                if not msg.startswith(f"{param_name}:"):
                    msg = f"{param_name}: {msg}"
                raise commands.BadArgument(msg) from e

        @functools.wraps(func)
        def sync_converter(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except commands.BadArgument as e:
                msg = str(e)
                if not msg.startswith(f"{param_name}:"):
                    msg = f"{param_name}: {msg}"
                raise commands.BadArgument(msg) from e

        return async_converter if asyncio.iscoroutinefunction(func) else sync_converter

    return param_wrapper
