import pytest

from utils import find_who, find_self_reference, run_async, needs_help, Token


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
        (
            "jsem naposledy měl pásku co měla base 200 díky tem monster itemům",
            "naposledy měl pásku co měla base 200 díky tem monster itemům",
        ),
        ("Já jsem debil, zapomněl jsem doma klíče", "debil"),
        ("Já jsem úplně v prdeli a nevím jak dál", "úplně v prdeli a nevím jak dál"),
    ],
)
def test_dad_who(content, expected):
    # already assumes lowercased text
    assert find_who(content, "jsem") == expected


@pytest.mark.parametrize(
    "content, expected",
    [
        ("jsem programátor.", (True, "programátore")),
        ("jsem, programátor.", (False, "")),
        ("jsem velmi dobrý programátor.", (True, "velmi dobrý programátore")),
        ("jsemprogramátor.", (False, "")),
        ("jsem programátor", (True, "programátore")),
        ("jsem založen, a ty ne, lol", (False, "založen")),
        ("jsem založen! a ty ne, lol", (False, "založen")),
        ("jsem založen? a ty ne, lol", (False, "založen")),
        ("jsem založen. a ty ne, lol", (False, "založen")),
        ("jsem", (False, "")),
        ("Už jsem expert na prsteny :kekW:", (True, "experte na prsteny")),
        ("a vymazal jsem si to poprvé", (False, "si to poprvé")),
        ("tohle jsou settings se kterýma jsem to rozjel", (False, "to rozjel")),
        (
            "jsem naposledy měl pásku co měla base 200 díky tem monster itemům",
            (False, "naposledy měl pásku co měla base 200 díky tem monster itemům"),
        ),
        ("Já jsem debil, zapomněl jsem doma klíče", (True, "debile")),
        ("Já jsem úplně v prdeli a nevím jak dál", (False, "úplně v prdeli a nevím jak dál")),
        ("Jsem sobí hnusec", (True, "sobí hnusec")),
        ("jsem píča", (True, "píčo")),
        ("Jsem to ale kokot", (True, "to ale kokote")),
        ("Jsem to ale zaskočen", (False, "to ale zaskočen")),
        ("jsem pomoc", (False, "pomoc")),
        (
            "jo, to mi přišlo cool na výšce, protože z progtestů jsem měl pocit, že prohazování proměnných je něco co děláš každý druhý den jako programátor",
            (False, "měl pocit"),
        ),
        ("kdyžtak jsem an voice", (False, "an voice")),
        ("jsem zvědavý, jestli to bude fungovat", (False, "zvědavý")),
        (
            "(možná jsem bricknul jedno API a asi bych to tak přes vánoce neměl nechávat.. :D)",
            (False, "bricknul jedno api a asi bych to tak přes vánoce neměl nechávat"),
        ),
        ("protože jsem za hordu nebrdoval", (False, "za hordu nebrdoval")),
        ("@John Doe jsem tu", (False, "tu")),
        ("also, dělal jsem i improvemnts na bota and shit cmon :D", (True, "i improvemnts na boto and shit cmon")),
        ("aspoň jsem implementoval toho autogreetera", (False, "implementoval toho autogreetera")),
        (
            "a jo 5GHz nemám, musím koupit přijímač, jen jsem se k tomu ještě nedostal 😄",
            (False, "se k tomu ještě nedostal"),
        ),
        ("už jsem to fixnul dávno :D", (False, "to fixnul dávno")),
        (
            "Teda s tím, že jsem se nikdy ani nesnažil datit. Basically jsem nikdy neudělal první krok a pak jsem byl často",
            (False, "se nikdy ani nesnažil datit"),
        ),
        (
            "lol, jsem chtel creditnout umelce a Facebook blokuje twitter linky:",
            (False, "chtel creditnout umelce a facebooku blokuje twitter linky"),
        ),
        ("jsem velký blbec", (True, "velký blbče")),
        ("jsem blbec velký", (True, "blbče velký")),
        ("jsem expert na prsteny a trouba", (True, "experte na prsteny a troubo")),
        ("jsem trouba a expert na prsteny", (True, "troubo a experte na prsteny")),
    ],
)
def test_self_reference(content, expected):
    # already assumes lowercased text
    result = find_self_reference(content, "jsem", True)
    assert result[:2] == expected


async def test_run_async():
    is_self_reference, who, _ = await run_async(find_self_reference, "jsem to ale čuník buník", "jsem", False)
    assert is_self_reference, who == (True, "to ale čuník buník")


@pytest.mark.parametrize(
    "content, expected",
    [
        ("nejsem pomoc", False),
        ('V 90% tam není punchline, protože ta zpráva není "pomoc" ale je to jako slovo v nějaké větě.', False),
        ("chtěl jsem jen pomoct, jelikož sám vím, jak hrozně mě bolelo, když jsem měl velké očekávání", False),
        ("Sunny poskytla topícímu se dítěti první pomoc", False),
        ("pomoc, jsem utlačovanej", True),
        ("potřebuju pomoct", True),
        ("žádám o pomoc", True),
    ],
)
def test_needs_help(content, expected):
    assert needs_help(content) == expected

@pytest.mark.parametrize(
    "token, tag, expected",
    [
        (Token("", ",", "Z:-------------", ","), "*:-", True),
        (Token("", "Alena_;Y", "NNFS1-----A----", "Alena"), "NN*S1", True),
        (Token("", "Alena_;Y", "NNFS1-----A----", "Alena"), "NNMS1", False),
        (Token("", "poskytnout", "VpQW----R-AAP-1", "poskytla"), "VpQ", True),
        (Token("", "první-1", "CrFS1----------", "první"), "NrM", False),
        (Token("", "být", "VB-S---1P-AAI--", "jsem"), "NN*S", False),
    ],
)
def test_token(token: Token, tag: str, expected: True):
    assert token.tag_matches(tag) == expected
