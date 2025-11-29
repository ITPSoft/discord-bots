import io
from collections.abc import Iterable
from enum import StrEnum
from urllib.parse import urlparse

import aiohttp


def has_any(content: str, words: Iterable) -> bool:
    return any(word in content for word in words)


def has_all(content: str, words: Iterable) -> bool:
    return all(word in content for word in words)


class ResponseType(StrEnum):
    EMBED = "embed"
    CONTENT = "content"


async def prepare_http_response(
    http_session: aiohttp.ClientSession | None, url: str, resp_key: str, error_message: str
) -> tuple[io.BytesIO | str, ResponseType]:
    assert http_session is not None
    try:
        async with http_session.get(url) as api_call:
            if api_call.status == 200:
                match api_call.content_type:
                    case "image/gif" | "image/jpeg" | "image/png":
                        result = await api_call.content.read()
                        bytes_io = io.BytesIO()
                        bytes_io.write(result)
                        bytes_io.seek(0)
                        return bytes_io, ResponseType.EMBED
                    case "application/json":
                        result = (await api_call.json())[resp_key]
                        return result, ResponseType.CONTENT
            else:
                return error_message, ResponseType.CONTENT
    except Exception as exc:
        print(f"Encountered exception:\n {exc}")
        return "Oh nyo?!?! Something went ^w^ wwong!!", ResponseType.CONTENT


def is_url(string):
    parsed = urlparse(string)
    return bool(parsed.scheme) and bool(parsed.netloc)
