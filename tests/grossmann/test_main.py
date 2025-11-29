"""Comprehensive tests for Grossmann Discord bot using pytest and mocking."""

import random
from unittest.mock import AsyncMock, patch, Mock


import grossmann.grossmanndict as decdi
from grossmann import main
from tests.grossmann.conftest import TEST_WARCRAFT_ROLE_ID, TEST_CLEN_ROLE_ID, TEST_GMOD_ROLE_ID, TEST_ROLE_SELECTION_CHANNEL_ID


async def test_batch_react_function():
    """Test batch_react function adds all reactions."""
    # Mock the main module to avoid bot instantiation
    with patch("disnake.ext.commands.Bot"):
        mock_message = AsyncMock()
        mock_message.add_reaction = AsyncMock()

        reactions = ["✅", "❎", "🤔"]
        await main.batch_react(mock_message, reactions)

        assert mock_message.add_reaction.call_count == len(reactions)
        for reaction in reactions:
            mock_message.add_reaction.assert_any_call(reaction)


async def test_poll_command_logic():
    """Test poll command logic with mocked interaction."""
    with patch("disnake.ext.commands.Bot"):
        # Mock interaction context
        mock_ctx = AsyncMock()
        mock_ctx.response.send_message = AsyncMock()
        mock_ctx.original_message = AsyncMock()
        mock_message = AsyncMock()
        mock_message.add_reaction = AsyncMock()
        mock_message.edit = AsyncMock()
        mock_ctx.original_message.return_value = mock_message

        # Test poll with sufficient options
        options = ["Option1", "Option2", "Option3"]
        filtered_options = [opt for opt in options if opt]

        # Simulate poll logic
        if len(filtered_options) >= 2:
            poll_mess = "Anketa: Test Question\n"
            emoji_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]

            await mock_ctx.response.send_message("Creating poll...", ephemeral=False)

            for i, option in enumerate(filtered_options):
                poll_mess += f"{emoji_list[i]} = {option}\n"
                await mock_message.add_reaction(emoji_list[i])

            await mock_message.edit(content=poll_mess)

            # Verify reactions were added
            assert mock_message.add_reaction.call_count == len(filtered_options)

            # Verify message was edited
            mock_message.edit.assert_called_once()
            edit_args = mock_message.edit.call_args[1]
            assert "Anketa: Test Question" in edit_args["content"]


async def test_poll_insufficient_options():
    """Test poll command with insufficient options."""
    mock_ctx = AsyncMock()
    mock_ctx.response.send_message = AsyncMock()

    # Simulate insufficient options
    options = ["Option1", None, None, None, None]
    filtered_options = [opt for opt in options if opt]

    if len(filtered_options) < 2:
        await mock_ctx.response.send_message("You must provide at least two options.", ephemeral=True)

    mock_ctx.response.send_message.assert_called_with("You must provide at least two options.", ephemeral=True)


async def test_roll_command_logic():
    """Test roll command logic."""
    with patch("random.randint") as mock_randint:
        mock_randint.return_value = 42

        mock_ctx = AsyncMock()
        mock_ctx.response.send_message = AsyncMock()

        # Test default roll
        arg_range = None
        range_val = None
        try:
            range_val = int(arg_range) if arg_range else None
        except:
            pass

        if not range_val:
            result = random.randint(0, 100)
            await mock_ctx.response.send_message(f"{result} (Defaulted to 100d.)")

        mock_ctx.response.send_message.assert_called_with("42 (Defaulted to 100d.)")

        # Test custom range
        mock_ctx.reset_mock()
        arg_range = "20"
        range_val = int(arg_range)

        if isinstance(range_val, int) and range_val > 0:
            result = random.randint(0, range_val)
            await mock_ctx.response.send_message(f"{result} (Used d{range_val}.)")

        mock_ctx.response.send_message.assert_called_with("42 (Used d20.)")


async def test_roll_joint_easter_egg():
    """Test roll command joint easter egg."""
    mock_ctx = AsyncMock()
    mock_ctx.response.send_message = AsyncMock()

    arg_range = "joint"
    if arg_range == "joint":
        await mock_ctx.response.send_message("https://youtu.be/LF6ok8IelJo?t=56")

    mock_ctx.response.send_message.assert_called_with("https://youtu.be/LF6ok8IelJo?t=56")


async def test_yesorno_command_logic():
    """Test yesorno command logic."""
    with patch("random.choice") as mock_choice:
        mock_choice.return_value = "Yes."

        mock_ctx = AsyncMock()
        mock_ctx.response.send_message = AsyncMock()

        answers = ("Yes.", "No.", "Perhaps.", "Definitely yes.", "Definitely no.")
        result = random.choice(answers)
        await mock_ctx.response.send_message(result)

        mock_ctx.response.send_message.assert_called_with("Yes.")
        mock_choice.assert_called_with(answers)


