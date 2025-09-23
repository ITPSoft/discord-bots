HELP = r"""
    ***Bot commands:***
    _arguments in \{\} are optional, arguments with \[\] are required_
    $_bothelp_ or _commands_
        Shows help.
    $_ping_
        Shows bot's ping and API latency.
    $_roll_ \{number\}
        Rolls a random number between 1 and \{number\}. Defaults number to 100,
        if not specified.
    $_yesorno_
        Answers a question with yes or no.
    $_warcraft_ \{time\}
        Creates a warcraft play session announcement from template.
    $_gmod_ \{time\}
        Creates a gmod play session announcement from template.
    $_poll_ [name_of_poll] [option_1] [option2] \{option3\} \{option4\} \{option5\}
        Use underscores as spaces. Bot will automatically edit them for you.
    $_today_
        Tells you which international day it is today.
    """

WARCRAFTY_CZ = """
<@&871817685439234108> - Warcrafty 3 dnes{0}?
React with attendance:
:white_check_mark: Ano
:negative_squared_cross_mark: Ne
:thinking: Možná

Chceme hrát:
:one: - Survival Chaos
:two: - Legion TD nebo Element TD
:three: - Blood Tournament
:four: - Risk
:five: - Luckery/Uther Party/Temple Escape
:six: - Objevovat nové mapy.
:question: - Něco jiného? Napište jako reply.
"""

WOWKA_CZ = """
<@&1120426868697473024> Další raid je naplánován na {0}, od {1}.
Půjde se:
{3}

Ready buďte alespoň 15 minut před začátkem.

Dorazíte?
:white_check_mark: Ano
:negative_squared_cross_mark: Ne
:thinking: Možná
:orthodox_cross: Ano, ale pozdě.

Role?
:regional_indicator_t: Tank
:regional_indicator_h: Healer
:regional_indicator_d: Dps
:regional_indicator_o: Můžu víc rolí
"""

GMOD_CZ = """
<@&951457356221394975> - Garry's Mod dnes v cca {0}?
    React with attendance:
    :white_check_mark: Ano
    :negative_squared_cross_mark: Ne
    :thinking: Možná

    Chceme hrát:
    :one: - TTT (OG Among Us)
    :two: - PropHunt/Hide&Seek (schováváte se na mapě jako props a hlídači vás hledají)
    :three: - Stranded (RPG mapa, něco jako Rust)
    :four: - DropZone (arena s různýma spellama něco jako Warloci ve W3)
    :five: - Flood
    :question: - Něco jiného? Napište jako reply.

"""


GIDS = [276720867344646144]
TWITTERPERO = 1042052161338626128
WELCOMEPERO = 1104877855466344569
