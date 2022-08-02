from nextcord.ext import commands
import nextcord, youtube_dl, os, asyncio
from nextcord.ext.commands import Context
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")


queuelist = []
filestodelete = []

intents = nextcord.Intents.all()

bot = commands.Bot(command_prefix=commands.when_mentioned_or(
    '++'), intents=intents) 

@bot.command()
@commands.has_role("DJ")
async def join(ctx : Context):
    await ctx.author.voice.channel.connect()

 
@bot.command()
@commands.has_role("DJ")
async def leave(ctx : Context, help = "leaves the Voice Channel"):
    await ctx.voice_client.disconnect()
 
@bot.command()
@commands.has_role("DJ")
async def play(ctx : Context, *, searchword):
    ydl_opts = {}
    voice = ctx.voice_client
 
    #Get the Title
    if searchword[0:4] == "http" or searchword[0:3] == "www":
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(searchword, download = False)
            title = info["title"]
            url = searchword
 
    if searchword[0:4] != "http" and searchword[0:3] != "www":
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{searchword}", download = False)["entries"][0]
            title = info["title"]
            url = info["webpage_url"]
 
    ydl_opts = {
        'format' : 'bestaudio/best',
        "outtmpl" : f"{title}.mp3",
        "postprocessors": 
        [{"key" : "FFmpegExtractAudio", "preferredcodec" : "mp3", "preferredquality" : "192"}],   
    }
 
    #Downloads the Audio File with the Title, it is run in a different thread so that the bot can communicate to the discord server while downloading
    def download(url):
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, download, url)
 
    #Playing and Queueing Audio
    if voice.is_playing():
        queuelist.append(title)
        await ctx.send(f"Added to Queue: ** {title} **")
    else:
        voice.play(nextcord.FFmpegPCMAudio(f"{title}.mp3"), after = lambda e : check_queue())
        await ctx.send(f"Playing ** {title} ** :musical_note:")
        filestodelete.append(title)
        await bot.change_presence(activity = nextcord.Activity(type = nextcord.ActivityType.listening, name = title))
 
    #the after function that gets called after the first song ends, then it checks whether a song is in the queuelist
    #if there is a song in the queuelist, it plays that song 
    #if there is no song in the queuelist, it deletes all the files in filestodelete
    def check_queue():
        try:
            if queuelist[0] != None:
                voice.play(nextcord.FFmpegPCMAudio(f"{queuelist[0]}.mp3"), after = lambda e : check_queue())
                coro = bot.change_presence(activity = nextcord.Activity(type = nextcord.ActivityType.listening, name = queuelist[0]))
                fut = asyncio.run_coroutine_threadsafe(coro,bot.loop)
                fut.result()
                filestodelete.append(queuelist[0])
                queuelist.pop(0)
        except IndexError:
            for file in filestodelete:
                os.remove(f"{file}.mp3")
            filestodelete.clear()     
 
#Stop, Resume and Pause
@bot.command()
@commands.has_role("DJ")
async def pause(ctx : Context):
    voice = ctx.voice_client
    if voice.is_playing() == True:
        voice.pause()
    else:
        await ctx.send("Bot is not playing Audio!")
 
@bot.command(aliases = ["skip"])
@commands.has_role("DJ")
async def stop(ctx : Context):
    voice = ctx.voice_client
    if voice.is_playing() == True:
        voice.stop()
    else:
        await ctx.send("Bot is not playing Audio!")
 
@bot.command()
@commands.has_role("DJ")
async def resume(ctx : Context):
    voice = ctx.voice_client
    if voice.is_playing() == True:
        await ctx.send("Bot is playing Audio!")
    else:
        voice.resume()
 
#function that displays the current queue
@bot.command()
async def viewqueue(ctx : Context):
    await ctx.send(f"Queue:  ** {str(queuelist)} ** ")
 

 
 
bot.run(TOKEN)