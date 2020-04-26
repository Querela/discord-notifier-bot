import argparse
import configparser
import logging
import os
import pathlib
import sys

from discord_notifier_bot.bot import send_message
from discord_notifier_bot.bot import send_file as bot_send_file


LOGGER = logging.getLogger(__name__)


# ---------------------------------------------------------------------------


CONFIG_SECTION_NAME = "discord-bot"

CONFIG_PATHS = [
    pathlib.Path.home() / ".dbot.conf",
    pathlib.Path.home() / "dbot.conf",
    pathlib.Path(".") / ".dbot.conf",
    pathlib.Path(".") / "dbot.conf",
    pathlib.Path("/etc/dbot.conf"),
]


def find_config_file():
    for filename in CONFIG_PATHS:
        if filename.exists():
            LOGGER.info(f"Found config file: {filename}")
            return filename

    LOGGER.error("Found no configuration file in search path!")
    return None


def load_config_file(filename):
    config = configparser.ConfigParser()

    LOGGER.debug(f"Try loading configurations from {filename}")

    try:
        config.read(filename)

        if CONFIG_SECTION_NAME not in config:
            LOGGER.error(f"Missing configuration section header: {CONFIG_SECTION_NAME}")
            return None

        configs = config[CONFIG_SECTION_NAME]

        return {
            "token": configs["token"].strip('"'),
            "channel": int(configs["channel"]),
        }
    except KeyError as ex:
        LOGGER.error(f"Missing configuration key! >>{ex.args[0]}<<")
    except:  # pylint: disable=bare-except
        LOGGER.exception("Loading configuration failed!")
    return None


def load_config(filename=None, **kwargs):
    configs = None

    if filename and os.path.isfile(filename):
        configs = load_config_file(filename)
        if configs is None:
            LOGGER.error("Loading given config file failed! Trying default ones ...")

    if configs is None:
        filename = find_config_file()
        if filename is not None:
            configs = load_config_file(filename)

    if configs is None:
        if "token" not in kwargs or "channel" not in kwargs:
            raise Exception("No configuration file found!")

    configs = {**configs, **kwargs}

    return configs


# ---------------------------------------------------------------------------


def send_file(bot_token, channel_id, message, filename):
    if not os.path.isfile(filename):
        raise Exception(f"filename '{filename}' is not a file!")

    LOGGER.info(f"Send file: {filename} ...")
    bot_send_file(bot_token, channel_id, message, filename)


# ---------------------------------------------------------------------------


def parse_args(args=None):
    parser = argparse.ArgumentParser()

    actions = ("message", "file")

    parser.add_argument("action", choices=actions, help="Bot action")
    parser.add_argument("message", help="Message to send")
    parser.add_argument(
        "--type",
        type=str,
        nargs="?",
        const="",
        default=None,
        help="Markdown type for text messages, or default if as flag",
    )
    parser.add_argument(
        "-f",
        "--file",
        required=False,
        type=str,
        default=None,
        help="Optional file to attach to message",
    )
    parser.add_argument("-c", "--config", type=str, default=None, help="Config file")
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug logging"
    )

    args = parser.parse_args(args)
    return args


def setup_logging(debug=False):
    if debug:
        # logging.basicConfig(format="* %(message)s", level=logging.INFO)
        logging.basicConfig(
            format="[%(levelname).1s] {%(name)s} %(message)s", level=logging.DEBUG
        )
        logging.getLogger("websockets.protocol").setLevel(logging.WARNING)
        logging.getLogger("websockets.client").setLevel(logging.WARNING)
        logging.getLogger("discord.client").setLevel(logging.WARNING)


# ---------------------------------------------------------------------------


def main(args=None):
    args = parse_args(args)

    setup_logging(args.debug)

    configs = load_config(filename=args.config)
    LOGGER.debug(f"Run bot with configs: {configs}")

    if args.message == "-":
        LOGGER.debug("Read message from STDIN ...")
        message = sys.stdin.read()
        LOGGER.debug(f"Read {len(message)} characters.")
    else:
        message = args.message

    if args.type is not None:
        LOGGER.info(f"Wrap message in markdown, type={args.type}")
        message = f"```{args.type}\n{message}\n```"

    if args.action == "message":
        LOGGER.info(f"Send message: {message} ...")
        send_message(configs["token"], configs["channel"], message)
    elif args.action == "file":
        send_file(configs["token"], configs["channel"], message, args.file)

    LOGGER.info("Done.")


# ---------------------------------------------------------------------------


def main_message():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("message")
        parser.add_argument(
            "-c", "--config", type=str, default=None, help="Config file"
        )
        parser.add_argument(
            "--type",
            type=str,
            nargs="?",
            const="",
            default=None,
            help="Markdown type, or default if without value",
        )
        args = parser.parse_args()

        configs = load_config(filename=args.config)
        LOGGER.debug(f"Run bot with configs: {configs}")

        if args.message == "-":
            message = sys.stdin.read()
        else:
            message = args.message

        if args.type is not None:
            LOGGER.info(f"Wrap message in markdown, type={args.type}")
            message = f"```{args.type}\n{message}\n```"

        LOGGER.info(f"Send message: {message} ...")
        send_message(configs["token"], configs["channel"], message)
    except:  # pylint: disable=bare-except
        sys.exit(1)


def main_file():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("file")
        parser.add_argument("message")
        parser.add_argument(
            "-c", "--config", type=str, default=None, help="Config file"
        )
        args = parser.parse_args()

        configs = load_config(filename=args.config)
        LOGGER.debug(f"Run bot with configs: {configs}")

        send_file(configs["token"], configs["channel"], args.message, args.file)
    except:  # pylint: disable=bare-except
        sys.exit(1)


# ---------------------------------------------------------------------------
