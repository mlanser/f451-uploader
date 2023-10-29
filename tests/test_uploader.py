"""Test cases for f451 Labs Uploader module.

Some of these test cases will send data to and/or receive 
data from Adafruit IO and Arduino Cloud services. These 
tests require the presence of valid account IDs and secrets 
in the 'settings.toml' file.
"""

import pytest
import time
import sys
import asyncio
from pathlib import Path
from random import randint

from src.f451_uploader.uploader import Uploader

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


# =========================================================
#              M I S C .   C O N S T A N T S
# =========================================================
KWD_TST_VAL = "TST_VAL"

# =========================================================
#          F I X T U R E S   A N D   H E L P E R S
# =========================================================
@pytest.fixture
def valid_str():
    return "Hello world"


@pytest.fixture(scope="session")
def config():
    settings = "src/f451_uploader/settings.toml"
    try:
        with open(Path(__file__).parent.parent.joinpath(settings), mode="rb") as fp:
            config = tomllib.load(fp)
    except tomllib.TOMLDecodeError:
        pytest.fail("Invalid 'settings.toml' file")      
    except FileNotFoundError:
        pytest.fail("Missing 'settings.toml' file")      

    return config


@pytest.fixture(scope="session")
def uploader(config):
    uploader = Uploader(config)

    return uploader


# =========================================================
#                    T E S T   C A S E S
# =========================================================
def test_dummy(valid_str):
    """Dummy test case.
    
    This is only a placeholder test case.
    """
    assert valid_str == "Hello world"


def test_config(config):
    setting = config[KWD_TST_VAL]

    assert setting == "test1-2-3"


def test_init_aio(config):
    uploader = Uploader(config)

    assert uploader.aio_is_active


@pytest.mark.online
@pytest.mark.adafruit
def test_aio_create_and_delete_feed(uploader):
    feedName = 'TEST-FEED-' + str(time.time_ns())

    feedInfo = uploader.aio_create_feed(feedName)
    feedList = uploader.aio_feed_list()
    nameList = [feed.name for feed in feedList]
    assert feedName in nameList

    uploader.aio_delete_feed(feedInfo.key)
    feedList = uploader.aio_feed_list()
    nameList = [feed.name for feed in feedList]
    assert feedName not in nameList


@pytest.mark.online
@pytest.mark.adafruit
def test_aio_send_and_delete_data(uploader):
    feedName = 'TEST-FEED-' + str(time.time_ns())
    dataPt = randint(1, 100)

    feedInfo = uploader.aio_create_feed(feedName)
    asyncio.run(uploader.aio_send_data(feedInfo.key, dataPt))
    checkData = asyncio.run(uploader.aio_receive_data(feedInfo.key))
    uploader.aio_delete_feed(feedInfo.key)
    assert int(checkData) == dataPt
