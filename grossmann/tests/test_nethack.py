"""Tests for NetHack module functionality."""

import pytest
import disnake
from disnake.ext import commands
import discord.ext.test as dpytest
from unittest.mock import AsyncMock, patch, MagicMock
from PIL import Image
import nethack_module


@pytest.fixture
async def bot():
    """Create a test bot instance with NetHack commands."""
    intents = disnake.Intents.all()
    intents.message_content = True

    bot = commands.Bot(intents=intents, test_guilds=[dpytest.get_config().guilds])

    # Setup NetHack commands
    nethack_module.setup_nethack_commands(bot, [dpytest.get_config().guilds[0]])

    dpytest.configure(bot)
    yield bot
    await dpytest.empty_queue()


async def test_nethack_start_command_admin(bot):
    """Test NetHack start command with admin permissions."""
    guild = dpytest.get_config().client.guilds[0]
    channel = guild.text_channels[0]

    # Mock admin role
    admin_role = MagicMock()
    admin_role.id = nethack_module.ADMIN_ROLE_ID

    member = guild.members[0]
    member.roles = [admin_role]

    # Mock the allowed channel
    with patch.object(nethack_module, "ALLOWED_CHANNEL_ID", channel.id):
        with patch("nethack_module.start_nethack") as mock_start:
            mock_start.return_value = "NetHack started successfully"

            interaction = dpytest.get_application_command_context(
                "nethack start", guild=guild, channel=channel, user=member
            )

            # Execute the command
            nethack_cmd = bot.get_slash_command("nethack")
            start_cmd = None
            for cmd in nethack_cmd.children.values():
                if cmd.name == "start":
                    start_cmd = cmd
                    break

            assert start_cmd is not None

            with patch.object(interaction, "response") as mock_response:
                mock_response.defer = AsyncMock()
                with patch.object(interaction, "followup") as mock_followup:
                    mock_followup.send = AsyncMock()

                    await start_cmd(interaction)

                    mock_response.defer.assert_called_once()
                    mock_start.assert_called_once()


async def test_nethack_start_command_wrong_channel(bot):
    """Test NetHack start command in wrong channel."""
    guild = dpytest.get_config().client.guilds[0]
    channel = guild.text_channels[0]

    # Set a different allowed channel ID
    with patch.object(nethack_module, "ALLOWED_CHANNEL_ID", 999999):
        interaction = dpytest.get_application_command_context(
            "nethack start", guild=guild, channel=channel, user=guild.members[0]
        )

        nethack_cmd = bot.get_slash_command("nethack")
        start_cmd = None
        for cmd in nethack_cmd.children.values():
            if cmd.name == "start":
                start_cmd = cmd
                break

        with patch.object(interaction, "response") as mock_response:
            mock_response.send_message = AsyncMock()

            await start_cmd(interaction)

            mock_response.send_message.assert_called_with(
                "This command can only be used in the designated NetHack channel.", ephemeral=True
            )


async def test_nethack_start_command_no_admin(bot):
    """Test NetHack start command without admin permissions."""
    guild = dpytest.get_config().client.guilds[0]
    channel = guild.text_channels[0]
    member = guild.members[0]
    member.roles = []  # No admin role

    with patch.object(nethack_module, "ALLOWED_CHANNEL_ID", channel.id):
        interaction = dpytest.get_application_command_context(
            "nethack start", guild=guild, channel=channel, user=member
        )

        nethack_cmd = bot.get_slash_command("nethack")
        start_cmd = None
        for cmd in nethack_cmd.children.values():
            if cmd.name == "start":
                start_cmd = cmd
                break

        with patch.object(interaction, "response") as mock_response:
            mock_response.send_message = AsyncMock()

            await start_cmd(interaction)

            mock_response.send_message.assert_called_with(
                "You do not have permission to start NetHack.", ephemeral=True
            )


async def test_nethack_key_command(bot):
    """Test NetHack key command."""
    guild = dpytest.get_config().client.guilds[0]
    channel = guild.text_channels[0]
    member = guild.members[0]

    with patch.object(nethack_module, "ALLOWED_CHANNEL_ID", channel.id):
        with patch("nethack_module.send_key") as mock_send_key:
            mock_send_key.return_value = Image.new("RGB", (100, 100))

            interaction = dpytest.get_application_command_context(
                "nethack key", guild=guild, channel=channel, user=member
            )

            nethack_cmd = bot.get_slash_command("nethack")
            key_cmd = None
            for cmd in nethack_cmd.children.values():
                if cmd.name == "key":
                    key_cmd = cmd
                    break

            with patch.object(interaction, "response") as mock_response:
                mock_response.defer = AsyncMock()
                with patch.object(interaction, "followup") as mock_followup:
                    mock_followup.send = AsyncMock()

                    await key_cmd(interaction, "h", "none")

                    mock_response.defer.assert_called_once()
                    mock_send_key.assert_called_with("h", "none")


