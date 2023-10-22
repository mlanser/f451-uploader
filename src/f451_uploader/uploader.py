"""f451 Labs Uploader module.

The f451 Labs Uploader module encapsulates the Adafruit IO REST and MQTT client 
classes, the Arduino IoT-API client class, and adds a few more features that are 
commonly used in f451 Labs projects.

Dependencies:
 - logging
 - pprint
 - random
 - oauthlib
 - tomllib / tomli
 - arduino-iot-client
 - requests-authlib
 - adafruit-io
 - typing-extensions < Python 3.10
 - frozendict
"""

import logging

from random import randint
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from Adafruit_IO import Client as aioREST, MQTTClient as aioMQTT, Feed as aioFeed
from Adafruit_IO import RequestError, ThrottlingError

import iot_api_client as ardClient
from iot_api_client.rest import ApiException as ardAPIError
from iot_api_client.configuration import Configuration as ardConfig


# =========================================================
#                     M A I N   C L A S S
# =========================================================
class Uploader:
    """Main Uploader class for manaing IoT data uploads.

    This class encapsulates both Adafruit IO and Arduino Cloud clients
    and makes it easier to upload data to and/or receive data from either
    cloud service.

    Attributes:
        aio_is_active:
            boolean flag indicating that Adafruit IO clients are initialized
        ard_is_active:
            boolean flag indicating that Arduino Cloud client is initialized

    Methods:
        aio_create_feed:
            method to create a new Adafruit IO feed
        aio_feed_info:
            method to get info/metadata for an Adafruit IO feed
        aio_delete_feed:
            method to delete an existing Adafruit IO feed
    """
    def __init__(self, aioID="", aioKey="", ardID="", ardKey="", logger=None):
        """Initialize Uploader

        Args:
            aioID:
                Adafruit IO user name
            aioKey:
                Adafruit IO secret/key
            ardID:
                Arduino Cloud client ID
            ardKey:
                Arduino Cloud client secret/key
            logger:
                f451 Labs Logger object - if available, then this object 
                can log errors as needed    
        """
        self.aio_is_active, self._aioREST, self._aioMQTT = self._init_aio(aioID, aioKey)
        self._ardREST = None
        self._LOG = logger
        
    def _init_aio_rest(self, aioID, aioKey):
        """Initialize Adafruit IO REST and MQTT clients."""
        flg = False
        aRC = aMC = None

        if aioID and aioKey:
            aRC = self.aioREST(aioID, aioKey)
            aRC = self.aioREST(aioID, aioKey)
            flg = True

        return flg, aRC, aMC    

    def aio_create_feed(self, feedName):
        """Create Adafruit IO feed

        Args:
            feedName:
                'str' name of new Adafruit IO feed
        Returns:
            Adafruit feed info

        Raises:
            RequestError
        """
        if self.aio_is_active:
            feed = aioFeed(name=feedName)
            try:
                info = self._aioREST.create_feed(feed)

            except RequestError as e:
                if self._LOG:
                    self._LOG.log(logging.ERROR, f"Failed to create feed - ADAFRUIT REQUEST ERROR: {e}")
                raise
        
            return info
        
        else:
            raise RequestError

    def aio_feed_info(self, feedKey):
        """Get Adafruit IO feed info

        Args:
            feedKey:
                'str' with Adafruit IO feed key
        Returns:
            Adafruit feed info
        """
        if self.aio_is_active:
            try:
                info = self._aioREST.feeds(feedKey)

            except RequestError as e:
                if self._LOG:
                    self._LOG.log(logging.ERROR, f"Failed to get feed info - ADAFRUIT REQUEST ERROR: {e}")
                raise
            
            return info
        
        else:
            raise RequestError

    def aio_delete_feed(self, feedKey):
        """Delete Adafruit IO feed

        Args:
            feedKey:
                'str' with Adafruit IO feed key
        Returns:
            Adafruit feed info
        """
        if self.aio_is_active:
            try:
                info = self._aioREST.feeds(feedKey)

            except RequestError as e:
                if self._LOG:
                    self._LOG.log(logging.ERROR, f"Failed to get feed info - ADAFRUIT REQUEST ERROR: {e}")
                raise
            
            return info
        
        else:
            raise RequestError

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
            RequestError:
                When API request fails
            ThrottlingError:
                When exceeding Adafruit IO rate limit
        """
        if self.aio_is_active:
            try:
                self._aioREST.send_data(feedKey, dataPt)
            except RequestError as e:
                if self._LOG:
                    self._LOG.log(logging.ERROR, f"Upload failed for {feedKey} - REQUEST ERROR: {e}")
                raise
            
            except ThrottlingError as e:
                if self._LOG:
                    self._LOG.log(logging.ERROR, f"Upload failed for {feedKey} - THROTTLING ERROR: {e}")
                raise
        
        else:
            raise RequestError

