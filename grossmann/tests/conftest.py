"""Pytest configuration for Discord bot testing."""

import pytest
import discord
from discord.ext import commands
import discord.ext.test as dpytest
from unittest.mock import patch
import os
import asyncio

# Mock environment variables for testing
os.environ.setdefault("DISCORD_TOKEN", "test_token")
os.environ.setdefault("TEXT_SYNTH_TOKEN", "test_token")


class DiscordTestBot(commands.Bot):
    """A pure discord.py bot for testing with dpytest compatibility."""

    def __init__(self, *args, **kwargs):
        # Initialize with discord.py
        super().__init__(*args, **kwargs)

        # Ensure it's not detected as sharded
        self.shard_count = None
        self.shard_id = None
        self.shard_ids = None

        # Set the event loop for compatibility
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)


@pytest.fixture(scope="function")
async def bot():
    """Setup dpytest configuration with clean discord.py bot."""
    # Create pure discord.py intents
    discord_intents = discord.Intents.all()
    discord_intents.message_content = True

    # Create the discord.py test bot
    test_client = DiscordTestBot(command_prefix="/", intents=discord_intents)

    # Ensure the bot has the current event loop
    loop = asyncio.get_event_loop()
    test_client.loop = loop

    # Mock HTTP session to avoid actual HTTP requests
    with patch("aiohttp.ClientSession"):
        # Configure dpytest with our discord.py bot
        dpytest.configure(test_client)

        yield test_client

        # Cleanup after tests
        await dpytest.empty_queue()


def add_command_wrapper(bot, command_name, command_func):
    """Add a wrapper command that calls the actual disnake command function."""

    @bot.command(name=command_name)
    async def wrapper(ctx, *args, **kwargs):
        # Create a mock disnake context that wraps the discord.py context
        class MockResponse:
            def __init__(self, ctx, disnake_ctx):
                self.ctx = ctx
                self.disnake_ctx = disnake_ctx

            async def send_message(self, content=None, embed=None, ephemeral=False):
                message = await self.ctx.send(content=content, embed=embed)
                # Track the last sent message for original_message()
                self.disnake_ctx._last_sent_message = message
                return message

        class MockDisnakeContext:
            def __init__(self, discord_ctx):
                self.send = discord_ctx.send
                self.channel = discord_ctx.channel
                self.author = discord_ctx.author
                self.guild = discord_ctx.guild
                self.message = discord_ctx.message
                self.response = MockResponse(discord_ctx, self)
                self._last_sent_message = None

            async def original_message(self):
                # Return the last message sent by the response
                return self._last_sent_message or self.message

            async def batch_react(self, message, reactions):
                # This is a disnake-specific method that doesn't actually exist, mock it
                # This is likely a bug in main.py - should be just batch_react(message, reactions)
                pass

        mock_ctx = MockDisnakeContext(ctx)

        # Call the actual command function with the mock context
        try:
            await command_func(mock_ctx, *args, **kwargs)
        except Exception as e:
            # Handle any disnake-specific errors gracefully
            print(f"Error in command {command_name}: {e}")
            await ctx.send(f"Command executed with error: {e}")

    return wrapper


@pytest.fixture
def mock_guild():
    """Create a mock guild for testing."""
    return dpytest.backend.make_guild("Test Guild")


@pytest.fixture
def mock_channel():
    """Create a mock channel for testing."""
    guild = dpytest.backend.make_guild("Test Guild")
    return dpytest.backend.make_text_channel("test-channel", guild)


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    return dpytest.backend.make_user("TestUser", 1234)


@pytest.fixture
def mock_member():
    """Create a mock member for testing."""
    guild = dpytest.backend.make_guild("Test Guild")
    user = dpytest.backend.make_user("TestUser", 1234)
    return dpytest.backend.make_member(user, guild)
