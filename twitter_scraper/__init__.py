from .settings import BASELINE_USER_IDS
import os

if not os.path.exists(BASELINE_USER_IDS):
    raise LookupError("Baseline user IDs was not found")

import discord

intents = discord.Intents.default()
intents.message_content = True
DISCORD_CLIENT = discord.Client(intents=intents)
