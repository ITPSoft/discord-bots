import logging
import os
import random
import time
from datetime import datetime
from enum import Enum

import aiohttp
import disnake
from disnake import Message, ApplicationCommandInteraction, Embed, ButtonStyle
from disnake.ui import Button
from disnake.ext.commands import Bot, Param, InteractionBot, default_member_permissions
from dotenv import load_dotenv

from common.utils import has_any, prepare_http_response, ResponseType
from grossmann import grossmanndict as decdi

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s:%(levelname)s:%(name)s: %(message)s")


# TODO: logging
# TODO: make all stuff loadable modules

# todo: ekonpolipero mit na nakliknutelnou roli, ale v ekonpolipera to hodí anketu a musí to třeba 3 lidi approvnout
# todo: role na selfservice přidávat commandem
#   a pak přidat command na dump uložených rolí do zdrojáku
#   nějak to parametrizovat per server
# aby člověk commandem mohl přidat herní nebo městskou roli


# todo: figure out how to make it a subclass
class SelfServiceRoles(str, Enum):
    """Seznam rolí, co si lidi sami můžou naklikat"""

    CLEN = "Člen"
    OSTRAVAK = "Ostravák"
    PRAZAK = "Pražák"
    BRNAK = "brnak"
    MAGIC_THE_GATHERING = "magicTheGathering"
    CARFAG = "carfag"

    @property
    def role_id(self) -> int:
        """Get the Discord role ID for this role"""
        match self:
            case SelfServiceRoles.CLEN:
                return 804431648959627294
            case SelfServiceRoles.OSTRAVAK:
                return 988431391807131690
            case SelfServiceRoles.PRAZAK:
                return 998636130511630386
            case SelfServiceRoles.BRNAK:
                return 1105227159712309391
            case SelfServiceRoles.MAGIC_THE_GATHERING:
                return 1327396658605981797
            case SelfServiceRoles.CARFAG:
                return 1057281159509319800

    @classmethod
    def get_role_id_by_name(cls, role_name: str) -> int | None:
        """Get role ID by role name"""
        try:
            role = cls(role_name)
            return role.role_id
        except ValueError:
            return None


class GamingRoles(str, Enum):
    """Seznam rolí, co si lidi sami můžou naklikat"""

    # název role
    WARCRAFT = "warcraft"
    GMOD = "gmod"
    VALORANT = "valorant"
    KYOUDAI = "kyoudai"
    LOLKO = "lolko"
    DOTA2 = "dota2"
    CSGO = "csgo"
    SEA_OF_THIEVES = "sea of thieves"
    MINECRAFT = "Minecraft"
    DARK_AND_DARKER = "Dark and Darker"
    GOLFISTI = "golfisti"
    WOWKO = "WoWko"
    ROCKANDSTONE = "kámen a šutr"
    HOTS = "hots"
    GTAONLINE = "GTA Online"
    WARFRAME = "Warframe"
    HELLDIVERS = "helldivers"
    VOIDBOYS = "voidboys"
    THEFINALS = "finalnici"
    BEYOND_ALL_REASON = "BeyondAllReason"
    VALHEIM = "valheim"
    ARC_RAIDERS = "ArcRaiders"
    FRIENDSLOP = "Friendslop"

    @property
    def role_id(self) -> int:
        """Get the Discord role ID for this role"""
        match self:
            case GamingRoles.WARCRAFT:
                return 871817685439234108
            case GamingRoles.GMOD:
                return 951457356221394975
            case GamingRoles.VALORANT:
                return 991026818054225931
            case GamingRoles.KYOUDAI:
                return 1031510557163008010
            case GamingRoles.LOLKO:
                return 994302892561399889
            case GamingRoles.DOTA2:
                return 994303445735587991
            case GamingRoles.CSGO:
                return 994303566082740224
            case GamingRoles.SEA_OF_THIEVES:
                return 994303863643451442
            case GamingRoles.MINECRAFT:
                return 1049052005341069382
            case GamingRoles.DARK_AND_DARKER:
                return 1054111346733617222
            case GamingRoles.GOLFISTI:
                return 1076931268555587645
            case GamingRoles.WOWKO:
                return 1120426868697473024
            case GamingRoles.ROCKANDSTONE:
                return 1107334623983312897
            case GamingRoles.HOTS:
                return 1140376580800118835
            case GamingRoles.GTAONLINE:
                return 1189322955063316551
            case GamingRoles.WARFRAME:
                return 1200135734590451834
            case GamingRoles.HELLDIVERS:
                return 1228002980754751621
            case GamingRoles.VOIDBOYS:
                return 1281326981878906931
            case GamingRoles.THEFINALS:
                return 1242187454837035228
            case GamingRoles.BEYOND_ALL_REASON:
                return 1358445521227874424
            case GamingRoles.VALHEIM:
                return 1356164640152883241
            case GamingRoles.ARC_RAIDERS:
                return 1432779821183930401
            case GamingRoles.FRIENDSLOP:
                return 1435240483852124292

    @classmethod
    def get_role_id_by_name(cls, role_name: str) -> int | None:
        """Get role ID by role name"""
        try:
            role = cls(role_name)
            return role.role_id
        except ValueError:
            return None


