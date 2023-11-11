# f451 Labs Uploader module v0.3.0

## Overview

The *f451 Labs Uploader* module encapsulates the *Adafruit IO* REST and MQTT clients, as well as the *Arduino Cloud* client within a single class. Most *f451 Labs* projects upload to and/or receive data from one or both of these services, and the `Uploader` class simplifies these tasks by standardizing send and receive methods, and so on.

## Install

This module is not (yet) available on PyPi. however, you can still use `pip` to install the module directly from Github (see below).

### Dependencies

This module is dependent on the following libraries:

- [adafruit-io](https://adafruit-io-python-client.readthedocs.io/en/latest/index.html)
- [arduino-iot-client](https://docs.arduino.cc/arduino-cloud/getting-started/arduino-iot-api#python)
- [requests-oauthlib](https://pypi.org/project/requests-oauthlib/)

### Installing from Github using `pip`

You can use `pip install` to install this module directly from Github as follows:

Using HTTPS:

```bash
$ pip install 'f451-uploader @ git+https://github.com/mlanser/f451-uploader.git'
```

Using SSH:

```bash
$ pip install 'f451-uploader @ git+ssh://git@github.com:mlanser/f451-uploader.git'
```

## How to use

Using the module is straightforward. Simply `import` it into your code and instantiate an `Uploader` object which you can then use throughout your code.

```Python
# Import f451 Labs Uploader
from f451_uploader.uploader import Uploader

# Initialize 'Uploader'
myUploader = Uploader(
    AIO_ID = "<ADAFRUIT IO USERNAME>", 
    AIO_KEY = "<ADAFRUIT IO KEY>"
)

# Create an Adafruit IO feed
feed = myUploader.aio_create_feed('my-new-feed')

# Upload data to Adafruit IO feed
asyncio.run(myUploader.aio_send_data(feed.key, randint(1, 100)))

# Receiving latest data from Adafruit IO feed
data = asyncio.run(myUploader.aio_receive_data(feed.key, True))

# Adafruit IO returns data in form of 'namedtuple' and we can 
# use the '_asdict()' method to convert it to regular 'dict'.
# We then pass the 'dict' to 'json.dumps()' to prettify before 
# we print out the whole structure.
pretty = json.dumps(data._asdict(), indent=4, sort_keys=True)
print(pretty)
```
