import pytest

from utils import find_who


@pytest.mark.parametrize(
    "content, expected",
    [
        ("jsem programátor.", "programátor"),
        ("jsem, programátor.", ""),
        ("jsem velmi dobrý programátor.", "velmi dobrý programátor"),
        ("jsemprogramátor.", ""),
        ("jsem programátor", "programátor"),
        ("jsem založen, a ty ne, lol", "založen"),
        ("jsem založen! a ty ne, lol", "založen"),
        ("jsem založen? a ty ne, lol", "založen"),
        ("jsem založen. a ty ne, lol", "založen"),
        ("jsem", ""),
        ("Už jsem expert na prsteny :kekW:", "expert na prsteny :kekW:"),
        ("a vymazal jsem si to poprvé", "si to poprvé"),
        ("tohle jsou settings se kterýma jsem to rozjel", "to rozjel"),
        ("jsem naposledy měl pásku co měla base 200 díky tem monster itemům", "naposledy měl pásku co měla base 200 díky tem monster itemům"),
        ("Já jsem debil, zapomněl jsem doma klíče", "debil"),
        ("Já jsem úplně v prdeli a nevím jak dál", "úplně v prdeli a nevím jak dál"),
    ],
)
def test_dad_who(content, expected):
    # already assumes lowercased text
    assert find_who(content, "jsem") == expected
