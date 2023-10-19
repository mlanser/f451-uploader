"""Demo for using f451 Labs Uploader Module."""

import time
import sys
import asyncio
from pathlib import Path
from random import randint

from f451_uploader.uploader import Uploader

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


# =========================================================
#          G L O B A L S   A N D   H E L P E R S
# =========================================================
KWD_AIO_ID = "AIO_ID"
KWD_AIO_KEY = "AIO_KEY"
KWD_ARD_ID = "ARD_ID"
KWD_ARD_KEY = "ARD_KEY"

def get_setting(settings, key, default=None):
    """Get a config value from settings
    
    Args:
        settings:
            'dict' with settings values
        key:
            'str' with name of settings key
        defaul:
            Default value

    Returns:
        Settings value        
    """
    return settings[key] if key in settings else default


# =========================================================
#                    D E M O   A P P
# =========================================================
def main():
    # Get app dir
    appDir = Path(__file__).parent

    # Initialize TOML parser and load 'settings.toml' file
    try:
        with open(appDir.joinpath("settings.toml"), mode="rb") as fp:
            config = tomllib.load(fp)
    except tomllib.TOMLDecodeError:
        sys.exit("Invalid 'settings.toml' file")      

    iot = Uploader(
        get_setting(config, KWD_AIO_ID),
        get_setting(config, KWD_AIO_KEY),
        get_setting(config, KWD_ARD_ID),
        get_setting(config, KWD_ARD_KEY)
    )

    feedName = 'TEST_FEED_' + str(time.time_ns())

    print(f"Creating new Adafruit IO feed: {feedName}")
    feed = iot.aio_create_feed(feedName)

    dataPt = randint(1, 100)
    print(f"Uploading random value '{dataPt}' to Adafruit IO feed: {feed.key}")
    asyncio.run(iot.aio_send_data(feed.key, dataPt))


if __name__ == "__main__":
    main()