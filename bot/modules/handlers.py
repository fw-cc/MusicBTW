from nextcord.ext import commands

import logging
import traceback
import sys


class HandlersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("MusicBTW.Handlers")
        self.logger.debug("test")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        silent_exceptions = [
            commands.CommandOnCooldown,
            commands.PrivateMessageOnly,
            commands.CheckFailure
        ]
        if type(error) not in silent_exceptions:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            self.logger.exception("Exception occurred", exc_info=(type(error), error, error.__traceback__))
        elif type(error) == commands.PrivateMessageOnly:
            await ctx.message.delete()
            await ctx.send(f"{error}", delete_after=10)
        # else:
        #     await ctx.send(f"{error}")


def setup(bot):
    bot.add_cog(HandlersCog(bot))