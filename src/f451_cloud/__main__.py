"""Demo for using f451 Labs Cloud Module."""

import time
import sys
import asyncio
from pathlib import Path
from random import randint
import json

from .cloud import Cloud

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


# =========================================================
#                    D E M O   A P P
# =========================================================
def main():
    # Initialize TOML parser and try to load 'settings.toml' file
    try:
        with open(Path(__file__).parent.joinpath("settings.toml"), mode="rb") as fp:
            config = tomllib.load(fp)
    except (FileNotFoundError, tomllib.TOMLDecodeError):
        config = {
            "AIO_ID": None,         # Set your 'ADAFRUIT IO USERNAME'
            "AIO_KEY": None,        # set your 'ADAFRUIT IO KEY'
        }

    # Check for creds
    if not config.get("AIO_ID", None) or not config.get("AIO_KEY", None):
        sys.exit("ERROR: Missing Adafruit IO credentials")      

    iot = Cloud(config)
    feedName = 'TEST_FEED_' + str(time.time_ns())

    print("\n===== [Demo of f451 Labs Cloud Module] =====")
    print(f"Creating new Adafruit IO feed: {feedName}")
    feed = iot.aio_create_feed(feedName)

    dataPt = randint(1, 100)
    print(f"Uploading random value '{dataPt}' to Adafruit IO feed: {feed.key}")
    asyncio.run(iot.aio_send_data(feed.key, dataPt))

    print(f"Receiving latest from Adafruit IO feed: {feed.key}")
    data = asyncio.run(iot.aio_receive_data(feed.key, True))

    # Adafruit IO returns data in form of 'namedtuple' and we can 
    # use the '_asdict()' method to convert it to regular 'dict'.
    # We then pass the 'dict' to 'json.dumps()' to prettify before 
    # we print out the whole structure.
    pretty = json.dumps(data._asdict(), indent=4, sort_keys=True)
    print(pretty)

    print("=============== [End of Demo] =================\n")


if __name__ == "__main__":
    main()