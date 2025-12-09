import io
import logging
from collections.abc import Iterable
from enum import StrEnum
from urllib.parse import urlparse

from common.http import get_http_session

logger = logging.getLogger(__name__)


def has_any(content: str, words: Iterable) -> bool:
    return any(word in content for word in words)


def has_all(content: str, words: Iterable) -> bool:
    return all(word in content for word in words)


class ResponseType(StrEnum):
    EMBED = "embed"
    CONTENT = "content"


async def prepare_http_response(url: str, resp_key: str, error_message: str) -> tuple[io.BytesIO | str, ResponseType]:
    try:
        async with get_http_session().get(url) as api_call:
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
        logger.error(f"Encountered exception: {exc}")
        return "Something crashed", ResponseType.CONTENT
    return "Something crashed relly bad", ResponseType.CONTENT


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
