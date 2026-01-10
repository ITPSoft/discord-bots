import pytest

from common.constants import Server, _DEFAULT_GIDS
from common.utils import get_gids


class TestGetGids:
    def test_returns_defaults_when_env_not_set(self, monkeypatch):
        monkeypatch.delenv("DISCORD_GUILD_IDS", raising=False)
        result = get_gids()
        assert set(result) == _DEFAULT_GIDS

    def test_returns_parsed_ids_from_env(self, monkeypatch):
        monkeypatch.setenv("DISCORD_GUILD_IDS", str(Server.TEST_SERVER.value))
        result = get_gids()
        assert result == [Server.TEST_SERVER.value]

    def test_returns_multiple_ids_from_env(self, monkeypatch):
        env_value = f"{Server.KOUZELNICI.value},{Server.TEST_SERVER.value}"
        monkeypatch.setenv("DISCORD_GUILD_IDS", env_value)
        result = get_gids()
        assert set(result) == {Server.KOUZELNICI.value, Server.TEST_SERVER.value}

    def test_handles_whitespace_in_env(self, monkeypatch):
        env_value = f" {Server.KOUZELNICI.value} , {Server.TEST_SERVER.value} "
        monkeypatch.setenv("DISCORD_GUILD_IDS", env_value)
        result = get_gids()
        assert set(result) == {Server.KOUZELNICI.value, Server.TEST_SERVER.value}

    def test_raises_on_invalid_guild_id(self, monkeypatch):
        monkeypatch.setenv("DISCORD_GUILD_IDS", "999999999999999999")
        with pytest.raises(ValueError, match="contains invalid guild IDs"):
            get_gids()

    def test_raises_on_non_integer(self, monkeypatch):
        monkeypatch.setenv("DISCORD_GUILD_IDS", "not_a_number")
        with pytest.raises(ValueError, match="must contain comma-separated integers"):
            get_gids()

    def test_raises_on_mixed_valid_invalid(self, monkeypatch):
        env_value = f"{Server.TEST_SERVER.value},123456789012345678"
        monkeypatch.setenv("DISCORD_GUILD_IDS", env_value)
        with pytest.raises(ValueError, match="contains invalid guild IDs"):
            get_gids()
