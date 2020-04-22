import datetime
import logging
import os
from collections import defaultdict

import discord
from discord.ext import commands, tasks

from discord_notifier_bot.sysinfo import get_info_message
from discord_notifier_bot.sysinfo import get_local_machine_name
from discord_notifier_bot.sysinfo import (
    get_cpu_info,
    get_disk_info,
    get_gpu_info,
)
from discord_notifier_bot.sysinfo import make_observable_limits

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


def make_sysinfo_embed():
    embed = discord.Embed(title=f"System Status of `{get_local_machine_name()}`")
    # embed.set_thumbnail(url="")  # TODO: add "private" logo (maybe as an config option ...)
    embed.add_field(
        name="System information", value=get_cpu_info() or "N/A", inline=False
    )
    embed.add_field(
        name="Disk information", value=get_disk_info() or "N/A", inline=False
    )
    embed.add_field(name="GPU information", value=get_gpu_info() or "N/A", inline=False)
    embed.set_footer(text=f"Date: {datetime.datetime.now()}")

    return embed


# ---------------------------------------------------------------------------


class SystemResourceObserverCog(commands.Cog):
    def __init__(self, bot, channel_id):
        self.bot = bot
        self.channel_id = channel_id

        self.limits = dict()
        self.notified = defaultdict(int)
        self.stats = defaultdict(int)
        self.num_good_needed = 3

        self.init_limit()

    def init_limit(self):
        # TODO: pack them in an optional file (like Flask configs) and try to load else nothing.
        self.limits.update(make_observable_limits())

        for name in self.limits.keys():
            self.notified[name] = 0

    def reset_notifications(self):
        for name in self.notified.keys():
            self.notified[name] = 0

    @tasks.loop(minutes=5.0)
    async def observe_system(self):
        LOGGER.debug("Running observe system task loop ...")

        for name, limit in self.limits.items():
            LOGGER.debug(f"Running check: {limit.name}")
            try:
                cur_value = limit.fn_retrieve()
                ok = limit.fn_check(cur_value, limit.threshold)
                if not ok:
                    self.stats["num_limits_reached"] += 1
                    if not self.notified[name]:
                        self.stats["num_limits_notified"] += 1
                        await self.send(
                            limit.message.format(
                                cur_value=cur_value, threshold=limit.threshold
                            )
                        )
                        self.notified[name] = self.num_good_needed
                else:
                    # decrease counters
                    if self.notified[name] > 0:
                        self.notified[name] = max(0, self.notified[name] - 1)
                        if self.notified[name] == 0:
                            await self.send(f"*{limit.name} has recovered*")
            except Exception as ex:
                LOGGER.debug(f"Failed to evaulate limit: {ex}")

        self.stats["num_checks"] += 1

    @observe_system.before_loop
    async def before_observe_start(self):
        LOGGER.debug("Wait for observer bot to be ready ...")
        await self.bot.wait_until_ready()

    async def send(self, message):
        # TODO: send to default channel?
        channel = self.bot.get_channel(self.channel_id)
        await channel.send(message)

    def cog_unload(self):
        self.observe_system.cancel()  # pylint: disable=no-member

    @commands.command(name="observer-start")
    async def start(self, ctx):
        """Starts the background system observer loop."""
        # NOTE: check for is_running() only added in version 1.4.0
        if self.observe_system.get_task() is None:  # pylint: disable=no-member
            await ctx.send("Observer started")
            self.observe_system.start()  # pylint: disable=no-member
        else:
            self.observe_system.restart()  # pylint: disable=no-member
            await ctx.send("Observer restarted")

    @commands.command(name="observer-stop")
    async def stop(self, ctx):
        """Stops the background system observer."""
        self.observe_system.cancel()  # pylint: disable=no-member
        self.reset_notifications()
        await ctx.send("Observer stopped")

    @commands.command(name="observer-status")
    async def status(self, ctx):
        """Displays statistics about notifications etc."""
        await ctx.send(f"{dict(self.stats)}")
        await ctx.send(r"¯\_(ツ)_/¯")  # TODO: make fancy ...


def run_observer(token, channel_id):
    observer_bot = commands.Bot(command_prefix=".")

    @observer_bot.event
    async def on_ready():  # pylint: disable=unused-variable
        LOGGER.info(f"Logged on as {observer_bot.user}")
        LOGGER.debug(f"name: {observer_bot.user.name}, id: {observer_bot.user.id}")

        if channel_id is not None:
            channel = observer_bot.get_channel(channel_id)
            LOGGER.info(f"Channel: {channel} {type(channel)} {repr(channel)}")
            await channel.send(
                f"Running observer bot on `{get_local_machine_name()}`...\n"
                f"Type `{observer_bot.command_prefix}help` to display available commands."
            )

    @observer_bot.event
    async def on_disconnect():  # pylint: disable=unused-variable
        LOGGER.warning("Bot disconnected!")

    @observer_bot.command()
    async def ping(ctx):  # pylint: disable=unused-variable
        """Standard Ping-Pong latency/is-alive test."""
        await ctx.send(f"Pong (latency: {observer_bot.latency * 1000:.1f} ms)")

    @observer_bot.command()
    async def info(ctx):  # pylint: disable=unused-variable
        """Query local system information and send it back."""
        # message = get_info_message()
        # await ctx.send(message)
        embed = make_sysinfo_embed()
        await ctx.send(embed=embed)

    observer_bot.add_cog(SystemResourceObserverCog(observer_bot, channel_id))

    # @commands.command()
    # async def test(ctx): pass
    # observer_bot.add_command(test)

    LOGGER.info("Start observer bot ...")
    observer_bot.run(token)
    LOGGER.info("Quit observer bot.")


# ---------------------------------------------------------------------------