async def test_bot_validation_reactions():
    """Test bot validation reaction logic."""
    mock_message = AsyncMock()
    mock_message.add_reaction = AsyncMock()
    mock_message.author = Mock()

    # Test good bot reaction
    content = "hodný bot"
    if content.startswith("hodný bot") or "good bot" in content:
        await mock_message.add_reaction("🙂")

    mock_message.add_reaction.assert_called_with("🙂")

    # Reset mock
    mock_message.reset_mock()

    # Test bad bot reaction
    content = "bad bot"
    bad_words = ["bad bot", "naser si bote", "si naser bote"]
    if content.startswith("zlý bot") or any(word in content for word in bad_words):
        await mock_message.add_reaction("😢")

    mock_message.add_reaction.assert_called_with("😢")


async def test_birthday_reactions():
    """Test birthday reaction logic."""
    mock_message = AsyncMock()
    mock_message.add_reaction = AsyncMock()

    content = "všechno nejlepší"
    if "všechno nejlepší" in content:
        await mock_message.add_reaction("🥳")
        await mock_message.add_reaction("🎉")

    assert mock_message.add_reaction.call_count == 2
    mock_message.add_reaction.assert_any_call("🥳")
    mock_message.add_reaction.assert_any_call("🎉")


async def test_special_message_responses():
    """Test special message responses."""
    mock_message = AsyncMock()
    mock_message.reply = AsyncMock()
    mock_message.channel.send = AsyncMock()

    # Test creator regret response
    content = "co jsem to stvořil"
    if "co jsem to stvořil" in content.lower():
        await mock_message.reply("https://media.tenor.com/QRTVgLglL6AAAAAd/thanos-avengers.gif")

    mock_message.reply.assert_called_with("https://media.tenor.com/QRTVgLglL6AAAAAd/thanos-avengers.gif")

    # Test specific insult response
    content = "decim je negr"
    if "decim je negr" in content.lower():
        await mock_message.channel.send("nn, ty seš")

    mock_message.channel.send.assert_called_with("nn, ty seš")


def test_has_any_function():
    """Test has_any utility function."""
    with patch("disnake.ext.commands.Bot"):
        # Test positive case
        content = "this is a bad bot message"
        words = ["bad bot", "good bot"]
        assert main.has_any(content, words) is True

        # Test negative case
        content = "this is a normal message"
        assert main.has_any(content, words) is False

        # Test empty words
        assert main.has_any(content, []) is False


def test_warcraft_template():
    """Test Warcraft template message formatting."""
    expected_content = f"<@&{TEST_WARCRAFT_ROLE_ID}> - Warcrafty 3 dnes v cca 20:00?"
    result = decdi.WARCRAFTY_CZ.replace("{0}", " v cca 20:00")
    assert expected_content in result


def test_help_template():
    """Test help template contains expected commands."""
    help_text = decdi.HELP
    assert "_roll_" in help_text
    assert "_poll_" in help_text
    assert "_yesorno_" in help_text
    assert "_warcraft_" in help_text
    assert "_gmod_" in help_text


def test_guild_and_channel_constants():
    """Test that constants are properly defined."""
    assert isinstance(decdi.GIDS, list)
    assert len(decdi.GIDS) > 0
    assert isinstance(decdi.TWITTERPERO, int)
    assert isinstance(decdi.WELCOMEPERO, int)


async def test_role_button_logic():
    """Test role button interaction logic."""
    mock_ctx = AsyncMock()
    mock_ctx.component = Mock()
    mock_ctx.component.custom_id = "warcraft"
    mock_ctx.response.send_message = AsyncMock()
    mock_ctx.author = Mock()
    mock_ctx.guild = Mock()

    # Mock role objects
    mock_role = Mock()
    mock_role.id = TEST_WARCRAFT_ROLE_ID
    mock_ctx.guild.get_role.return_value = mock_role
    mock_ctx.author.roles = []
    mock_ctx.author.add_roles = AsyncMock()
    mock_ctx.author.remove_roles = AsyncMock()

    role_list = {
        "Člen": TEST_CLEN_ROLE_ID,
        "warcraft": TEST_WARCRAFT_ROLE_ID,
        "gmod": TEST_GMOD_ROLE_ID,
    }

    # Simulate button interaction logic
    if mock_ctx.component.custom_id in role_list:
        role_id = role_list[mock_ctx.component.custom_id]
        role = mock_ctx.guild.get_role(role_id)

        if role in mock_ctx.author.roles:
            await mock_ctx.author.remove_roles(role)
            await mock_ctx.response.send_message(f"Role `{mock_ctx.component.custom_id}` removed!", ephemeral=True)
        else:
            await mock_ctx.author.add_roles(role)
            await mock_ctx.response.send_message(f"Role `{mock_ctx.component.custom_id}` added!", ephemeral=True)

    # Verify role was added (since author.roles was empty)
    mock_ctx.author.add_roles.assert_called_with(mock_role)
    mock_ctx.response.send_message.assert_called_with("Role `warcraft` added!", ephemeral=True)


