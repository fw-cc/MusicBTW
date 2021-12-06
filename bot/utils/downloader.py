import youtube_dl

from concurrent.futures import ThreadPoolExecutor
from functools import partial


ytdl_options = {
    "format": "bestaudio/best",
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
}


class Downloader:
    def __init__(self, output_dir=None, max_workers=4) -> None:
        self.__pool = ThreadPoolExecutor(max_workers=max_workers)
        self.ytdl = youtube_dl.YoutubeDL(ytdl_options)
        if output_dir is not None:
            pass

    async def get(self, loop, *args, **kwargs):
        """Runs an instance of YoutubeDL extract_info in the threadpool, returning a future
        that'll shove itself into the event loop when it's done.
        This will require work for the ungodly errors that can come out of YTDL.
        """
        return await loop.run_in_executor(self.__pool, partial(self.ytdl.extract_info, *args, **kwargs))
