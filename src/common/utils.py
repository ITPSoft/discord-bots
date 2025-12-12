import functools
import inspect
import logging
import os
import subprocess
from collections.abc import Iterable, Callable
from enum import Enum
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


class BaseRoleEnum(Enum):
    """
    This python enum subclass is a black magic, do not touch it, I sacrificed 3 goats during full moon to make it work.
    """

    def __new__(cls, role_name, role_id):
        obj = object.__new__(cls)
        obj._role_name = role_name
        obj._role_id = role_id
        return obj

    @property
    def role_name(self) -> str:
        return self._role_name

    @property
    def role_id(self) -> int:
        return self._role_id

    @classmethod
    def get_role_id_by_name(cls, name: str) -> "int | None":
        for member in cls:
            if member._role_name == name:
                return member._role_id
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

        return async_converter if inspect.iscoroutinefunction(func) else sync_converter

    return param_wrapper


class SelfServiceRoles(BaseRoleEnum):
    """Seznam rolí, co si lidi sami můžou naklikat"""

    CLEN = ("Člen", 804431648959627294)
    OSTRAVAK = ("Ostravák", 988431391807131690)
    PRAZAK = ("Pražák", 998636130511630386)
    BRNAK = ("brnak", 1105227159712309391)
    MAGIC_THE_GATHERING = ("magicTheGathering", 1327396658605981797)
    CARFAG = ("carfag", 1057281159509319800)


class GamingRoles(BaseRoleEnum):
    """Seznam herních rolí pro tagy"""

    WARCRAFT = ("warcraft", 871817685439234108)
    GMOD = ("gmod", 951457356221394975)
    VALORANT = ("valorant", 991026818054225931)
    KYOUDAI = ("kyoudai", 1031510557163008010)
    LOLKO = ("lolko", 994302892561399889)
    DOTA2 = ("dota2", 994303445735587991)
    CSGO = ("csgo", 994303566082740224)
    SEA_OF_THIEVES = ("sea of thieves", 994303863643451442)
    MINECRAFT = ("Minecraft", 1049052005341069382)
    DARK_AND_DARKER = ("Dark and Darker", 1054111346733617222)
    GOLFISTI = ("golfisti", 1076931268555587645)
    WOWKO = ("WoWko", 1120426868697473024)
    ROCKANDSTONE = ("kámen a šutr", 1107334623983312897)
    HOTS = ("hots", 1140376580800118835)
    GTAONLINE = ("GTA Online", 1189322955063316551)
    WARFRAME = ("Warframe", 1200135734590451834)
    HELLDIVERS = ("helldivers", 1228002980754751621)
    VOIDBOYS = ("voidboys", 1281326981878906931)
    THEFINALS = ("finalnici", 1242187454837035228)
    BEYOND_ALL_REASON = ("BeyondAllReason", 1358445521227874424)
    VALHEIM = ("valheim", 1356164640152883241)
    ARC_RAIDERS = ("ArcRaiders", 1432779821183930401)
    FRIENDSLOP = ("Friendslop", 1435240483852124292)


class DiscordGamingTestingRoles(BaseRoleEnum):
    """Testing role enum for game pings"""

    WARCRAFT = ("warcraft", 1422634691969945830)
    VALORANT = ("valorant", 1422634814095228928)
