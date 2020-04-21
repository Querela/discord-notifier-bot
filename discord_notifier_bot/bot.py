import logging
import os
import discord

LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------------


class AbstractSingleActionClient(discord.Client):
    async def do_work(self):
        raise NotImplementedError()

    async def on_ready(self):
        LOGGER.info(f"Logged on as {self.user}")
        LOGGER.debug(f"name: {self.user.name}, id: {self.user.id}")

        await self.do_work()

        await self.close()


# ---------------------------------------------------------------------------


def send_message(token, channel_id, message):
    class SendMessageClient(AbstractSingleActionClient):
        async def do_work(self):
            channel = self.get_channel(channel_id)
            LOGGER.info(f"Channel: {channel} {type(channel)} {repr(channel)}")

            result = await channel.send(message)
            LOGGER.debug(f"MSG result: {result} {type(result)} {repr(result)}")

    client = SendMessageClient()
    client.run(token)


def send_file(token, channel_id, message, filename):
    name = os.path.basename(filename)  # only show last part of path
    # wrap file for discord
    dfile = discord.File(filename, filename=name)

    class SendFileMessageClient(AbstractSingleActionClient):
        async def do_work(self):
            channel = self.get_channel(channel_id)
            LOGGER.info(f"Channel: {channel} {type(channel)} {repr(channel)}")

            # attach file to message
            result = await channel.send(message, file=dfile)
            LOGGER.debug(f"MSG result: {result} {type(result)} {repr(result)}")

    client = SendFileMessageClient()
    client.run(token)


# ---------------------------------------------------------------------------
