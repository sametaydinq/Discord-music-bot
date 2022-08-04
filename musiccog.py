import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Context
import yt_dlp
import asyncio
import os

intents = nextcord.Intents.all()
intents.members = True

filestodelete = []
queuelist = []

bot = commands.Bot(command_prefix=commands.when_mentioned_or(
    '--'), intents=intents, help_command=None)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["connect"])
    async def join(self, ctx: Context):
        await ctx.author.voice.channel.connect()
        await ctx.message.add_reaction("✅")

    @commands.command(aliases=["disconnect"])
    async def leave(self, ctx: Context):
        global queuelist
        await ctx.voice_client.disconnect()
        queuelist = []
        await ctx.message.add_reaction("✅")

    @commands.command(aliases=["p"])
    async def play(self, ctx: Context, *, searchword):
        await ctx.message.add_reaction("<a:loading:1004527255575334972>")
        ydl_opts = {}
        voice = ctx.voice_client

        # Get the Title
        if searchword[0:4] == "http" or searchword[0:3] == "www":
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(searchword, download=False)
                title = info["title"]
                url = searchword

        if searchword[0:4] != "http" and searchword[0:3] != "www":
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{searchword}", download=False)[
                    "entries"][0]
                title = info["title"]
                url = info["webpage_url"]

        title = title.replace(':', '')

        ydl_opts = {
            'format': 'bestaudio/best',
            "outtmpl": f"{title}.mp3",
            "postprocessors":
            [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3",
                "preferredquality": "96"}],
        }

        # Downloads the Audio File with the Title, it is run in a different thread so that the bot can communicate to the discord server while downloading
        def download(url):
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, download, url)

        # Playing and Queueing Audio
        if voice.is_playing():
            queuelist.append(title)
            await ctx.message.clear_reactions()
            await ctx.message.add_reaction("✅")
            await ctx.send(f"Added to Queue: ** {title} **")
        else:
            voice.play(nextcord.FFmpegPCMAudio(
                f"{title}.mp3"), after=lambda e: check_queue())
            await ctx.message.clear_reactions()
            await ctx.message.add_reaction("✅")
            await ctx.send(f"Playing ** {title} ** :musical_note:")
            filestodelete.append(title)

        # the after function that gets called after the first song ends, then it checks whether a song is in the queuelist
        # if there is a song in the queuelist, it plays that song
        # if there is no song in the queuelist, it deletes all the files in filestodelete
        def check_queue():
            try:
                if queuelist[0] != None:
                    voice.play(nextcord.FFmpegPCMAudio(
                        f"{queuelist[0]}.mp3"), after=lambda e: check_queue())
                    fut = asyncio.run_coroutine_threadsafe(bot.loop)
                    fut.result()
                    filestodelete.append(queuelist[0])
                    queuelist.pop(0)
            except IndexError:
                for file in filestodelete:
                    os.remove(f"{file}.mp3")
                filestodelete.clear()

    #Stop, Resume and Pause

    @commands.command(aliases=["stop"])
    async def pause(self, ctx: Context):
        voice = ctx.voice_client
        if voice.is_playing() == True:
            voice.pause()
            await ctx.message.add_reaction("✅")
        else:
            await ctx.send("Bot is not playing Audio!")

    @commands.command()
    async def resume(self, ctx: Context):
        voice = ctx.voice_client
        if voice.is_playing() == True:
            await ctx.send("Bot is playing Audio!")
        else:
            voice.resume()
            await ctx.message.add_reaction("✅")

    # function that displays the current queue
    @commands.command(aliases=["viewqueue"])
    async def queue(self, ctx: Context):
        await ctx.message.add_reaction("✅")
        await ctx.send(f"Queue:  ** {str(queuelist)} ** ")

    @commands.command()
    async def clearqueue(self, ctx: Context):
        global queuelist
        queuelist = []
        await ctx.message.add_reaction("✅")

def setup(bot):
    bot.add_cog(Music(bot))