class DiscordGamingTestingRoles(str, Enum):
    """Seznam rolí, co si lidi sami můžou naklikat"""

    WARCRAFT = "warcraft"
    VALORANT = "valorant"

    @property
    def role_id(self) -> int:
        """Get the Discord role ID for this role"""
        match self:
            case DiscordGamingTestingRoles.WARCRAFT:
                return 1422634691969945830
            case DiscordGamingTestingRoles.VALORANT:
                return 1422634814095228928

    @classmethod
    def get_role_id_by_name(cls, role_name: str) -> int | None:
        """Get role ID by role name"""
        try:
            role = cls(role_name)
            return role.role_id
        except ValueError:
            return None


# preload all useful stuff
load_dotenv()
TOKEN = os.getenv("GROSSMANN_DISCORD_TOKEN")
TEXT_SYNTH_TOKEN = os.getenv("TEXT_SYNTH_TOKEN")


# TODO is this even useful?
class UnfilteredBot(Bot):
    """An overridden version of the Bot class that will listen to other bots."""

    async def process_commands(self, message):
        """Override process_commands to listen to bots."""
        ctx = await self.get_context(message)
        await self.invoke(ctx)


# needed setup to be able to read message contents
intents = disnake.Intents.all()
intents.message_content = True
client = InteractionBot(intents=intents)  # maybe use UnfilteredBot instead?

# Global HTTP session - will be initialized when bot starts
http_session: aiohttp.ClientSession | None = None

# Store last 50 forwarded message IDs for hall of fame duplicate checking
# Dict maps message_id -> timestamp
hall_of_fame_message_ids: dict[int, datetime] = {}


# on_ready event - happens when bot connects to Discord API
@client.event
async def on_ready():
    global http_session, hall_of_fame_message_ids
    # Initialize the global HTTP session with SSL disabled
    http_session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
    # Preload last 50 message IDs from hall of fame channel
    hall_of_fame_channel = client.get_channel(1276805111506796605)
    if hall_of_fame_channel:
        current_time = datetime.now()
        async for msg in hall_of_fame_channel.history(limit=50):
            # Extract original message ID from forwarded message
            # Forwarded messages have a reference to the original message
            if msg.reference and msg.reference.message_id:
                original_id = msg.reference.message_id
                # Use message creation time as timestamp, or current time if unavailable
                timestamp = msg.created_at if hasattr(msg, "created_at") else current_time
                hall_of_fame_message_ids[original_id] = timestamp
        # Keep only the 50 most recent entries (by timestamp)
        if len(hall_of_fame_message_ids) > 50:
            sorted_items = sorted(hall_of_fame_message_ids.items(), key=lambda x: x[1], reverse=True)
            hall_of_fame_message_ids = dict(sorted_items[:50])
    print(f"{client.user} has connected to Discord!")


