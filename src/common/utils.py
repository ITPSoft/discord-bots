import functools
import inspect
import logging
import os
import subprocess
from collections.abc import Iterable, Callable
from enum import Enum, StrEnum
from functools import lru_cache
from typing import Self
from urllib.parse import urlparse

from disnake import ApplicationCommandInteraction
from disnake.ext.commands import InteractionBot

from common.constants import Server, Channel
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


class BaseRoleEnum(Enum):
    """
    This python enum subclass is a black magic, do not touch it, I sacrificed 3 goats during full moon to make it work.
    """

    _role_name: str
    _role_id: int
    _button_label: str

    def __new__(cls, role_name, role_id, button_label=None):
        obj = object.__new__(cls)
        obj._role_name = role_name
        obj._role_id = role_id
        obj._button_label = button_label if button_label is not None else role_name
        return obj

    @property
    def role_name(self) -> str:
        return self._role_name

    @property
    def role_id(self) -> int:
        return self._role_id

    @property
    def button_label(self) -> str:
        return self._button_label

    @property
    def role_tag(self) -> str:
        return f"<@&{self._role_id}>"

    @classmethod
    def get_role_id_by_name(cls, name: str) -> int | None:
        for member in cls:
            if member._role_name == name:
                return member._role_id
        return None

    @classmethod
    def get_by_role_id(cls, role_id: int) -> Self | None:
        for member in cls:
            if member._role_id == role_id:
                return member
        return None

    @classmethod
    def get_by_button_label(cls, button_label: str) -> Self | None:
        for member in cls:
            if member._button_label == button_label:
                return member
        return None


class SelfServiceRoles(BaseRoleEnum):
    """Seznam rolí, co si lidi sami můžou naklikat"""

    CLEN = ("Člen", 804431648959627294)
    OSTRAVAK = ("Ostravák", 988431391807131690)
    PRAZAK = ("Pražák", 998636130511630386)
    BRNAK = ("Brňák", 1105227159712309391)
    CARFAG = ("carfag", 1057281159509319800, "Carfag-péro")
    MAGIC_THE_GATHERING = ("MagicTheGathering", 1327396658605981797, "Magic The Gathering")
    KNIZNI_KLUB = ("knižní klub", 1455224895641227409, "Knižní klub")


class GamingRoles(BaseRoleEnum):
    """Seznam herních rolí pro tagy"""

    WARCRAFT = ("warcraft", 871817685439234108, "Warcraft 3")
    GMOD = ("gmod", 951457356221394975, "Garry's Mod")
    VALORANT = ("valorant", 991026818054225931, "Valorant")
    KYOUDAI = ("kyoudai", 1031510557163008010, "Kyoudai (Yakuza/Mahjong)")
    LOLKO = ("lolko", 994302892561399889, "LoL")
    DOTA2 = ("dota2", 994303445735587991, "Dota 2")
    CSGO = ("csgo", 994303566082740224, "CS:GO")
    SEA_OF_THIEVES = ("sea of thieves", 994303863643451442, "Sea of Thieves")
    MINECRAFT = ("Minecraft", 1049052005341069382)
    DARK_AND_DARKER = ("Dark and Darker", 1054111346733617222, "Dark and Darker")
    GOLFISTI = ("golfisti", 1076931268555587645, "Golf With Your Friends")
    WOWKO = ("WoWko", 1120426868697473024)
    ROCKANDSTONE = ("kámen a šutr", 1107334623983312897, "ROCK AND STONE (Deep rock Gal.)")
    HOTS = ("hots", 1140376580800118835, "Heroes of the Storm")
    GTAONLINE = ("GTA Online", 1189322955063316551)
    WARFRAME = ("Warframe", 1200135734590451834)
    HELLDIVERS = ("helldivers", 1228002980754751621, "Helldivers II")
    VOIDBOYS = ("voidboys", 1281326981878906931, "Void Crew")
    THEFINALS = ("finalnici", 1242187454837035228, "Finálníci (the Finals)")
    BEYOND_ALL_REASON = ("BeyondAllReason", 1358445521227874424, "Beyond All Reason")
    VALHEIM = ("valheim", 1356164640152883241)
    ARC_RAIDERS = ("ArcRaiders", 1432779821183930401, "Arc Raiders")
    FRIENDSLOP = ("Friendslop", 1435240483852124292)
    BAROTRAUMA = ("barotrauma", 1405232484987437106)
    TABLE_TOP_SIMULATOR = ("TabletopSimulator", 1422635058996711614, "Table Top Simulator")


class DiscordGamingTestingRoles(BaseRoleEnum):
    """Testing role enum for game pings"""

    WARCRAFT = ("warcraft", 1422634691969945830, "Warcraft 3")
    VALORANT = ("valorant", 1422634814095228928, "Valorant")


GAMING_ROLES_PER_SERVER = {Server.KOUZELNICI: GamingRoles, Server.TEST_SERVER: DiscordGamingTestingRoles}


class ChamberRoles(BaseRoleEnum):
    """Private-ish roles requiring access appeal poll"""

    ITPERO = ("ITPéro m o n k e", 786618350095695872, "IT Péro")
    ECONPOLIPERO = ("Ekonpolipéro m o n k e", 1454177855943741492, "Ekon-poli-péro")

    def get_channel(self) -> Channel:
        match self:
            case ChamberRoles.ITPERO:
                return Channel.IT_PERO
            case ChamberRoles.ECONPOLIPERO:
                return Channel.ECONPOLIPERO
            case _:
                raise ValueError(f"Unknown chamber role: {self.role_name}")

    @classmethod
    def get_channels(cls) -> list[tuple[str, int]]:
        return [(i.button_label, i.get_channel()) for i in cls]

    @classmethod
    def get_channel_names(cls) -> list[str]:
        return [i[0] for i in cls.get_channels()]


class SpecialRoles(BaseRoleEnum):
    """Single-instance role IDs for specific functionality."""

    PAUSED = ("Paused", 1449758326304014438)


class SpecialTestingRoles(BaseRoleEnum):
    PAUSED = ("Paused", 1449757350482280641)


def get_paused_role_id(guild_id: int) -> int:
    """Get the Paused role ID for a specific guild."""
    if guild_id == Server.TEST_SERVER:
        return SpecialTestingRoles.PAUSED.role_id
    return SpecialRoles.PAUSED.role_id

class ListenerType(StrEnum):
    ROLEPICKER = "rolepicker"
    ANONYMPOLL = "anonympoll"
    ACCESSPOLL = "accesspoll"