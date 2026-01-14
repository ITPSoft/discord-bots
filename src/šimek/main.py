import datetime as dt
import logging
import os
import random
import re
import textwrap

import disnake

from common.constants import Channel, ŠIMEK_NAME, KEKWR
from common.http import close_http_session, prepare_http_response, TextResponse
from common.utils import has_any, has_all, ping_function, ping_content, get_gids
from common import discord_logging
from disnake import Message, ApplicationCommandInteraction, Forbidden
from disnake.ext.commands import InteractionBot, default_member_permissions, Param
from dotenv import load_dotenv
from šimek import šimekdict
from šimek.šimekdict import RANDOM_EMOJIS

# preload all useful stuff
load_dotenv()

# add intents for bot
intents = disnake.Intents.all()
client = InteractionBot(intents=intents)  # so we can have debug commands

discord_logging.configure_logging(client)

# so logger is configured, this is intentional, files are read when importing these
from šimek.utils import format_time_ago, markov_chain
from šimek.morphodita_utils import find_self_reference_a, needs_help_a

logger = logging.getLogger(__name__)

TOKEN = os.getenv("ŠIMEK_DISCORD_TOKEN")
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
    "Bruh.",
    "Nemám tušení.",
)  # repeated ano/ne/perhaps to give it a more common occurrence

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

COOLDOWN = 30  # sekund

# for easier testing
CUSTOM_COOLDOWNS = {
    Channel.BOT_TESTING.value: 0,
}

last_reaction_time: dict[int, dt.datetime] = {}


@client.slash_command(description="Show last reaction times", guild_ids=get_gids())
@default_member_permissions(administrator=True)
async def show_last_reaction_times(inter: ApplicationCommandInteraction):
    await inter.response.send_message(last_reaction_times())


def last_reaction_times() -> str:
    response = "Last reaction times per channel:\n"
    for channel_id, time in last_reaction_time.items():
        channel = client.get_channel(channel_id)
        if channel:
            time_ago = format_time_ago(time)
            response += f"{channel.name}: {time.strftime('%Y-%m-%d %H:%M:%S')} ({time_ago})\n"
    return response


@client.slash_command(name="ping_šimek", description="check šimek latency", guild_ids=get_gids())
@default_member_permissions(administrator=True)
async def ping(ctx: ApplicationCommandInteraction):
    await ping_function(client, ctx)


@client.slash_command(name="debug_šimek", description="check šimek latency", guild_ids=get_gids())
@default_member_permissions(administrator=True)
async def debug_dump(ctx: ApplicationCommandInteraction):
    response = textwrap.dedent(f"""
        {ping_content(client)}
        {get_gids()=}
        {last_reaction_times()}
    """)
    await ctx.response.send_message(response)


# debug command/trolling
@client.slash_command(name="respond_šimek", description="Respond something as šimek (admin only)", guild_ids=get_gids())
@default_member_permissions(administrator=True)
async def respond(
    ctx: ApplicationCommandInteraction,
    message: str,
    chance: int = Param(default=1, gt=0, description="Chance to respond"),
    reaction: bool = Param(default=False, description="React instead of replying"),
):
    target_msg = await ctx.channel.send("debug message")  # reply-able message
    await do_response(message, target_msg, chance=chance, reaction=reaction)


# on_ready event - happens when bot connects to Discord API
@client.event
async def on_ready():
    logger.info(f"{client.user} has connected to Discord!")


# we use an evil class magic to hack match case to check for substrings istead of exact matches
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


async def do_response(reply: str, m: Message, *, chance: int = 10, reaction: bool = False):
    """
    reply: str - text or emoji to reply with
    m: Message - message object to reply to
    chance: int - 1 in `chance` probability to reply
    reaction: bool - if True, add reaction instead of reply
    """
    # safeguard against all role tags
    if random.randint(1, chance) == 1:
        try:
            reply = remove_mentions(reply)
            if reaction:
                await m.add_reaction(reply)
            else:
                await m.reply(reply)
            last_reaction_time[m.channel.id] = dt.datetime.now()
        except Forbidden:
            logger.warning(f"Tried to post {reply=} to {m.content=} in {m.channel.name=}, but it's not allowed")
        except Exception as e:
            logger.exception(f"Failed to send {reply=}, {reaction=} in {m.channel.name=}", exc_info=e)


def remove_mentions(reply: str) -> str:
    return re.sub(r"<@!?&?\d+>|@everyone|@here", "`někdo`", reply)