# constants
# TODO check if needed, HELP/MOT/Linux is šimek stuff, gaming callouts are not used anymore
HELP = decdi.HELP
WARCRAFTY_CZ = decdi.WARCRAFTY_CZ


# useful functions/methods
async def batch_react(m: Message, reactions: list):
    # asyncio.gather would not guarantee order, so we need to add them one by one
    for reaction in reactions:
        await m.add_reaction(reaction)


# on_member_join - happens when a new member joins guild
@client.event
async def on_member_join(member: disnake.Member):
    welcome_channel = client.get_channel(decdi.WELCOMEPERO)
    await welcome_channel.send(f"""
Vítej, {member.mention}!
Prosím, přesuň se do <#1314388851304955904> a naklikej si role. Nezapomeň na roli Člen, abys viděl i ostatní kanály!
---
Please, go to the <#1314388851304955904> channel and select your roles. Don't forget the 'Člen'/Member role to see other channels!
                        """)
    pass


## Commands here ->
# Show all available commands
@client.slash_command(description="Show all available commands", guild_ids=decdi.GIDS)
async def decimhelp(ctx: ApplicationCommandInteraction):
    await ctx.response.send_message(HELP, ephemeral=True, delete_after=60)


@client.slash_command(description="Show ids of posts forwarded to fame", guild_ids=decdi.GIDS)
async def show_forwarded_fames(ctx: ApplicationCommandInteraction):
    response = "Last messages forwarded to hall of fame ids and times:\n"
    for message_id, sent_time in hall_of_fame_message_ids.items():
        response += f"{message_id}: {sent_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    await ctx.response.send_message(response)


# debug command/trolling
@client.slash_command(description="Say something as the bot (admin only)", guild_ids=decdi.GIDS)
@default_member_permissions(administrator=True)
async def say(ctx: ApplicationCommandInteraction, message: str):
    await ctx.response.send_message("Message sent!")
    await ctx.channel.send(message)


# poll creation, takes up to five arguments
# TODO check as slash command, probably make as embed?
# TODO add anonymity voting option (better in embed)
@client.slash_command(name="poll", description="Creates a poll with given arguments.", guild_ids=decdi.GIDS)
async def poll(
    ctx: ApplicationCommandInteraction,
    question: str,
    option1: str,
    option2: str,
    option3: str | None = None,
    option4: str | None = None,
    option5: str | None = None,
):
    options = [option for option in [option1, option2, option3, option4, option5] if option]
    if len(options) < 2:
        await ctx.send("You must provide at least two options.", ephemeral=True)
        return
    poll_mess = f"Anketa: {question}\n"
    await ctx.send("Creating poll...", ephemeral=False)
    m = await ctx.original_response()
    emoji_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
    for i, option in enumerate(options):
        poll_mess += f"{emoji_list[i]} = {option}\n"
        await m.add_reaction(emoji_list[i])
    await m.edit(content=poll_mess)


# rolls a dice
@client.slash_command(name="roll", description="Rolls a dice with given range.", guild_ids=decdi.GIDS)
async def roll(ctx: ApplicationCommandInteraction, arg_range=None):
    range = None
    try:
        range = int(arg_range)
    except Exception:
        pass

    if arg_range == "joint":
        await ctx.response.send_message("https://youtu.be/LF6ok8IelJo?t=56")
    elif not range:
        await ctx.response.send_message(f"{random.randint(0, 6)} (Defaulted to 6d.)")
    elif type(range) is int and range > 0:
        await ctx.response.send_message(f"{random.randint(0, int(range))} (Used d{range}.)")
    else:
        await ctx.response.send_message("Something's wrong. Check your syntax.")


