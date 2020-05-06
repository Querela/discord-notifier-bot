from setuptools import setup


def load_content(filename):
    with open(filename, "r", encoding="utf-8") as fp:
        return fp.read()


setup(
    name="discord-notifier-bot",
    version="0.3.3",
    license="MIT License",
    author="Erik Körner",
    author_email="koerner@informatik.uni-leipzig.de",
    description="A cli bot to send simple messages to a Discord channel.",
    long_description=load_content("README.rst"),
    long_description_content_type="text/x-rst",
    url="https://github.com/Querela/discord-notifier-bot",
    keywords=["discord", "bot", "notifier", "cli"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Utilities",
    ],
    packages=["discord_notifier_bot"],
    python_requires=">=3.6",
    install_requires=["discord.py"],
    entry_points={
        "console_scripts": [
            "dbot-run = discord_notifier_bot.cli:main",
            "dbot-message = discord_notifier_bot.cli:main_message",
            "dbot-file = discord_notifier_bot.cli:main_file",
        ]
    },
)
