from bot import bot

import os
import shutil


if __name__ == "__main__":
    # Lazy way of emptying folder
    if not os.path.exists("./track_cache/"):
        os.mkdir("./track_cache")
    else:
        shutil.rmtree("./track_cache/")
        os.mkdir("./track_cache")

    if not "MUSICBTW_DEV_TOKEN" in os.environ:
        input("`MUSICBTW_DEV_TOKEN` must be set as an environment variable, press any key to exit")
        exit()
    else:
        musicbtw = bot.MusicBTW(command_prefix="!")
        musicbtw.run(os.environ.get("MUSICBTW_DEV_TOKEN"))