# "twitter" functionality
# works as intended, tested troughly
@client.slash_command(name="tweet", description="Posts a 'tweet' in #twitter-pero channel.", guild_ids=decdi.GIDS)
async def tweet(ctx: ApplicationCommandInteraction, content: str, media: str = "null", anonym: bool = False):
    twitterpero = client.get_channel(decdi.TWITTERPERO)
    sentfrom = f"Sent from #{ctx.channel.name}"
    assert http_session is not None

    if anonym:
        random_city = "Void"
        random_name = "Jan Jelen"
        result = None

        try:
            async with http_session.get("https://randomuser.me//api") as api_call:
                if api_call.status == 200:
                    result = (await api_call.json())["results"][0]
                    randomizer_opt = ["0", "1", "2", "3", "4"]  # lazy way
                    randomizer_opt[0] = result["login"]["username"]
                    randomizer_opt[1] = result["email"].split("@")[0]
                    randomizer_opt[2] = result["login"]["password"] + str(result["dob"]["age"])
                    randomizer_opt[3] = result["gender"] + "goblin" + str(result["dob"]["age"])
                    randomizer_opt[4] = "lil" + result["location"]["country"].lower() + "coomer69"

                    random_name = f"@{randomizer_opt[random.randint(0, len(randomizer_opt) - 1)]}"
                    random_city = result["location"]["city"]
        except:
            pass

        embed = disnake.Embed(
            title=f"{random_name} tweeted:", description=f"{content}", color=disnake.Colour.dark_purple()
        )
        if result is not None:
            embed.set_thumbnail(url=result["picture"]["medium"])
        sentfrom = f"Sent from {random_city} (#{ctx.channel.name})"
    else:
        embed = disnake.Embed(
            title=f"{ctx.author.display_name} tweeted:", description=f"{content}", color=disnake.Colour.dark_purple()
        )
        embed.set_thumbnail(url=ctx.author.avatar)

    if media != "null":
        embed.set_image(url=media)
    embed.add_field(name="_", value=sentfrom, inline=True)
    await ctx.response.send_message(content="Tweet posted! 👍", ephemeral=True)
    m = await twitterpero.send(embed=embed)
    await batch_react(m, ["💜", "🔁", "⬇️", "💭", "🔗"])


@client.slash_command(name="pingdecim", description="check decim latency", guild_ids=decdi.GIDS)
@default_member_permissions(administrator=True)
async def ping(ctx: ApplicationCommandInteraction):
    await ctx.response.send_message(f"Pong! API Latency is {round(client.latency * 1000)}ms.")


@client.slash_command(name="yesorno", description="Answers with a random yes/no answer.", guild_ids=decdi.GIDS)
async def yesorno(ctx: ApplicationCommandInteraction):
    answers = ("Yes.", "No.", "Perhaps.", "Definitely yes.", "Definitely no.")
    await ctx.response.send_message(f"{random.choice(answers)}")


@client.slash_command(
    name="warcraft_ping", description="Pings Warcraft role and open planning menu", guild_ids=decdi.GIDS
)
async def warcraft(ctx: ApplicationCommandInteraction, start_time: str | None = None):
    # send z templaty
    message_content = WARCRAFTY_CZ.replace("{0}", f" v cca {start_time}" if start_time else "")

    await ctx.response.send_message(message_content)
    m = await ctx.original_message()
    # přidání reakcí
    await batch_react(m, ["✅", "❎", "🤔", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "❓"])


@client.slash_command(name="game_ping", description="Pings any game", guild_ids=decdi.GIDS)
async def game_ping(
    ctx: ApplicationCommandInteraction,
    # role: DiscordGamingRoles,
    game: DiscordGamingTestingRoles,
    time: str,
    note: str = "",
):
    # send z templaty
    message_content = decdi.GAME_EN
    # role_id = str(DiscordGamingRoles(role).role_id)
    role = DiscordGamingTestingRoles(game)
    message_content = message_content.replace("{0}", str(role.role_id))
    message_content = message_content.replace("{1}", str(role.value))
    message_content = message_content.replace("{2}", f" at {time}")
    message_content = message_content.replace("{3}", note)

    await ctx.response.send_message(message_content)
    m = await ctx.original_message()
    # přidání reakcí
    await batch_react(m, ["✅", "❎", "🤔", "☦️"])


