"""
Script for listing users who wrote or reacted in channel recently.
"""

import asyncio

from disnake import Client
from tqdm.asyncio import tqdm

from common.constants import Server, Channel
from šimek.main import TOKEN


async def main():
    client = Client()  # reusing client from Šimek was causing errors
    await client.login(TOKEN)
    # hack to make client connect without stealing the even loop
    connect_task = asyncio.create_task(client.connect())  # not awaiting here is the secret sauce
    await client.wait_until_ready()
    await main_stuff(client)

    # Cleanly shut down
    await client.close()
    await connect_task  # or handle CancelledError if you prefer


async def main_stuff(client: Client):
    guild = await client.fetch_guild(Server.KOUZELNICI)
    # channel = await guild.fetch_channel(Channel.ECONPOLIPERO)
    channel = await guild.fetch_channel(Channel.MAGIC_THE_GATHERING_GENERAL)
    authors = set()
    all_reactors = set()
    message_limit = 500
    async for message in tqdm(channel.history(limit=message_limit), desc="Fetching messages", total=message_limit):
        if not message.author.bot:
            authors.add(message.author)
        for reaction in message.reactions:
            async for user in reaction.users():
                if not user.bot:
                    all_reactors.add(user)
    # print all authors and reactors nicely
    print("\n=== Authors ===")
    for author in sorted(authors, key=lambda u: u.name):
        print(f"  {author.name} (ID: {author.id})")

    print("\n=== Additional Reactors ===")
    for reactor in sorted(all_reactors, key=lambda u: u.name):
        if reactor in authors:
            continue
        print(f"  {reactor.name} (ID: {reactor.id})")

    print("\n=== Summary ===")
    print(f"Total authors: {len(authors)}")
    print(f"Total reactors: {len(all_reactors)}")
    print(f"Users who both authored and reacted: {len(authors & all_reactors)}")
    print(f"Users who authored or reacted: {len(authors | all_reactors)}")


if __name__ == "__main__":
    asyncio.run(main())
