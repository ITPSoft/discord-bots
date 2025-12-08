"""Basic smoke tests for Šimek Discord bot."""

from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock, patch, MagicMock, call

import aiohttp
import pytest

from šimek import main


@pytest.fixture()
def first_rand_answer() -> Generator[MagicMock, Any, None]:
    # Use the same mock object for both patches
    with patch("random.choice") as mock_choice:
        mock_choice.side_effect = lambda x: x[0]  # force random to return first element
        yield mock_choice


@pytest.fixture()
def always_answer() -> Generator[MagicMock, Any, None]:
    # Create a single mock object
    # Use the same mock object for both patches
    with patch("random.randint") as mock_randint:
        mock_randint.return_value = 1  # so the probability triggers always in tests
        yield mock_randint


@pytest.fixture(autouse=True)
async def cleanup_http_session():
    """Ensure HTTP session is cleaned up after each test."""
    yield
    if main.http_session and not main.http_session.closed:
        await main.http_session.close()
        main.http_session = None


@pytest.fixture(scope="function")
def mock_message():
    """Create a mock Message object."""
    message = AsyncMock()
    message.channel.id = 932301697836003358  # bot-testing

    # Mock channel.history() as an async generator
    async def mock_history(*args, **kwargs):
        # Return some sample messages for markov chain generation
        mock_msg1 = AsyncMock()
        mock_msg1.content = "hello world test"
        mock_msg2 = AsyncMock()
        mock_msg2.content = "world test again"
        mock_msg3 = AsyncMock()
        mock_msg3.content = "some other message"
        for msg in [mock_msg1, mock_msg2, mock_msg3]:
            yield msg

    message.channel.history = MagicMock(return_value=mock_history())
    return message


@pytest.mark.parametrize(
    "user_message,expected_responses,expected_reactions",
    [
        # Groku pravda variations
        ("Groku, je toto pravda?", ["Ano."], []),
        ("Groku, je to pravda?", ["Ano."], []),
        ("Groku je to pravda", ["Ano."], []),
        ("Groku je toto pravda", ["Ano."], []),
        # Windows problem
        (
            "mám velký problém s windows",
            ["Radikální řešení :point_right: https://fedoraproject.org/workstation/download :kekWR:"],
            [],
        ),
        (
            "mé windows mají velký problém",
            ["Radikální řešení :point_right: https://fedoraproject.org/workstation/download :kekWR:"],
            [],
        ),
        # Nvidia driver issue
        ("linux nvidia driver problem", ["Nemůžu za to, že si neumíš vybrat distro, smh"], []),
        ("driver nvidia na linux", ["Nemůžu za to, že si neumíš vybrat distro, smh"], []),
        # Operating systems
        ("používám windows", [], ["😔"]),
        ("mám debian", [], ["💜"]),
        ("linux je nejlepší", [], ["🐧"]),
        ("gnu/linux masterrace", [], ["🐧"]),
        # Birthday wish
        ("všechno nejlepší k narozeninám", [], ["🥳"]),
        # Help requests
        ("pomoc potřebuji pomoct", [], []),  # Will have Oogway quote
        ("hilfe bitte", [], []),
        ("help me", [], []),
        # Novinky
        ("novinky z dneška", [], ["😖"]),
        # Schizo
        ("schizo moment", ["never forgeti"], []),
        # Brain damage
        ("brain damage od Pink Floyd", ["https://www.youtube.com/watch?v=kyg1uxOsAUY"], []),
        ("anureysm incoming", ["https://www.youtube.com/watch?v=kyg1uxOsAUY"], []),
        ("aneuerysm moment", ["https://www.youtube.com/watch?v=kyg1uxOsAUY"], []),
        ("brian damage lol", ["https://www.youtube.com/watch?v=kyg1uxOsAUY"], []),
        # YouTube links
        ("https://youtube.com/shorts/mI1j_27pE-s?si=ezwOsgzXzsjqd1_G", ["recenze: strašnej banger"], []),
        ("podívej na https://youtu.be/dQw4w9WgXcQ", ["recenze: strašnej banger"], []),
        # Questions
        ("co se děje?", ["Ano."], []),
        # Note: "?" case is checked before "proč/proc", so messages ending with ? will trigger "?" case
        ("proč to tak je", ["skill issue"], []),  # No question mark to avoid "?" case
        ("proc ne", ["skill issue"], []),  # No question mark to avoid "?" case
        # Jsi/negr combinations
        ("jsi negr", ["Tvoje máma je negr."], []),
        ("nejsi negr", [":pensive:", ":+1:"], []),
        # Cum zone
        ("jsi v cum zone", ["https://www.youtube.com/watch?v=j0lN0w5HVT8"], []),
        ("welcome to the cum zone", ["https://www.youtube.com/watch?v=j0lN0w5HVT8"], []),
        # Israel
        ("israel konflikt", [":pensive:"], []),
        ("izrael válka", [":pensive:"], []),
        # Lagtrain
        ("lagtrain je banger", ["https://www.youtube.com/watch?v=UnIhRpIT7nc"], []),
        # Crab rave
        ("crab rave time", ["https://youtu.be/LDU_Txk06tM?t=75"], []),
        # Já jo/ne
        ("já jo rozhodně", ["já ne"], []),
        ("já ne vůbec", ["já jo"], []),
        # Suicidal
        ("chci se zabít", ["omg don't kill yourself, ur too sexy, haha"], []),
        ("feeling suicidal", ["omg don't kill yourself, ur too sexy, haha"], []),
        # V píči
        ("jsem v píči", ["stejně tak moc v píči jako já včera večer v tvojí mámě loool"], []),
        ("to je v pici", ["stejně tak moc v píči jako já včera večer v tvojí mámě loool"], []),
        # Business correct
        ("dobrý business", [], [":+1:"]),
        ("nějaký byznys", [], [":+1:"]),
        # Reminder
        ("reminder pro všechny", ["kind reminder: ur a bitch :)"], []),
        # Bad bot
        ("špatný bot", ["i'm trying my best :pensive:"], []),
        ("spatny bot", ["i'm trying my best :pensive:"], []),
        # Good bot
        ("hodný bot", [], ["🙂"]),
        # Opinions
        ("podle mě je to správně", ["souhlasím"], []),
        ("myslím si, že ano", ["souhlasím"], []),
        ("myslim si ze ne", ["souhlasím"], []),
        # Twitter with links (should respond with twitter-péro)
        ("podívej https://example.com/twitter má twitter post", ["preferuji #twitter-péro"], []),
        ("https://example.com/ twiter je lepší", ["preferuji #twitter-péro"], []),
        # Social media links that should be ignored
        ("https://fxtwitter.com/litteralyme0/status/1994088426300232075", [], []),
        ("https://cdn.discordapp.com/attachments/xyz/abc/ssstwitter.com_1764410721090.mp4", [], []),
    ],
)
async def test_maybe_respond(
    mock_message, user_message, expected_responses, expected_reactions, first_rand_answer, always_answer
):
    """Test special message responses."""
    main.http_session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
    main.COOLDOWN = -1  # to test all answers
    mock_message.content = user_message

    await main.manage_response(mock_message)

    if expected_responses:
        mock_message.reply.assert_has_calls([call(r) for r in expected_responses])
    if expected_reactions:
        mock_message.add_reaction.assert_has_calls([call(r) for r in expected_reactions])


