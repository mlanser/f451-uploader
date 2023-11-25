"""f451 Labs Cloud module.

The f451 Labs Cloud module encapsulates the Adafruit IO REST and MQTT client 
classes, the Arduino IoT-API client class, and adds a few more features that are 
commonly used in f451 Labs projects.

Dependencies:
 - random
 - oauthlib
 - tomllib / tomli
 - arduino-iot-client
 - requests-authlib
 - adafruit-io
 - typing-extensions < Python 3.10
 - frozendict
"""

import json
import asyncio

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from Adafruit_IO import Client as aioREST, MQTTClient as aioMQTT, Feed as aioFeed
# from Adafruit_IO import RequestError, ThrottlingError

import iot_api_client as ardClient
from iot_api_client.rest import ApiException as ardAPIError
from iot_api_client.configuration import Configuration as ardConfig

__all__ = [
    "Cloud",
    "CloudError",    
    "KWD_AIO_ID",
    "KWD_AIO_KEY",
    "KWD_ARD_ID",
    "KWD_ARD_KEY",
    "KWD_AIO_LOC_ID",
    "KWD_AIO_RWRD_ID",
    "KWD_AIO_RNUM_ID",
]


# =========================================================
#    K E Y W O R D S   F O R   C O N F I G   F I L E S
# =========================================================
KWD_AIO_ID = "AIO_ID"
KWD_AIO_KEY = "AIO_KEY"
KWD_AIO_LOC_ID = "AIO_LOC_ID"
KWD_AIO_RWRD_ID = "AIO_RWRD_ID"
KWD_AIO_RNUM_ID = "AIO_RNUM_ID"

KWD_ARD_ID = "ARD_ID"
KWD_ARD_KEY = "ARD_KEY"


# =========================================================
#                        H E L P E R S
# =========================================================
class CloudError(Exception):
    """Custom exception class"""
    pass


