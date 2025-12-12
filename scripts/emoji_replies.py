"""
Script for testing which emojis fail to send.
"""

import asyncio

from disnake import Client

from common.constants import Channel
from šimek.main import TOKEN
from šimek.šimekdict import RANDOM_EMOJIS


async def main():
    client = Client()  # reusing client from Šimek was causing errors
    await client.login(TOKEN)
    # hack to make client connect without stealing the even loop
    connect_task = asyncio.create_task(client.connect())  # not awaiting here is the secret sauce
    await client.wait_until_ready()
    channel = await client.fetch_channel(Channel.BOT_TESTING.value)
    assert channel is not None
    m = await channel.fetch_message(1449172564298436699)
    assert m is not None
    await m.add_reaction("🙂")
    await m.add_reaction("😔")
    await m.add_reaction("💜")
    await m.add_reaction("🥳")
    await m.add_reaction("🐧")
    await m.add_reaction("😖")
    await m.add_reaction("👍")
    # await m.add_reaction(":+1:")  # this raises unknown emoji
    for emoji in RANDOM_EMOJIS:
        await m.add_reaction(emoji)

    # Cleanly shut down
    await client.close()
    await connect_task  # or handle CancelledError if you prefer


if __name__ == "__main__":
    asyncio.run(main())
