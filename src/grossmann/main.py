import logging
import os
import random
from datetime import datetime

import disnake
from common import discord_logging
from common.constants import GIDS, Channel, GROSSMAN_NAME, HALL_OF_FAME_EMOJIS
from common.http import (
    get_http_session,
    close_http_session,
)
from common.utils import has_any, get_commit_hash, SelfServiceRoles, GamingRoles, GAMING_ROLES_PER_SERVER
from disnake import (
    Message,
    ApplicationCommandInteraction,
    ButtonStyle,
    Reaction,
    Member,
    User,
    MessageInteraction,
    Embed,
    Colour,
    Intents,
)
from disnake.ext.commands import Param, InteractionBot, default_member_permissions
from disnake.ui import Button, View
from dotenv import load_dotenv
from grossmann import grossmanndict as grossdi
from grossmann.grossmanndict import WAIFU_CATEGORIES, WAIFU_ALLOWED_NSFW, WELCOME, GAME_EN, GAME_CZ
from grossmann.utils import (
    batch_react,
    send_http_response,
    validate_image_url,
    validate_waifu_category,
    validate_game_role,
    role_tag2id,
)

# preload all useful stuff
load_dotenv()
TOKEN = os.getenv("GROSSMANN_DISCORD_TOKEN")
TEXT_SYNTH_TOKEN = os.getenv("TEXT_SYNTH_TOKEN")

# needed setup to be able to read message contents
intents = Intents.all()
intents.message_content = True
client = InteractionBot(intents=intents)

discord_logging.configure_logging(client)

logger = logging.getLogger(__name__)

# Store last 50 forwarded message IDs for hall of fame duplicate checking
# Dict maps message_id -> timestamp
hall_of_fame_message_ids: dict[int, datetime] = {}


# Load and register NetHack commands
# from nethack_module import setup_nethack_commands
# setup_nethack_commands(client, decdi.GIDS)


async def bot_validate(content: str, m: Message):
    if content.startswith("hodný bot") or "good bot" in content:
        await m.add_reaction("🙂")
    if content.startswith("zlý bot") or has_any(content, ["bad bot", "naser si bote", "si naser bote"]):
        await m.add_reaction("😢")


async def twitter_pero(anonym: bool, content: str, ctx: ApplicationCommandInteraction, image_url: str | None):
    twitterpero = client.get_channel(Channel.TWITTERPERO)
    sent_from = f"Sent from #{ctx.channel.name}"

    if anonym:
        random_city = "Void"
        random_name = "Jan Jelen"
        result = None

        try:
            async with get_http_session().get("https://randomuser.me/api") as api_call:
                if api_call.status == 200:
                    result = (await api_call.json())["results"][0]
                    age = str(result["dob"]["age"])
                    randomizer_opt = [
                        result["login"]["username"],
                        result["email"].split("@")[0],
                        result["login"]["password"] + age,
                        result["gender"] + "goblin" + age,
                        "lil" + result["location"]["country"].lower() + "coomer69",
                    ]
                    random_name = f"@{random.choice(randomizer_opt)}"
                    random_city = result["location"]["city"]
                else:
                    logger.error(f"Failed to get random user, api returned {api_call.status}")
        except Exception as e:
            logger.error("Failed to get random user", exc_info=e)

        embed = Embed(title=f"{random_name} tweeted:", description=f"{content}", color=Colour.dark_purple())
        if result is not None:
            embed.set_thumbnail(url=result["picture"]["medium"])
        sent_from = f"Sent from {random_city} (#{ctx.channel.name})"
    else:
        embed = Embed(title=f"{ctx.author.display_name} tweeted:", description=f"{content}", color=Colour.dark_purple())
        embed.set_thumbnail(url=ctx.author.avatar)

    if image_url is not None:
        embed.set_image(url=image_url)
    embed.add_field(name="_", value=sent_from, inline=True)
    await ctx.response.send_message(content="Tweet posted! 👍", ephemeral=True)
    m = await twitterpero.send(embed=embed)
    await batch_react(m, ["💜", "🔁", "⬇️", "💭", "🔗"])