async def test_nethack_status_command(bot):
    """Test NetHack status command."""
    guild = dpytest.get_config().client.guilds[0]
    channel = guild.text_channels[0]
    member = guild.members[0]

    with patch.object(nethack_module, "ALLOWED_CHANNEL_ID", channel.id):
        with patch("nethack_module.nethack_proc", None):
            interaction = dpytest.get_application_command_context(
                "nethack status", guild=guild, channel=channel, user=member
            )

            nethack_cmd = bot.get_slash_command("nethack")
            status_cmd = None
            for cmd in nethack_cmd.children.values():
                if cmd.name == "status":
                    status_cmd = cmd
                    break

            with patch.object(interaction, "response") as mock_response:
                mock_response.defer = AsyncMock()
                with patch.object(interaction, "followup") as mock_followup:
                    mock_followup.send = AsyncMock()

                    await status_cmd(interaction)

                    mock_response.defer.assert_called_once()
                    mock_followup.send.assert_called_with("NetHack is not running.")


def test_is_admin():
    """Test admin role checking."""
    # Mock interaction with admin role
    mock_inter = MagicMock()
    admin_role = MagicMock()
    admin_role.id = nethack_module.ADMIN_ROLE_ID
    mock_inter.author.roles = [admin_role]

    assert nethack_module.is_admin(mock_inter) is True

    # Mock interaction without admin role
    mock_inter.author.roles = []
    assert nethack_module.is_admin(mock_inter) is False


def test_is_correct_channel():
    """Test channel checking."""
    mock_inter = MagicMock()
    mock_inter.channel_id = nethack_module.ALLOWED_CHANNEL_ID

    assert nethack_module.is_correct_channel(mock_inter) is True

    mock_inter.channel_id = 999999
    assert nethack_module.is_correct_channel(mock_inter) is False


async def test_start_nethack():
    """Test NetHack start function."""
    with patch("pexpect.spawn") as mock_spawn:
        with patch("nethack_module.nethack_proc", None):
            mock_process = MagicMock()
            mock_process.read_nonblocking.return_value = "test output"
            mock_spawn.return_value = mock_process

            with patch("nethack_module.render_screen") as mock_render:
                mock_render.return_value = "rendered screen"

                result = await nethack_module.start_nethack()

                assert result == "rendered screen"
                mock_spawn.assert_called_once()


async def test_stop_nethack():
    """Test NetHack stop function."""
    mock_process = MagicMock()
    mock_process.terminate = MagicMock()
    mock_process.isalive.return_value = False

    with patch("nethack_module.nethack_proc", mock_process):
        result = await nethack_module.stop_nethack()

        assert result == "NetHack stopped."
        mock_process.terminate.assert_called_once()


async def test_send_key():
    """Test key sending functionality."""
    mock_process = MagicMock()
    mock_process.send = MagicMock()
    mock_process.read_nonblocking.return_value = "output"

    with patch("nethack_module.nethack_proc", mock_process):
        with patch("nethack_module.render_screen") as mock_render:
            mock_render.return_value = "rendered"

            result = await nethack_module.send_key("h", "none")

            assert result == "rendered"
            mock_process.send.assert_called_with("h")


async def test_send_key_with_modifier():
    """Test key sending with modifiers."""
    mock_process = MagicMock()
    mock_process.sendcontrol = MagicMock()
    mock_process.send = MagicMock()
    mock_process.read_nonblocking.return_value = "output"

    with patch("nethack_module.nethack_proc", mock_process):
        with patch("nethack_module.render_screen") as mock_render:
            mock_render.return_value = "rendered"

            # Test CTRL modifier
            await nethack_module.send_key("c", "CTRL")
            mock_process.sendcontrol.assert_called_with("c")

            # Test ALT modifier
            await nethack_module.send_key("h", "ALT")
            mock_process.send.assert_called_with("\x1bh")


def test_render_pyte_to_image():
    """Test pyte screen to image rendering."""
    # Mock screen object
    mock_screen = MagicMock()
    mock_screen.buffer = {}

    # Create mock character
    mock_char = MagicMock()
    mock_char.data = "X"
    mock_char.fg = "white"

    # Setup buffer
    mock_row = {0: mock_char}
    mock_screen.buffer = {0: mock_row}

    with patch("PIL.ImageFont.truetype") as mock_font:
        mock_font.return_value.getbbox.return_value = (0, 0, 10, 10)

        result = nethack_module.render_pyte_to_image(mock_screen)

        assert isinstance(result, Image.Image)


async def test_send_output_to_channel_image():
    """Test sending image output to channel."""
    mock_inter = MagicMock()
    mock_inter.followup.send = AsyncMock()

    test_image = Image.new("RGB", (100, 100))

    await nethack_module.send_output_to_channel(mock_inter, test_image)

    mock_inter.followup.send.assert_called_once()
    # Check that a file was sent
    args, kwargs = mock_inter.followup.send.call_args
    assert "file" in kwargs


async def test_send_output_to_channel_text():
    """Test sending text output to channel."""
    mock_inter = MagicMock()
    mock_inter.followup.send = AsyncMock()

    await nethack_module.send_output_to_channel(mock_inter, "Test message")

    mock_inter.followup.send.assert_called_with("Test message")


if __name__ == "__main__":
    pytest.main([__file__])
