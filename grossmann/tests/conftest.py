"""Pytest configuration for Discord bot testing."""

import os
import pytest
from unittest.mock import AsyncMock, patch

import disnake
from disnake.ext import commands
import discord.ext.test as dpytest

# Mock environment variables for testing
os.environ.setdefault("DISCORD_TOKEN", "test_token")
os.environ.setdefault("TEXT_SYNTH_TOKEN", "test_token")
os.environ.setdefault("BOT_PREFIX", "/")

# Import decimdictionary for testing
import decimdictionary as decdi


@pytest.fixture
async def bot():
    """Create a test bot instance configured for dpytest."""
    intents = disnake.Intents.all()
    intents.message_content = True
    
    # Create InteractionBot like in main.py
    test_bot = commands.InteractionBot(intents=intents)
    
    # Configure dpytest with the bot
    dpytest.configure(test_bot, 2, decdi.GIDS)
    
    yield test_bot
    
    # Cleanup after test
    await dpytest.empty_queue()


@pytest.fixture(autouse=True)
async def cleanup():
    """Auto cleanup after each test."""
    yield
    await dpytest.empty_queue()


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
        "expected_reactions": ["1️⃣", "2️⃣", "3️⃣"]
    }


@pytest.fixture
def bot_validation_cases():
    """Test cases for bot validation."""
    return [
        ("good bot", "🙂"),
        ("hodný bot", "🙂"), 
        ("bad bot", "😢"),
        ("zlý bot", "😢"),
        ("naser si bote", "😢")
    ]


def assert_reactions_added(mock_message, expected_reactions):
    """Helper function to assert that all expected reactions were added."""
    assert mock_message.add_reaction.call_count == len(expected_reactions)
    for reaction in expected_reactions:
        mock_message.add_reaction.assert_any_call(reaction)