async def send_role_picker(ctx: ApplicationCommandInteraction):
    embed = Embed(
        title="Role picker",
        description="Here you can pick your roles:",
        color=Colour.light_gray(),
    )
    embed.add_field(
        name="Zde jsou role na přístup do různých 'pér'.\nDejte si člena, abyste viděli všude jinde.", value="_"
    )

    gamingembed = Embed(
        title="Gaming Roles", description="Here you can pick your gaming tag roles:", color=Colour.dark_purple()
    )
    gamingembed.add_field(name="Zde jsou role na získání tagovacích rolí na hry.", value="_")

    role_rows = [
        [SelfServiceRoles.CLEN],
        [SelfServiceRoles.PRAZAK, SelfServiceRoles.OSTRAVAK, SelfServiceRoles.BRNAK],
        [SelfServiceRoles.CARFAG],  # další péra strkejte sem
    ]
    row_colors = [
        ButtonStyle.red,
        ButtonStyle.green,
        ButtonStyle.blurple,
    ]
    role_rows_inv = {role: row for row, roles in enumerate(role_rows) for role in roles}
    self_service_buttons = [
        Button(
            label=role.button_label,
            style=row_colors[role_rows_inv[role]],
            custom_id=role.role_name,
            row=role_rows_inv[role],
        )
        for role in SelfServiceRoles
    ]
    # view needs to be used so rows have some effect
    view = View()
    for b in self_service_buttons:
        view.add_item(b)
    await ctx.channel.send(
        embed=embed,
        view=view,
    )

    # Build gaming role buttons dynamically from the server's gaming roles enum
    gaming_roles_enum = GAMING_ROLES_PER_SERVER.get(ctx.guild_id, GamingRoles)
    gaming_buttons = [
        Button(label=role.button_label, style=ButtonStyle.blurple, custom_id=role.role_name)
        for role in gaming_roles_enum
    ]

    await ctx.channel.send(embed=gamingembed, components=gaming_buttons)

    await ctx.response.send_message(content="Done!", ephemeral=True)


#########################
#         events        #
#########################


# on_ready event - happens when bot connects to Discord API
@client.event
async def on_ready():
    global hall_of_fame_message_ids
    # Preload last 50 message IDs from hall of fame channel
    await hall_of_fame_history_fetching()
    logger.info(f"{client.user} has connected to Discord!")


async def hall_of_fame_history_fetching():
    global hall_of_fame_message_ids
    hall_of_fame_channel = client.get_channel(Channel.HALL_OF_FAME)
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


@client.event
async def on_message(m: Message):
    content = m.content.lower()
    if not content:
        return
    elif str(m.author) == GROSSMAN_NAME:
        return
    else:
        await bot_validate(content, m)


# on reaction add event - hall of fame functionality
@client.event
async def on_reaction_add(reaction: Reaction, user: Member | User):
    global hall_of_fame_message_ids
    hall_of_fame_channel = client.get_channel(Channel.HALL_OF_FAME)
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

    # anything that is interesting enough to cause more than 10 reactions with specific emoji should be interesting enough for hall of fame
    for r in message.reactions:
        if str(r.emoji) in HALL_OF_FAME_EMOJIS and r.count > 10:
            # Add message ID to cache BEFORE forwarding to prevent race conditions
            # This ensures that if multiple reactions come in simultaneously, only one forward happens
            current_time = datetime.now()
            hall_of_fame_message_ids[message.id] = current_time
            # Keep only the 50 most recent entries (by timestamp)
            if len(hall_of_fame_message_ids) > 50:
                # Sort by timestamp (oldest first) and remove the oldest
                sorted_items = sorted(hall_of_fame_message_ids.items(), key=lambda x: x[1])
                hall_of_fame_message_ids = dict(sorted_items[-50:])

            await message.forward(hall_of_fame_channel)  # forward that specific messeage
            break


# on_member_join - happens when a new member joins guild
@client.event
async def on_member_join(member: Member):
    welcome_channel = client.get_channel(Channel.WELCOMEPERO)
    await welcome_channel.send(WELCOME.substitute(member=member.mention))


