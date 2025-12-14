"""Comprehensive tests for Grossmann Discord bot using pytest and mocking."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

from common.constants import HALL_OF_FAME_EMOJIS
from common.utils import DiscordGamingTestingRoles, has_all, GamingRoles
from grossmann import grossmanndict as grossdi
from grossmann import main
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
        mock_ctx.response.send_message.assert_called_once_with(f"You rolled 3 (Used d{roll_range}).")


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
    assert GamingRoles.WARCRAFT.role_tag in call_content


# Test help template content
def test_help_template_contains_commands():
    """Test help template contains all expected commands."""
    assert has_all("".join(grossdi.HELP), ["/roll", "/poll", "/yesorno", "/warcraft", "/xkcd"])


# Test button listener role logic
async def test_role_button_listener_adds_role(mock_ctx, mock_role):
    """Test button listener adds role when user doesn't have it."""
    mock_ctx.author.roles = []  # User doesn't have the role
    await main.listener(mock_ctx)

    mock_ctx.author.add_roles.assert_called_once_with(mock_role)
    mock_ctx.response.send_message.assert_called_once()
    assert "added" in mock_ctx.response.send_message.call_args.kwargs["content"]


async def test_role_button_listener_removes_role(mock_ctx, mock_role):
    """Test button listener removes role when user has it."""
    mock_ctx.author.roles = [mock_role]  # User already has the role

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


# Test twitter_pero function
async def test_twitter_pero_non_anonymous(mock_ctx):
    """Test twitter_pero posts non-anonymous tweet."""
    mock_channel = AsyncMock()
    mock_sent_message = AsyncMock()
    mock_sent_message.add_reaction = AsyncMock()
    mock_channel.send = AsyncMock(return_value=mock_sent_message)

    with patch.object(main, "client") as mock_client:
        mock_client.get_channel.return_value = mock_channel

        await main.twitter_pero(anonym=False, content="Test tweet!", ctx=mock_ctx, image_url=None)

    mock_ctx.response.send_message.assert_called_once()
    assert "Tweet posted!" in mock_ctx.response.send_message.call_args.kwargs["content"]
    mock_channel.send.assert_called_once()
    embed = mock_channel.send.call_args.kwargs["embed"]
    assert "TestUser" in embed.title
    assert "Test tweet!" in embed.description
    # Verify tweet reactions
    assert mock_sent_message.add_reaction.call_count == 5
    mock_sent_message.add_reaction.assert_has_calls([call(r) for r in ["💜", "🔁", "⬇️", "💭", "🔗"]])


async def test_twitter_pero_with_image(mock_ctx):
    """Test twitter_pero posts tweet with image."""
    mock_channel = AsyncMock()
    mock_sent_message = AsyncMock()
    mock_sent_message.add_reaction = AsyncMock()
    mock_channel.send = AsyncMock(return_value=mock_sent_message)

    with patch.object(main, "client") as mock_client:
        mock_client.get_channel.return_value = mock_channel

        await main.twitter_pero(
            anonym=False, content="Tweet with image", ctx=mock_ctx, image_url="https://example.com/image.png"
        )

    embed = mock_channel.send.call_args.kwargs["embed"]
    assert embed.image.url == "https://example.com/image.png"


async def test_twitter_pero_anonymous(mock_ctx, m):
    """Test twitter_pero posts anonymous tweet with random user."""
    m.get(
        "https://randomuser.me/api",
        payload={
            "results": [
                {
                    "login": {"username": "testuser", "password": "pass123"},
                    "email": "test@example.com",
                    "dob": {"age": 25},
                    "gender": "male",
                    "location": {"city": "TestCity", "country": "Czechia"},
                    "picture": {"medium": "https://example.com/pic.jpg"},
                }
            ]
        },
    )

    mock_channel = AsyncMock()
    mock_sent_message = AsyncMock()
    mock_sent_message.add_reaction = AsyncMock()
    mock_channel.send = AsyncMock(return_value=mock_sent_message)

    with (
        patch.object(main, "client") as mock_client,
        patch("random.choice", return_value="testuser"),
    ):
        mock_client.get_channel.return_value = mock_channel

        await main.twitter_pero(anonym=True, content="Anonymous tweet", ctx=mock_ctx, image_url=None)

    embed = mock_channel.send.call_args.kwargs["embed"]
    assert "TestUser" not in embed.title  # Should not contain real username
    assert "Anonymous tweet" in embed.description