# TODO is this even used?
@client.slash_command(description="Fetch guild roles (admin only)", guild_ids=decdi.GIDS)
@default_member_permissions(administrator=True)
async def fetchrole(ctx: ApplicationCommandInteraction):
    roles = await ctx.guild.fetch_roles()
    role_list = "\n".join([f"{role.name} (ID: {role.id})" for role in roles])
    await ctx.response.send_message(f"Guild roles:\n```\n{role_list}\n```", ephemeral=True)


# TODO design more dynamic approach for role picker, probably side load file with roles and ids to be able to add/remove roles and regenerate messeage without code edit
@client.slash_command(name="createrolewindow", description="Posts a role picker window.", guild_ids=decdi.GIDS)
@default_member_permissions(administrator=True)
async def command(ctx):
    embed = disnake.Embed(
        title="Role picker",
        description="Here you can pick your roles:",
        color=disnake.Colour.light_gray(),
    )
    embed.add_field(
        name="Zde jsou role na přístup do různých 'pér'.\nDejte si člena, abyste viděli všude jinde.", value="_"
    )

    gamingembed = disnake.Embed(
        title="Gaming Roles", description="Here you can pick your gaming tag roles:", color=disnake.Colour.dark_purple()
    )
    gamingembed.add_field(name="Zde jsou role na získání tagovacích rolí na hry.", value="_")

    await ctx.response.send_message(content="Done!", ephemeral=True)

    await ctx.channel.send(
        embed=embed,
        components=[
            Button(label="Člen", style=ButtonStyle.grey, custom_id=SelfServiceRoles.CLEN, row=0),
            Button(label="Pražák", style=ButtonStyle.green, custom_id=SelfServiceRoles.PRAZAK, row=1),
            Button(label="Ostravák", style=ButtonStyle.green, custom_id=SelfServiceRoles.OSTRAVAK, row=1),
            Button(label="Brňák", style=ButtonStyle.green, custom_id=SelfServiceRoles.BRNAK, row=1),
            Button(label="Carfag-péro", style=ButtonStyle.grey, custom_id=SelfServiceRoles.CARFAG, row=2),
        ],
    )
    await ctx.channel.send(
        embed=gamingembed,
        components=[
            Button(label="Warcraft 3", style=ButtonStyle.blurple, custom_id=GamingRoles.WARCRAFT),
            Button(label="Wowko", style=ButtonStyle.blurple, custom_id=GamingRoles.WOWKO),
            Button(label="Garry's Mod", style=ButtonStyle.blurple, custom_id=GamingRoles.GMOD),
            Button(label="Valorant", style=ButtonStyle.blurple, custom_id=GamingRoles.VALORANT),
            Button(label="LoL", style=ButtonStyle.blurple, custom_id=GamingRoles.LOLKO),
            Button(label="Dota 2", style=ButtonStyle.blurple, custom_id=GamingRoles.DOTA2),
            Button(label="CS:GO", style=ButtonStyle.blurple, custom_id=GamingRoles.CSGO),
            Button(label="Sea of Thieves", style=ButtonStyle.blurple, custom_id=GamingRoles.SEA_OF_THIEVES),
            Button(label="Kyoudai (Yakuza/Mahjong)", style=ButtonStyle.blurple, custom_id=GamingRoles.KYOUDAI),
            Button(label="Minecraft", style=ButtonStyle.blurple, custom_id=GamingRoles.MINECRAFT),
            Button(label="Dark and Darker", style=ButtonStyle.blurple, custom_id=GamingRoles.DARK_AND_DARKER),
            Button(label="Golf With Your Friends", style=ButtonStyle.blurple, custom_id=GamingRoles.GOLFISTI),
            Button(
                label="ROCK AND STONE (Deep rock Gal.)", style=ButtonStyle.blurple, custom_id=GamingRoles.ROCKANDSTONE
            ),
            Button(label="Heroes of the Storm", style=ButtonStyle.blurple, custom_id=GamingRoles.HOTS),
            Button(label="GTA V online", style=ButtonStyle.blurple, custom_id=GamingRoles.GTAONLINE),
            Button(label="Warframe", style=ButtonStyle.blurple, custom_id=GamingRoles.WARFRAME),
            Button(label="Helldivers II", style=ButtonStyle.blurple, custom_id=GamingRoles.HELLDIVERS),
            Button(label="Void Crew", style=ButtonStyle.blurple, custom_id=GamingRoles.VOIDBOYS),
            Button(label="Finálníci (the Finals)", style=ButtonStyle.blurple, custom_id=GamingRoles.THEFINALS),
            Button(label="Beyond All Reason", style=ButtonStyle.blurple, custom_id=GamingRoles.BEYOND_ALL_REASON),
            Button(label="Valheim", style=ButtonStyle.blurple, custom_id=GamingRoles.VALHEIM),
            Button(
                label="Mariáš The Gathering",
                style=ButtonStyle.blurple,
                custom_id=SelfServiceRoles.MAGIC_THE_GATHERING,
                row=1,
            ),
            Button(label="Friendslop", style=ButtonStyle.blurple, custom_id=GamingRoles.FRIENDSLOP),
            Button(label="Arc Raiders", style=ButtonStyle.blurple, custom_id=GamingRoles.ARC_RAIDERS),
        ],
    )