@client.listen("on_button_click")
async def listener(ctx: MessageInteraction):
    gaming_roles_enum = GAMING_ROLES_PER_SERVER.get(ctx.guild_id, GamingRoles)
    role_id = SelfServiceRoles.get_role_id_by_name(ctx.component.custom_id) or gaming_roles_enum.get_role_id_by_name(
        ctx.component.custom_id
    )
    logging.info(f"Role ID: {role_id=}, {ctx.component.custom_id=}, {ctx.author.name=}")
    if role_id is not None:
        role = ctx.guild.get_role(role_id)
        if role.position > ctx.me.top_role.position:
            raise Exception(f"Role `{ctx.component.custom_id}` is higher than bot role, something is messed up")
        if role in ctx.author.roles:
            await ctx.author.remove_roles(role)
            await ctx.response.send_message(content=f"Role `{ctx.component.custom_id}` removed!", ephemeral=True)
        else:
            await ctx.author.add_roles(role)
            await ctx.response.send_message(content=f"Role `{ctx.component.custom_id}` added!", ephemeral=True)
    else:
        raise Exception(f"Unknown role ID for custom ID `{ctx.component.custom_id}`")


#########################
#        commands       #
#########################


## Commands here ->
# Show all available commands
@client.slash_command(description="Show all available commands", guild_ids=GIDS)
@default_member_permissions(administrator=True)  # only for admins until updated, not that useful for slash commands
async def decimhelp(ctx: ApplicationCommandInteraction):
    await ctx.response.send_message(grossdi.HELP, ephemeral=True, delete_after=60)


# debug command
@client.slash_command(description="Show ids of posts forwarded to fame", guild_ids=GIDS)
@default_member_permissions(administrator=True)
async def show_forwarded_fames(ctx: ApplicationCommandInteraction):
    response = "Last messages forwarded to hall of fame ids and times:\n"
    for message_id, sent_time in hall_of_fame_message_ids.items():
        response += f"{message_id}: {sent_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    await ctx.response.send_message(response)


# debug command/trolling
@client.slash_command(description="Say something as the bot (admin only)", guild_ids=GIDS)
@default_member_permissions(administrator=True)
async def say(ctx: ApplicationCommandInteraction, message: str):
    await ctx.response.send_message("Message sent!")
    await ctx.channel.send(message)


# poll creation, takes up to five arguments
@client.slash_command(name="poll", description="Creates a poll with given arguments.", guild_ids=GIDS)
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
@client.slash_command(name="roll", description="Rolls a dice with given range.", guild_ids=GIDS)
async def roll(
    ctx: ApplicationCommandInteraction,
    roll_range: int = Param(default=6, gt=0, description="Enter a positive integer (1 or higher, default 6)"),
):
    await ctx.response.send_message(f"You rolled {random.randint(0, roll_range)} (Used d{roll_range}).")


# "twitter" functionality
# works as intended, tested thoroughly
@client.slash_command(name="tweet", description="Posts a 'tweet' in #twitter-pero channel.", guild_ids=GIDS)
async def tweet(
    ctx: ApplicationCommandInteraction,
    content: str,
    media: str | None = Param(
        default=None, converter=validate_image_url("media"), max_length=2000, description="Image URL (PNG, JPG, etc.)"
    ),
    anonym: bool = Param(default=False, description="Post as anonymous under random username"),
):
    await twitter_pero(anonym, content, ctx, media)


@client.slash_command(name="ping_grossmann", description="check grossmann latency", guild_ids=GIDS)
@default_member_permissions(administrator=True)
async def ping(ctx: ApplicationCommandInteraction):
    await ctx.response.send_message(
        f"Pong! API Latency is {round(client.latency * 1000)}ms. Commit: {get_commit_hash()}"
    )


@client.slash_command(name="yesorno", description="Answers with a random yes/no answer.", guild_ids=GIDS)
async def yesorno(ctx: ApplicationCommandInteraction):
    answers = ("Yes.", "No.", "Perhaps.", "Definitely yes.", "Definitely no.")
    await ctx.response.send_message(f"{random.choice(answers)}")


@client.slash_command(name="warcraft_ping", description="Pings Warcraft role and open planning menu", guild_ids=GIDS)
async def warcraft(
    ctx: ApplicationCommandInteraction,
    start_time: str | None = Param(default=None, description="Time to start playing"),
):
    # send z templaty
    message_content = grossdi.WARCRAFTY_CZ.substitute(time=f" v cca {start_time}" if start_time else "")

    await ctx.response.send_message(message_content)
    m = await ctx.original_message()
    # přidání reakcí
    await batch_react(m, ["✅", "❎", "🤔", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "❓"])


