from queue import Queue

import logging


class Player:
    def __init__(self, bot) -> None:
        self.logger = logging.getLogger("MusicBTW.Player")
        self.current_track = None
        self.__playing = False
        self.__queue = Queue(bot)

    @property
    def queue(self):
        return self.__queue.queue

    @property
    def playing(self):
        return self.current_track.playing
    
    def pause(self):
        pass

    def resume(self):
        pass

    def stop(self):
        self.__queue.clear()

    async def next(self):
        self.current_track = self.__queue.next()