async def test_business(mock_message, always_answer):
    main.COOLDOWN = -1  # to test all answers
    main.http_session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
    mock_message.content = "Dobrý buisness"
    await main.manage_response(mock_message)
    mock_message.reply.assert_called_once()
    assert "příště raději napiš 'byznys'" in mock_message.reply.call_args[0][0]


async def test_mama_joke_api(mock_message, always_answer):
    """Test yo mama joke API call."""
    main.COOLDOWN = -1
    mock_message.content = "tvoje mama"

    # Mock the HTTP session
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"joke": "Yo mama so fat..."})

    # Create a proper async context manager
    mock_context_manager = MagicMock()
    mock_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
    mock_context_manager.__aexit__ = AsyncMock(return_value=None)

    mock_session = MagicMock()
    mock_session.get = MagicMock(return_value=mock_context_manager)

    main.http_session = mock_session

    await main.manage_response(mock_message)

    mock_message.reply.assert_called_once_with("Yo mama so fat...")


async def test_jsem_self_reference(mock_message, always_answer):
    """Test 'jsem' self-reference response."""
    main.COOLDOWN = -1
    mock_message.content = "jsem hloupý"

    with patch("šimek.main.find_self_reference_a", new_callable=AsyncMock) as mock_find:
        mock_find.return_value = (True, "hloupý", "")

        await main.manage_response(mock_message)

        mock_message.reply.assert_called_once_with("Ahoj, hloupý. Já jsem táta.")


@pytest.mark.parametrize(
    "mention,expected",
    [
        ("<@&123456789>", "Hello <nějaká role>"),
        ("<@123456789>", "Hello <nějaká role>"),
    ],
)
async def test_do_response_escaping(mock_message, always_answer, mention, expected):
    """Test that do_response escapes mentions."""
    reply_text = f"Hello {mention}"

    await main.do_response(reply_text, mock_message)

    mock_message.reply.assert_called_once_with(expected)
