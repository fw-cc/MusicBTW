# Commented as moving to Lavalink backend
# from bot.utils.player import Player
# from bot.utils.sourcer import Sourcer

from discord.ext import commands

import logging


class Interface(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        # Commented for move to Lavalink backend
        # self.player = {Player(bot)}
        # self.sourcer = Sourcer(bot)
        self.logger = logging.getLogger("MusicBTW.Interface")

    def cog_unload(self):
        self.player.stop()

    @commands.command()
    async def play(self, ctx, link: str):
        """Add track(s) contained within `link` to the queue, must be a valid Youtube 
        video/playlist or Spotify Album, Playlist, or track."""
        pass

    @commands.command()
    async def skip(self, ctx):
        """Skips the current entry in the queue."""
        pass

    @commands.command()
    async def stop(self, ctx):
        """Stops playback and clears the queue."""
        self.player.stop()

    @commands.command()
    async def pause(self, ctx):
        """Pauses playback."""
        pass

    @commands.command()
    async def resume(self, ctx):
        """Resumes playback."""
        pass

    async def cog_check(self, ctx):
        if not ctx.guild:
            await ctx.reply("Music interface commands may only be used within Guild text channels.")
            return False
        return True


def setup(bot):
    bot.add_cog(Interface(bot))
