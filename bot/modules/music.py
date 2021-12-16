from typing import Optional
from discord import voice_client
from discord.ext import commands

from bot.utils.spotify import Sourcer

import discord
import lavalink

import logging
import re


url_rx = re.compile(r'https?://(?:www\.)?.+')


class LavalinkVoiceClient(discord.VoiceClient):
    """Slightly modifed example from Lavalink.py
    https://github.com/Devoxin/Lavalink.py/blob/master/examples/music.py
    
    Manages interfacing between the bot and the Lavalink source.
    """
    def __init__(self, client, voice_channel):
        self.client = self.bot = client
        self.channel = voice_channel
        self._is_playing_bgm = False
        # In the case there's an existing lavalink link link link
        if hasattr(self.client, "lavalink"):
            self.lavalink = self.client.lavalink
        else:
            self.client.lavalink = lavalink.Client(client.user.id)
            self.client.lavalink.add_node(
                "lavalink",
                2333,
                "itsindockersoitsprobablyfine",
                "eu",
                "default-node"
            )
            self.lavalink = self.client.lavalink

    async def on_voice_server_update(self, data):
        # the data needs to be transformed before being handed down to
        # voice_update_handler
        lavalink_data = {
                't': 'VOICE_SERVER_UPDATE',
                'd': data
                }
        await self.lavalink.voice_update_handler(lavalink_data)

    async def on_voice_state_update(self, data):
        # the data needs to be transformed before being handed down to
        # voice_update_handler
        lavalink_data = {
                't': 'VOICE_STATE_UPDATE',
                'd': data
                }
        await self.lavalink.voice_update_handler(lavalink_data)
    
    @property
    def is_playing_bgm(self):
        return self._is_playing_bgm

    async def connect(self, *, timeout: float, reconnect: bool) -> None:
        """
        Connect the bot to the voice channel and create a player_manager
        if it doesn't exist yet.
        """
        # ensure there is a player_manager when creating a new voice_client
        player = self.lavalink.player_manager.create(guild_id=self.channel.guild.id)
        await self.channel.guild.change_voice_state(channel=self.channel)

    async def disconnect(self, *, force: bool) -> None:
        """
        Handles the disconnect.
        Cleans up running player and leaves the voice client.
        """
        player = self.lavalink.player_manager.get(self.channel.guild.id)

        # no need to disconnect if we are not connected
        if not force and not player.is_connected:
            return

        # None means disconnect
        await self.channel.guild.change_voice_state(channel=None)

        # update the channel_id of the player to None
        # this must be done because the on_voice_state_update that
        # would set channel_id to None doesn't get dispatched after the 
        # disconnect
        player.channel_id = None
        self.cleanup()


