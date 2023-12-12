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
        with open(Path(__file__).parent.joinpath('settings.toml'), mode='rb') as fp:
            config = tomllib.load(fp)
    except (FileNotFoundError, tomllib.TOMLDecodeError):
        config = {
            'AIO_ID': None,         # Set your 'ADAFRUIT IO USERNAME'
            'AIO_KEY': None,        # set your 'ADAFRUIT IO KEY'
            'AIO_LOC_ID': None,     # set your 'ADAFRUIT IO Weather Location ID'
        }

    # Check for creds
    if not config.get('AIO_ID', None) or not config.get('AIO_KEY', None):
        sys.exit('ERROR: Missing Adafruit IO credentials')

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

    # Get weather forecast from Adafruit IO as JSON
    print("\n--------------------------------------------")
    print("Receiving latest weather data from Adafruit IO")
    forecast = asyncio.run(iot.aio_receive_weather())
    print(json.dumps(forecast, indent=4, sort_keys=True))

    # Parse the current forecast
    # current = forecast['current']
    # print("Current Forecast")
    # print(f"It's {current['conditionCode']} and {current['temperature']}C")

    # Parse 2-day forecast
    # forecast2d = forecast['forecast_days_2']
    # print("\nWeather in Two Days")
    # print(f"It'll be {forecast2d['conditionCode']} with a high of {forecast2d['temperatureMin']}C and a low of {forecast2d['temperatureMax']}C.")

    # Parse the five day forecast
    # forecast5d = forecast['forecast_days_5']
    # print('\nWeather in Five Days')
    # print(f"It'll be {forecast5d['conditionCode']} with a high of {forecast5d['temperatureMin']}C and a low of {forecast5d['temperatureMax']}C.")

    # Get random data from Adafruit IO
    print("\n--------------------------------------------")
    # someWord = asyncio.run(iot.aio_receive_random_word())
    # print(f"Receiving random word from Adafruit IO: {someWord}")
    print("Receiving random word from Adafruit IO")
    someWord = asyncio.run(iot.aio_receive_random(iot.aioRandWord, True))
    print(json.dumps(someWord, indent=4, sort_keys=True))

    print("\n--------------------------------------------")
    # someNumber = asyncio.run(iot.aio_receive_random_number())
    # print(f"Receiving random number from Adafruit IO: {someNumber}")
    print("Receiving random number from Adafruit IO")
    someNumber = asyncio.run(iot.aio_receive_random(iot.aioRandNumber, True))
    print(json.dumps(someNumber, indent=4, sort_keys=True))

    print("=============== [End of Demo] =================\n")


if __name__ == '__main__':
    main()
