"""Integration tests for Grossmann bot scenarios and business logic."""

import pytest
from unittest.mock import patch

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


async def test_gmod_ping_command_integration(patched_main, mock_ctx_with_message, gaming_reactions):
    """Test gmod ping command with actual business logic from main.py."""
    mock_ctx, mock_message = mock_ctx_with_message
    
    # Execute the actual gmod command function with time parameter
    await patched_main.gmod(mock_ctx, "19:30")
    
    # Verify the message was sent with correct content
    mock_ctx.response.send_message.assert_called_once()
    sent_content = mock_ctx.response.send_message.call_args[0][0]
    
    # Verify content matches the template with time
    expected_content = decdi.GMOD_CZ.replace("{0}", "19:30")
    assert sent_content == expected_content
    
    # Verify original_message was called to get message for reactions
    mock_ctx.original_message.assert_called_once()
    
    # Verify batch_react was called with expected reactions
    assert_reactions_added(mock_message, gaming_reactions)


async def test_poll_command_integration(patched_main, mock_ctx_with_response_message, sample_poll_data):
    """Test poll command with actual business logic from main.py."""
    mock_ctx, mock_message = mock_ctx_with_response_message
    
    # Execute the actual poll command function
    question = sample_poll_data["question"]
    options = sample_poll_data["options"]
    await patched_main.poll(mock_ctx, question, options[0], options[1], options[2], None, None)
    
    # Verify initial message was sent
    mock_ctx.response.send_message.assert_called_once_with("Creating poll...", ephemeral=False)
    
    # Verify poll reactions were added
    expected_reactions = sample_poll_data["expected_reactions"]
    assert_reactions_added(mock_message, expected_reactions)
    
    # Verify the message was edited with poll content
    mock_message.edit.assert_called_once()
    edit_call_args = mock_message.edit.call_args
    poll_content = edit_call_args.kwargs['content']
    assert f"Anketa: {question}" in poll_content
    for i, option in enumerate(options):
        assert f"{expected_reactions[i]} = {option}" in poll_content


async def test_poll_command_insufficient_options(patched_main, mock_ctx):
    """Test poll command with insufficient options."""
    # Execute the actual poll command function with insufficient options
    await patched_main.poll(mock_ctx, "Test?", "OnlyOption", "", None, None, None)
    
    # Verify error message was sent
    mock_ctx.response.send_message.assert_called_once_with(
        "You must provide at least two options.", ephemeral=True
    )


async def test_yesorno_command_integration(patched_main, mock_ctx, yesorno_answers):
    """Test yesorno command with actual business logic from main.py."""
    with patch('random.choice') as mock_choice:
        mock_choice.return_value = "Yes."
        
        # Execute the actual yesorno command function
        await patched_main.yesorno(mock_ctx)
        
        # Verify response was sent with the mocked choice
        mock_ctx.response.send_message.assert_called_once_with("Yes.")
        
        # Verify random.choice was called with the correct answers
        mock_choice.assert_called_once_with(yesorno_answers)


@pytest.mark.parametrize("content,expected_reaction", [
    ("good bot", "🙂"),
    ("hodný bot", "🙂"), 
    ("bad bot", "😢"),
    ("zlý bot", "😢"),
    ("naser si bote", "😢")
])
async def test_bot_validation_integration(patched_main, mock_message, content, expected_reaction):
    """Test bot validation logic with actual main.py function."""
    await patched_main.bot_validate(content, mock_message)
    mock_message.add_reaction.assert_called_with(expected_reaction)


async def test_batch_react_integration(patched_main, mock_message):
    """Test batch_react function from main.py."""
    reactions = ["✅", "❎", "🤔"]
    
    await patched_main.batch_react(mock_message, reactions)
    
    # Verify all reactions were added in order
    assert_reactions_added(mock_message, reactions)


@pytest.mark.parametrize("content,words,expected", [
    ("this contains bad bot text", ["bad bot", "good bot"], True),
    ("this is normal text", ["bad bot", "good bot"], False),
    ("any text", [], False),
    ("good bot here", ["good bot"], True),
    ("no match here", ["xyz", "abc"], False)
])
def test_has_any_utility_integration(patched_main, content, words, expected):
    """Test has_any utility function from main.py."""
    assert patched_main.has_any(content, words) is expected


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
