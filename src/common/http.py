import io
import logging
from dataclasses import dataclass

import aiohttp

logger = logging.getLogger(__name__)

_http_session: aiohttp.ClientSession | None = None


@dataclass
class Response:
    status_code: int


@dataclass
class TextResponse(Response):
    text: str


@dataclass
class EmbedResponse(Response):
    content: io.BytesIO


@dataclass
class ErrorResponse(Response):
    pass


def get_http_session() -> aiohttp.ClientSession:
    """Get the global HTTP session, creating it lazily if needed."""
    global _http_session
    if _http_session is None or _http_session.closed:
        _http_session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
    return _http_session


async def close_http_session() -> None:
    """Close the global HTTP session if it's open."""
    global _http_session
    if _http_session and not _http_session.closed:
        await _http_session.close()
        _http_session = None


async def prepare_http_response(url: str, resp_key: str) -> Response:
    try:
        async with get_http_session().get(url) as api_call:
            if 200 <= api_call.status < 300:
                match api_call.content_type:
                    case "image/gif" | "image/jpeg" | "image/png":
                        result = await api_call.content.read()
                        bytes_io = io.BytesIO()
                        bytes_io.write(result)
                        bytes_io.seek(0)
                        # although disnake.File accepts both bytes and io.BytesIO
                        # it treats bytes as filename, not file contents
                        return EmbedResponse(api_call.status, content=bytes_io)
                    case "application/json":
                        result = (await api_call.json())[resp_key]
                        return TextResponse(api_call.status, result)
            elif api_call.status == 404:  # show error but don't log
                return ErrorResponse(api_call.status)
            else:
                logger.error(f"HTTP error response: {api_call.status=} for {url=}")
                return ErrorResponse(api_call.status)
    except Exception as exc:
        logger.error(f"Encountered exception when calling {url=}", exc_info=exc)
        return ErrorResponse(0)
    return ErrorResponse(0)
