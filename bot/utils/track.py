import downloader

from typing import Optional, List
import logging


__logger = logging.getLogger("MusicBTW.Track")


class Track:
    """Tracks represent audio files to be played and during initialisation 
    will ensure all resources required prior to playback are fetched.
    
    Upon entry into the Queue and setting of """
    def __init__(self, source: str, local_downloader: downloader.Downloader) -> None:
        """ Initialisation of the `Track` object
        
        `source` must assume the form of one of a URL.
        URLs must be from Youtube. 
        """
        self.logger = __logger
        self.source = source
        self.ready_to_play = False
        self.options = None
        self.location = None
        self.downloader = local_downloader
        self.__track = None

    async def load(self):
        """Load the track, must be done before playback, else it will not be buffered
        on disk for playback."""
        self.__track = await self.downloader.get()

    def unload(self):
        pass

    @property
    def track(self):
        return self.__track
        
    def __search_youtube(self):
        pass