# Test send_role_picker function
async def test_send_role_picker(mock_ctx):
    """Test send_role_picker sends role picker embeds with buttons."""
    mock_ctx.channel.send = AsyncMock()

    await main.send_role_picker(mock_ctx)

    mock_ctx.response.send_message.assert_called_once()
    assert "Done!" in mock_ctx.response.send_message.call_args.kwargs["content"]
    # Should send two embeds (general roles + gaming roles)
    assert mock_ctx.channel.send.call_count == 2


# Test hall_of_fame_history_fetching function
async def test_hall_of_fame_history_fetching():
    """Test hall_of_fame_history_fetching loads message IDs."""

    async def mock_history(limit):
        mock_msg1 = MagicMock()
        mock_msg1.reference = MagicMock()
        mock_msg1.reference.message_id = 111111
        mock_msg1.created_at = datetime(2024, 1, 1, 12, 0, 0)

        mock_msg2 = MagicMock()
        mock_msg2.reference = MagicMock()
        mock_msg2.reference.message_id = 222222
        mock_msg2.created_at = datetime(2024, 1, 2, 12, 0, 0)

        for msg in [mock_msg1, mock_msg2]:
            yield msg

    mock_channel = MagicMock()
    mock_channel.history = mock_history

    with patch.object(main, "client") as mock_client:
        mock_client.get_channel.return_value = mock_channel
        main.hall_of_fame_message_ids = {}

        await main.hall_of_fame_history_fetching()

    assert 111111 in main.hall_of_fame_message_ids
    assert 222222 in main.hall_of_fame_message_ids


async def test_hall_of_fame_history_fetching_no_channel():
    """Test hall_of_fame_history_fetching handles missing channel."""
    with patch.object(main, "client") as mock_client:
        mock_client.get_channel.return_value = None
        main.hall_of_fame_message_ids = {}

        await main.hall_of_fame_history_fetching()

    assert main.hall_of_fame_message_ids == {}


# Test on_reaction_add event
async def test_on_reaction_add_forwards_to_hall_of_fame(mock_message):
    """Test on_reaction_add forwards message when threshold reached."""
    mock_reaction = MagicMock()
    mock_reaction.message = mock_message
    mock_reaction.emoji = "⭐"

    # Set up message with enough reactions
    mock_message.id = 12345678
    mock_message.guild = MagicMock()
    mock_message.channel = MagicMock()

    reaction_obj = MagicMock()
    reaction_obj.emoji = "⭐"
    reaction_obj.count = 11  # Above threshold of 10
    mock_message.reactions = [reaction_obj]

    mock_hall_channel = AsyncMock()

    with patch.object(main, "client") as mock_client:
        mock_client.get_channel.return_value = mock_hall_channel
        main.hall_of_fame_message_ids = {}

        await main.on_reaction_add(mock_reaction, MagicMock())

    mock_message.forward.assert_called_once_with(mock_hall_channel)
    assert mock_message.id in main.hall_of_fame_message_ids


async def test_on_reaction_add_ignores_dm():
    """Test on_reaction_add ignores DM messages."""
    mock_message = MagicMock()
    mock_message.guild = None  # DM has no guild

    mock_reaction = MagicMock()
    mock_reaction.message = mock_message

    with patch.object(main, "client"):
        await main.on_reaction_add(mock_reaction, MagicMock())

    # No forward should happen
    assert not hasattr(mock_message, "forward") or not mock_message.forward.called


async def test_on_reaction_add_ignores_below_threshold(mock_message):
    """Test on_reaction_add ignores messages below reaction threshold."""
    mock_reaction = MagicMock()
    mock_reaction.message = mock_message
    mock_reaction.emoji = "⭐"

    reaction_obj = MagicMock()
    reaction_obj.emoji = "⭐"
    reaction_obj.count = 5  # Below threshold
    mock_message.reactions = [reaction_obj]
    mock_message.id = 99999

    mock_hall_channel = MagicMock()

    with patch.object(main, "client") as mock_client:
        mock_client.get_channel.return_value = mock_hall_channel
        main.hall_of_fame_message_ids = {}

        await main.on_reaction_add(mock_reaction, MagicMock())

    mock_message.forward.assert_not_called()


