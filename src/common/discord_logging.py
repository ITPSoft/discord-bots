import logging
import os
import socket
import sys

fs = "%(asctime)s - {} - %(name)s - %(levelname)s - %(message).100s".format(socket.gethostname())

# separated from utils, because this executes code on import
try:
    # discord handler should be used only if it's in production, not for development
    from discord_handler import DiscordHandler

    webhook = os.getenv("DISCORD_MONITORING_WEBHOOK", "")
    if not webhook:
        handler = None
    else:
        handler = DiscordHandler(webhook, "Discord bots logging", emit_as_code_block=True, max_size=1_900)
        handler.setLevel(logging.ERROR)
        # discord handler must have the message less than 2000 characters, so I'm trimming this here
        # formatter copied from basicConfig
        handler.setFormatter(logging.Formatter(fs))
except ImportError:
    handler = None


def configure_logging():
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    handlers = [stream_handler]

    if handler is not None:
        handlers.append(handler)

    logging.basicConfig(
        level=logging.INFO,
        format=fs,
        handlers=handlers,
    )



configure_logging()

logger = logging.getLogger(__name__)

def exception_hook(exc_type, exc_value, exc_traceback):
    # propagating all exceptions into discord webhook
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = exception_hook