@client.slash_command(name="game_ping", description="Pings any game", guild_ids=GIDS)
async def game_ping(
    ctx: ApplicationCommandInteraction,
    game_role: str = Param(
        converter=validate_game_role("game_role"), description="Game role tag: @rolename, use discord suggestions."
    ),
    time: str = Param(description="Time to start playing"),
    lang: str = Param(name="lang", choices=["cz", "en"], default="cz", description="Message language"),
    note: str = Param(default="", description="Additional note"),
):
    role = GAMING_ROLES_PER_SERVER[ctx.guild_id].get_by_role_id(role_tag2id(game_role))
    template = GAME_CZ if lang == "cz" else GAME_EN
    message_content = template.substitute(role_id=role.role_id, game=role.role_name, time=time, note=note)

    await ctx.response.send_message(message_content)
    m = await ctx.original_message()
    await batch_react(m, ["✅", "❎", "🤔", "☦️"])


@client.slash_command(description="Fetch guild roles (admin only)", guild_ids=GIDS)
@default_member_permissions(administrator=True)
async def fetchrole(ctx: ApplicationCommandInteraction):
    # useful for debugging, quickly gives IDs
    roles = await ctx.guild.fetch_roles()
    role_list = "\n".join([f"{role.name} (ID: {role.id})" for role in roles])
    await ctx.response.send_message(f"Guild roles:\n```\n{role_list}\n```", ephemeral=True)


@client.slash_command(name="createrolewindow", description="Posts a role picker window.", guild_ids=GIDS)
@default_member_permissions(administrator=True)
async def command(ctx: ApplicationCommandInteraction):
    await send_role_picker(ctx)


@client.slash_command(name="iwantcat", description="Sends a random cat image.", guild_ids=GIDS)
async def cat(
    ctx: ApplicationCommandInteraction,
    width: int | None = Param(default=None, gt=60, lt=1000, description="Enter width"),
    height: int | None = Param(default=None, gt=60, lt=1000, description="Enter height"),
):
    w = random.randint(64, 640) if width is None else width
    h = random.randint(64, 640) if height is None else height
    await send_http_response(
        ctx, f"https://placecats.com/{w}/{h}", "image", "Server connection error :( No cat image for you."
    )


@client.slash_command(name="iwantfox", description="Sends a random fox image.", guild_ids=GIDS)
async def fox(ctx: ApplicationCommandInteraction):
    await send_http_response(
        ctx, "https://randomfox.ca/floof/", "image", "Server connection error :( No fox image for you."
    )


@client.slash_command(name="waifu", description="Sends a random waifu image.", guild_ids=GIDS)
async def waifu(
    ctx: ApplicationCommandInteraction,
    content_type: str = Param(name="type", choices=list(WAIFU_CATEGORIES.keys()), default="sfw"),
    category: str = Param(converter=validate_waifu_category("category"), default="neko"),
):
    # Validate the channel based on content_type
    if content_type == "nsfw" and ctx.channel.id not in WAIFU_ALLOWED_NSFW:
        await ctx.response.send_message(
            f"S {content_type} {category} anime ženami jdi do <#{WAIFU_ALLOWED_NSFW[0]}>, ty prase.",
            ephemeral=False,  # public shaming
        )
        return
    url = f"https://api.waifu.pics/{content_type}/{category}"
    await send_http_response(ctx, url, "url", "Server connection error :( No waifu image for you.")


@waifu.autocomplete("category")
async def category_autocomplete(ctx: disnake.ApplicationCommandInteraction, current: str):
    # Get the selected category from the interaction
    category = ctx.options.get("type")

    if not category or category not in WAIFU_CATEGORIES:
        return []  # No category selected yet

    # Filter subcategories by current input
    categories = WAIFU_CATEGORIES[category]
    filtered = [category for category in categories if current.lower() in category.lower()]

    return filtered[:25]  # Discord limits to 25 choices


# sends an xkcd comic
@client.slash_command(
    name="xkcd", description="Sends an xkcd comic by ID or the latest one if no ID is provided.", guild_ids=GIDS
)
async def xkcd(
    ctx: ApplicationCommandInteraction,
    xkcd_id: int | None = Param(default=None, gt=0, description="Enter an XKCD strip number."),
):
    if xkcd_id:
        url = f"https://xkcd.com/{xkcd_id}/info.0.json"
    else:
        url = "https://xkcd.com/info.0.json"
    await send_http_response(ctx, url, "img", "No such xkcd comics with this ID found.")


#########################
#       disconnect      #
#########################


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
