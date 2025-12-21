from string import Template

from common.constants import Channel
from common.utils import GamingRoles

WELCOME = Template(f"""
Vítej, $member!
Prosím, přesuň se do <#{Channel.ROLES}> a naklikej si role. Nezapomeň na roli Člen, abys viděl i ostatní kanály!
---
Welcome, $member!
Please, go to the <#{Channel.ROLES}> channel and select your roles. Don't forget the 'Člen'/Member role to see other channels!
""")

HELP = {
    "/poll [opt1] [opt2] {opt3} {opt4} {opt5}": "Vytvoří anketu podle 2 až 5 argumentů.",
    "/roll {počet stěn}": "Hodí kostkou s počtem stěn daným v argumentu, výchozí je 6.",
    "/tweet [text] {url obrázku} {anonym}": "Pošle 'tweet' do kanálu #twitter-pero.",
    # "/ping_grossmann": "Zkontroluje Grossmannovu latenci.",   # jen pro adminy
    "/yesorno": "Odpoví náhodně ano/ne.",
    "/warcraft_ping {čas}": "Zmíní roli Warcraft a otevře plánovací menu.",
    "/game_ping [role] [čas] {jazyk CZ/EN} {poznámka}": "Zmíní roli jakékoliv hry.",
    # "/createrolewindow": "Otevře menu pro výběr rolí.",   # jen pro adminy
    "/iwantcat": "Pošle náhodný kočkobrázek.",
    "/iwantfox": "Pošle náhodný liškobrázek.",
    "/waifu": "Pošle náhodný láskobrázek.",
    "/xkcd {ID}": "Pošle xkcd komiks s daným ID, výchozí je poslední vydaný.",
    "/pause_me [hours]": "Pozastaví na [hours] hodin přístup k serveru, užitečné, pokud se potřebujete soustředit.",
    "/request_role": "Požádá o přidání do uzavřenějších kanálů."
}

WARCRAFTY_CZ = Template(f"""
{GamingRoles.WARCRAFT.role_tag} - Warcrafty 3 dnes$time?
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
""")

GAME_EN = Template("""
<@&$role_id> Shall we play $game today at $time?

Will you join?
:white_check_mark: Yes
:negative_squared_cross_mark: No
:thinking: Maybe
:orthodox_cross: Yes, but later.

$note
""")

GAME_CZ = Template("""
<@&$role_id> Zahrajeme si $game dnes v $time?

Přidáš se?
:white_check_mark: Ano
:negative_squared_cross_mark: Ne
:thinking: Možná
:orthodox_cross: Ano, ale později.

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