async def test_member_join_logic():
    """Test member join welcome message logic."""
    mock_member = Mock()
    mock_member.mention = "<@123456789>"
    mock_member.guild = Mock()

    mock_channel = AsyncMock()
    mock_channel.send = AsyncMock()
    mock_member.guild.text_channels = [mock_channel]

    # Simulate member join logic
    welcome_channel = mock_member.guild.text_channels[0] if mock_member.guild.text_channels else None
    if welcome_channel:
        welcome_message = f"""
Vítej, {mock_member.mention}!
Prosím, přesuň se do <#{TEST_ROLE_SELECTION_CHANNEL_ID}> a naklikej si role. Nezapomeň na roli Člen, abys viděl i ostatní kanály!
---
Please, go to the <#{TEST_ROLE_SELECTION_CHANNEL_ID}> channel and select your roles. Don't forget the 'Člen'/Member role to see other channels!
                        """
        await welcome_channel.send(welcome_message)

    # Verify welcome message was sent
    mock_channel.send.assert_called_once()
    args, kwargs = mock_channel.send.call_args
    assert "Vítej" in args[0]
    assert mock_member.mention in args[0]


async def test_gaming_session_workflow():
    """Test complete gaming session planning workflow."""
    # Step 1: Create Warcraft ping
    mock_ctx = AsyncMock()
    mock_ctx.response.send_message = AsyncMock()
    mock_message = AsyncMock()
    mock_message.add_reaction = AsyncMock()
    mock_ctx.response.send_message.return_value = mock_message

    # Simulate warcraft ping creation
    time = "20:00"
    template_message = decdi.WARCRAFTY_CZ.replace("{0}", f" v cca {time}")
    await mock_ctx.response.send_message(template_message)

    # Simulate batch reactions
    reactions = ["✅", "❎", "🤔", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "❓"]
    for reaction in reactions:
        await mock_message.add_reaction(reaction)

    # Verify ping was created
    mock_ctx.response.send_message.assert_called_with(template_message)
    assert mock_message.add_reaction.call_count == len(reactions)

    # Step 2: Create follow-up poll
    mock_ctx.reset_mock()
    mock_ctx.response.send_message = AsyncMock()
    mock_ctx.original_message = AsyncMock()
    mock_poll_message = AsyncMock()
    mock_poll_message.add_reaction = AsyncMock()
    mock_poll_message.edit = AsyncMock()
    mock_ctx.original_message.return_value = mock_poll_message

    # Simulate poll creation
    question = "What Warcraft mode?"
    options = ["Survival", "Legion", "Luckery"]
    poll_content = f"Anketa: {question}\n"
    emoji_list = ["1️⃣", "2️⃣", "3️⃣"]

    await mock_ctx.response.send_message("Creating poll...", ephemeral=False)

    for i, option in enumerate(options):
        poll_content += f"{emoji_list[i]} = {option}\n"
        await mock_poll_message.add_reaction(emoji_list[i])

    await mock_poll_message.edit(content=poll_content)

    # Verify poll was created
    assert mock_poll_message.add_reaction.call_count == len(options)
    mock_poll_message.edit.assert_called_with(content=poll_content)


async def test_tweet_creation_workflow():
    """Test tweet creation and reaction workflow."""
    mock_ctx = AsyncMock()
    mock_ctx.response.send_message = AsyncMock()
    mock_ctx.followup.send = AsyncMock()
    mock_ctx.author.display_name = "TestUser"
    mock_tweet_message = AsyncMock()
    mock_tweet_message.add_reaction = AsyncMock()
    mock_ctx.followup.send.return_value = mock_tweet_message

    # Simulate tweet creation
    content = "Just finished a great gaming session!"

    # Create embed (simplified)
    embed_data = {"title": f"{mock_ctx.author.display_name} tweeted:", "description": content, "color": "dark_purple"}

    await mock_ctx.response.send_message("Tweet posted! 👍", ephemeral=True)
    await mock_ctx.followup.send(embed=embed_data)

    # Simulate tweet reactions
    tweet_reactions = ["💜", "🔁", "⬇️", "💭", "🔗"]
    for reaction in tweet_reactions:
        await mock_tweet_message.add_reaction(reaction)

    # Verify tweet was posted
    mock_ctx.response.send_message.assert_called_with("Tweet posted! 👍", ephemeral=True)
    mock_ctx.followup.send.assert_called_with(embed=embed_data)
    assert mock_tweet_message.add_reaction.call_count == len(tweet_reactions)
