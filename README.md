Discord-Notifier-Bot
====================

A simple python [Discord](https://discordapp.com/) bot to send messages to discord channel via command line.

It allows markdown formatted messages and attaching files.

It registers the following commands:

- `dbot-run` - main CLI entry-point
- `dbot-message` - (short-hand) to send a message, or even pipe `-` message contents
- `dbot-file` - (short-hand) to send a file with an message

## Requirements

- [discord.py](https://github.com/Rapptz/discord.py)

## Configuration

Configuration is done by placing a .dbot.conf file in one of the following directories:

   * `$HOME/.dbot.conf`
   * `$HOME/dbot.conf`
   * `./.dbot.conf`
   * `./dbot.conf`
   * `/etc/dbot.conf`

Alternatively a configuration file can be provided via `-c`/`--config` CLI options.

The configuration file should be a standard INI file. A template can be found in the `templates` folder. All configurations are placed under the `discord-bot` section.

## Bot Creation etc.

See information provided by:

- https://github.com/Chikachi/DiscordIntegration/wiki/How-to-get-a-token-and-channel-ID-for-Discord
- https://discordapp.com/developers/applications/

## Credits

* [easy-telegram-cli](https://github.com/JaBorst/easy-telegram-cli)