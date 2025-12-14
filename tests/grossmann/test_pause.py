"""Tests for the pause functionality in Grossmann bot."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from grossmann import main
from grossmann import pause_persistence as pp
from grossmann.pause_persistence import PausedUser


@pytest.fixture
def temp_pause_file(tmp_path):
    """Create a temporary pause file for testing."""
    pause_file = tmp_path / "paused_users.json"
    with patch.object(pp, "_get_pause_file_path", return_value=pause_file):
        # Reset and reinitialize cache with the patched path
        pp._reset_cache()
        pp._init_cache()
        yield pause_file
        # Clean up cache after test
        pp._reset_cache()


@pytest.fixture
def mock_paused_role():
    """Create a mock Paused role."""
    role = MagicMock()
    role.id = 123456789
    role.position = 10
    return role


@pytest.fixture
def mock_ctx_for_pause(mock_paused_role):
    """Create a mock context for pause commands."""
    ctx = MagicMock()
    ctx.guild_id = 276720867344646144  # Kouzelnici
    ctx.guild.get_role.return_value = mock_paused_role
    ctx.me.top_role.position = 50
    ctx.author.id = 999888777
    ctx.author.__str__ = MagicMock(return_value="Admin#1234")
    ctx.response = AsyncMock()
    ctx.response.send_message = AsyncMock()
    return ctx


class TestPausePersistence:
    """Tests for pause_persistence module."""

    def test_get_paused_users_empty_file(self, temp_pause_file):
        """Test loading from non-existent file returns empty list."""
        result = pp.get_paused_users()
        assert result == []

    def test_add_and_get_paused_users(self, temp_pause_file):
        """Test adding and getting paused users."""
        pp.add_paused_user(123, 456, 1.0)

        result = pp.get_paused_users()
        assert len(result) == 1
        assert result[0].user_id == 123
        assert result[0].guild_id == 456

    def test_add_paused_user(self, temp_pause_file):
        """Test adding a paused user."""
        with patch("grossmann.pause_persistence.datetime") as mock_dt:
            mock_dt.now.return_value.timestamp.return_value = 1700000000.0
            mock_dt.fromtimestamp = datetime.fromtimestamp

            expires_at = pp.add_paused_user(123, 456, 2.0)

        result = pp.get_paused_users()
        assert len(result) == 1
        assert result[0].user_id == 123
        assert result[0].guild_id == 456
        # 2 hours = 7200 seconds
        assert result[0].expires_at == 1700007200.0

    def test_add_paused_user_replaces_existing(self, temp_pause_file):
        """Test that adding a user who is already paused replaces the old entry."""
        pp.add_paused_user(123, 456, 1.0)
        pp.add_paused_user(123, 456, 5.0)

        result = pp.get_paused_users()
        assert len(result) == 1
        assert result[0].user_id == 123

    def test_remove_paused_user_exists(self, temp_pause_file):
        """Test removing an existing paused user."""
        pp.add_paused_user(123, 456, 1.0)

        removed = pp.remove_paused_user(123, 456)

        assert removed is True
        assert pp.get_paused_users() == []

    def test_remove_paused_user_not_exists(self, temp_pause_file):
        """Test removing a user who is not paused."""
        removed = pp.remove_paused_user(123, 456)
        assert removed is False

    def test_get_expired_pauses(self, temp_pause_file):
        """Test getting expired pauses."""
        now = datetime.now().timestamp()
        # Add expired user (expires 100 seconds ago)
        pp._paused_users_cache.append(PausedUser(user_id=1, guild_id=100, expires_at=now - 100))
        # Add non-expired user (expires in 1 hour)
        pp._paused_users_cache.append(PausedUser(user_id=2, guild_id=100, expires_at=now + 3600))

        expired = pp.get_expired_pauses()

        assert len(expired) == 1
        assert expired[0].user_id == 1

    def test_remove_expired_pauses(self, temp_pause_file):
        """Test removing expired pauses."""
        now = datetime.now().timestamp()
        # Add expired user (expires 100 seconds ago)
        pp._paused_users_cache.append(PausedUser(user_id=1, guild_id=100, expires_at=now - 100))
        # Add non-expired user (expires in 1 hour)
        pp._paused_users_cache.append(PausedUser(user_id=2, guild_id=100, expires_at=now + 3600))

        removed = pp.remove_expired_pauses()

        assert len(removed) == 1
        assert removed[0].user_id == 1

        remaining = pp.get_paused_users()
        assert len(remaining) == 1
        assert remaining[0].user_id == 2

    def test_get_user_pause_exists(self, temp_pause_file):
        """Test getting pause entry for existing user."""
        pp.add_paused_user(123, 456, 1.0)

        pause = pp.get_user_pause(123, 456)

        assert pause is not None
        assert pause.user_id == 123
        assert pause.guild_id == 456

    def test_get_user_pause_not_exists(self, temp_pause_file):
        """Test getting pause entry for non-existent user."""
        pause = pp.get_user_pause(123, 456)
        assert pause is None


class TestPauseCommand:
    """Tests for the /pause_me command (self-service pause)."""

    async def test_pause_command_success(self, mock_ctx_for_pause, mock_paused_role, temp_pause_file):
        """Test successful pause command."""
        # ctx.author is the user who will be paused
        mock_ctx_for_pause.author.id = 111222333
        mock_ctx_for_pause.author.mention = "<@111222333>"
        mock_ctx_for_pause.author.add_roles = AsyncMock()

        with patch.object(main, "get_paused_role_id", return_value=mock_paused_role.id):
            await main.pause_me(mock_ctx_for_pause, 2)

        mock_ctx_for_pause.author.add_roles.assert_called_once()
        mock_ctx_for_pause.response.send_message.assert_called_once()
        call_content = mock_ctx_for_pause.response.send_message.call_args[0][0]
        assert "have been paused" in call_content
        assert "2 hours" in call_content

    async def test_pause_command_role_not_configured(self, mock_ctx_for_pause, temp_pause_file):
        """Test pause command when role is not configured."""
        mock_ctx_for_pause.guild.get_role.return_value = None

        with patch.object(main, "get_paused_role_id", return_value=0):
            await main.pause_me(mock_ctx_for_pause, 2)

        mock_ctx_for_pause.response.send_message.assert_called_once()
        call_kwargs = mock_ctx_for_pause.response.send_message.call_args[1]
        assert call_kwargs.get("ephemeral") is True
        assert "not configured" in mock_ctx_for_pause.response.send_message.call_args[0][0]

    async def test_pause_command_role_too_high(self, mock_ctx_for_pause, mock_paused_role, temp_pause_file):
        """Test pause command when role is higher than bot's role."""
        mock_paused_role.position = 100
        mock_ctx_for_pause.me.top_role.position = 50

        with patch.object(main, "get_paused_role_id", return_value=mock_paused_role.id):
            await main.pause_me(mock_ctx_for_pause, 2)

        mock_ctx_for_pause.response.send_message.assert_called_once()
        call_kwargs = mock_ctx_for_pause.response.send_message.call_args[1]
        assert call_kwargs.get("ephemeral") is True
        assert "cannot manage" in mock_ctx_for_pause.response.send_message.call_args[0][0]

    async def test_pause_command_already_paused(self, mock_ctx_for_pause, mock_paused_role, temp_pause_file):
        """Test pause command when user is already paused."""
        mock_ctx_for_pause.author.id = 111222333
        pp.add_paused_user(mock_ctx_for_pause.author.id, mock_ctx_for_pause.guild_id, 1.0)

        with patch.object(main, "get_paused_role_id", return_value=mock_paused_role.id):
            await main.pause_me(mock_ctx_for_pause, 2)

        call_kwargs = mock_ctx_for_pause.response.send_message.call_args[1]
        assert call_kwargs.get("ephemeral") is True
        assert "already paused" in mock_ctx_for_pause.response.send_message.call_args[0][0]


