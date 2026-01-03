"""Pytest configuration for Discord bot testing."""

import os
from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from common.utils import ListenerType, ChamberRoles
from ..conftest import MOCK_USER_ID, MOCK_VOTER_ID

# Mock environment variables for testing
os.environ.setdefault("DISCORD_TOKEN", "test_token")

# Test guild and channel IDs
TEST_GUILD_ID = 12345
TEST_CHANNEL_ID = 67890
TEST_ADMIN_ROLE_ID = 11111
TEST_ALLOWED_CHANNEL_ID = 22222
MOCK_CHAMBER_ROLE_ID = ChamberRoles.ITPERO.role_id


@pytest.fixture
def mock_ctx_with_message(mock_ctx, mock_message):
    """Create a mock context that returns a message from original_message()."""
    mock_ctx.original_message = AsyncMock(return_value=mock_message)
    return mock_ctx, mock_message


@pytest.fixture
def patched_main():
    """Patch main.client to avoid bot instantiation issues."""
    with patch("grossmann.main.client"):
        from grossmann import main

        yield main


@pytest.fixture
def poll_emojis():
    """Standard poll emoji list."""
    return ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]


@pytest.fixture
def gaming_reactions():
    """Standard gaming command reactions."""
    return ["✅", "❎", "🤔", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "❓"]


@pytest.fixture
def yesorno_answers():
    """Standard yesorno command answers."""
    return ("Yes.", "No.", "Perhaps.", "Definitely yes.", "Definitely no.")


@pytest.fixture
def sample_poll_data():
    """Sample poll data for testing."""
    return {
        "question": "What game?",
        "options": ["Warcraft", "GMod", "Valorant"],
        "expected_reactions": ["1️⃣", "2️⃣", "3️⃣"],
    }


@pytest.fixture
def mock_interaction(mock_ctx):
    """Create a mock ApplicationCommandInteraction for NetHack commands."""
    mock_ctx.channel_id = TEST_ALLOWED_CHANNEL_ID
    return mock_ctx


@pytest.fixture
def mock_admin_interaction(mock_interaction):
    """Create a mock ApplicationCommandInteraction with admin role."""
    admin_role = AsyncMock()
    admin_role.id = TEST_ADMIN_ROLE_ID
    mock_interaction.author.roles = [admin_role]
    return mock_interaction


@pytest.fixture
def mock_wrong_channel_interaction():
    """Create a mock ApplicationCommandInteraction in wrong channel."""
    interaction = AsyncMock()
    interaction.channel_id = TEST_CHANNEL_ID  # Different from allowed channel
    interaction.response = AsyncMock()
    interaction.response.send_message = AsyncMock()
    interaction.author = AsyncMock()
    interaction.author.roles = []
    return interaction


def assert_reactions_added(mock_message, expected_reactions):
    """Helper function to assert that all expected reactions were added."""
    assert mock_message.add_reaction.call_count == len(expected_reactions)
    for reaction in expected_reactions:
        mock_message.add_reaction.assert_any_call(reaction)


@pytest.fixture(autouse=True)
def mock_is_correct_channel() -> Generator[MagicMock, Any, None]:
    with patch("grossmann.nethack_module.is_correct_channel") as _fixture:
        _fixture.side_effect = lambda channel: channel.channel_id == TEST_ALLOWED_CHANNEL_ID
        yield _fixture


@pytest.fixture
def mock_access_voting_interaction_allow(mock_message_interaction):
    """Create a mock AccessVoting object for testing."""
    mock_message_interaction.component.custom_id = (
        f"{ListenerType.ACCESSPOLL}:{MOCK_CHAMBER_ROLE_ID}:{MOCK_USER_ID}:allow"
    )
    mock_message_interaction.author.id = MOCK_VOTER_ID
    return mock_message_interaction


@pytest.fixture
def mock_access_voting_interaction_deny(mock_message_interaction):
    """Create a mock AccessVoting object for testing."""
    mock_message_interaction.component.custom_id = (
        f"{ListenerType.ACCESSPOLL}:{MOCK_CHAMBER_ROLE_ID}:{MOCK_USER_ID}:deny"
    )
    mock_message_interaction.author.id = MOCK_VOTER_ID
    return mock_message_interaction
