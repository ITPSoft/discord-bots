import os
import random
import datetime as dt
import re

import disnake
from disnake import Message, ApplicationCommandInteraction
from disnake.ext.commands import InteractionBot, default_member_permissions
from collections import defaultdict, Counter

import aiohttp

from common.constants import GIDS, Channel
from common.utils import has_any, has_all
from šimek import šimekdict

from dotenv import load_dotenv
import pickle

from šimek.utils import find_self_reference_a, format_time_ago, needs_help_a

# Global HTTP session - will be initialized when bot starts
http_session: aiohttp.ClientSession | None = None

# preload all useful stuff
load_dotenv()
TOKEN = os.getenv("ŠIMEK_DISCORD_TOKEN")
TEXT_SYNTH_TOKEN = os.getenv("TEXT_SYNTH_TOKEN")
REPLIES = (
    "Ano.",
    "Ne.",
    "Ano.",
    "Ne.",
    "Perhaps.",
    "Ano.",
    "Ne.",
    "Perhaps.",
    "Možná.",
    "Pravděpodobně.",
    "bruh",
    "nemám tušení",
)  # repeat ano/ne/perhaps to give it more common occurrence

MOT_HLASKY = šimekdict.MOT_HLASKY
LINUX_COPYPASTA = šimekdict.LINUX_COPYPASTA
RECENZE = šimekdict.RECENZE

ALLOW_CHANNELS = [
    Channel.BOT_DEBUG_GENERAL,
    Channel.GENERAL,
    Channel.MEMES_SHITPOSTING,
    Channel.BOT_TESTING,
    Channel.GAMING_GENERAL,
    Channel.DESKOVKY_GENERAL,
    Channel.MAGIC_THE_GATHERING_GENERAL,
    Channel.PHASE_CONNECT,
    Channel.MINECRAFT_GENERAL,
    Channel.WARCRAFT3_GENERAL,
    Channel.GACHA,
    Channel.IT_PERO,
    Channel.DYMKOPERO,
    Channel.JIDLOPERO,
    Channel.SCHIZOPERO,
    Channel.KOUZELNICI_GENERAL,
]
MARKOV_FILE = "markov_twogram.pkl"

COOLDOWN = 30  # sekund

# for easier testing
CUSTOM_COOLDOWNS = {
    Channel.BOT_TESTING.value: 0,
}

# add intents for bot
intents = disnake.Intents.all()
client = InteractionBot(intents=intents)  # so we can have debug commands

last_reaction_time: dict[int, dt.datetime] = {}


@client.slash_command(description="Show last reaction times")
@default_member_permissions(administrator=True)
async def show_last_reaction_times(inter: ApplicationCommandInteraction):
    response = "Last reaction times per channel:\n"
    for channel_id, time in last_reaction_time.items():
        channel = client.get_channel(channel_id)
        if channel:
            time_ago = format_time_ago(time)
            response += f"{channel.name}: {time.strftime('%Y-%m-%d %H:%M:%S')} ({time_ago})\n"
    await inter.response.send_message(response)


@client.slash_command(name="ping_šimek", description="check šimek latency", guild_ids=GIDS)
@default_member_permissions(administrator=True)
async def ping(ctx: ApplicationCommandInteraction):
    await ctx.response.send_message(f"Pong! API Latency is {round(client.latency * 1000)}ms.")


# on_ready event - happens when bot connects to Discord API
@client.event
async def on_ready():
    global http_session
    # Initialize the global HTTP session with SSL disabled
    http_session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
    print(f"{client.user} has connected to Discord!")


def build_trigram_counts(messages):
    words = " ".join(messages).lower().split()
    if len(words) < 3:
        return {}
    markov = defaultdict(list)
    for i in range(len(words) - 2):
        key = (words[i], words[i + 1])
        next_word = words[i + 2]
        markov[key].append(next_word)
    markov_counts = {k: Counter(v) for k, v in markov.items()}
    return markov_counts


