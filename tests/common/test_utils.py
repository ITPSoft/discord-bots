import pytest

from common.utils import has_any


@pytest.mark.parametrize(
    "content,words,expected",
    [
        ("this contains bad bot text", ["bad bot", "good bot"], True),
        ("this is normal text", ["bad bot", "good bot"], False),
        ("any text", [], False),
        ("good bot here", ["good bot"], True),
        ("no match here", ["xyz", "abc"], False),
        ("this is a bad bot message", ["bad bot", "good bot"], True),
    ],
)
def test_has_any(content, words, expected):
    """Test has_any utility function from main.py."""
    assert has_any(content, words) is expected
