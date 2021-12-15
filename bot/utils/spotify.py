import logging
import re
import spotipy

from spotipy.oauth2 import SpotifyClientCredentials


class Sourcer:
    def __init__(self, spotify_credentials=SpotifyClientCredentials):
        self.spotify_api = spotipy.Spotify(client_credentials_manager=spotify_credentials())
        self.logger = logging.getLogger("MusicBTW.Spotify")

    async def _get_equiv_track_from_yt(self, spotify_track, node):
        # Stopgap solution, will simply return a string containing the
        # title, album, and artist for Lavalink to query.
        self.logger.debug(spotify_track)
        artists = [artist["name"] for artist in spotify_track["artists"]]
        query = f"ytsearch:{spotify_track['name']} {spotify_track['album']['name']}"
        # query = f"ytsearch:{spotify_track['name']}"
        for artist in artists:
            query = f"{query} {artist}"
        self.logger.debug(query)
        return await node.get_tracks(query)

    def __spotify_tracks_getter(self, spotify_response, from_album=False, from_playlist=False):
        """Generates a list of tracks for Spotify API responses to albums and playlists"""
        tracks_obj = spotify_response["tracks"]
        tracks_data_list = []
        tracks_data_list.extend(tracks_obj["items"])
        while tracks_obj['next'] is not None:
            # Since the Spotify API doesn't like us getting too much in one response we'll have to
            # batch get things ;-;        
            tracks_obj = self.spotify_api.next(tracks_obj)
            tracks_data_list.extend(tracks_obj["items"])
        
        if from_playlist:
            tracks_data_list = [track["track"] for track in tracks_data_list]
        elif from_album:
            for track in tracks_data_list:
                try:
                    _ = track["album"]
                except KeyError:
                    track["album"] = {"name": spotify_response["name"]}
        return tracks_data_list

    async def get_tracks(self, source: str, node):
        SPOTIFY_PATTERN = r"^(?P<main_url>(https?:\/\/open.)?spotify.com\/(?P<type>\w{4,20})\/.*)\?.*"
        # YOUTUBE_PATTERN = r"^https?://.*(youtube\.com/(playlist\?list|watch)=|youtu\.be/)(.{34}|.{11})(\?t=(?P<time_offset>\d+))?"
        if regex_match := re.search(SPOTIFY_PATTERN, source):
            self.logger.debug("Matched Spotify URL")
            try:
                cleaned_url = regex_match.group("main_url")
                url_type = regex_match.group("type")
            except IndexError as e:
                self.logger.warning("Failed to match cleaned URL or URL type")
                self.logger.debug(e)
                return
            ### Handle Spotify
            initial_source = "spotify"
            sp_track_list = None
            try:
                if url_type == "album":
                    sp_track_list = self.__spotify_tracks_getter(self.spotify_api.album(source), from_album=True)
                elif url_type == "playlist":
                    sp_track_list = self.__spotify_tracks_getter(self.spotify_api.playlist(source), from_playlist=True)
                elif url_type == "track":
                    sp_track_list = [self.spotify_api.track(source)]
                else:
                    self.logger.warn("Unsupported Spotify URL")
                    return
            except Exception as e:
                self.logger.debug(e)
            for sp_track in sp_track_list:
                yield (await self._get_equiv_track_from_yt(sp_track, node), url_type)
            # return [await self._get_equiv_track_from_yt(sp_track, node) for sp_track in sp_track_list], url_type
            
