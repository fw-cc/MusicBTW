from typing import Optional, List
import logging
import re

import youtube_dl
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


__logger = logging.getLogger("MusicBTW.Track")


class Track:
    """Tracks represent audio files to be played and during initialisation 
    will ensure all resources required prior to playback are fetched.
    
    Upon entry into the Queue and setting of """
    def __init__(self, sp_api, ) -> None:
        """ Initialisation of the `Track` object
        
        `source` must assume the form of one of: URL, Search String.
        URLs must be from Youtube or Spotify, Search Strings will be used to search Youtube 
        and will resolve to a user option. 
        """

        self.logger = __logger
        self.initial_source = None
        self.ready_to_queue = False
        self.options = None
        
    def __search_youtube(self):
        pass


def __spotify_tracks_getter(spotify_response, sp_api) -> List[Track]:
    """Generates a list of tracks for Spotify API responses to albums and playlists"""
    tracks_obj = spotify_response["tracks"]
    tracks_basic_list = []
    while tracks_obj['next'] is not None:
        # Since the Spotify API doesn't like us getting too much in one response we'll have to
        # batch get things ;-;

        tracks_basic_list.append(None)


def gen_tracks(source: str, spotify_credentials: Optional[SpotifyClientCredentials]=None) -> List[Track]:
    SPOTIFY_PATTERN = r"^(?P<main_url>(https?:\/\/open.)?spotify.com\/(?P<type>\w{4,20})\/.*)\?.*"
    YOUTUBE_PATTERN = r"^https?://.*(youtube\.com/(playlist\?list|watch)=|youtu\.be/)(.{34}|.{11})(\?t=(?P<time_offset>\d+))?"
    initial_source = None
    url_type = None

    # test = re.match(SPOTIFY_PATTERN, source)
    if regex_match := re.search(SPOTIFY_PATTERN, source):
        __logger.debug("Matched Spotify URL")
        try:
            cleaned_url = regex_match.group("main_url")
            url_type = regex_match.group("type")
        except IndexError as e:
            __logger.warning("Failed to match cleaned URL or URL type")
            __logger.debug(e)
            return []
        ### Handle Spotify
        initial_source = "spotify"
        result = None
        sp_api = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
        if url_type == "album":
            result = sp_api.album(source)
            return __spotify_tracks_getter(result, sp_api)
        elif url_type == "playlist":
            result = sp_api.playlist(source)
            return __spotify_tracks_getter(result, sp_api)
        elif url_type == "track":
            result = sp_api.track(source)
            return [result]
    elif regex_match := re.match(YOUTUBE_PATTERN, source):
        __logger.debug("Matched Youtube URL")
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
        __logger.warn("Only Youtube and Spotify URLs are supported at this time.")
        return []
    else:
        # Likely a search term for youtube
        initial_source = "search"
    print("")

if __name__ == "__main__":
    gen_tracks("https://open.spotify.com/playlist/4u6d7ePvdNpZb1NWbebTzA?si=addc4754fb6341f9")
    print("")
