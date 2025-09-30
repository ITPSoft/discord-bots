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

GAME_EN = """
<@{0}> Shall we play {1} today{2}?.

Will you join?
:white_check_mark: Yes
:negative_squared_cross_mark: No
:thinking: Maybe
:orthodox_cross: Yes, but later.

"""

GIDS = [
    # 276720867344646144,  # kouzelníci
    1420168840511492149,  # test server
]
TWITTERPERO = 1042052161338626128
WELCOMEPERO = 1104877855466344569