# TODO same as above, design more dynamic approach for role picker
@client.listen("on_button_click")
async def listener(ctx: disnake.MessageInteraction):
    role_id = SelfServiceRoles.get_role_id_by_name(ctx.component.custom_id) or GamingRoles.get_role_id_by_name(
        ctx.component.custom_id
    )
    logging.info(f"Role ID: {role_id=}, {ctx.component.custom_id=}, {ctx.author.name=}")
    if role_id is not None:
        role = ctx.guild.get_role(role_id)
        if role in ctx.author.roles:
            await ctx.author.remove_roles(role)
            await ctx.response.send_message(content=f"Role `{ctx.component.custom_id}` removed!", ephemeral=True)
        else:
            await ctx.author.add_roles(role)
            await ctx.response.send_message(content=f"Role `{ctx.component.custom_id}` added!", ephemeral=True)
    else:
        raise Exception(f"Unknown role ID for custom ID `{ctx.component.custom_id}`")


# todo: role by měly svítit podle toho, jestli je uživatel má nebo nemá, pokud by to šlo


@client.slash_command(name="iwantcat", description="Sends a random cat image.", guild_ids=decdi.GIDS)
async def cat(ctx: ApplicationCommandInteraction, width: int | None = None, height: int | None = None):
    if width and height:
        w = width
        h = height
    else:
        w = random.randint(64, 640)
        h = random.randint(64, 640)

    await send_http_response(
        ctx, f"https://placecats.com/{w}/{h}", "image", "Server connection error :( No fox image for you."
    )


async def send_http_response(
    ctx: ApplicationCommandInteraction,
    http_session: aiohttp.ClientSession | None,
    url: str,
    resp_key: str,
    error_message: str,
) -> None:
    resp, resp_type = prepare_http_response(
        http_session=ctx.client.http_session, url=url, resp_key=resp_key, error_message=error_message
    )
    match resp_type:
        case ResponseType.EMBED:
            await respond(ctx, embed=Embed().set_image(file=disnake.File(fp=resp, filename="image.png")))
        case ResponseType.CONTENT:
            await respond(ctx, content=error_message)


async def respond(ctx: ApplicationCommandInteraction, **results):
    if ctx.response.is_done():
        print("using followup instead of response")
        await ctx.followup.send(**results)
    else:
        await ctx.response.send_message(**results)


