"""Basic smoke tests for Šimek Discord bot."""

from unittest.mock import MagicMock, patch

# Mock the dictionary modules
mock_decimdictionary = MagicMock()
mock_schizodict = MagicMock()
with patch.dict("sys.modules", {"decimdictionary": mock_decimdictionary, "schizodict": mock_schizodict}):
    with patch("disnake.ext.commands.Bot"):
        import main


def test_build_trigram_counts():
    """Test trigram counting function."""
    messages = ["hello world test", "world test again"]
    result = main.build_trigram_counts(messages)

    assert isinstance(result, dict)
    assert ("hello", "world") in result
    assert ("world", "test") in result


def test_markov_chain_insufficient_data():
    """Test markov chain with insufficient data."""
    messages = ["hi"]
    result = main.markov_chain(messages)

    assert "Not enough data" in result