def save_trigram_counts(markov_counts, filename=MARKOV_FILE):
    with open(filename, "wb") as f:
        pickle.dump(markov_counts, f)


def load_trigram_counts(filename=MARKOV_FILE):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except Exception:
        return {}


def markov_chain(messages, max_words=20):
    # Build and save trigram counts
    markov_counts = build_trigram_counts(messages)
    # save_trigram_counts(markov_counts)
    #
    # # Load trigram counts
    # markov_counts = load_trigram_counts()

    if not markov_counts:
        return "Not enough data for trigram Markov chain."

    start_key = random.choice(list(markov_counts.keys()))
    sentence = [start_key[0], start_key[1]]

    for _ in range(max_words - 2):
        if start_key in markov_counts:
            next_words, weights = zip(*markov_counts[start_key].items())
            next_word = random.choices(next_words, weights=weights)[0]
            sentence.append(next_word)
            if next_word.endswith((".", "!", "?:D", ":D", ":)", "😂", "🤣", ":kekw:")):
                break
            start_key = (start_key[1], next_word)
        else:
            break

    return " ".join(sentence).lower()


# trigram Markov chain functions end


# we use a evil class magic to hack match case to check for substrings istead of exact matches
# https://stackoverflow.com/a/78046484
class Substring(str):
    def __eq__(self, other):
        return other in self


# evil hack end


def cooldown(channel_id: int):
    """
    Allows different cooldown per channel
    """
    if channel_id in CUSTOM_COOLDOWNS:
        return CUSTOM_COOLDOWNS[channel_id]
    return COOLDOWN


async def do_response(reply: str, m: Message, *, chance=10, reaction=False):
    """
    reply: str - text or emoji to reply with
    m: Message - message object to reply to
    chance: int - 1 in `chance` probability to reply
    reaction: bool - if True, add reaction instead of reply
    """
    # safeguard against all role tags
    if random.randint(1, chance) == 1:
        reply = re.sub(r"<@!?&?\d+>", "<nějaká role>", reply)
        if reaction:
            await m.add_reaction(reply)
        else:
            await m.reply(reply)
        last_reaction_time[m.channel.id] = dt.datetime.now()