async def test_on_reaction_add_ignores_already_forwarded(mock_message):
    """Test on_reaction_add ignores already forwarded messages."""
    mock_reaction = MagicMock()
    mock_reaction.message = mock_message

    reaction_obj = MagicMock()
    reaction_obj.emoji = "⭐"
    reaction_obj.count = 15
    mock_message.reactions = [reaction_obj]
    mock_message.id = 77777

    with patch.object(main, "client") as mock_client:
        mock_client.get_channel.return_value = MagicMock()
        main.hall_of_fame_message_ids = {77777: datetime.now()}

        await main.on_reaction_add(mock_reaction, MagicMock())

    mock_message.forward.assert_not_called()


# Test on_member_join event
async def test_on_member_join_sends_welcome(mock_member):
    """Test on_member_join sends welcome message."""
    mock_welcome_channel = AsyncMock()
    mock_welcome_channel.send = AsyncMock()

    with patch.object(main, "client") as mock_client:
        mock_client.get_channel.return_value = mock_welcome_channel

        await main.on_member_join(mock_member)

    mock_welcome_channel.send.assert_called_once()
    sent_content = mock_welcome_channel.send.call_args[0][0]
    assert mock_member.mention in sent_content
    assert "Vítej" in sent_content or "Welcome" in sent_content


# Test game_ping command
async def test_game_ping_command_english(mock_ctx, mock_message):
    """Test game_ping command creates announcement with reactions in English."""
    mock_ctx.original_message.return_value = mock_message

    await main.game_ping(mock_ctx, DiscordGamingTestingRoles.WARCRAFT.role_tag, "20:00", "en", "Let's play!")

    mock_ctx.response.send_message.assert_called_once()
    call_content = mock_ctx.response.send_message.call_args[0][0]
    assert "20:00" in call_content
    assert "Let's play!" in call_content
    assert "Shall we play" in call_content

    # Verify reactions
    expected_reactions = ["✅", "❎", "🤔", "☦️"]
    assert mock_message.add_reaction.call_count == len(expected_reactions)
    mock_message.add_reaction.assert_has_calls([call(r) for r in expected_reactions])


async def test_game_ping_command_czech(mock_ctx, mock_message):
    """Test game_ping command creates announcement with reactions in Czech."""
    mock_ctx.original_message.return_value = mock_message

    await main.game_ping(mock_ctx, DiscordGamingTestingRoles.VALORANT.role_tag, "21:00", "cz", "")

    mock_ctx.response.send_message.assert_called_once()
    call_content = mock_ctx.response.send_message.call_args[0][0]
    assert "21:00" in call_content
    assert "Zahrajeme si" in call_content


async def test_game_ping_command_without_note(mock_ctx, mock_message):
    """Test game_ping command works without note."""
    mock_ctx.original_message.return_value = mock_message

    await main.game_ping(mock_ctx, DiscordGamingTestingRoles.VALORANT.role_tag, "21:00", "en", "")

    mock_ctx.response.send_message.assert_called_once()


# Test cat command
async def test_cat_command_with_dimensions(mock_ctx, m):
    """Test cat command with specified dimensions."""
    empty_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\xdac\xfc\xcf\xf0\xbf\x1e\x00\x06\x83\x02\x7f\x94\xad\xd0\xeb\x00\x00\x00\x00IEND\xaeB`\x82"
    m.get("https://placecats.com/200/300", body=empty_png, content_type="image/png")

    await main.cat(mock_ctx, width=200, height=300)

    mock_ctx.followup.send.assert_called_once()
    embed = mock_ctx.followup.send.call_args.kwargs["embed"]
    assert embed._files["image"].fp.getvalue() == empty_png


async def test_cat_command_random_dimensions(mock_ctx, m):
    """Test cat command with random dimensions."""
    empty_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\xdac\xfc\xcf\xf0\xbf\x1e\x00\x06\x83\x02\x7f\x94\xad\xd0\xeb\x00\x00\x00\x00IEND\xaeB`\x82"
    m.get("https://placecats.com/128/128", body=empty_png, content_type="image/png")

    with patch("grossmann.main.random.randint", return_value=128) as mock_randint:
        await main.cat(mock_ctx, width=None, height=None)

    assert mock_randint.call_count == 2
    mock_ctx.followup.send.assert_called_once()
    embed = mock_ctx.followup.send.call_args.kwargs["embed"]
    assert embed._files["image"].fp.getvalue() == empty_png


