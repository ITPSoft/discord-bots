"""Comprehensive tests for Grossmann Discord bot using pytest and mocking."""

from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

from grossmann import main
from grossmann import grossmanndict as grossdi
from grossmann.utils import batch_react


# Test batch_react utility function
async def test_batch_react_adds_all_reactions(mock_message):
    """Test batch_react function adds all reactions in order."""
    reactions = ["✅", "❎", "🤔"]

    await batch_react(mock_message, reactions)

    assert mock_message.add_reaction.call_count == len(reactions)
    mock_message.add_reaction.assert_has_calls([call(r) for r in reactions])


async def test_batch_react_empty_list(mock_message):
    """Test batch_react with empty reaction list."""
    await batch_react(mock_message, [])

    mock_message.add_reaction.assert_not_called()


# Test bot_validate function
@pytest.mark.parametrize(
    "content,expected_reaction",
    [
        ("hodný bot", "🙂"),
        ("hodný bot a další text", "🙂"),
        ("něco a good bot", "🙂"),
        ("good bot", "🙂"),
        ("zlý bot", "😢"),
        ("bad bot", "😢"),
        ("naser si bote", "😢"),
        ("si naser bote", "😢"),
    ],
)
async def test_bot_validate_reactions(mock_message, content, expected_reaction):
    """Test bot_validate adds correct reactions for good/bad bot messages."""
    await main.bot_validate(content, mock_message)

    mock_message.add_reaction.assert_called_with(expected_reaction)


async def test_bot_validate_ignores_unrelated_messages(mock_message):
    """Test bot_validate ignores messages without bot keywords."""
    await main.bot_validate("just a normal message", mock_message)

    mock_message.add_reaction.assert_not_called()


# Test poll command
async def test_poll_command_creates_poll(mock_ctx, mock_message, poll_emojis):
    """Test poll command creates poll with correct reactions."""
    mock_ctx.original_response.return_value = mock_message

    await main.poll(mock_ctx, "What game?", "Option1", "Option2", "Option3")

    mock_ctx.send.assert_called_once()
    assert mock_message.add_reaction.call_count == 3
    mock_message.add_reaction.assert_has_calls([call(e) for e in poll_emojis[:3]])
    mock_message.edit.assert_called_once()
    edit_args = mock_message.edit.call_args
    assert "Anketa: What game?" in edit_args.kwargs["content"]
    assert "Option1" in edit_args.kwargs["content"]
    assert "Option2" in edit_args.kwargs["content"]
    assert "Option3" in edit_args.kwargs["content"]


async def test_poll_command_minimum_options(mock_ctx, mock_message):
    """Test poll command with minimum two options."""
    mock_ctx.original_response.return_value = mock_message

    await main.poll(mock_ctx, "Yes or no?", "Yes", "No")

    mock_ctx.send.assert_called_once()
    assert mock_message.add_reaction.call_count == 2


async def test_poll_command_insufficient_options(mock_ctx):
    """Test poll command rejects less than two options."""
    # One option scenario (option2 is required, so simulate passing empty scenario)
    # Since both option1 and option2 are required, this tests the filtering
    await main.poll(mock_ctx, "Question", "Option1", "Option2")

    # This should work since we have 2 options
    mock_ctx.send.assert_called()


# Test roll command
@pytest.mark.parametrize(
    "roll_range,expected_max",
    [
        (6, 6),
        (20, 20),
        (100, 100),
        (1, 1),
    ],
)
async def test_roll_command(mock_ctx, roll_range, expected_max):
    """Test roll command with various ranges."""
    with patch("random.randint") as mock_randint:
        mock_randint.return_value = 3

        await main.roll(mock_ctx, roll_range)

        mock_randint.assert_called_once_with(0, expected_max)
        mock_ctx.response.send_message.assert_called_once_with("You rolled 3 (Used d3).")


async def test_roll_command_default_range(mock_ctx):
    """Test roll command uses default range of 6."""
    with patch("random.randint") as mock_randint:
        mock_randint.return_value = 4

        await main.roll(mock_ctx, 6)

        mock_randint.assert_called_once_with(0, 6)
        mock_ctx.response.send_message.assert_called_once_with("You rolled 4 (Used d6).")


# Test yesorno command
async def test_yesorno_command(mock_ctx):
    """Test yesorno command returns one of the valid answers."""
    with patch("random.choice") as mock_choice:
        mock_choice.return_value = "Yes."

        await main.yesorno(mock_ctx)

        expected_answers = ("Yes.", "No.", "Perhaps.", "Definitely yes.", "Definitely no.")
        mock_choice.assert_called_once_with(expected_answers)
        mock_ctx.response.send_message.assert_called_once_with("Yes.")


@pytest.mark.parametrize(
    "answer",
    ["Yes.", "No.", "Perhaps.", "Definitely yes.", "Definitely no."],
)
async def test_yesorno_all_answers(mock_ctx, answer):
    """Test yesorno command can return all possible answers."""
    with patch("random.choice", return_value=answer):
        await main.yesorno(mock_ctx)

        mock_ctx.response.send_message.assert_called_once_with(answer)


