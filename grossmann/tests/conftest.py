"""Pytest configuration for Discord bot testing."""

import os
import pytest
from unittest.mock import AsyncMock, patch

# Mock environment variables for testing
os.environ.setdefault("DISCORD_TOKEN", "test_token")
os.environ.setdefault("TEXT_SYNTH_TOKEN", "test_token")

# Test guild and channel IDs
TEST_GUILD_ID = 12345
TEST_CHANNEL_ID = 67890
TEST_ADMIN_ROLE_ID = 11111
TEST_ALLOWED_CHANNEL_ID = 22222

# Test role IDs (using actual IDs from the bot for consistency in tests)
TEST_CLEN_ROLE_ID = 804431648959627294
TEST_WARCRAFT_ROLE_ID = 871817685439234108
TEST_GMOD_ROLE_ID = 951457356221394975

# Test channel IDs for specific features
TEST_ROLE_SELECTION_CHANNEL_ID = 1314388851304955904


@pytest.fixture
def mock_ctx():
    """Create a mock ApplicationCommandInteraction context."""
    ctx = AsyncMock()
    ctx.response.send_message = AsyncMock()
    return ctx


@pytest.fixture
def mock_message():
    """Create a mock Message object."""
    message = AsyncMock()
    message.add_reaction = AsyncMock()
    message.edit = AsyncMock()
    return message


@pytest.fixture
def mock_ctx_with_message(mock_ctx, mock_message):
    """Create a mock context that returns a message from original_message()."""
    mock_ctx.original_message = AsyncMock(return_value=mock_message)
    return mock_ctx, mock_message


@pytest.fixture
def mock_ctx_with_response_message(mock_ctx, mock_message):
    """Create a mock context where send_message returns a message object."""
    mock_ctx.response.send_message = AsyncMock(return_value=mock_message)
    return mock_ctx, mock_message


@pytest.fixture
def patched_main():
    """Patch main.client to avoid bot instantiation issues."""
    with patch("main.client"):
        import main

        yield main


@pytest.fixture
def gaming_reactions():
    """Standard gaming command reactions."""
    return ["✅", "❎", "🤔", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "❓"]


@pytest.fixture
def poll_reactions():
    """Standard poll emoji reactions."""
    return ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]


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
def bot_validation_cases():
    """Test cases for bot validation."""
    return [("good bot", "🙂"), ("hodný bot", "🙂"), ("bad bot", "😢"), ("zlý bot", "😢"), ("naser si bote", "😢")]


@pytest.fixture
def mock_interaction():
    """Create a mock interaction for NetHack commands."""
    interaction = AsyncMock()
    interaction.channel_id = TEST_ALLOWED_CHANNEL_ID
    interaction.response = AsyncMock()
    interaction.response.defer = AsyncMock()
    interaction.response.send_message = AsyncMock()
    interaction.followup = AsyncMock()
    interaction.followup.send = AsyncMock()
    interaction.author = AsyncMock()
    interaction.author.roles = []
    return interaction


@pytest.fixture
def mock_admin_interaction(mock_interaction):
    """Create a mock interaction with admin role."""
    admin_role = AsyncMock()
    admin_role.id = TEST_ADMIN_ROLE_ID
    mock_interaction.author.roles = [admin_role]
    return mock_interaction


@pytest.fixture
def mock_wrong_channel_interaction():
    """Create a mock interaction in wrong channel."""
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