class TestBackgroundTask:
    """Tests for the background task that checks expired pauses."""

    async def test_check_expired_pauses_removes_role(self, temp_pause_file):
        """Test that expired pauses are processed and roles removed."""
        now = datetime.now().timestamp()
        pp._paused_users_cache.append(PausedUser(user_id=123, guild_id=456, expires_at=now - 100))

        mock_role = MagicMock()
        mock_role.id = 999
        mock_member = AsyncMock()
        mock_member.roles = [mock_role]
        mock_guild = MagicMock()
        mock_guild.get_role.return_value = mock_role
        mock_guild.fetch_member = AsyncMock(return_value=mock_member)

        with (
            patch.object(main, "client") as mock_client,
            patch.object(main, "get_paused_role_id", return_value=999),
        ):
            mock_client.get_guild.return_value = mock_guild
            await main.check_expired_pauses()

        mock_member.remove_roles.assert_called_once()
        assert pp.get_paused_users() == []

    async def test_restore_paused_users_on_startup(self, temp_pause_file):
        """Test that paused users are restored when bot starts."""
        now = datetime.now().timestamp()
        pp._paused_users_cache.append(PausedUser(user_id=123, guild_id=456, expires_at=now + 3600))

        mock_role = MagicMock()
        mock_role.id = 999
        mock_member = AsyncMock()
        mock_member.roles = []  # Role not present (needs restoration)
        mock_guild = MagicMock()
        mock_guild.get_role.return_value = mock_role
        mock_guild.fetch_member = AsyncMock(return_value=mock_member)

        with (
            patch.object(main, "client") as mock_client,
            patch.object(main, "get_paused_role_id", return_value=999),
        ):
            mock_client.get_guild.return_value = mock_guild
            await main.restore_paused_users()

        mock_member.add_roles.assert_called_once()

    async def test_restore_paused_users_skips_expired(self, temp_pause_file):
        """Test that expired pauses are not restored on startup."""
        now = datetime.now().timestamp()
        pp._paused_users_cache.append(PausedUser(user_id=123, guild_id=456, expires_at=now - 100))

        mock_guild = MagicMock()
        mock_guild.get_role.return_value = MagicMock()

        with (
            patch.object(main, "client") as mock_client,
            patch.object(main, "get_paused_role_id", return_value=999),
        ):
            mock_client.get_guild.return_value = mock_guild
            await main.restore_paused_users()

        # fetch_member should not be called for expired entries
        mock_guild.fetch_member.assert_not_called()
