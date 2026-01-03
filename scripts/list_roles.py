"""
Script for testing which emojis fail to send.
"""

import asyncio

from disnake import Client

from common.constants import Server
from šimek.main import TOKEN


async def main():
    client = Client()  # reusing client from Šimek was causing errors
    await client.login(TOKEN)
    # hack to make client connect without stealing the even loop
    connect_task = asyncio.create_task(client.connect())  # not awaiting here is the secret sauce
    await client.wait_until_ready()
    guild = await client.fetch_guild(Server.KOUZELNICI)
    role = await guild.fetch_role(1453909720715755682)

    # Cleanly shut down
    await client.close()
    await connect_task  # or handle CancelledError if you prefer


if __name__ == "__main__":
    asyncio.run(main())
