"""Basic smoke tests for Šimek Discord bot."""

from unittest.mock import AsyncMock, patch

import pytest

import main


@pytest.fixture(scope="function")
def mock_message():
    """Create a mock Message object."""
    message = AsyncMock()
    message.channel.id = 932301697836003358  # bot-testing
    return message


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


@pytest.mark.parametrize(
    "content,expected_response",
    [
        ("Groku, je toto pravda?", "Ano."),
        ("Groku, je to pravda?", "Ano."),
        # ("Groku je to pravda", "Ano."),
        # ("Groku je toto pravda", "Ano."),
    ],
)
async def test_maybe_respond(mock_message, content, expected_response):
    """Test special message responses."""
    mock_message.content = content

    with patch("random.choice") as mock_choice:
        mock_choice.return_value = expected_response
        await main.maybe_respond(mock_message)
        mock_message.reply.assert_called_once_with(expected_response)


async def test_business(mock_message):
    mock_message.content = "Dobrý buisness"
    await main.maybe_respond(mock_message)
    mock_message.reply.assert_called_once()
    assert "příště raději napiš 'byznys'" in mock_message.reply.call_args[0][0]
