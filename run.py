from bot import bot

import os


if __name__ == "__main__":
    if not "MUSICBTW_DEV_TOKEN" in os.environ:
        input("`MUSICBTW_DEV_TOKEN` must be set as an environment variable, press any key to exit")
        exit()
    else:
        musicbtw = bot.MusicBTW(command_prefix="!")
        musicbtw.run(os.environ.get("MUSICBTW_DEV_TOKEN"))
