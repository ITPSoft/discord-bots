"""Pytest configuration for Discord bot testing."""

import os
import pytest
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