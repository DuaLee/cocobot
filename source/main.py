import asyncio
from asyncio.windows_events import NULL
import os

import discord
from discord import activity
from discord import message
from discord.client import Client
import validators
import youtube_dl

from discord.ext import commands

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ""


ytdl_format_options = {
    "format": "bestaudio/best",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",
}

ffmpeg_options = {"options": "-vn"}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=1.0):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get("title")
        self.creator = data.get("creator")
        self.uploader = data.get("uploader")
        self.is_live = data.get("is_live")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream)
        )

        if "entries" in data:
            # take first item from a playlist
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def ping(self, ctx):
        """Check status of bot."""
        alert = await ctx.send("🏓 **Pong!**")
        await alert.add_reaction("⚪")

        
    @commands.command()
    async def say(self, ctx, *, input):
        """Have the bot secretly say a message."""
        await ctx.message.delete()
        await ctx.send("{}".format(input))

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []

    def stepQueue(self):
        self.queue = self.queue[1:]

    @commands.command(aliases=['l'])
    async def lyrics(self, ctx):
        """Displays subtitles for Youtube videos."""
        
        #work-in-progress
        
    @commands.command(aliases=['q'])
    async def queue(self, ctx):
        """Displays tracks in queue."""
        if len(self.queue) > 0:
            async with ctx.typing():
                songs_in_q = "**{} track(s) in queue:**\n".format(
                    len(self.queue)
                )

                count = 1
                songs_in_q = songs_in_q + "```"
                for song in self.queue:
                    songs_in_q += str(count) + " - " + song +"\n"
                    count = count + 1
            await ctx.send(songs_in_q + "```")
        else:
            message = await ctx.send("**0 tracks in queue**")

    @commands.command()
    async def skip(self, ctx):
        """Skips to next track in queue."""
        alert = await ctx.send("⏭️ **Skipped**")
        await alert.add_reaction("✅")

        ctx.voice_client.stop()
        # self.stepQueue()

    @commands.command(aliases=['c'])
    async def clear(self, ctx):
        """Clears queue."""
        self.queue = []
        alert = await ctx.send("🧹 The queue has been cleared.")
        await alert.add_reaction("✅")

    @commands.command(aliases=['j'])
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins your voice channel."""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()
        # await ctx.guild.change_voice_state(channel=channel, self_deaf=True)

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, input):
        """Adds a track from url or Youtube search to queue."""

        if len(self.queue) > 0:
            alert = await ctx.send("📚 **Queued ** `{}`".format(input))
            await alert.add_reaction("✅")
            self.queue.append(input)
            while self.queue[0] != input:
                await asyncio.sleep(0.5)

            # Just for good measure
            ctx.voice_client.stop()
        else:
            self.queue.append(input)

        async with ctx.typing():
            if not validators.url(input):
                print("'", input, "'", "was not a url, attempting search...")
                input = ytdl.extract_info(f"ytsearch:{input}", download=False)[
                    "entries"
                ][0]["webpage_url"]
                print("Found:", input, "\n")

            player = await YTDLSource.from_url(input, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(
                player,
                after=(
                    lambda e: print("Player error: %s" % e) if e else self.stepQueue()
                ),
            )

        if player.is_live:
            alert = await ctx.send("🔴 **Now streaming** `{}` by **`{}`**".format(player.title, player.uploader))
        else:
            alert = await ctx.send("▶️ **Now playing** `{}` by **`{}`**".format(player.title, player.creator))
        
        await alert.add_reaction("✅")


    @commands.command(aliases=['v'])
    async def volume(self, ctx, volume: int):
        """Changes music volume."""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        alert = await ctx.send("🎚️ **Volume set to** {}%".format(volume))
        await alert.add_reaction("✅")

    @commands.command(aliases=['leave'])
    async def stop(self, ctx):
        """Leaves voice channel and clears the queue."""

        if ctx.voice_client.is_playing():
            alert = await ctx.send("⏹️ **Stopped.**")
            await alert.add_reaction("❤️")
            await ctx.voice_client.disconnect()
            self.queue = []
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")


bot = commands.Bot(
    command_prefix=commands.when_mentioned_or( "!", "-" ),
    # help_command=None,
    description="CocoBot Commands:",
)


@bot.event
async def on_ready():
    print("Logged in as {0} ({0.id})".format(bot.user))
    print("------")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='you... | !help'), status=discord.Status.dnd)


bot.add_cog(Music(bot))
bot.add_cog(Fun(bot))

# get bot token from local env file
from decouple import config

BOT_TOKEN = config('BOT_TOKEN')
bot.run(BOT_TOKEN)