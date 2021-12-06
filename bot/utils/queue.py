from bot.utils.track import Track

from typing import Union, List

import logging
import random


class Queue:
    def __init__(self, bot) -> None:
        self.logger = logging.getLogger("MusicBTW.Queue")
        # Could use a dequeue or some other advanced tech here but would that be cool or trendy?
        # maybe idk...
        self.bot = bot
        self.__queued_tracks = []
    
    @property
    def queue(self) -> List[Track]:
        """Queue list getter

        Returns:
            queue (List[Track]): List of tracks in the queue
        """
        return self.__queued_tracks

    def add(self, tracks: Union[Track, List[Track]]):
        """Adds a Track or list of Tracks to the playlist.

        Args:
            tracks (Union[Track, List[Track]]): Track or list of Tracks
                to be added to the playlist
        """
        preload = False
        if len(self.queue) == 0:
            preload = True

        if isinstance(tracks, Track):
            self.__queued_tracks.append(tracks)
            self.logger.debug("Added track to queue.")
        else:
            self.__queued_tracks.extend(tracks)
            self.logger.debug(f"Added {len(tracks)} tracks to queue.")

        if preload:
            self.__queued_tracks[0].load()

    def next(self) -> Union[None, Track]:
        """Returns (by pop) the next (zeroth) Track of the queue."""
        if len(self.queue) == 0:
            return None
        try:
            if not self.__queued_tracks[1].ready_to_play:
                self.__queued_tracks[1].load()
        except IndexError:
            pass
        return self.__queued_tracks.pop(0)
    
    def shuffle(self):
        """Shuffles the queue."""
        if first_track := self.__queued_tracks[0].ready_to_play:
            first_track.unload()
        random.shuffle(self.__queued_tracks)
        self.__queued_tracks[0].load()
    
    def clear(self):
        """Clear the queue."""
        # Bless Python's garbo collection
        for track in self.__queued_tracks:
            if track.ready_to_play:
                track.unload()
        self.__queued_tracks = []