async def manage_response(m: Message):
    # grok feature is above all others and will trigger anywhere
    response = ""
    mess = m.content.lower()

    now = dt.datetime.now()
    # higher priority than the rest
    if "drž hubu" in mess and m.reference and m.reference.resolved and m.reference.resolved.author == client.user:
        await do_response("ok", m, chance=1)
        last_reaction_time[m.channel.id] = now + dt.timedelta(minutes=5)  # 5-minute timeout after being told to shut up
        return  # skip setting the time again at the end of the function

    last_time = last_reaction_time.get(m.channel.id)
    if last_time and (seconds_diff := (now - last_time).total_seconds()) < cooldown(m.channel.id):
        logger.debug(f"Too soon, last replied {seconds_diff} seconds ago")
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
                msg.content = remove_mentions(msg.content)  # remove bot mentions
                msg.content = msg.content.replace(",", "")  # cleanup
                if msg.author == client.user:  # throw away messages from itself
                    continue
                messages.append(msg.content)
        response = f"{random.choice(REPLIES)} Protože "
        response += markov_chain(messages, max_words=random.randint(15, 40))
        try:
            await m.reply(response)
            last_reaction_time[m.channel.id] = dt.datetime.now()
        except Forbidden:
            logger.warning(f"Tried to post {response=} to {m.content=} in {m.channel.name=}, but it's not allowed")
        return

    # ECONPOLIPERO IS A SERIOUS CHANNEL, NO SHITPOSTING ALLOWED gif
    if m.channel.id == Channel.ECONPOLIPERO:
        if has_any(
            mess, [":kekwr:", ":kekw:"]
        ):  # need to compare lowered versions, here we don't care of specific kekw instance
            await do_response(
                "https://media.discordapp.net/attachments/786626221856391199/1420065025896349777/a6yolw.gif?ex=68f0625d&is=68ef10dd&hm=084f583c9cc1b0a6e6279ccf44933984cdb51167c7fe265c52c3be44725540cf&=&width=450&height=253",
                m,
                chance=4,
                reaction=False,
            )
        return

    elif m.channel.id not in ALLOW_CHANNELS:
        return
    logger.debug("Check passed, getting into main loop")
    # we are matching whole substrings now, not exact matches, only one case will be executed, if none match, default case will be executed

    # analysing dad jokes and mom jokes
    jsi_is_ref = jsem_is_ref = False
    jsi_who = jsem_who = ""
    help_needed = False
    if "jsi" in mess:
        jsi_is_ref, jsi_who, _ = await find_self_reference_a(mess, "jsi", False)
    if "jsem" in mess:
        jsem_is_ref, jsem_who, _ = await find_self_reference_a(mess, "jsem", True)

    matched = True
    oogway_help = f"""„{random.choice(šimekdict.MOT_HLASKY)}“
                                                                                - Mistr Oogway, {random.randint(461, 490)} př. n. l."""
    if "pomo" in mess:
        help_needed = await needs_help_a(mess)

    match Substring(mess):
        case "hodný bot":
            await do_response("🙂", m, chance=1, reaction=True)
        case _ if has_all(mess, ["problém", "windows"]):
            await do_response(
                f"Radikální řešení :point_right: https://fedoraproject.org/workstation/download {KEKWR}",
                m,
                chance=1,
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
            await do_response(random.choice([šimekdict.LINUX_COPYPASTA, šimekdict.CESKA_LINUX_COPYPASTA]), m, chance=20)
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
            await do_response("👍", m, chance=30)
        case "israel" | "izrael":
            await do_response(":pensive:", m, chance=5)
        case "mama" | "mamá" | "mami" | "mommy" | "mamka" | "mamko":
            match await prepare_http_response(url="https://yomama-jokes.com/api/random", resp_key="joke"):
                case TextResponse(_, content):
                    await do_response(content, m, chance=4)
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
            await do_response("👍", m, chance=1, reaction=True)
        case "reminder":
            await do_response("kind reminder: ur a bitch :)", m, chance=4)
        case "youtu.be" | "youtube.com":
            await do_response(random.choice(šimekdict.RECENZE), m, chance=5)
        case "špatný bot" | "spatny bot":
            await do_response("i'm trying my best :pensive:", m, chance=1)
        case "podle mě" | "myslím si" | "myslim si":
            await do_response(f"{random.choice(['souhlasím', 'nesouhlasím', ''])}", m, chance=10)
        case "roll joint":
            await do_response("https://youtu.be/LF6ok8IelJo?t=56", m, chance=1)
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
                            'dissnul bych tě, ale budu hodnej, takže uhhh to bude dobrý 👍',
                            'https://www.youtube.com/watch?v=kyg1uxOsAUY',
                        ]
                    )
                }",
                m,
                chance=50000,
            )

            await do_response(f"{random.choice(RANDOM_EMOJIS)}", m, reaction=True, chance=1000)


@client.event
async def on_message(m: Message):
    logger.debug(
        f"guild id: {m.guild.id if m.guild else 'DM'}, channel id: {m.channel.id}, author: {m.author}, content: {m.content}"
    )
    if m.guild and m.guild.id not in get_gids():
        return
    if not m.content:
        return
    if str(m.author) == ŠIMEK_NAME:
        return
    await manage_response(m)


async def cleanup():
    """Clean up resources when bot shuts down"""
    await close_http_session()


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
