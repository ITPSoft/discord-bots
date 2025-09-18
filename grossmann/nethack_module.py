# nethack_module.py
import os
import asyncio
import pexpect
import pyte
import disnake
import datetime
from disnake.ext import commands
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# Constants for access control
ALLOWED_CHANNEL_ID = 1381296005441523885
ADMIN_ROLE_ID = 786618350095695872

# Globals for NetHack session
nethack_proc = None
nethack_screen = None
nethack_stream = None
nethack_lock = asyncio.Lock()

NETHACK_PATH = os.getenv("NETHACK_PATH", "nethack")
NETHACK_ROWS = 34
NETHACK_COLS = 80

# Game control functions
async def start_nethack():
    global nethack_proc, nethack_screen, nethack_stream
    if nethack_proc is not None:
        return "NetHack is already running."

    nethack_screen = pyte.Screen(NETHACK_COLS, NETHACK_ROWS)
    nethack_stream = pyte.Stream()
    nethack_stream.attach(nethack_screen)

    env = os.environ.copy()
    env["LINES"] = str(NETHACK_ROWS)
    env["COLUMNS"] = str(NETHACK_COLS)
    env["TERM"] = "xterm-256color"
    env["LANG"] = "en_US.UTF-8"
    env["LC_ALL"] = "en_US.UTF-8"
    env["NCURSES_NO_UTF8_ACS"] = "1"
    
    env["NETHACKOPTIONS"] = (
    "number_pad:1,"
    "windowtype:curses,"
    "IBMGraphics_2:1,"
    "perm_invent,"
    f"term_rows:{NETHACK_ROWS},"
    f"term_cols:{NETHACK_COLS},"
    "statuslines:2,"
    "pickup_types:$?!/(,"
    "pickup_burden:unencumbered,"
    "align_status:bottom,"
    "align_message:top,"
    "windowborders:2"
    )

    nethack_proc = pexpect.spawn(
        NETHACK_PATH, 
        encoding='cp437',
        dimensions=(NETHACK_ROWS, NETHACK_COLS),
        env=env
    )
    await asyncio.sleep(1)
    try:
        output = nethack_proc.read_nonblocking(size=4096, timeout=5)
        nethack_stream.feed(output)
        return render_screen()
    except Exception as e:
        return f"Error starting NetHack: {e}"

async def stop_nethack():
    global nethack_proc
    if nethack_proc:
        nethack_proc.terminate(force=True)
        nethack_proc = None
        nethack_screen = None
        nethack_stream = None
        await asyncio.sleep(1)  # Give time for the process to terminate
        if nethack_proc.isalive():
            nethack_proc.kill(0)
        nethack_lock = asyncio.Lock()  # Reset the lock
        return "NetHack stopped."
    return "NetHack is not running."

def render_screen():
    #if not nethack_screen:
    #    return "Screen not initialized."
    #body = "\n".join("".join([c.data for c in nethack_screen.buffer[y].values()]) for y in range(nethack_screen.lines))
    #embed = disnake.Embed(
    #    title="NETHACK Status",
    #    description=f"```\n{body}\n```",
    #    timestamp=datetime.datetime.now(),
    #)
    #return embed
    return render_pyte_to_image(screen=nethack_screen)


def render_pyte_to_image(screen, font_path="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", font_size=16, padding=8):

    font = ImageFont.truetype(font_path, font_size)
    char_w, char_h = font.getbbox("W")[2:]
    img_w = NETHACK_COLS * char_w + padding * 2
    img_h = NETHACK_ROWS * char_h + padding * 2

    img = Image.new("RGB", (img_w, img_h), color="#13001f")
    draw = ImageDraw.Draw(img)

    y = padding
    for row in screen.buffer.values():
        for x, char in row.items():
            fg = char.fg if (char.fg and char.fg != 'default') else "white"
            # Map xterm-256color names to hex codes
            xterm_to_hex = {
                "black": "#000000",
                "red": "#cd0000",
                "green": "#00cd00",
                "yellow": "#cdcd00",
                "blue": "#0000ee",
                "magenta": "#cd00cd",
                "cyan": "#00cdcd",
                "white": "#dcdfe0",
                "brightblack": "#7f7f7f",
                "brightred": "#ff0000",
                "brightgreen": "#00ff00",
                "brightyellow": "#ffff00",
                "brightblue": "#5c5cff",
                "brightmagenta": "#ff00ff",
                "brightcyan": "#00ffff", 
                "brightwhite": "#ffffff", 
                "default": "#b099ad", 
                None: "#ffffff",
            }
            fg = xterm_to_hex.get(fg, "#ffffff")
            draw.text((padding + x * char_w, y), char.data, font=font, fill=fg) #already UTF-8 encoded
            #draw.text((padding, y), line, font=font, fill=fg)
        y += char_h

    return img

