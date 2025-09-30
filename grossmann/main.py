import io
import os
import random
from collections.abc import Iterable
from enum import Enum

import aiohttp
import disnake
from disnake import Message, ApplicationCommandInteraction, Embed
from disnake.ext.commands import Bot, default_member_permissions, Param, InteractionBot
from dotenv import load_dotenv

import decimdictionary as decdi

# TODO: logging
# TODO: make all stuff loadable modules

# todo: ekonpolipero mit na nakliknutelnou roli, ale v ekonpolipera to hodí anketu a musí to třeba 3 lidi approvnout
# todo: role na selfservice přidávat commandem
#   a pak přidat command na dump uložených rolí do zdrojáku
#   nějak to parametrizovat per server

# todo: figure out how to make it a subclass
class DiscordSelfServiceRoles(str, Enum):
    """Seznam rolí, co si lidi sami můžou naklikat"""
    CLEN = "Člen"
    OSTRAVAK = "Ostravák"
    PRAZAK = "Pražák"
    BRNAK = "brnak"
    MAGIC_THE_GATHERING = "magicTheGathering"

    @property
    def role_id(self) -> int:
        """Get the Discord role ID for this role"""
        match self:
            case DiscordSelfServiceRoles.CLEN:
                return 804431648959627294
            case DiscordSelfServiceRoles.OSTRAVAK:
                return 988431391807131690
            case DiscordSelfServiceRoles.PRAZAK:
                return 998636130511630386
            case DiscordSelfServiceRoles.BRNAK:
                return 1105227159712309391
            case DiscordSelfServiceRoles.MAGIC_THE_GATHERING:
                return 1327396658605981797

    @classmethod
    def get_role_id_by_name(cls, role_name: str) -> int | None:
        """Get role ID by role name"""
        try:
            role = cls(role_name)
            return role.role_id
        except ValueError:
            return None


class DiscordGamingRoles(str, Enum):
    """Seznam rolí, co si lidi sami můžou naklikat"""
    WARCRAFT = "warcraft"
    GMOD = "gmod"
    VALORANT = "valorant"
    KYOUDAI = "kyoudai"
    LOLKO = "lolko"
    DOTA2 = "dota2"
    CSGO = "csgo"
    SEA_OF_THIEVES = "sea of thieves"
    DUHOVA_SESTKA = "duhová šestka"
    MINECRAFT = "minecraft"
    DARK_AND_DARKER = "dark and darker"
    GOLFISTI = "golfisti"
    WOWKO = "WoWko"
    CIVKY = "civky"
    ROCKANDSTONE = "rockandstone"
    HOTS = "hots"
    GTAONLINE = "gtaonline"
    WARFRAME = "warframe"
    HELLDIVERS = "helldivers"
    VOIDBOYS = "voidboys"
    THEFINALS = "thefinals"
    BEYOND_ALL_REASON = "BeyondAllReason"
    VALHEIM = "Valheim"

    @property
    def role_id(self) -> int:
        """Get the Discord role ID for this role"""
        match self:
            case DiscordGamingRoles.WARCRAFT:
                return 871817685439234108
            case DiscordGamingRoles.GMOD:
                return 951457356221394975
            case DiscordGamingRoles.VALORANT:
                return 991026818054225931
            case DiscordGamingRoles.KYOUDAI:
                return 1031510557163008010
            case DiscordGamingRoles.LOLKO:
                return 994302892561399889
            case DiscordGamingRoles.DOTA2:
                return 994303445735587991
            case DiscordGamingRoles.CSGO:
                return 994303566082740224
            case DiscordGamingRoles.SEA_OF_THIEVES:
                return 994303863643451442
            case DiscordGamingRoles.DUHOVA_SESTKA:
                return 1011212649704460378
            case DiscordGamingRoles.MINECRAFT:
                return 1049052005341069382
            case DiscordGamingRoles.DARK_AND_DARKER:
                return 1054111346733617222
            case DiscordGamingRoles.GOLFISTI:
                return 1076931268555587645
            case DiscordGamingRoles.WOWKO:
                return 1120426868697473024
            case DiscordGamingRoles.CIVKY:
                return 1070800908729995386
            case DiscordGamingRoles.ROCKANDSTONE:
                return 1107334623983312897
            case DiscordGamingRoles.HOTS:
                return 1140376580800118835
            case DiscordGamingRoles.GTAONLINE:
                return 1189322955063316551
            case DiscordGamingRoles.WARFRAME:
                return 1200135734590451834
            case DiscordGamingRoles.HELLDIVERS:
                return 1228002980754751621
            case DiscordGamingRoles.VOIDBOYS:
                return 1281326981878906931
            case DiscordGamingRoles.THEFINALS:
                return 1242187454837035228
            case DiscordGamingRoles.BEYOND_ALL_REASON:
                return 1358445521227874424
            case DiscordGamingRoles.VALHEIM:
                return 1356164640152883241

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
TOKEN = os.getenv("DISCORD_TOKEN")
TEXT_SYNTH_TOKEN = os.getenv("TEXT_SYNTH_TOKEN")
PREFIX = os.getenv("BOT_PREFIX") #TODO remove

