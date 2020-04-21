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

A simple python `Discord <https://discordapp.com/>`_ bot to send messages to discord channel via command line.

It allows markdown formatted messages and attaching files.

It registers the following commands:

* ``dbot-run`` - main CLI entry-point
* ``dbot-message`` - (short-hand) to send a message, or even pipe `-` message contents
* ``dbot-file`` - (short-hand) to send a file with an message

Requirements
------------

* `discord.py <https://github.com/Rapptz/discord.py>`_

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

Bot Creation etc.
-----------------

See information provided by:

* `<https://github.com/Chikachi/DiscordIntegration/wiki/How-to-get-a-token-and-channel-ID-for-Discord>`_
* `<https://discordapp.com/developers/applications/>`_

Credits
-------

* `easy-telegram-cli <https://github.com/JaBorst/easy-telegram-cli>`_

Copyright and License Information
---------------------------------

Copyright (c) 2020 Erik Körner.  All rights reserved.

See the file "LICENSE" for information on the history of this software, terms &
conditions for usage, and a DISCLAIMER OF ALL WARRANTIES.

All trademarks referenced herein are property of their respective holders.
