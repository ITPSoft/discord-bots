"""Basic smoke tests for Grossmann Discord bot."""

from unittest.mock import patch

# Mock Discord bot to prevent actual connection
with patch("disnake.ext.commands.Bot"):
    import main


async def test_batch_react():
    """Test batch_react function."""
    from unittest.mock import AsyncMock

    mock_message = AsyncMock()
    mock_message.add_reaction = AsyncMock()

    await main.batch_react(mock_message, ["✅", "❎"])

    assert mock_message.add_reaction.call_count == 2