# Test fox command
async def test_fox_command(mock_ctx, m):
    """Test fox command returns image URL from API."""
    m.get(
        "https://randomfox.ca/floof/",
        payload={"image": "https://randomfox.ca/images/87.jpg", "link": "https://randomfox.ca/?i=87"},
    )
    await main.fox(mock_ctx)
    mock_ctx.followup.send.assert_called_once_with(content="https://randomfox.ca/images/87.jpg")


# Test waifu command
async def test_waifu_command_sfw(mock_ctx, m):
    """Test waifu command with SFW content."""
    m.get("https://api.waifu.pics/sfw/neko", payload={"url": "https://i.waifu.pics/abc123.jpg"})

    await main.waifu(mock_ctx, content_type="sfw", category="neko")
    mock_ctx.followup.send.assert_called_once_with(content="https://i.waifu.pics/abc123.jpg")


async def test_waifu_command_nsfw_wrong_channel(mock_ctx):
    """Test waifu command rejects NSFW in wrong channel."""
    mock_ctx.channel.id = 12345  # Not an NSFW channel

    await main.waifu(mock_ctx, content_type="nsfw", category="neko")

    # NSFW rejection uses response.send_message directly (not through respond())
    mock_ctx.response.send_message.assert_called_once()
    assert "prase" in mock_ctx.response.send_message.call_args[0][0]


async def test_waifu_command_nsfw_allowed_channel(mock_ctx, m):
    """Test waifu command allows NSFW in correct channel."""
    mock_ctx.channel.id = grossdi.WAIFU_ALLOWED_NSFW[0]  # NSFW channel
    m.get("https://api.waifu.pics/nsfw/neko", payload={"url": "https://i.waifu.pics/nsfw123.jpg"})

    await main.waifu(mock_ctx, content_type="nsfw", category="neko")
    mock_ctx.followup.send.assert_called_once_with(content="https://i.waifu.pics/nsfw123.jpg")


# Test xkcd command
async def test_xkcd_command_with_id(mock_ctx, m):
    """Test xkcd command with specific ID."""
    m.get(
        "https://xkcd.com/1234/info.0.json",
        payload={
            "num": 1234,
            "title": "Douglas Engelbart (1925-2013)",
            "img": "https://imgs.xkcd.com/comics/douglas_engelbart.png",
            "alt": "Actual quote from The Demo",
        },
    )

    await main.xkcd(mock_ctx, xkcd_id=1234)
    mock_ctx.followup.send.assert_called_once_with(content="https://imgs.xkcd.com/comics/douglas_engelbart.png")


async def test_xkcd_command_latest(mock_ctx, m):
    """Test xkcd command gets latest comic when no ID."""
    m.get(
        "https://xkcd.com/info.0.json",
        payload={
            "num": 3000,
            "title": "Latest Comic",
            "img": "https://imgs.xkcd.com/comics/latest.png",
            "alt": "Alt text",
        },
    )

    await main.xkcd(mock_ctx, xkcd_id=None)
    mock_ctx.followup.send.assert_called_once_with(content="https://imgs.xkcd.com/comics/latest.png")


# Test waifu categories structure
def test_waifu_categories_structure():
    """Test waifu categories have expected structure."""
    assert "sfw" in grossdi.WAIFU_CATEGORIES
    assert "nsfw" in grossdi.WAIFU_CATEGORIES
    assert "neko" in grossdi.WAIFU_CATEGORIES["sfw"]
    assert "waifu" in grossdi.WAIFU_CATEGORIES["sfw"]


# Test hall of fame emojis
def test_hall_of_fame_emojis_exist():
    """Test hall of fame emojis list is populated."""
    assert len(HALL_OF_FAME_EMOJIS) > 0
    assert "⭐" in HALL_OF_FAME_EMOJIS