# TODO is this even useful?
class UnfilteredBot(Bot):
    """An overridden version of the Bot class that will listen to other bots."""

    async def process_commands(self, message):
        """Override process_commands to listen to bots."""
        ctx = await self.get_context(message)
        await self.invoke(ctx)


# add intents for bot and command prefix for classic command support
intents = disnake.Intents.all()
intents.message_content = True
client = InteractionBot(intents=intents)  # maybe use UnfilteredBot instead?

# Global HTTP session - will be initialized when bot starts
http_session: aiohttp.ClientSession | None = None


# on_ready event - happens when bot connects to Discord API
@client.event
async def on_ready():
    global http_session
    # Initialize the global HTTP session with SSL disabled
    http_session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
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
    ctx: ApplicationCommandInteraction, question: str, option1: str, option2: str, option3: str = None, option4: str = None, option5: str = None
):
    options = [option for option in [option1, option2, option3, option4, option5] if option]
    if len(options) < 2:
        await ctx.response.send_message("You must provide at least two options.", ephemeral=True)
        return
    poll_mess = f"Anketa: {question}\n"
    m = await ctx.response.send_message("Creating poll...", ephemeral=False)
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

    if anonym:
        random_city = "Void"
        random_name = "Jan Jelen"

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
async def yesorno(ctx: ApplicationCommandInteraction, *args):
    answers = ("Yes.", "No.", "Perhaps.", "Definitely yes.", "Definitely no.")
    await ctx.response.send_message(f"{random.choice(answers)}")

@client.slash_command(
    name="warcraft_ping", description="Pings Warcraft role and open planning menu", guild_ids=decdi.GIDS
)
async def warcraft(ctx: ApplicationCommandInteraction, time: str = None):
    # send z templaty
    message_content = WARCRAFTY_CZ.replace("{0}", f" v cca {time}" if time else "")
    
    await ctx.response.send_message(message_content)
    m = await ctx.original_message()
    # přidání reakcí
    await batch_react(m, ["✅", "❎", "🤔", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "❓"])


