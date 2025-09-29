"""Pytest configuration for Discord bot testing."""

import os

# Mock environment variables for testing
os.environ.setdefault("DISCORD_TOKEN", "test_token")
os.environ.setdefault("TEXT_SYNTH_TOKEN", "test_token")
os.environ.setdefault("BOT_PREFIX", "/")

# Import decimdictionary for testing
import decimdictionary as decdi