"""Basic smoke tests for Šimek Discord bot."""
from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock, patch, MagicMock

import aiohttp
import pytest

import main


@pytest.fixture()
def first_rand_answer() -> Generator[MagicMock, Any, None]:
    # Use the same mock object for both patches
    with patch("random.choice") as mock_choice, patch("random.randint") as mock_randint:
        mock_choice.side_effect = lambda x: x[0]  # force random to return first element
        yield mock_choice

@pytest.fixture()
def always_answer() -> Generator[MagicMock, Any, None]:
    # Create a single mock object
    # Use the same mock object for both patches
    with patch("random.randint") as mock_randint:
        mock_randint.return_value = 1   # so the probability triggers always in tests
        yield mock_randint



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
    "user_message,expected_response",
    [
        ("Groku, je toto pravda?", "Ano."),
        ("Groku, je to pravda?", "Ano."),
        ("Groku je to pravda", "Ano."),
        ("Groku je toto pravda", "Ano."),
        ("mám velký problém s windows", "Radikální řešení :point_right: https://fedoraproject.org/workstation/download :kekWR:"),
        ("mé windows mají velký problém", "Radikální řešení :point_right: https://fedoraproject.org/workstation/download :kekWR:"),
        ("https://youtube.com/shorts/mI1j_27pE-s?si=ezwOsgzXzsjqd1_G", "recenze: strašnej banger"),
        ("co se děje?", "Ano."),
        ("jsi negr", 'Tvoje máma je negr.'),
        ("nejsi negr", ":+1:"),
        ("jsi v cum zone", "https://www.youtube.com/watch?v=j0lN0w5HVT8"),
    ],
)
async def test_maybe_respond(mock_message, user_message, expected_response, first_rand_answer, always_answer):
    main.http_session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
    """Test special message responses."""
    mock_message.content = user_message

    await main.manage_response(mock_message)
    mock_message.reply.assert_called_once_with(expected_response)


async def test_business(mock_message):
    mock_message.content = "Dobrý buisness"
    await main.manage_response(mock_message)
    mock_message.reply.assert_called_once()
    assert "příště raději napiš 'byznys'" in mock_message.reply.call_args[0][0]
