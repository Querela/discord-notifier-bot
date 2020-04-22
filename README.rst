====================
Discord-Notifier-Bot
====================

.. start-badges

.. image:: https://img.shields.io/github/release/Querela/discord-notifier-bot.svg
   :alt: GitHub release
   :target: https://github.com/Querela/discord-notifier-bot/releases/latest

.. image:: https://img.shields.io/github/languages/code-size/Querela/discord-notifier-bot.svg
   :alt: GitHub code size in bytes
   :target: https://github.com/Querela/discord-notifier-bot/archive/master.zip

.. image:: https://img.shields.io/github/license/Querela/discord-notifier-bot.svg
   :alt: MHTML License
   :target: https://github.com/Querela/discord-notifier-bot/blob/master/LICENSE

.. image:: https://img.shields.io/pypi/pyversions/discord-notifier-bot.svg
   :alt: PyPI supported Python versions
   :target: https://pypi.python.org/pypi/discord-notifier-bot

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :alt: Code style: black
   :target: https://github.com/psf/black

.. end-badges

A simple python `Discord <https://discordapp.com/>`_ bot to send messages to Discord channel via command line.

It allows markdown formatted messages and attaching files.

It registers the following commands:

* ``dbot-run`` - main CLI entry-point
* ``dbot-message`` - (short-hand) to send a message, or even pipe `-` message contents
* ``dbot-file`` - (short-hand) to send a file with an message
* ``dbot-info`` - (short-hand) to send a message with system information
  (*extra dependencies have to be installed!*)

Requirements
------------

* Python >= 3.6 (*see badges above*)
* `discord.py <https://github.com/Rapptz/discord.py>`_
* Extra:

  * ``cpu``: `psutil <https://github.com/giampaolo/psutil>`_
  * ``gpu``: `GPUtil <https://github.com/anderskm/gputil>`_

Installation
------------

.. code-block:: bash

   python3 -m pip install discord-notifier-bot

Optionally, install it locally with ``--user``.

For system info messages using ``dbot-info`` or ``dbot-run info [...]``, you have to install extra dependencies.
You can choose between cpu (cpu + disk information) and gpu (``nvidia-smi`` information):

.. code-block:: bash

   python3 -m pip install discord-notifier-bot[cpu,gpu]

Configuration
-------------

Configuration is done by placing a .dbot.conf file in one of the following directories:

   * ``$HOME/.dbot.conf``
   * ``$HOME/dbot.conf``
   * ``./.dbot.conf``
   * ``./dbot.conf``
   * ``/etc/dbot.conf``

Alternatively a configuration file can be provided via ``-c``/``--config`` CLI options.

The configuration file should be a standard INI file. A template can be found in the ``templates`` folder. All configurations are placed under the ``discord-bot`` section.

Example:

.. code-block:: ini

   [discord-bot]
   # the bot token (used for login)
   token = abc
   # the numeric id of a channel, can be found when activating the developer options in appearances
   channel = 123

Usage
-----

``dbot-message`` and ``dbot-file`` are simpler versions of ``dbot-run``.

Print help and available options:

.. code-block:: bash

   dbot-run -h

Sending messages:

.. code-block:: bash

   # send a simple message
   dbot-run message "Test message"
   # or shorter:
   dbot-message "Test **message**"

   # pipe output
   echo "Test" | dbot-emessage -
   
   # wrap it inside a code-block ```
   # optionally with a type
   cat `which dbot-message` | dbot-message - --type
   cat `which dbot-message` | dbot-message - --type python

Sending a file:

.. code-block:: bash

   dbot-file README.rst "Your message to desribe the attached file"
   # or with no visible message:
   dbot-file README.rst ""

   # optionally also like this:
   dbot-run file -f README.rst "Message ..."

You are always able to specify the configuration file like this:

.. code-block:: bash

   dbot-run -c /path/to/dbot.conf [...]
   dbot-{message,file} -c /path/to/dbot.conf [...]

**Only with** ``dbot-run``: To display debugging information (api calls, log messages etc.):

.. code-block:: bash

   dbot-run -v [...]

You may also run the bot with the python module notation. But it will only run the same entry-point like ``dbot-run``.

.. code-block:: bash

   python -m discord_notifier_bot [...]


Bot Creation etc.
-----------------

See information provided by:

* `Tutorial for setting up a bot <https://github.com/Chikachi/DiscordIntegration/wiki/How-to-get-a-token-and-channel-ID-for-Discord>`_
* `Discord developer application page <https://discordapp.com/developers/applications/>`_

Short description
~~~~~~~~~~~~~~~~~

**You have to own a Discord server! Or know someone with administrator/moderation(?) privileges.**

1. Visit and login to the `Discord developer page <https://discordapp.com/developers/applications/>`_.
#. Create a new application. The given name is also the visible name of the bot. (default, can be changed later?)
#. Create a bot (on the *Bot* page). You should disable the *Public Bot* option.

   * The bot login token (credentials) can be found on the *Bot* page.

#. Change to the *OAuth2* page and check

   * Scopes: *Bot*
   * Bot Permissions: *Send Messages*, *Attach Files* (in the *Text Permissions* column)

#. Copy the URL in the *Scopes* section and paste it in a new browser tab.

   * Now you can choose one (?) of your **own** Discord servers to add the bot to.
     *(For this you need server administration permissions, or be the owner..?)*

To get the channel id, send the following message on your server ``\#channelname``, or enable developer options.
You may want to visit the following pages for more information:

* `Discord Help <https://support.discordapp.com/hc/de/articles/206346498-Wie-finde-ich-meine-Server-ID->`_,
* `reddit post <https://www.reddit.com/r/discordapp/comments/50thqr/finding_channel_id/>`_.

Credits
-------

* `easy-telegram-cli <https://github.com/JaBorst/easy-telegram-cli>`_

Copyright and License Information
---------------------------------

Copyright (c) 2020 Erik Körner.  All rights reserved.

See the file "LICENSE" for information on the history of this software, terms &
conditions for usage, and a DISCLAIMER OF ALL WARRANTIES.

All trademarks referenced herein are property of their respective holders.
