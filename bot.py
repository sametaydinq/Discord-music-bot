import yt_dlp
from nextcord.ext import commands
import nextcord
import os
import asyncio  # yt_dlp
from nextcord.ext.commands import Context
from xd import SAMET_TOKEN, TESTBOT_TOKEN

intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix=commands.when_mentioned_or(
    '++'), intents=intents)


bot.load_extension("musiccog")

bot.run(SAMET_TOKEN)
