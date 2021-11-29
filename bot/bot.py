import logging
import datetime
import os

from logging import handlers

from discord.ext import commands


class MusicBTW(commands.Bot):
    def __init__(self, command_prefix, description=None, **options) -> None:
        super().__init__(command_prefix, description=description, **options)
        self.start_datetime = datetime.datetime.now()
        self.logger = self.__config_logging(logging_level=logging.DEBUG)
        self.logger.info(f"Command prefix: {command_prefix}")
        # Any other statup stuffs can go here
    
    @staticmethod
    def __config_logging(logging_level=logging.INFO, outdir="./logs"):
        logger = logging.getLogger("MusicBTW")
        logger.setLevel(logging_level)
        formatter = logging.Formatter('[{asctime}] [{levelname:}] {name}: {message}',
                                      '%Y-%m-%d %H:%M:%S', style='{')
        # file_log = handlers.RotatingFileHandler(f'{outdir}/{self.start_datetime.strftime("%Y%m%d_%H%M%S")}.log',
        #                                         encoding="utf-8", mode="a", backupCount=3, maxBytes=10000000)
        console_log = logging.StreamHandler()
        # file_log.setFormatter(formatter)
        console_log.setFormatter(formatter)
        # logger.addHandler(file_log)
        logger.addHandler(console_log)
        logger.debug("Logging configured")
        return logger


if __name__ == "__main__":
    input("This script is not to be called directly, invoke ./run.py instead.\n\nPress any key to exit.")
    exit()