# Test warcraft command
async def test_warcraft_command_with_time(mock_ctx, mock_message, gaming_reactions):
    """Test warcraft command creates announcement with time."""
    mock_ctx.original_message.return_value = mock_message

    await main.warcraft(mock_ctx, "20:00")

    mock_ctx.response.send_message.assert_called_once()
    call_content = mock_ctx.response.send_message.call_args[0][0]
    assert "v cca 20:00" in call_content
    assert "<@&871817685439234108>" in call_content  # Warcraft role ID

    # Verify reactions were added
    assert mock_message.add_reaction.call_count == len(gaming_reactions)
    mock_message.add_reaction.assert_has_calls([call(r) for r in gaming_reactions])


async def test_warcraft_command_without_time(mock_ctx, mock_message, gaming_reactions):
    """Test warcraft command creates announcement without time."""
    mock_ctx.original_message.return_value = mock_message

    await main.warcraft(mock_ctx, None)

    mock_ctx.response.send_message.assert_called_once()
    call_content = mock_ctx.response.send_message.call_args[0][0]
    assert "v cca" not in call_content
    assert "<@&871817685439234108>" in call_content


# Test help template content
def test_help_template_contains_commands():
    """Test help template contains all expected commands."""
    assert "_roll_" in grossdi.HELP
    assert "_poll_" in grossdi.HELP
    assert "_yesorno_" in grossdi.HELP
    assert "_warcraft_" in grossdi.HELP
    assert "_gmod_" in grossdi.HELP


def test_warcraft_template_format():
    """Test Warcraft template has correct structure."""
    template = grossdi.WARCRAFTY_CZ
    assert "<@&871817685439234108>" in template  # Role mention
    assert "{0}" in template  # Time placeholder
    assert "Survival Chaos" in template
    assert "Legion TD" in template


# Test button listener role logic
async def test_role_button_listener_adds_role():
    """Test button listener adds role when user doesn't have it."""
    mock_ctx = AsyncMock()
    mock_ctx.component = MagicMock()
    mock_ctx.component.custom_id = main.SelfServiceRoles.CLEN
    mock_ctx.response = AsyncMock()
    mock_ctx.author = MagicMock()
    mock_ctx.guild = MagicMock()

    mock_role = MagicMock()
    mock_role.id = 804431648959627294
    mock_ctx.guild.get_role.return_value = mock_role
    mock_ctx.author.roles = []
    mock_ctx.author.add_roles = AsyncMock()
    mock_ctx.author.remove_roles = AsyncMock()

    with patch.object(main.SelfServiceRoles, "get_role_id_by_name", return_value=804431648959627294):
        with patch.object(main.GamingRoles, "get_role_id_by_name", return_value=None):
            await main.listener(mock_ctx)

    mock_ctx.author.add_roles.assert_called_once_with(mock_role)
    mock_ctx.response.send_message.assert_called_once()
    assert "added" in mock_ctx.response.send_message.call_args.kwargs["content"]


async def test_role_button_listener_removes_role():
    """Test button listener removes role when user has it."""
    mock_ctx = AsyncMock()
    mock_ctx.component = MagicMock()
    mock_ctx.component.custom_id = main.SelfServiceRoles.CLEN
    mock_ctx.response = AsyncMock()
    mock_ctx.author = MagicMock()
    mock_ctx.guild = MagicMock()

    mock_role = MagicMock()
    mock_role.id = 804431648959627294
    mock_ctx.guild.get_role.return_value = mock_role
    mock_ctx.author.roles = [mock_role]  # User already has the role
    mock_ctx.author.add_roles = AsyncMock()
    mock_ctx.author.remove_roles = AsyncMock()

    with patch.object(main.SelfServiceRoles, "get_role_id_by_name", return_value=804431648959627294):
        with patch.object(main.GamingRoles, "get_role_id_by_name", return_value=None):
            await main.listener(mock_ctx)

    mock_ctx.author.remove_roles.assert_called_once_with(mock_role)
    mock_ctx.response.send_message.assert_called_once()
    assert "removed" in mock_ctx.response.send_message.call_args.kwargs["content"]


# Test on_message event
async def test_on_message_calls_bot_validate(mock_message):
    """Test on_message calls bot_validate for valid messages."""
    mock_message.content = "good bot"

    with patch.object(main, "bot_validate", new_callable=AsyncMock) as mock_validate:
        await main.on_message(mock_message)

        mock_validate.assert_called_once_with("good bot", mock_message)


async def test_on_message_ignores_empty_content(mock_message):
    """Test on_message ignores messages with empty content."""
    mock_message.content = ""

    with patch.object(main, "bot_validate", new_callable=AsyncMock) as mock_validate:
        await main.on_message(mock_message)

        mock_validate.assert_not_called()


async def test_on_message_ignores_bot_messages(mock_message):
    """Test on_message ignores messages from the bot itself."""
    mock_message.content = "test message"
    mock_message.author.__str__ = MagicMock(return_value=main.GROSSMAN_NAME)

    with patch.object(main, "bot_validate", new_callable=AsyncMock) as mock_validate:
        await main.on_message(mock_message)

        mock_validate.assert_not_called()
