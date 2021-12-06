import track

from typing import Optional, List
import logging
import re

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


class Sourcer:
    def __init__(self, bot, spotify_credentials=SpotifyClientCredentials):
        self.spotify_api = spotipy.Spotify(client_credentials_manager=spotify_credentials())
        self.loop = bot.loop
        self.logger = logging.getLogger("MusicBTW.Sourcer")

    def __get_track_from_spotify(self, spotify_track) -> track.Track:
        pass

    def __spotify_tracks_getter(self, spotify_response):
        """Generates a list of tracks for Spotify API responses to albums and playlists"""
        tracks_obj = spotify_response["tracks"]
        tracks_data_list = []
        tracks_data_list.extend(tracks_obj["items"])
        while tracks_obj['next'] is not None:
            # Since the Spotify API doesn't like us getting too much in one response we'll have to
            # batch get things ;-;        
            tracks_obj = self.spotify_api.next(tracks_obj)
            tracks_data_list.extend(tracks_obj["items"])
        
        return tracks_data_list

    def gen_tracks(self, source: str) -> List[track.Track]:
        SPOTIFY_PATTERN = r"^(?P<main_url>(https?:\/\/open.)?spotify.com\/(?P<type>\w{4,20})\/.*)\?.*"
        YOUTUBE_PATTERN = r"^https?://.*(youtube\.com/(playlist\?list|watch)=|youtu\.be/)(.{34}|.{11})(\?t=(?P<time_offset>\d+))?"
        initial_source = None
        url_type = None

        # test = re.match(SPOTIFY_PATTERN, source)
        if regex_match := re.search(SPOTIFY_PATTERN, source):
            self.logger.debug("Matched Spotify URL")
            try:
                cleaned_url = regex_match.group("main_url")
                url_type = regex_match.group("type")
            except IndexError as e:
                self.logger.warning("Failed to match cleaned URL or URL type")
                self.logger.debug(e)
                return []
            ### Handle Spotify
            initial_source = "spotify"
            sp_track_list = None
            # sp_api = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
            if url_type == "album":
                sp_track_list = self.__spotify_tracks_getter(self.spotify_api.album(source))
            elif url_type == "playlist":
                sp_track_list = self.__spotify_tracks_getter(self.spotify_api.playlist(source))
            elif url_type == "track":
                sp_track_list = [self.spotify_api.track(source)]
            else:
                self.logger.warn("Unsupported Spotify URL")
                return
            return [self.__get_yt_from_spotify(sp_track) for sp_track in sp_track_list]

        elif regex_match := re.match(YOUTUBE_PATTERN, source):
            self.logger.debug("Matched Youtube URL")
            try:
                track_start_offset = regex_match.group("time_offset")
            except IndexError:
                # This is expected in the case that no ?t=xyz is included at the end of the URL 
                track_start_offset = 0
            ### Handle youtube
            initial_source = "youtube"
            if "playlist" in source:
                url_type = "playlist"
            else:
                url_type = "track"
        elif "http" in source:
            self.logger.warn("Only Youtube and Spotify URLs are supported at this time.")
            return []
        else:
            # Likely a search term for youtube
            initial_source = "search"
        print("")


if __name__ == "__main__":
    sourcer = Sourcer()
    sourcer.gen_tracks("https://open.spotify.com/playlist/2sFqkTzVenkPWeNl3nykgM?si=bfadfdf582ed40fc")
    print("")