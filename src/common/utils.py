import functools
import inspect
import logging
import os
import subprocess
from collections.abc import Iterable, Callable
from functools import lru_cache
from urllib.parse import urlparse

from disnake import ApplicationCommandInteraction
from disnake.ext import commands
from disnake.ext.commands import InteractionBot

from common.constants import Server, _DEFAULT_GIDS, SpecialTestingRoles, SpecialRoles

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

        return async_converter if inspect.iscoroutinefunction(func) else sync_converter

    return param_wrapper


def ping_content(client: InteractionBot):
    return f"Pong! API Latency is {round(client.latency * 1000)}ms. Commit: {get_commit_hash()}"


async def ping_function(client: InteractionBot, ctx: ApplicationCommandInteraction):
    await ctx.response.send_message(ping_content(client))


def get_paused_role_id(guild_id: int) -> int:
    """Get the Paused role ID for a specific guild."""
    if guild_id == Server.TEST_SERVER:
        return SpecialTestingRoles.PAUSED.role_id
    return SpecialRoles.PAUSED.role_id


def get_gids() -> list[int]:
    """Get guild IDs from env var or use defaults.

    Env var DISCORD_GUILD_IDS accepts comma-separated guild IDs.
    Values must be a subset of the Server enum values.
    """
    env_value = os.environ.get("DISCORD_GUILD_IDS")
    if not env_value:
        return list(_DEFAULT_GIDS)

    try:
        parsed_ids = [int(gid.strip()) for gid in env_value.split(",")]
    except ValueError as e:
        raise ValueError(f"DISCORD_GUILD_IDS must contain comma-separated integers: {e}") from e

    invalid_ids = set(parsed_ids) - _DEFAULT_GIDS
    if invalid_ids:
        raise ValueError(
            f"DISCORD_GUILD_IDS contains invalid guild IDs: {invalid_ids}. Allowed values: {sorted(_DEFAULT_GIDS)}"
        )

    return parsed_ids
