from string import Template

from common.constants import Channel

WELCOME = Template("""
Vítej, $member!
Prosím, přesuň se do <#{Channel.ROLES}> a naklikej si role. Nezapomeň na roli Člen, abys viděl i ostatní kanály!
---
Welcome, $member!
Please, go to the <#{Channel.ROLES}> channel and select your roles. Don't forget the 'Člen'/Member role to see other channels!
""")

HELP = r"""
    ***Bot commands:***
    _arguments in \{\} are optional, arguments with \[\] are required_
    /_bothelp_ or _commands_
        Shows help.
    /_ping_
        Shows bot's ping and API latency.
    /_roll_ \{number\}
        Rolls a random number between 1 and \{number\}. Defaults number to 100,
        if not specified.
    /_yesorno_
        Answers a question with yes or no.
    /_warcraft_ \{time\}
        Creates a warcraft play session announcement from template.
    /_gmod_ \{time\}
        Creates a gmod play session announcement from template.
    /_poll_ [name_of_poll] [option_1] [option2] \{option3\} \{option4\} \{option5\}
        Use underscores as spaces. Bot will automatically edit them for you.
    /_today_
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

GAME_EN = Template("""
<@&$role_id> Shall we play $game today at $time?.

Will you join?
:white_check_mark: Yes
:negative_squared_cross_mark: No
:thinking: Maybe
:orthodox_cross: Yes, but later.

$note
""")

# based on https://waifu.pics/docs
WAIFU_CATEGORIES = {
    "sfw": [
        "waifu",
        "neko",
        "shinobu",
        "megumin",
        "bully",
        "cuddle",
        "cry",
        "hug",
        "awoo",
        "kiss",
        "lick",
        "pat",
        "smug",
        "bonk",
        "yeet",
        "blush",
        "smile",
        "wave",
        "highfive",
        "handhold",
        "nom",
        "bite",
        "glomp",
        "slap",
        "kick",
        "happy",
        "wink",
        "poke",
        "dance",
        "cringe",
        # commented out options valid for API but unwanted
        # "kill"
    ],
    "nsfw": [
        "waifu",
        "neko",
        "trap",
        "blowjob",
    ],
}

WAIFU_ALLOWED_NSFW = [Channel.NSFW]
