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
        self._aioREST = aioREST(aioID, aioKey)
        self._aioMQTT = None
        self._ardREST = None
        self._LOG = logger
        
    def aio_create_feed(self, feedName):
        """Create Adafruit IO feed

        Args:
            feedName:
                'str' name of new Adafruit IO feed
        Returns:
            Adafruit feed info
        """
        feed = aioFeed(name=feedName)
        try:
            info = self._aioREST.create_feed(feed)

        except RequestError as e:
            if self._LOG:
                self._LOG.log(logging.ERROR, f"Failed to create feed - ADAFRUIT REQUEST ERROR: {e}")
            raise
        
        return info

    def aio_get_feed_info(self, feedKey):
        """Get Adafruit IO feed info

        Args:
            feedKey:
                'str' with Adafruit IO feed key
        Returns:
            Adafruit feed info
        """
        try:
            info = self._aioREST.feeds(feedKey)

        except RequestError as e:
            if self._LOG:
                self._LOG.log(logging.ERROR, f"Failed to get feed info - ADAFRUIT REQUEST ERROR: {e}")
            raise
        
        return info

    def aio_delete_feed(self, feedKey):
        """Delete Adafruit IO feed

        Args:
            feedKey:
                'str' with Adafruit IO feed key
        Returns:
            Adafruit feed info
        """
        try:
            info = self._aioREST.feeds(feedKey)

        except RequestError as e:
            if self._LOG:
                self._LOG.log(logging.ERROR, f"Failed to get feed info - ADAFRUIT REQUEST ERROR: {e}")
            raise
        
        return info

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
