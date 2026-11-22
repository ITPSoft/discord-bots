import logging
import os
import socket
import sys
from typing import Any

from discord_handler import DiscordHandler
from disnake import ApplicationCommandInteraction
from disnake.ext.commands import InteractionBot, Context, CommandError, UserInputError

fs = "%(asctime)s:{}:%(name)s:%(levelname)s:%(message).200s".format(socket.gethostname())  # max 200 chars of message

class DiscordFormatter(logging.Formatter):
    def __init__(self, fmt: str | None = None, max_size: int = 1_900):
        super().__init__(fmt)
        self.max_size = max_size

    def format(self, record: logging.LogRecord) -> str:
        formatted = super().format(record)

        if len(formatted) <= self.max_size:
            return formatted

        exception_text = getattr(record, "exc_text", None)
        if exception_text:
            traceback_rows = exception_text.splitlines()
            available_size = self.max_size - len("\n...\n")

            head_size = available_size // 2
            tail_size = available_size - head_size

            while traceback_rows and sum(
                len(row) + 1 for row in traceback_rows[: len(traceback_rows)]
            ) > available_size:
                traceback_rows = traceback_rows[1:-1]

            traceback_text = "\n".join(traceback_rows)
            if len(traceback_text) > available_size:
                traceback_text = (
                    traceback_text[:head_size].rstrip()
                    + "\n...\n"
                    + traceback_text[-tail_size:].lstrip()
                )

            formatted = formatted.replace(exception_text, traceback_text)

        return formatted[: self.max_size]

def configure_logging(client: InteractionBot, level=logging.INFO):
    try:
        webhook = os.getenv("DISCORD_MONITORING_WEBHOOK", "")
        if not webhook:
            handler = None
        # by default excluding developers machines so they don't spam the discord
        elif socket.gethostname() in ["WA-7WFYKN3"]:
            handler = None
        else:
            handler = DiscordHandler(webhook, "Discord bots logging", emit_as_code_block=True, max_size=1_900)
            handler.setLevel(logging.ERROR)
            # discord handler must have the message less than 2000 characters, so I'm trimming this here
            # formatter copied from basicConfig
            handler.setFormatter(DiscordFormatter(fs, max_size=1_900))
    except ImportError:
        handler = None

    stream_handler = logging.StreamHandler(sys.stdout)
    handlers = [stream_handler]

    if handler is not None:
        handlers.append(handler)

    logging.basicConfig(
        level=level,
        format=fs,
        handlers=handlers,
    )

    sys.excepthook = exception_hook

    if handler is None:
        logger.info("Logging configured without discord")
    else:
        logger.info("Logging configured including discord")

    # we need to set all error kinds
    # https://docs.disnake.dev/en/latest/ext/commands/api/bots.html#disnake.ext.commands.Bot

    @client.event
    async def on_error(event_method: str, *args: Any, **kwargs: Any):
        logger.exception(f"Uncaught exception in event {event_method=}, {args=}, {kwargs=}")

    @client.event
    async def on_command_error(context: Context, error: CommandError):
        logger.exception(
            f"Uncaught exception in command in channel {context.channel.name=}, {context=}", exc_info=error
        )

    @client.event
    async def on_gateway_error(event: str, data: Any, shard_id: int | None, exc: Exception):
        logger.exception(f"Uncaught exception in event {event}", exc_info=exc)

    @client.event
    async def on_message_command_error(ctx: ApplicationCommandInteraction, exception: CommandError):
        logger.exception(
            f"Uncaught exception in on_message_command_error in channel {ctx.channel.name=}, {ctx}", exc_info=exception
        )

    @client.event
    async def on_slash_command_error(ctx: ApplicationCommandInteraction, error: CommandError):
        if isinstance(error, UserInputError):  # not handling validation errors
            await ctx.response.send_message(f"❌ Invalid input: {error}", ephemeral=True)
            return
        logger.exception(
            f"Uncaught exception in on_slash_command_error in channel {ctx.channel.name=}, {ctx=}", exc_info=error
        )

    @client.event
    async def on_user_command_error(ctx: ApplicationCommandInteraction, error: CommandError):
        logger.exception(
            f"Uncaught exception in on_user_command_error in channel {ctx.channel.name=}, {ctx=}", exc_info=error
        )


logger = logging.getLogger(__name__)


def exception_hook(exc_type, exc_value, exc_traceback):
    # propagating all exceptions into discord webhook
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