class Interface(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.logger = logging.getLogger("MusicBTW.Interface")
        self.logger.debug("test")
        self.bot = bot
        self.sourcer = None
        try:
            if not hasattr(bot, 'lavalink'):  # This ensures the client isn't overwritten during cog reloads.
                self.lavalink = lavalink.Client(bot.user.id)
                self.logger.info("Attempting to connect to Lavalink, may fail on first attempt in docker-compose.")
                self.lavalink.add_node('lavalink', 2333, 'itsindockersoitsprobablyfine', 'eu', 'default-node')
                self.logger.info("Added Lavalink node, will query until success.")
            else:
                self.lavalink: lavalink.Client = bot.lavalink
                self.logger.debug("Interface reloaded, bot has lavalink attribute already")
            bot.lavalink = self.lavalink
        except Exception as e:
            self.logger.exception(e, exc_info=(type(e), e, e.__traceback__))
        # Probably worth adding some kind of decorator event hook registration interface
        # to lavalink.py at some point...
        lavalink.add_event_hook(self.on_queue_end, event=lavalink.events.QueueEndEvent)
        lavalink.add_event_hook(self.on_node_connect, event=lavalink.events.NodeConnectedEvent)
        lavalink.add_event_hook(self.on_node_disconnect, event=lavalink.events.NodeDisconnectedEvent)
        lavalink.add_event_hook(self.on_track_stuck, event=lavalink.events.TrackStuckEvent)
        lavalink.add_event_hook(self.on_track_error, event=lavalink.events.TrackExceptionEvent)
        lavalink.add_event_hook(self.on_node_change, event=lavalink.events.NodeChangedEvent)

    async def on_node_connect(self, event):
        if self.sourcer is None:
            self.sourcer = Sourcer()
        self.logger.info("Connected to {0.name} at {0.host}:{0.port}".format(event.node))
    
    async def on_node_disconnect(self, event):
        self.logger.info("Disconnected from {0.node.name} with code {0.code} and reason {0.reason}".format(event))
    
    async def on_node_change(self, event):
        self.logger.info("Node changed from {0.name} to {1.name}".format(event.old_node, event.new_node))
    
    async def on_track_stuck(self, player, track, threshold):
        self.logger.warn(f"Track {track.title} got stuck in playback, skipping")
        await player.skip()

    async def on_track_error(self, track, exception):
        self.logger.exception(f"Track {track.name} produced an exception in playback",
                              exc_info=(type(exception), exception, exception.__traceback__))

    async def on_queue_end(self, event):
        # Triggered on "QueueEndEvent" from lavalink.py
        # it indicates that there are no tracks left in the player's queue.
        # To save on resources, we can tell the bot to disconnect from the voice channel.
        self.logger.debug("QueueEndEvent triggered")
        guild_id = int(event.player.guild_id)
        guild = self.bot.get_guild(guild_id)
        try:
            if not guild.voice_client.is_playing_bgm:
                self.logger.debug("Disconnecting from event")
                await guild.voice_client.disconnect(force=True)
        except AttributeError:
            pass

    async def ensure_voice(self, ctx):
        """ This check ensures that the bot and command author are in the same voice channel. """
        player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        # Create returns a player if one exists, otherwise creates.
        # This line is important because it ensures that a player always exists for a guild.

        # Most people might consider this a waste of resources for guilds that aren't playing, but this is
        # the easiest and simplest way of ensuring players are created.

        # These are commands that require the bot to join a voice channel (i.e. initiating playback).
        # Commands such as volume/skip etc don't require the bot to be in a voice channel so don't need listing here.
        should_connect = ctx.command.name in ['play', 'bgm']

        if not ctx.author.voice or not ctx.author.voice.channel:
            # Our cog_command_error handler catches this and sends it to the voice channel.
            # Exceptions allow us to "short-circuit" command invocation via checks so the
            # execution state of the command goes no further.
            raise commands.CommandInvokeError('Join a voice channel first.')

        if not player.is_connected:
            if not should_connect:
                raise commands.CommandInvokeError('Not connected.')

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:  # Check user limit too?
                raise commands.CommandInvokeError('I need the `CONNECT` and `SPEAK` permissions.')

            player.store('channel', ctx.channel.id)
            await ctx.author.voice.channel.connect(cls=LavalinkVoiceClient)
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                raise commands.CommandInvokeError('You need to be in my voice channel.')

    def cog_unload(self):
        self.bot.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        """ Command before-invoke handler. """
        guild_check = ctx.guild is not None
        #  This is essentially the same as `@commands.guild_only()`
        #  except it saves us repeating ourselves (and also a few lines).

        if guild_check:
            await self.ensure_voice(ctx)
            #  Ensure that the bot and command author share a mutual voice channel.

        return guild_check

    async def _play(self, ctx, player: lavalink.BasePlayer, query: str):
        query = query.strip('<>')

        embed = discord.Embed(color=discord.Color.blurple())

        from_spotify = False
        res_type = None
        def track_load_handler(loc_results, spotify=False):
            track = loc_results['tracks'][0]
            if not spotify or res_type == "track":
                embed.title = 'Track Enqueued'
                embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
            # You can attach additional information to audiotracks through kwargs, however this involves
            # constructing the AudioTrack class yourself.
            track = lavalink.models.AudioTrack(track, ctx.author.id, recommended=True)
            player.add(requester=ctx.author.id, track=track)

        # Check if the user input might be a URL. If it isn't, we can Lavalink do a YouTube search for it instead.
        # SoundCloud searching is possible by prefixing "scsearch:" instead.
        newly_queued_tracks = 0
        if not url_rx.match(query):
            query = f'ytsearch:{query}'
            results = await player.node.get_tracks(query)
        elif "spotify" in query and self.sourcer is not None:
            # Use the extra special sourcer to get good equivalents
            # of spotify tracks on the youtube
            # results, res_type = await self.sourcer.get_tracks(query, player.node)
            # TODO: make this stop when the player is stopped!!!
            async for result, res_type in self.sourcer.get_tracks(query, player.node):
                if not result or not result['tracks']:
                    pass
                else:
                    track_load_handler(result, spotify=True)
                    newly_queued_tracks += 1
                    if newly_queued_tracks == 1 and not player.is_playing:
                        await player.play()
            from_spotify = True
        else:
            # Get the results for the query from Lavalink.
            results = await player.node.get_tracks(query)

        if not from_spotify:
            if not results or not results['tracks']:
                return await ctx.send('No results')
        
        if from_spotify:
            embed.title = "Kanker"  # f"{res_type.capitalize()} Enqueued"
            embed.description = f"{newly_queued_tracks} tracks added."

        else:
            # Kept here to protect from things being unhappy
            # Valid loadTypes are:
            #   TRACK_LOADED    - single video/direct URL)
            #   PLAYLIST_LOADED - direct URL to playlist)
            #   SEARCH_RESULT   - query prefixed with either ytsearch: or scsearch:.
            #   NO_MATCHES      - query yielded no results
            #   LOAD_FAILED     - most likely, the video encountered an exception during loading.
            if results['loadType'] == 'PLAYLIST_LOADED':
                tracks = results['tracks']

                for track in tracks:
                    # Add all of the tracks from the playlist to the queue.
                    player.add(requester=ctx.author.id, track=track)

                embed.title = 'Playlist Enqueued'
                embed.description = f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks' 
            else:
                track_load_handler(results)

        # We don't want to call .play() if the player is playing as that will effectively skip
        # the current track.
        if not player.is_playing:
            await player.play()

        return embed

    # @commands.group()
    # async def bgm(self, ctx: commands.Context):
    #     """Command group for BGM management"""
    #     if ctx.invoked_subcommand is None:
    #         pass

    async def _toggle_bgm(self, player, voice_client, force_on=False):
        if voice_client.is_playing_bgm:
            voice_client._is_playing_bgm = False
            await player.stop()
            player.set_repeat(False)
            player.set_shuffle(False)
        elif not voice_client.is_playing_bgm or force_on:
            # Stops the bot from running through the full on_queue_end method
            voice_client._is_playing_bgm = True
            await player.stop()
            player.set_repeat(True)
            player.set_shuffle(True)

    @commands.command()
    async def bgm(self, ctx: commands.Context, *, query: str):
        """Sets the player to queue and play background music until overwritten
        or told to stop.
        """
        player = self.lavalink.player_manager.get(ctx.guild.id)
        voice_client = ctx.guild.voice_client
        await self._toggle_bgm(player, voice_client, force_on=True)
        await ctx.send("BGM mode enabled (may be a buggy mess 🤪🤪🤪)")
        play_embed = await self._play(ctx, player, query)
        if not player.is_playing:
            await player.play()
    
    @commands.command(aliases=['p'])
    async def play(self, ctx, *, query: str):
        """Searches and plays a song from a given query."""
        # Get the player for this guild from cache.
        player = self.lavalink.player_manager.get(ctx.guild.id)
        # Remove leading and trailing <>. <> may be used to suppress embedding links in Discord.
        query = query.strip('<>')
        await ctx.send(embed=await self._play(ctx, player, query))

        # We don't want to call .play() if the player is playing as that will effectively skip
        # the current track.
        if not player.is_playing:
            await player.play()

    def sender_is_in_channel(self, ctx, player):
        return player.is_connected and ctx.author.voice.channel.id == int(player.channel_id)

    @commands.command(aliases=['dc'])
    async def disconnect(self, ctx):
        """ Disconnects the player from the voice channel and clears its queue. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            # We can't disconnect, if we're not connected.
            return await ctx.send('Not connected to any voice channel.')

        if not ctx.author.voice or self.sender_is_in_channel(ctx, player):
            # Abuse prevention. Users not in voice channels, or not in the same voice channel as the bot
            # may not disconnect the bot.
            return
        
        await self._dc(player)
        # Disconnect from the voice channel.
        await ctx.voice_client.disconnect(force=True)

    async def _dc(self, player):
        # Clear the queue to ensure old tracks don't start playing
        # when someone else queues something.
        player.queue.clear()
        # Stop the current track so Lavalink consumes less resources.
        await player.stop()

    @commands.command()
    async def skip(self, ctx):
        """Skips the current entry in the queue."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not self.sender_is_in_channel(ctx, player):
            return
        await player.skip()

    @commands.command()
    async def stop(self, ctx):
        """Stops playback and clears the queue."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not self.sender_is_in_channel(ctx, player):
            return
        await self._dc(player)
        # Disconnect from the voice channel.
        await ctx.voice_client.disconnect(force=True)
        await ctx.send('*⃣ | Disconnected.')

    @commands.command()
    async def pause(self, ctx):
        """Pauses playback."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not self.sender_is_in_channel(ctx, player):
            return
        if not player.paused:
            self.logger.debug("Pausing player")
            await player.set_pause(True)

    @commands.command()
    async def resume(self, ctx):
        """Resumes playback."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not self.sender_is_in_channel(ctx, player):
            self.logger.debug(self.sender_is_in_channel)
            return
        if player.paused:
            self.logger.debug("Resuming player")
            await player.set_pause(False)

    async def cog_check(self, ctx):
        if not ctx.guild:
            await ctx.reply("Music interface commands may only be used within Guild text channels.")
            return False
        return True


def setup(bot):
    bot.add_cog(Interface(bot))
