"""Tests for NetHack module functionality."""

import sys

import pytest
import disnake
from disnake.ext import commands
from unittest.mock import patch, MagicMock
from PIL import Image
import nethack_module
from conftest import TEST_ADMIN_ROLE_ID, TEST_ALLOWED_CHANNEL_ID


@pytest.fixture
async def bot():
    """Create a test bot instance with NetHack commands."""
    intents = disnake.Intents.all()
    intents.message_content = True

    bot = commands.Bot(intents=intents)

    # Setup NetHack commands
    nethack_module.setup_nethack_commands(bot, [])

    yield bot


async def test_nethack_start_command_admin(bot, mock_admin_interaction):
    """Test NetHack start command with admin permissions."""
    # Mock the allowed channel and admin role IDs
    with patch.object(nethack_module, "ALLOWED_CHANNEL_ID", TEST_ALLOWED_CHANNEL_ID):
        with patch.object(nethack_module, "ADMIN_ROLE_ID", TEST_ADMIN_ROLE_ID):
            with patch("nethack_module.start_nethack") as mock_start:
                mock_start.return_value = "NetHack started successfully"

                # Execute the command
                nethack_cmd = bot.get_slash_command("nethack")
                start_cmd = None
                for cmd in nethack_cmd.children.values():
                    if cmd.name == "start":
                        start_cmd = cmd
                        break

                assert start_cmd is not None

                await start_cmd(mock_admin_interaction)

                mock_admin_interaction.response.defer.assert_called_once()
                mock_start.assert_called_once()


async def test_nethack_start_command_wrong_channel(bot, mock_wrong_channel_interaction):
    """Test NetHack start command in wrong channel."""
    # Set a different allowed channel ID
    with patch.object(nethack_module, "ALLOWED_CHANNEL_ID", TEST_ALLOWED_CHANNEL_ID):
        nethack_cmd = bot.get_slash_command("nethack")
        start_cmd = None
        for cmd in nethack_cmd.children.values():
            if cmd.name == "start":
                start_cmd = cmd
                break

        await start_cmd(mock_wrong_channel_interaction)

        mock_wrong_channel_interaction.response.send_message.assert_called_with(
            "This command can only be used in the designated NetHack channel.", ephemeral=True
        )


async def test_nethack_start_command_no_admin(bot, mock_interaction):
    """Test NetHack start command without admin permissions."""
    with patch.object(nethack_module, "ALLOWED_CHANNEL_ID", TEST_ALLOWED_CHANNEL_ID):
        with patch.object(nethack_module, "ADMIN_ROLE_ID", TEST_ADMIN_ROLE_ID):
            nethack_cmd = bot.get_slash_command("nethack")
            start_cmd = None
            for cmd in nethack_cmd.children.values():
                if cmd.name == "start":
                    start_cmd = cmd
                    break

            await start_cmd(mock_interaction)

            mock_interaction.response.send_message.assert_called_with(
                "You do not have permission to start NetHack.", ephemeral=True
            )


async def test_nethack_key_command(bot, mock_interaction):
    """Test NetHack key command."""
    with patch.object(nethack_module, "ALLOWED_CHANNEL_ID", TEST_ALLOWED_CHANNEL_ID):
        with patch("nethack_module.send_key") as mock_send_key:
            mock_send_key.return_value = Image.new("RGB", (100, 100))

            nethack_cmd = bot.get_slash_command("nethack")
            key_cmd = None
            for cmd in nethack_cmd.children.values():
                if cmd.name == "key":
                    key_cmd = cmd
                    break

            await key_cmd(mock_interaction, "h", "none")

            mock_interaction.response.defer.assert_called_once()
            mock_send_key.assert_called_with("h", "none")


async def test_nethack_status_command(bot, mock_interaction):
    """Test NetHack status command."""
    with patch.object(nethack_module, "ALLOWED_CHANNEL_ID", TEST_ALLOWED_CHANNEL_ID):
        with patch("nethack_module.nethack_proc", None):
            nethack_cmd = bot.get_slash_command("nethack")
            status_cmd = None
            for cmd in nethack_cmd.children.values():
                if cmd.name == "status":
                    status_cmd = cmd
                    break

            await status_cmd(mock_interaction)

            mock_interaction.response.defer.assert_called_once()
            mock_interaction.followup.send.assert_called_with("NetHack is not running.")


def test_is_admin():
    """Test admin role checking."""
    with patch.object(nethack_module, "ADMIN_ROLE_ID", TEST_ADMIN_ROLE_ID):
        # Mock interaction with admin role
        mock_inter = MagicMock()
        admin_role = MagicMock()
        admin_role.id = TEST_ADMIN_ROLE_ID
        mock_inter.author.roles = [admin_role]

        assert nethack_module.is_admin(mock_inter) is True

        # Mock interaction without admin role
        mock_inter.author.roles = []
        assert nethack_module.is_admin(mock_inter) is False


def test_is_correct_channel():
    """Test channel checking."""
    with patch.object(nethack_module, "ALLOWED_CHANNEL_ID", TEST_ALLOWED_CHANNEL_ID):
        mock_inter = MagicMock()
        mock_inter.channel_id = TEST_ALLOWED_CHANNEL_ID

        assert nethack_module.is_correct_channel(mock_inter) is True

        mock_inter.channel_id = 999999
        assert nethack_module.is_correct_channel(mock_inter) is False


@pytest.mark.skipif(sys.platform == "win32", reason="Nethack is currently not supported on Windows")
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


@pytest.mark.skipif(sys.platform == "win32", reason="Nethack is currently not supported on Windows")
async def test_stop_nethack():
    """Test NetHack stop function."""
    mock_process = MagicMock()
    mock_process.terminate = MagicMock()
    mock_process.isalive.return_value = False

    with patch("nethack_module.nethack_proc", mock_process):
        result = await nethack_module.stop_nethack()

        assert result == "NetHack stopped."
        mock_process.terminate.assert_called_once()


@pytest.mark.skipif(sys.platform == "win32", reason="Nethack is currently not supported on Windows")
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


@pytest.mark.skipif(sys.platform == "win32", reason="Nethack is currently not supported on Windows")
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


@pytest.mark.skipif(sys.platform == "win32", reason="Nethack is currently not supported on Windows")
async def test_send_output_to_channel_image(mock_interaction):
    """Test sending image output to channel."""
    test_image = Image.new("RGB", (100, 100))

    await nethack_module.send_output_to_channel(mock_interaction, test_image)
    await nethack_module.send_output_to_channel(mock_interaction, test_image)

    mock_interaction.followup.send.assert_called_once()
    # Check that a file was sent
    args, kwargs = mock_interaction.followup.send.call_args
    assert "file" in kwargs


async def test_send_output_to_channel_text(mock_interaction):
    """Test sending text output to channel."""
    await nethack_module.send_output_to_channel(mock_interaction, "Test message")

    mock_interaction.followup.send.assert_called_with("Test message")