async def send_key(key: str, modifier: str):
    global nethack_proc
    if nethack_proc is None:
        return "NetHack is not running. Use /nethack start."

    async with nethack_lock:
        try:
            if modifier == "CTRL":
                nethack_proc.sendcontrol(key)
            elif modifier == "ALT":
                nethack_proc.send("\x1b" + key)
            else:
                nethack_proc.send(key)

            await asyncio.sleep(0.2)
            output = nethack_proc.read_nonblocking(size=4096, timeout=5)
            nethack_stream.feed(output)
            return render_screen()
        except Exception as e:
            return f"Error sending key: {e}"

def is_admin(inter: disnake.ApplicationCommandInteraction):
    return any(role.id == ADMIN_ROLE_ID for role in inter.author.roles)

def is_correct_channel(inter: disnake.ApplicationCommandInteraction):
    return inter.channel_id == ALLOWED_CHANNEL_ID

async def send_output_to_channel(inter: disnake.ApplicationCommandInteraction, message):
    if isinstance(message, disnake.Embed):
        await inter.followup.send(embed=message)
    elif isinstance(message, Image.Image):
        with BytesIO() as img_buffer:
            message.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            file = disnake.File(fp=img_buffer, filename="nethack.png")
            await inter.followup.send(file=file)
    else:
        await inter.followup.send(message)

def setup_nethack_commands(bot: commands.InteractionBot, GIDS):
    @bot.slash_command(description="Control the shared NetHack game", guild_ids=GIDS)
    async def nethack(inter: disnake.ApplicationCommandInteraction):
        pass

    @nethack.sub_command(description="Start NetHack")
    async def start(inter: disnake.ApplicationCommandInteraction):
        if not is_correct_channel(inter):
            await inter.response.send_message("This command can only be used in the designated NetHack channel.", ephemeral=True)
            return
        if not is_admin(inter):
            await inter.response.send_message("You do not have permission to start NetHack.", ephemeral=True)
            return
        await inter.response.defer()
        msg = await start_nethack()
        await send_output_to_channel(inter, msg)

    @nethack.sub_command(description="Send a keystroke")
    async def key(
        inter: disnake.ApplicationCommandInteraction,
        key: str = commands.Param(description="send key or 'UP', 'DOWN', 'LEFT', 'RIGHT' 'ENTER' 'SPACE' 'ESC'"),
        modifier: str = commands.Param(choices=["none", "CTRL", "ALT"], default="none", description="Modifier key")
    ):
        if not is_correct_channel(inter):
            await inter.response.send_message("This command can only be used in the designated NetHack channel.", ephemeral=True)
            return
        
        if key == "UP":
            key = "\x1b[A"
        elif key == "DOWN":
            key = "\x1b[B"
        elif key == "LEFT":
            key = "\x1b[D"
        elif key == "RIGHT":
            key = "\x1b[C"
        elif key == "ENTER":
            key = "\r"
        elif key == "SPACE":
            key = " "
        elif key == "ESC":
            key = "\x1b"
        elif len(key) != 1 or not key.isprintable():
            await inter.response.send_message("Invalid key. Please enter a single printable character.", ephemeral=True)
            return  

        await inter.response.defer()
        msg = await send_key(key, modifier)
        await send_output_to_channel(inter, msg)

    @nethack.sub_command(description="Stop NetHack")
    async def stop(inter: disnake.ApplicationCommandInteraction):
        if not is_correct_channel(inter):
            await inter.response.send_message("This command can only be used in the designated NetHack channel.", ephemeral=True)
            return
        if not is_admin(inter):
            await inter.response.send_message("You do not have permission to stop NetHack.", ephemeral=True)
            return
        await inter.response.defer()
        await send_output_to_channel(inter, stop_nethack())

    @nethack.sub_command(description="Show current screen")
    async def status(inter: disnake.ApplicationCommandInteraction):
        if not is_correct_channel(inter):
            await inter.response.send_message("This command can only be used in the designated NetHack channel.", ephemeral=True)
            return
        await inter.response.defer()
        if nethack_proc is None:
            await inter.followup.send("NetHack is not running.")
        else:
            await send_output_to_channel(inter, render_screen())

