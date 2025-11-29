"""Basic smoke tests for Krampol Discord bot."""

from unittest.mock import AsyncMock, patch, MagicMock

# Mock the automaton module
mock_automaton = MagicMock()
with patch.dict("sys.modules", {"automaton": mock_automaton}):
    with patch("disnake.ext.commands.Bot"):
        import krampol.main as main


async def test_work_loop_empty():
    """Test work_loop handles empty job list."""
    result = await main.work_loop([])
    assert result is None


async def test_process_command():
    """Test process_command function."""
    mock_channel = AsyncMock()
    mock_message = AsyncMock()

    with patch.object(main.client, "get_channel", return_value=mock_channel):
        mock_channel.send = AsyncMock(return_value=mock_message)
        mock_message.delete = AsyncMock()

        await main.process_command("$", "testcommand-itpero")

        main.client.get_channel.assert_called_once()
        mock_channel.send.assert_called_once()
        mock_message.delete.assert_called_once()
