from collections.abc import Iterator
from unittest.mock import AsyncMock, MagicMock

import pytest
from aioresponses import aioresponses
from common.utils import SelfServiceRoles

from common import http
from common.constants import Channel, Server

MOCK_MESSAGE_ID = 12345678


@pytest.fixture(scope="function")
def mock_role():
    role = MagicMock()
    role.id = SelfServiceRoles.CLEN.role_id
    role.position = 42
    return role


@pytest.fixture(scope="function")
def mock_member():
    member = MagicMock()
    member.mention = "<@987654321>"
    member.guild.id = Server.TEST_SERVER
    return member


@pytest.fixture(scope="function")
def mock_ctx(mock_role):
    """Create a mock ApplicationCommandInteraction context."""

    ctx = AsyncMock()
    ctx.component.custom_id = SelfServiceRoles.CLEN.role_name
    ctx.me.top_role.position = 69
    ctx.author.roles = []
    ctx.author.display_name = "TestUser"
    ctx.author.avatar = "https://example.com/avatar.png"
    ctx.channel.name = "test-channel"
    ctx.channel.id = 12345
    ctx.guild = MagicMock()
    ctx.guild_id = Server.TEST_SERVER
    ctx.guild.id = Server.TEST_SERVER
    ctx.guild.get_role.return_value = mock_role

    return ctx


@pytest.fixture(scope="function")
def mock_message():
    """Create a mock Message object."""
    message = AsyncMock()
    message.author.__str__.return_value = "TestUser#1234"
    message.content = ""
    message.channel.id = Channel.BOT_TESTING
    message.guild.id = Server.TEST_SERVER
    message.id = MOCK_MESSAGE_ID

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


@pytest.fixture(scope="function")
def mock_message_interaction():
    """Create a mock MessageInteraction for button_vote_access tests."""
    ctx = AsyncMock()
    ctx.author.id = 11111
    ctx.message.embeds = [MagicMock()]
    ctx.guild.get_member = MagicMock()
    ctx.guild.get_role = MagicMock()
    return ctx


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