@client.slash_command(name="iwantfox", description="Sends a random fox image.", guild_ids=decdi.GIDS)
async def fox(ctx: ApplicationCommandInteraction):
    await send_http_response(
        ctx, "https://randomfox.ca/floof/", "image", "Server connection error :( No fox image for you."
    )


@client.slash_command(name="waifu", description="Sends a random waifu image.", guild_ids=decdi.GIDS)
async def waifu(
    ctx: ApplicationCommandInteraction,
    content_type: str = Param(choices=["sfw", "nsfw"], default="sfw"),
    category: str = Param(default="neko"),
):
    url = f"https://api.waifu.pics/{content_type}/{category}"
    await send_http_response(ctx, url, "url", "Server connection error :( No waifu image for you.")


# sends an xkcd comic
@client.slash_command(
    name="xkcd", description="Sends an xkcd comic by ID or the latest one if no ID is provided.", guild_ids=decdi.GIDS
)
async def xkcd(ctx: ApplicationCommandInteraction, xkcd_id: str | None = None):
    if xkcd_id:
        url = f"https://xkcd.com/{xkcd_id}/info.0.json"
    else:
        url = "https://xkcd.com/info.0.json"
    await send_http_response(ctx, url, "img", "No such xkcd comics with this ID found.")


async def bot_validate(content: str, m: Message):
    if content.startswith("hodný bot") or "good bot" in content:
        await m.add_reaction("🙂")
    if content.startswith("zlý bot") or has_any(content, ["bad bot", "naser si bote", "si naser bote"]):
        await m.add_reaction("😢")


# on message eventy
@client.event
async def on_message(m: Message):
    content = m.content.lower()
    if not m.content:
        pass
    elif str(m.author) != "DecimBOT 2.0#8467":  # todo: načíst si aám sebe
        await bot_validate(content, m)


# on reaction add event - hall of fame functionality
@client.event
async def on_reaction_add(reaction, user):
    global hall_of_fame_message_ids
    hall_of_fame_channel = client.get_channel(1276805111506796605)  # antispiral halloffame channel
    message = reaction.message
    # Ensure the message is on server (not a DM)
    if not message.guild:
        return
    if message.channel == hall_of_fame_channel:  # ignore hall of fame channel itself
        return

    # Avoid duplicate forwarding by checking if already sent
    # Check against cached message IDs (much faster than fetching channel history)
    if message.id in hall_of_fame_message_ids:
        return

    # Custom emojis (IDs must match actual server emojis)
    # TODO check that the match is correctly done
    hall_of_fame_emojis = [
        "⭐",
        "👍",
        "😀",
        "😃",
        "😄",
        "😁",
        "😆",
        "😅",
        "😂",
        "🤣",
        "<:kekw:940326430028488794>",
        "<:kekW:940324801585741844>",
        "<:kekWR:1063089161587933204>",
        "<:pepela:940324919739314216>",
        "<:pog:940324188172976170>",
        "<:kekface:1097817686148386856>",
    ]

    # anything that is interesting enough to cause more than 10 reactions with specific emoji should be interesting enough for hall of fame
    for r in message.reactions:
        if str(r.emoji) in hall_of_fame_emojis and r.count > 10:
            # Add message ID to cache BEFORE forwarding to prevent race conditions
            # This ensures that if multiple reactions come in simultaneously, only one forward happens
            current_time = time.time()
            hall_of_fame_message_ids[message.id] = current_time
            # Keep only the 50 most recent entries (by timestamp)
            if len(hall_of_fame_message_ids) > 50:
                # Sort by timestamp (oldest first) and remove the oldest
                sorted_items = sorted(hall_of_fame_message_ids.items(), key=lambda x: x[1])
                hall_of_fame_message_ids = dict(sorted_items[-50:])

            await message.forward(hall_of_fame_channel)  # forward that specific messeage
            break


# Load and register NetHack commands
# from nethack_module import setup_nethack_commands
# setup_nethack_commands(client, decdi.GIDS)


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
