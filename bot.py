import yt_dlp
from nextcord.ext import commands
import nextcord
import os
import asyncio  # yt_dlp
from nextcord.ext.commands import Context


intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix=commands.when_mentioned_or(
    '++'), intents=intents)


bot.load_extension("musiccog")

bot.run("MTAwNDA3ODcxMzI3MDQ0MDEzMQ.GopAq1.w67e6cA9BtmWfInncoughloUpQxp9yS9x_UShQ")
