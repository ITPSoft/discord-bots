from collections.abc import Iterator
from unittest.mock import AsyncMock, MagicMock

import pytest
from aioresponses import aioresponses
from common.utils import SelfServiceRoles

from common import http
from common.constants import Channel


@pytest.fixture(scope="function")
def mock_role():
    role = MagicMock()
    role.id = SelfServiceRoles.CLEN.role_id
    return role

@pytest.fixture(scope="function")
def mock_ctx(mock_role):
    """Create a mock ApplicationCommandInteraction context."""

    ctx = AsyncMock()
    ctx.response = AsyncMock()
    ctx.response.send_message = AsyncMock()
    ctx.component = MagicMock()
    ctx.component.custom_id = SelfServiceRoles.CLEN
    ctx.send = AsyncMock()
    ctx.original_response = AsyncMock()
    ctx.original_message = AsyncMock()
    ctx.author = MagicMock()
    ctx.author.roles = []
    ctx.author.add_roles = AsyncMock()
    ctx.author.remove_roles = AsyncMock()
    ctx.author.display_name = "TestUser"
    ctx.author.avatar = "https://example.com/avatar.png"
    ctx.channel = MagicMock()
    ctx.channel.name = "test-channel"
    ctx.channel.id = 12345
    ctx.guild = MagicMock()

    ctx.guild.get_role.return_value = mock_role

    return ctx


@pytest.fixture(scope="function")
def mock_message():
    """Create a mock Message object."""
    message = AsyncMock()
    message.add_reaction = AsyncMock()
    message.edit = AsyncMock()
    message.author = MagicMock()
    message.author.__str__ = MagicMock(return_value="TestUser#1234")
    message.content = ""
    message.channel.id = Channel.BOT_TESTING

    # Mock channel.history() as an async generator
    async def mock_history(*args, **kwargs):
        # Return some sample messages for markov chain generation
        mock_msg1 = AsyncMock()
        mock_msg1.content = "hello world test"
        mock_msg2 = AsyncMock()
        mock_msg2.content = "world test again"
        mock_msg3 = AsyncMock()
        mock_msg3.content = "some other message"
        for msg in [mock_msg1, mock_msg2, mock_msg3]:
            yield msg

    message.channel.history = MagicMock(return_value=mock_history())
    return message


@pytest.fixture(autouse=True)
async def cleanup_http_session():
    """Ensure HTTP session is cleaned up after each test."""
    yield
    await http.close_http_session()


@pytest.fixture
def m() -> Iterator[aioresponses]:
    """Mock HTTP requests done by AioHTTP."""
    with aioresponses() as mock:
        yield mock