# =========================================================
#                     M A I N   C L A S S
# =========================================================
class Cloud:
    """Main Cloud class for managing IoT data uploads.

    This class encapsulates both Adafruit IO and Arduino Cloud clients
    and makes it easier to upload data to and/or receive data from either
    cloud service.

    NOTE: attributes follow same naming convention as used 
    in the 'settings.toml' file. This makes it possible to pass 
    in the 'config' object (or any other dict) as is.

    NOTE: we let users provide an entire 'dict' object with settings as 
    key-value pairs, or as individual settings. User can combine both and,
    for example, provide a standard 'config' object as well as individual
    settings which could override the values in the 'config' object.

    Example:
        myCloud = Cloud(config)           # Use values from 'config' 
        myCloud = Cloud(key=val)          # Use val
        myCloud = Cloud(config, key=val)  # Use values from 'config' and also use 'val' 

    Attributes:
        AIO_USERNAME:   Adafruit IO username
        AIO_KEY:        Adafruit IO secret/key
        ARD_USERNAME:   Arduino Cloud client ID
        ARD_KEY:        Arduino Cloud secret/key

    Methods:
        aio_create_feed:    Create a new Adafruit IO feed
        aio_feed_list:      Get complete list of Adafruit IO feeds
        aio_feed_info:      Get info/metadata for an Adafruit IO feed
        aio_delete_feed:    Delete an existing Adafruit IO feed
        aio_send_data:      Send data to an existing Adafruit IO feed
        aio_receive_data:   Receive data from an existing Adafruit IO feed
    """
    def __init__(self, *args, **kwargs):
        """Initialize Cloud

        Args:
            args:
                User can provide single 'dict' with settings
            kwargs:
                User can provide individual settings as key-value pairs
        """

        # We combine 'args' and 'kwargs' to allow users to provide the entire 
        # 'config' object and/or individual settings (which could override 
        # values in 'config').
        settings = {**args[0], **kwargs} if args and isinstance(args[0], dict) else kwargs

        self.aio_is_active, self._aioREST, self._aioMQTT = self._init_aio(**settings)
        self.ard_is_active, self._ardREST = self._init_ard(**settings)

        self._aioLocID = settings.get(KWD_AIO_LOC_ID)
        self._aioRndWrdID = settings.get(KWD_AIO_RWRD_ID)
        self._aioRndNumID = settings.get(KWD_AIO_RNUM_ID)

    def _init_aio(self, **kwargs):
        """Initialize Adafruit IO REST and MQTT clients."""
        flg = False
        aRC = aMC = None

        aioID = kwargs.get(KWD_AIO_ID)
        aioKey = kwargs.get(KWD_AIO_KEY)

        if aioID and aioKey:
            aRC = aioREST(aioID, aioKey)
            aMC = aioMQTT(aioID, aioKey)
            flg = bool(aRC) and bool(aMC)

        return flg, aRC, aMC    

    def _init_ard(self, **kwargs):
        """Initialize Arduino Cloud client."""
        flg = False
        ard = None

        ardID = kwargs.get(KWD_ARD_ID)
        ardKey = kwargs.get(KWD_ARD_KEY)

        if ardID and ardKey:
            ard = None          # TO DO: fix this placeholder
            flg = bool(ard)

        return flg, ard

    @property
    def aioRandWord(self):
        return self._aioRndWrdID

    @property
    def aioRandNumber(self):
        return self._aioRndNumID

    def aio_create_feed(self, feedName, strict=False):
        """Create Adafruit IO feed

        Args:
            feedName:
                'str' name of new Adafruit IO feed
            strict:
                If 'True' then exception is raised if feed already exists

        Returns:
            Adafruit feed info

        Raises:
            CloudError:
                When Adafruit IO client is not initiated
            RequestError:
                When API request fails
            ThrottlingError:
                When exceeding Adafruit IO rate limit
        """
        if self.aio_is_active:
            feed = aioFeed(name=feedName)

            if strict:
                feedList = self._aioREST.feeds()
                nameList = [feed.name for feed in feedList]
                if feedName in nameList:
                    raise CloudError(f"Adafruit IO already has a feed named '{feedName}'")
                
            return self._aioREST.create_feed(feed)
        
        else:
            raise CloudError("Adafruit IO client not initiated")

    def aio_feed_list(self):
        """Get Adafruit IO feed info

        Returns:
            List of feeds from Adafruit IO

        Raises:
            CloudError:
                When Adafruit IO client is not initiated
            RequestError:
                When API request fails
            ThrottlingError:
                When exceeding Adafruit IO rate limit
        """
        if self.aio_is_active:
            return self._aioREST.feeds()
        
        else:
            raise CloudError("Adafruit IO client not initiated")

    def aio_feed_info(self, feedKey):
        """Get Adafruit IO feed info

        Args:
            feedKey:
                'str' with Adafruit IO feed key
        Returns:
            Adafruit feed info

        Raises:
            CloudError:
                When Adafruit IO client is not initiated
            RequestError:
                When API request fails
            ThrottlingError:
                When exceeding Adafruit IO rate limit
        """
        if self.aio_is_active:
            return self._aioREST.feeds(feedKey)
        
        else:
            raise CloudError("Adafruit IO client not initiated")

    def aio_delete_feed(self, feedKey):
        """Delete Adafruit IO feed

        Args:
            feedKey:
                'str' with Adafruit IO feed key
        Returns:
            Adafruit feed info

        Raises:
            CloudError:
                When Adafruit IO client is not initiated
            RequestError:
                When API request fails
            ThrottlingError:
                When exceeding Adafruit IO rate limit
        """
        if self.aio_is_active:
            self._aioREST.delete_feed(feedKey)

        else:
            raise CloudError("Adafruit IO client not initiated")

    async def aio_send_data(self, feedKey, dataPt):
        """Send data value to Adafruit IO feed

        Args:
            feedKey:
                'str' with Adafruit IO feed key
            dataPt:
                'str'|'int'|'float' data point
        Returns:
            Adafruit feed info

        Raises:
            CloudError:
                When Adafruit IO client is not initiated
            RequestError:
                When API request fails
            ThrottlingError:
                When exceeding Adafruit IO rate limit
        """
        if self.aio_is_active:
            self._aioREST.send_data(feedKey, dataPt)
        
        else:
            raise CloudError("Adafruit IO client not initiated")

    async def aio_receive_data(self, feedKey, raw=False):
        """Receive last data value from Adafruit IO feed

        Args:
            feedKey:
                'str' with Adafruit IO feed key
            raw:
                If 'True' then raw data object (in form 
                of 'namedtuple') is returned    
        Returns:
            Adafruit feed info

        Raises:
            CloudError:
                When Adafruit IO client is not initiated
            RequestError:
                When API request fails
            ThrottlingError:
                When exceeding Adafruit IO rate limit
        """
        if self.aio_is_active:
            data = self._aioREST.receive(feedKey)
            return data if raw else data.value
        
        else:
            raise CloudError("Adafruit IO client not initiated")

    async def aio_receive_weather(self, weatherID=None, raw=False):
        """Receive weather data from Adafruit IO feed

        Args:
            weatherID:
                'int' with Adafruit IO weather ID
            raw:
                If 'True' then raw data object (in form 
                of 'namedtuple') is returned, else data
                is returned as JSON   
        Returns:
            Adafruit weather data

        Raises:
            CloudError:
                When Adafruit IO client is not initiated
            RequestError:
                When API request fails
            ThrottlingError:
                When exceeding Adafruit IO rate limit
        """
        if self.aio_is_active:
            wID = weatherID if weatherID is not None else self._aioLocID
            data = self._aioREST.receive_weather(wID)
            return data if raw else json.loads(json.dumps(data))
        
        else:
            raise CloudError("Adafruit IO client not initiated")

    async def aio_receive_random(self, randomID=None, raw=False):
        """Receive random value from Adafruit IO feed

        Args:
            randomID:
                'int' with Adafruit IO random generator ID
            raw:
                If 'True' then raw data object (in form 
                of 'namedtuple') is returned, else data
                is returned as JSON   
        Returns:
            Adafruit random data

        Raises:
            CloudError:
                When Adafruit IO client is not initiated
            RequestError:
                When API request fails
            ThrottlingError:
                When exceeding Adafruit IO rate limit
        """
        if self.aio_is_active:
            data = self._aioREST.receive_random(randomID)
            return data if raw else data.value
        
        else:
            raise CloudError("Adafruit IO client not initiated")

    # async def aio_receive_random_word(self):
    #     return asyncio.run(self.aio_receive_random(self._aioRndWrdID))

    # async def aio_receive_random_number(self):
    #     return asyncio.run(self.aio_receive_random(self._aioRndNumID))

