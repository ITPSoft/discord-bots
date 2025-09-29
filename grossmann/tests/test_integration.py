"""Integration tests for Grossmann bot scenarios and business logic."""

import pytest
from unittest.mock import AsyncMock, patch

# Import modules to test
import decimdictionary as decdi
from conftest import assert_reactions_added


async def test_warcraft_ping_command_integration(patched_main, mock_ctx_with_message, gaming_reactions):
    """Test warcraft ping command with actual business logic from main.py."""
    mock_ctx, mock_message = mock_ctx_with_message
    
    # Execute the actual warcraft command function with time parameter
    await patched_main.warcraft(mock_ctx, "20:00")
    
    # Verify the message was sent with correct content
    mock_ctx.response.send_message.assert_called_once()
    sent_content = mock_ctx.response.send_message.call_args[0][0]
    
    # Verify content matches the template with time
    expected_content = decdi.WARCRAFTY_CZ.replace("{0}", " v cca 20:00")
    assert sent_content == expected_content
    
    # Verify original_message was called to get message for reactions
    mock_ctx.original_message.assert_called_once()
    
    # Verify batch_react was called with expected reactions
    assert_reactions_added(mock_message, gaming_reactions)


async def test_gmod_ping_command_integration():
    """Test gmod ping command with actual business logic from main.py."""
    with patch("main.client"):
        import main
        
        # Create mock interaction context
        mock_ctx = AsyncMock()
        mock_ctx.response.send_message = AsyncMock()
        mock_original_message = AsyncMock()
        mock_ctx.original_message = AsyncMock(return_value=mock_original_message)
        
        # Execute the actual gmod command function with time parameter
        await main.gmod(mock_ctx, "19:30")
        
        # Verify the message was sent with correct content
        mock_ctx.response.send_message.assert_called_once()
        sent_content = mock_ctx.response.send_message.call_args[0][0]
        
        # Verify content matches the template with time
        expected_content = decdi.GMOD_CZ.replace("{0}", "19:30")
        assert sent_content == expected_content
        
        # Verify original_message was called to get message for reactions
        mock_ctx.original_message.assert_called_once()
        
        # Verify batch_react was called with expected reactions
        expected_reactions = ["✅", "❎", "🤔", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "❓"]
        assert mock_original_message.add_reaction.call_count == len(expected_reactions)
        for reaction in expected_reactions:
            mock_original_message.add_reaction.assert_any_call(reaction)


async def test_poll_command_integration():
    """Test poll command with actual business logic from main.py."""
    with patch("main.client"):
        import main
        
        # Create mock interaction context
        mock_ctx = AsyncMock()
        mock_message = AsyncMock()  # The message returned by send_message
        mock_ctx.response.send_message = AsyncMock(return_value=mock_message)
        
        # Execute the actual poll command function
        await main.poll(mock_ctx, "What game?", "Warcraft", "GMod", "Valorant", None, None)
        
        # Verify initial message was sent
        mock_ctx.response.send_message.assert_called_once_with("Creating poll...", ephemeral=False)
        
        # Verify poll reactions were added (3 options = 3 reactions)
        expected_reactions = ["1️⃣", "2️⃣", "3️⃣"]
        assert mock_message.add_reaction.call_count == len(expected_reactions)
        for reaction in expected_reactions:
            mock_message.add_reaction.assert_any_call(reaction)
        
        # Verify the message was edited with poll content
        mock_message.edit.assert_called_once()
        edit_call_args = mock_message.edit.call_args
        poll_content = edit_call_args.kwargs['content']
        assert "Anketa: What game?" in poll_content
        assert "1️⃣ = Warcraft" in poll_content
        assert "2️⃣ = GMod" in poll_content
        assert "3️⃣ = Valorant" in poll_content


async def test_poll_command_insufficient_options():
    """Test poll command with insufficient options."""
    with patch("main.client"):
        import main
        
        # Create mock interaction context
        mock_ctx = AsyncMock()
        mock_ctx.response.send_message = AsyncMock()
        
        # Execute the actual poll command function with insufficient options
        await main.poll(mock_ctx, "Test?", "OnlyOption", "", None, None, None)
        
        # Verify error message was sent
        mock_ctx.response.send_message.assert_called_once_with(
            "You must provide at least two options.", ephemeral=True
        )
        
        # Verify that no further processing occurred (no original_message call)
        assert not hasattr(mock_ctx, 'original_message') or not mock_ctx.original_message.called


async def test_yesorno_command_integration():
    """Test yesorno command with actual business logic from main.py."""
    with patch("main.client"):
        import main
        
        with patch('random.choice') as mock_choice:
            mock_choice.return_value = "Yes."
            
            # Create mock interaction context
            mock_ctx = AsyncMock()
            mock_ctx.response.send_message = AsyncMock()
            
            # Execute the actual yesorno command function
            await main.yesorno(mock_ctx)
            
            # Verify response was sent with the mocked choice
            mock_ctx.response.send_message.assert_called_once_with("Yes.")
            
            # Verify random.choice was called with the correct answers
            expected_answers = ("Yes.", "No.", "Perhaps.", "Definitely yes.", "Definitely no.")
            mock_choice.assert_called_once_with(expected_answers)


async def test_bot_validation_integration():
    """Test bot validation logic with actual main.py function."""
    with patch("main.client"):
        import main
        
        # Test good bot validation
        mock_message = AsyncMock()
        content = "good bot"
        
        await main.bot_validate(content, mock_message)
        mock_message.add_reaction.assert_called_with("🙂")
        
        # Reset mock
        mock_message.reset_mock()
        
        # Test bad bot validation
        content = "bad bot"
        await main.bot_validate(content, mock_message)
        mock_message.add_reaction.assert_called_with("😢")


async def test_batch_react_integration(patched_main, mock_message):
    """Test batch_react function from main.py."""
    reactions = ["✅", "❎", "🤔"]
    
    await patched_main.batch_react(mock_message, reactions)
    
    # Verify all reactions were added in order
    assert_reactions_added(mock_message, reactions)


async def test_has_any_utility_integration():
    """Test has_any utility function from main.py."""
    with patch("main.client"):
        import main
        
        # Test positive case
        content = "this contains bad bot text"
        words = ["bad bot", "good bot"]
        assert main.has_any(content, words) is True
        
        # Test negative case
        content = "this is normal text"
        assert main.has_any(content, words) is False
        
        # Test empty words
        assert main.has_any(content, []) is False


@pytest.mark.parametrize("template,replacement,expected_content", [
    (decdi.WARCRAFTY_CZ, " v cca 20:00", "<@&871817685439234108> - Warcrafty 3 dnes v cca 20:00?"),
    (decdi.GMOD_CZ, "21:00", "<@&951457356221394975> - Garry's Mod dnes v cca 21:00?"),
    (decdi.WARCRAFTY_CZ, "", "<@&871817685439234108> - Warcrafty 3 dnes?"),
])
def test_template_replacement_integration(template, replacement, expected_content):
    """Test that command templates work correctly with various inputs."""
    result = template.replace("{0}", replacement)
    assert expected_content in result


@pytest.mark.parametrize("command_name", [
    "_roll_", "_poll_", "_yesorno_", "_warcraft_", "_gmod_"
])
def test_help_template_contains_commands(command_name):
    """Test that help template contains all expected commands."""
    assert command_name in decdi.HELP