@client.slash_command(name="game_ping", description="Pings any game", guild_ids=decdi.GIDS)
async def game_ping(
    ctx: ApplicationCommandInteraction,
    # role: DiscordGamingRoles,
    role: DiscordGamingTestingRoles,
    game: str, time: str = "20:10"):
    # send z templaty
    message_content = decdi.GAME_EN
    # role_id = str(DiscordGamingRoles(role).role_id)
    role_id = str(DiscordGamingTestingRoles(role).role_id)
    message_content = message_content.replace("{0}", role_id)
    message_content = message_content.replace("{1}", game)
    message_content = message_content.replace("{2}", f" at {time}")

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
            disnake.ui.Button(label="Člen", style=disnake.ButtonStyle.grey, custom_id="Člen", row=0),
            disnake.ui.Button(label="Pražák", style=disnake.ButtonStyle.green, custom_id="Pražák", row=1),
            disnake.ui.Button(label="Ostravák", style=disnake.ButtonStyle.green, custom_id="Ostravák", row=1),
            disnake.ui.Button(label="Brňák", style=disnake.ButtonStyle.green, custom_id="brnak", row=1),
            disnake.ui.Button(label="Carfag-péro", style=disnake.ButtonStyle.grey, custom_id="carfag", row=2),
        ],
    )
    await ctx.channel.send(
        embed=gamingembed,
        components=[
            disnake.ui.Button(label="Warcraft 3", style=disnake.ButtonStyle.blurple, custom_id="warcraft"),
            disnake.ui.Button(label="Wowko", style=disnake.ButtonStyle.blurple, custom_id="wowko"),
            disnake.ui.Button(label="Garry's Mod", style=disnake.ButtonStyle.blurple, custom_id="gmod"),
            disnake.ui.Button(label="Valorant", style=disnake.ButtonStyle.blurple, custom_id="valorant"),
            disnake.ui.Button(label="LoL", style=disnake.ButtonStyle.blurple, custom_id="lolko"),
            disnake.ui.Button(label="Dota 2", style=disnake.ButtonStyle.blurple, custom_id="dota2"),
            disnake.ui.Button(label="CS:GO", style=disnake.ButtonStyle.blurple, custom_id="csgo"),
            disnake.ui.Button(label="Sea of Thieves", style=disnake.ButtonStyle.blurple, custom_id="sea of thieves"),
            disnake.ui.Button(label="Kyoudai (Yakuza/Mahjong)", style=disnake.ButtonStyle.blurple, custom_id="kyoudai"),
            disnake.ui.Button(label="Minecraft", style=disnake.ButtonStyle.blurple, custom_id="minecraft"),
            disnake.ui.Button(label="Dark and Darker", style=disnake.ButtonStyle.blurple, custom_id="dark and darker"),
            disnake.ui.Button(label="Rainbow Six Siege", style=disnake.ButtonStyle.blurple, custom_id="duhová šestka"),
            disnake.ui.Button(label="Golf With Your Friends", style=disnake.ButtonStyle.blurple, custom_id="golfisti"),
            disnake.ui.Button(label="Civilisation V", style=disnake.ButtonStyle.blurple, custom_id="civky"),
            disnake.ui.Button(
                label="ROCK AND STONE (Deep rock Gal.)", style=disnake.ButtonStyle.blurple, custom_id="rockandstone"
            ),
            disnake.ui.Button(label="Heroes of the Storm", style=disnake.ButtonStyle.blurple, custom_id="hots"),
            disnake.ui.Button(label="GTA V online", style=disnake.ButtonStyle.blurple, custom_id="gtaonline"),
            disnake.ui.Button(label="Warframe", style=disnake.ButtonStyle.blurple, custom_id="warframe"),
            disnake.ui.Button(label="Helldivers II", style=disnake.ButtonStyle.blurple, custom_id="helldivers"),
            disnake.ui.Button(label="Void Crew", style=disnake.ButtonStyle.blurple, custom_id="voidboys"),
            disnake.ui.Button(label="Finálníci (the Finals)", style=disnake.ButtonStyle.blurple, custom_id="thefinals"),
            disnake.ui.Button(
                label="Magic: The Gathering", style=disnake.ButtonStyle.blurple, custom_id="magicTheGathering"
            ),
            disnake.ui.Button(
                label="Beyond All Reason", style=disnake.ButtonStyle.blurple, custom_id="BeyondAllReason"
            ),
            disnake.ui.Button(label="Valheim", style=disnake.ButtonStyle.blurple, custom_id="Valheim"),
        ],
    )

