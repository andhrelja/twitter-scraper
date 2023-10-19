from .__version__ import __version__
from .settings import BASELINE_USER_IDS
import os

if not os.path.exists(BASELINE_USER_IDS):
    raise FileNotFoundError("Baseline user IDs not found at {}".format(BASELINE_USER_IDS))

import discord

intents = discord.Intents.default()
intents.message_content = True
DISCORD_CLIENT = discord.Client(intents=intents)