async def manage_response(m: Message):
    # grok feature is above all other and will trigger anywhere
    response = ""
    mess = m.content.lower()

    now = dt.datetime.now()
    # higher priority than rest
    if "drž hubu" in mess and m.reference and m.reference.resolved and m.reference.resolved.author == client.user:
        await do_response("ok", m, chance=1)
        last_reaction_time[m.channel.id] = now + dt.timedelta(minutes=5)  # 5 minute timeout after being told to shut up
        return  # skip setting the time again at the end of the function

    last_time = last_reaction_time.get(m.channel.id)
    if last_time and (seconds_diff := (now - last_time).total_seconds()) < cooldown(m.channel.id):
        print(f"too soon, last replied {seconds_diff} seconds ago")
        return

    if Substring(mess) in [
        "@grok",
        "@schizo",
        "@šimek",
        "@1420163586310803566",
        "@&1437546286487175252",
        "šimku",
        "simku",
    ]:
        # Fetch previous 50 messages (excluding the current one)
        messages = []
        async for msg in m.channel.history(limit=50, before=m):
            if msg.content:
                msg.content = msg.content.replace("@", "")  # remove bot mentions
                msg.content = msg.content.replace(",", "")  # cleanup
                if msg.author == client.user:  # throw away messages from itself
                    continue
                messages.append(msg.content)
        response = f"{random.choice(REPLIES)} Protože "
        response += markov_chain(messages, max_words=random.randint(15, 40))
        await m.reply(response)
        last_reaction_time[m.channel.id] = dt.datetime.now()
        return

    # ECONPOLIPERO IS A SERIOUS CHANNEL, NO SHITPOSTING ALLOWED gif
    if m.channel.id == Channel.ECONPOLIPERO:
        if has_any(mess, [":KekWR:", ":KekW:"]):
            await do_response(
                "https://media.discordapp.net/attachments/786626221856391199/1420065025896349777/a6yolw.gif?ex=68f0625d&is=68ef10dd&hm=084f583c9cc1b0a6e6279ccf44933984cdb51167c7fe265c52c3be44725540cf&=&width=450&height=253",
                m,
                chance=4,
                reaction=False,
            )
        return

    elif m.channel.id not in ALLOW_CHANNELS:
        return
    print("check passed getting into main loop")
    # we are matching whole substrings now, not exact matches, only one case will be executed, if none match, default case will be executed
    assert http_session is not None

    # analysing dad jokes and mom jokes
    jsi_is_ref = jsem_is_ref = False
    jsi_who = jsem_who = ""
    help_needed = False
    if "jsi" in mess:
        jsi_is_ref, jsi_who, _ = await find_self_reference_a(mess, "jsi", False)
    if "jsem" in mess:
        jsem_is_ref, jsem_who, _ = await find_self_reference_a(mess, "jsem", True)

    matched = True
    oogway_help = f"""„{random.choice(MOT_HLASKY)}“
                                                                                - Mistr Oogway, {random.randint(461, 490)} př. n. l."""
    if "pomo" in mess:
        help_needed = await needs_help_a(mess)

    match Substring(mess):
        case "hodný bot":
            await do_response("🙂", m, chance=1, reaction=True)
        case _ if has_all(mess, ["problém", "windows"]):
            await do_response(
                "Radikální řešení :point_right: https://fedoraproject.org/workstation/download :kekWR:", m, chance=1
            )
        case _ if has_all(mess, ["nvidia", "driver", "linux"]):
            await do_response("Nemůžu za to, že si neumíš vybrat distro, smh", m, chance=2)
        case "windows":
            await do_response("😔", m, chance=4, reaction=True)
        case "debian":
            await do_response("💜", m, chance=4, reaction=True)
        case "všechno nejlepší":
            await do_response("🥳", m, chance=1, reaction=True)
        case "linux" | "gnu/linux":
            await do_response("🐧", m, chance=10, reaction=True)
            await do_response(LINUX_COPYPASTA, m, chance=10)
        case "hilfe" | "help":
            await do_response(oogway_help, m, chance=3)
        case "pomo" if help_needed:  # better analysis of czech help, there is no nicer way to do it, pomoz etc.
            await do_response(oogway_help, m, chance=3)
        case "novinky":
            await do_response("😖", m, chance=3, reaction=True)
            await do_response("Přestaň postovat cringe, bro.", m, chance=10)
        case "jsem" if jsem_is_ref:
            await do_response(f"Ahoj, {jsem_who}. Já jsem táta.", m, chance=5)
        case "schizo":
            await do_response("never forgeti", m, chance=4)
        case "anureysm" | "aneuerysm" | "brain damage" | "brian damage":
            await do_response("https://www.youtube.com/watch?v=kyg1uxOsAUY", m, chance=2)
        case "groku je to pravda" | "groku je toto pravda" | "groku, je to pravda" | "groku, je toto pravda":
            await do_response(random.choice(REPLIES), m, chance=1)
        case "?" if m.content[-1] == "?":  # to not trigger on Youtube links and similar
            await do_response(f"{random.choice(REPLIES)}", m, chance=12)
        case "proč" | "proc":
            await do_response("skill issue", m, chance=8)
        case "jsi" if jsi_is_ref:
            await do_response(f"Tvoje máma je {jsi_who}.", m, chance=8)
        case "negr":
            await do_response(":pensive:", m, chance=10)
            await do_response(":+1:", m, chance=30)
        case "israel" | "izrael":
            await do_response(":pensive:", m, chance=5)
        case "mama" | "mamá" | "mami" | "mommy" | "mamka" | "mamko":
            async with http_session.get("https://www.yomama-jokes.com/api/v1/jokes/random/") as api_call:
                if api_call.status == 200:
                    await do_response(f"{(await api_call.json())['joke']}", m, chance=4)
        case "lagtrain":
            await do_response("https://www.youtube.com/watch?v=UnIhRpIT7nc", m, chance=1)
        case "cum zone":
            await do_response("https://www.youtube.com/watch?v=j0lN0w5HVT8", m, chance=1)
        case "crab rave":
            await do_response("https://youtu.be/LDU_Txk06tM?t=75", m, chance=1)
        case "já jo":
            await do_response("já ne", m, chance=4)
        case "já ne":
            await do_response("já jo", m, chance=4)
        case "chci se zabít" | "suicidal":
            await do_response("omg don't kill yourself, ur too sexy, haha", m, chance=1)
        case "v píči" | "v pici":
            await do_response("stejně tak moc v píči jako já včera večer v tvojí mámě loool", m, chance=10)
        case "buisness" | "buisnes" | "buissnes" | "bussiness" | "bussines":
            await do_response(
                "KÁMO lmao ukažte si na toho blbečka, co neumí napsat 'business' XDDDD :index_pointing_at_the_viewer: příště raději napiš 'byznys' dík :)",
                m,
                chance=1,
            )
        case "business" | "byznys":
            await do_response(":+1:", m, chance=1, reaction=True)
        case "reminder":
            await do_response("kind reminder: ur a bitch :)", m, chance=4)
        case "youtu.be" | "youtube.com":
            await do_response(random.choice(RECENZE), m, chance=2)  # není to tak vtipné, když je to pokaždé
        case "špatný bot" | "spatny bot":
            await do_response("i'm trying my best :pensive:", m, chance=1)
        case "podle mě" | "myslím si" | "myslim si":
            await do_response(f"{random.choice(['souhlasím', 'nesouhlasím', ''])}", m, chance=10)
        case _:
            matched = False
    if matched:
        return

    without_links = re.sub(r"https?://\S+", "", mess)
    match Substring(without_links):
        case "twitter" | "twiter":
            await do_response("preferuji #twitter-péro", m, chance=1)
        case _:
            if random.randint(1, 500) == 1:
                messages = []
                async for msg in m.channel.history(limit=50, before=m):
                    if msg.content:
                        messages.append(msg.content)
                response += markov_chain(messages)
                await m.reply(response)

            await do_response(
                f"{
                    random.choice(
                        [
                            'Mňau',
                            'víš co? raději drž hubu, protože z tohohle jsem chytil rakovinu varlat',
                            'dissnul bych tě, ale budu hodnej, takže uhhh to bude dobrý :+1:',
                            'https://www.youtube.com/watch?v=kyg1uxOsAUY',
                        ]
                    )
                }",
                m,
                chance=50000,
            )
            await do_response(
                f"{random.choice([':kekWR:', ':kekW:', ':heart:', ':5head:', ':adampat:', ':catworry:', ':maregg:', ':pepela:', ':pog:', ':333:'])}",
                m,
                reaction=True,
                chance=1000,
            )


@client.event
async def on_message(m: Message):
    print(
        f"guild id: {m.guild.id if m.guild else 'DM'}, channel id: {m.channel.id}, author: {m.author}, content: {m.content}"
    )
    if not m.content:
        return
    if str(m.author) == "šimek#3885":
        return
    await manage_response(m)


async def cleanup():
    """Clean up resources when bot shuts down"""
    global http_session
    if http_session and not http_session.closed:
        await http_session.close()


# Register cleanup to run when bot shuts down
@client.event
async def on_disconnect():
    await cleanup()


if __name__ == "__main__":
    try:
        client.run(TOKEN)
    finally:
        # Ensure cleanup runs even if there's an exception
        import asyncio

        asyncio.run(cleanup())
