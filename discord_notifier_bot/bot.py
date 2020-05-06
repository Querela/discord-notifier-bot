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


class SendSingleMessageClient(AbstractSingleActionClient):
    def __init__(self, channel_id, message, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_id = channel_id
        self.message = message

    async def do_work(self):
        channel = self.get_channel(self.channel_id)
        LOGGER.info(f"Channel: {channel} {type(channel)} {repr(channel)}")
        if channel is None:
            raise Exception(
                f"Channel with id {self.channel_id} does not seem to exist!"
            )

        result = await channel.send(self.message)
        LOGGER.debug(f"MSG result: {result} {type(result)} {repr(result)}")


class SendSingleFileMessageClient(AbstractSingleActionClient):
    def __init__(self, channel_id, file2send, *args, message=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_id = channel_id
        self.file2send = file2send
        if message is None:
            message = ""
        self.message = message

    async def do_work(self):
        channel = self.get_channel(self.channel_id)
        LOGGER.info(f"Channel: {channel} {type(channel)} {repr(channel)}")
        if channel is None:
            raise Exception(
                f"Channel with id {self.channel_id} does not seem to exist!"
            )

        # attach file to message
        result = await channel.send(self.message, file=self.file2send)
        LOGGER.debug(f"MSG result: {result} {type(result)} {repr(result)}")


# ---------------------------------------------------------------------------


def send_message(token, channel_id, message):
    client = SendSingleMessageClient(channel_id, message)
    client.run(token)


def send_file(token, channel_id, message, filename):
    name = os.path.basename(filename)  # only show last part of path
    # wrap file for discord
    dfile = discord.File(filename, filename=name)

    client = SendSingleFileMessageClient(channel_id, dfile, message=message)
    client.run(token)


# ---------------------------------------------------------------------------
