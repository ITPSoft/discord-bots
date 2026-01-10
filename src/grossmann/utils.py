import asyncio
import dataclasses
import logging
import re
from urllib.parse import urlparse

import aiohttp
from aiohttp import ClientTimeout
from disnake import Message, ApplicationCommandInteraction, Embed, File
from disnake.ext.commands import BadArgument

from common.constants import GAMING_ROLES_PER_SERVER
from common.http import (
    prepare_http_response,
    EmbedResponse,
    TextResponse,
    ErrorResponse,
    get_http_session,
)
from common.utils import validate_param
from grossmann.grossmanndict import WAIFU_CATEGORIES

logger = logging.getLogger(__name__)

ROLE_TAG_RE = re.compile(r"<@&(\d{10,30})>")


@dataclasses.dataclass
class AccessVoting:
    allow: int
    deny: int
    voters: list[int]


# useful functions/methods
async def batch_react(m: Message, reactions: list):
    # asyncio.gather would not guarantee order, so we need to add them one by one
    for reaction in reactions:
        await m.add_reaction(reaction)


async def send_http_response(ctx: ApplicationCommandInteraction, url: str, resp_key: str, error_message: str) -> None:
    match await prepare_http_response(url=url, resp_key=resp_key):
        case EmbedResponse(_, content):
            await respond(ctx, embed=Embed().set_image(file=File(fp=content, filename="image.png")))
        case TextResponse(_, content):
            await respond(ctx, content=content)
        case ErrorResponse():
            await respond(ctx, content=error_message)


async def respond(ctx: ApplicationCommandInteraction, **results):
    if ctx.response.is_done():
        logger.debug("Using followup instead of response")
        await ctx.followup.send(**results)
    else:
        await ctx.response.send_message(**results)


@validate_param
async def validate_image_url(ctx: ApplicationCommandInteraction, url: str | None) -> str | None:
    """Validate that URL is accessible and returns an image."""
    if url is None:
        return url

    # Basic URL validation
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            raise BadArgument("Špatný URL formát")
    except Exception:
        raise BadArgument("Špatný URL formát")

    # Check URL length (Discord limit ~2000 chars for URLs)
    if len(url) > 2000:
        raise BadArgument("URL je moc dlouhá")

    # Check MIME type with HEAD request
    try:
        async with get_http_session().head(url, timeout=ClientTimeout(total=2)) as resp:
            if resp.status != 200:
                raise BadArgument(f"URL vrátila status {resp.status}")

            content_type = resp.headers.get("Content-Type", "")
            if not content_type.startswith("image/"):
                raise BadArgument(f"URL is not an image (got {content_type})")

    except asyncio.TimeoutError:
        raise BadArgument("URL se načítala moc dlouho")
    except aiohttp.InvalidURL:
        raise BadArgument("Špatný URL formát")
    except Exception as e:
        raise BadArgument(f"Nešlo zvalidost URL obrázku: {str(e)}")

    return url


@validate_param
def validate_waifu_category(ctx: ApplicationCommandInteraction, argument: str) -> str:
    content_type = ctx.options.get("type")

    if not content_type or content_type not in WAIFU_CATEGORIES:
        raise BadArgument("Neznámý typ")

    valid_subcategories = WAIFU_CATEGORIES[content_type]
    if argument not in valid_subcategories:
        raise BadArgument(f"'{argument}' není v typu '{content_type}'. Vyber si z: {', '.join(valid_subcategories)}")

    return argument


def is_valid_role_tag(role_tag: str) -> bool:
    return ROLE_TAG_RE.fullmatch(role_tag) is not None


def role_tag2id(role_tag: str) -> int:
    m = ROLE_TAG_RE.fullmatch(role_tag)
    assert m is not None
    return int(m.group(1))


@validate_param
def validate_game_role(ctx: ApplicationCommandInteraction, game_role: str) -> str:
    if not is_valid_role_tag(game_role):
        raise BadArgument(f"'{game_role}' není role, použij @role, discord je našeptává.")
    if GAMING_ROLES_PER_SERVER[ctx.guild_id].get_by_role_id(role_tag2id(game_role)) is None:
        raise BadArgument(f"'{game_role}' není platná herní role.")
    return game_role