# TODO same as above, design more dynamic approach for role picker
@client.listen("on_button_click")
async def listener(ctx: disnake.MessageInteraction):
    role_id = DiscordSelfServiceRoles.get_role_id_by_name(ctx.component.custom_id)
    if role_id is not None:
        role = ctx.guild.get_role(role_id)
        if role in ctx.author.roles:
            await ctx.author.remove_roles(role)
            await ctx.response.send_message(content=f"Role `{ctx.component.custom_id}` removed!", ephemeral=True)
        else:
            await ctx.author.add_roles(role)
            await ctx.response.send_message(content=f"Role `{ctx.component.custom_id}` added!", ephemeral=True)
    else:
        pass


@client.slash_command(name="iwantcat", description="Sends a random cat image.", guild_ids=decdi.GIDS)
async def cat(ctx: ApplicationCommandInteraction, width: int = None, height: int = None):
    if width and height:
        w = width
        h = height
    else:
        w = random.randint(64, 640)
        h = random.randint(64, 640)

    await send_http_response(
        ctx, f"https://placecats.com/{w}/{h}", "image", "Server connection error :( No fox image for you."
    )

async def send_http_response(ctx: ApplicationCommandInteraction, url: str, resp_key: str, error_message: str) -> None:
    try:
        async with http_session.get(url) as api_call:
            if api_call.status == 200:
                match api_call.content_type:
                    case "image/gif" | "image/jpeg" | "image/png":
                        result = await api_call.content.read()
                        bytes_io = io.BytesIO()
                        bytes_io.write(result)
                        bytes_io.seek(0)
                        await respond(ctx, embed=Embed().set_image(file=disnake.File(fp=bytes_io, filename="image.png")))
                    case "application/json":
                        result = (await api_call.json())[resp_key]
                        await respond(ctx, content=result)
            else:
                await respond(ctx, content=error_message)
    except Exception as exc:
        print(f"Encountered exception:\n {exc}")
        await respond(ctx, content="Oh nyo?!?! Something went ^w^ wwong!!")


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
async def waifu(ctx: ApplicationCommandInteraction, content_type: str = Param(choices=["sfw", "nsfw"], default="sfw"), category: str = Param(default="neko")):
    url = f"https://api.waifu.pics/{content_type}/{category}"
    await send_http_response(ctx, url, "url", "Server connection error :( No waifu image for you.")


# TODO ?????
@client.slash_command(description="Auto status command", guild_ids=decdi.GIDS)
async def autostat(ctx: ApplicationCommandInteraction):
    await ctx.response.send_message("OK;")


# sends an xkcd comic
@client.slash_command(
    name="xkcd", description="Sends an xkcd comic by ID or the latest one if no ID is provided.", guild_ids=decdi.GIDS
)
async def xkcd(ctx: ApplicationCommandInteraction, id: str = None):
    if id:
        url = f"https://xkcd.com/{id}/info.0.json"
    else:
        url = "https://xkcd.com/info.0.json"
    await send_http_response(ctx, url, "img", "No such xkcd comics with this ID found.")


def has_any(content: str, words: Iterable) -> bool:
    return any(word in content for word in words)


async def bot_validate(content: str, m: Message):
    if content.startswith("hodný bot") or "good bot" in content:
        await m.add_reaction("🙂")
    if content.startswith("zlý bot") or has_any(content, ["bad bot", "naser si bote", "si naser bote"]):
        await m.add_reaction("😢")


# on message eventy
# TODO this can be mostly cleaned up/removed as Grossmann is more focused on slash commands and "being useful" (keep some simple silly interactons?)
@client.event
async def on_message(m: Message):
    content = m.content.lower()
    if not m.content:
        pass
    elif str(m.author) != "DecimBOT 2.0#8467":
        await bot_validate(content, m)
        if "všechno nejlepší" in m.content.lower():
            await m.add_reaction("🥳")
            await m.add_reaction("🎉")
        if "co jsem to stvořil" in m.content.lower() and m.author == "SkavenLord58#0420":
            await m.reply("https://media.tenor.com/QRTVgLglL6AAAAAd/thanos-avengers.gif")
        if "decim je negr" in m.content.lower():
            await m.channel.send("nn, ty seš")


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
