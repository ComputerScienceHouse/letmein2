import time, gc, os
import adafruit_dotstar
import board
import feathers2
import digitalio
import wifi
import socketpool
import ssl # TODO: Use this
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import ipaddress
import adafruit_requests

from secrets import secrets

# Make sure the 2nd LDO is turned on
feathers2.enable_LDO2(True)

# Create a DotStar instance
dotstar = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.5, auto_write=True)

# Say hello
print('''
    '{tttttttttttttttttttttttt^ *tttt
    :@@@@@@@@@@@@@@@@@@@@@@@@@m d@@@@N`
    :@@@@@@@@@@@@@@@@@@@@@@@@@m d@@@@N`
    :@@@@@m:::::::::::::rQ@@@@m d@@@@N`
    :@@@@@] vBBBBBBBBBN,`]oooo* d@@@@N`
    :@@@@@] o@@@NNNQ@@@"`ueeee| d@@@@N`
    :@@@@@] o@@&   ,||?`'Q@@@@m d@@@@N`
    :@@@@@] o@@Q]tt{{{z-'Q@@@@QOQ@@@@N`
    :@@@@@] o@@@@@@@@@@"'Q@@@@@@@@@@@N`
    :@@@@@] ';;;;;;y@@@"'Q@@@@N7Q@@@@N`
    :@@@@@] \KKe^^^a@@@"'Q@@@@m d@@@@N`
    :@@@@@] o@@@@@@@@@@" _::::' d@@@@N`
    :@@@@@] raaaaaaaaay..H####} d@@@@N`
    :@@@@@#eeeeeeeeeeeeek@@@@@m d@@@@N`
    :@@@@@@@@@@@@@@@@@@@@@@@@@m d@@@@N`
    :@@@@@@@@@@@@@@@@@@@@@@@@@e K@@@@W`
     .........................` `....-
''')
print("--  -- =- CSH LetMeIn! v2.0alpha1 -= -- --\n")

# Show available memory
print("Memory Info - gc.mem_free()")
print("---------------------------")
print("{} Bytes\n".format(gc.mem_free()))

flash = os.statvfs('/')
flash_size = flash[0] * flash[2]
flash_free = flash[0] * flash[3]
# Show flash size
print("Flash - os.statvfs('/')")
print("---------------------------")
print("Size: {} Bytes\nFree: {} Bytes\n".format(flash_size, flash_free))

# Set up gpio
s_stairs = digitalio.DigitalInOut(board.IO10)
level_1 = digitalio.DigitalInOut(board.IO7)
level_a = digitalio.DigitalInOut(board.IO3)
n_stairs = digitalio.DigitalInOut(board.IO1)
s_stairs.direction = digitalio.Direction.OUTPUT
level_1.direction = digitalio.Direction.OUTPUT
level_a.direction = digitalio.Direction.OUTPUT
n_stairs.direction = digitalio.Direction.OUTPUT

ack = digitalio.DigitalInOut(board.IO5)
ack.direction = digitalio.Direction.INPUT

sleep_len = 0.2

# Turn on the internal blue LED
feathers2.led_set(True)

# Connect to wifi
print("Connecting to %s" % secrets['ssid'])
print("mac address:", "%02x:%02x:%02x:%02x:%02x:%02x" % tuple(map(int, wifi.radio.mac_address)))
wifi.radio.connect(secrets['ssid'], secrets['password'])
print("Connected to %s!" % secrets['ssid'])


### CHOM


### Topic Setup ###

# MQTT Topic
# Use this topic if you'd like to connect to a standard MQTT broker
mqtt_topic = "test/topic"

# Adafruit IO-style Topic
# Use this topic if you'd like to connect to io.adafruit.com
# mqtt_topic = secrets["aio_username"] + '/feeds/temperature'

### Code ###
# Define callback methods which are called when events occur
# pylint: disable=unused-argument, redefined-outer-name
def connect(mqtt_client, userdata, flags, rc):
    # This function will be called when the mqtt_client is connected
    # successfully to the broker.
    print("Connected to MQTT Broker!")
    print("Flags: {0}\n RC: {1}".format(flags, rc))


def disconnect(mqtt_client, userdata, rc):
    # This method is called when the mqtt_client disconnects
    # from the broker.
    print("Disconnected from MQTT Broker!")


def subscribe(mqtt_client, userdata, topic, granted_qos):
    # This method is called when the mqtt_client subscribes to a new feed.
    print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))


def unsubscribe(mqtt_client, userdata, topic, pid):
    # This method is called when the mqtt_client unsubscribes from a feed.
    print("Unsubscribed from {0} with PID {1}".format(topic, pid))


def publish(mqtt_client, userdata, topic, pid):
    # This method is called when the mqtt_client publishes data to a feed.
    print("Published to {0} with PID {1}".format(topic, pid))


def message(client, topic, message):
    # Method called when a client's subscribed feed has a new value.
    print("New message on topic {0}: {1}".format(topic, message))


# Create a socket pool
pool = socketpool.SocketPool(wifi.radio)

# Set up a MiniMQTT Client
mqtt_client = MQTT.MQTT(
    broker=secrets["broker"],
    port=secrets["port"],
    socket_pool=pool,
    ssl_context=ssl.create_default_context(),
)

# Connect callback handlers to mqtt_client
mqtt_client.on_connect = connect
mqtt_client.on_disconnect = disconnect
mqtt_client.on_subscribe = subscribe
mqtt_client.on_unsubscribe = unsubscribe
mqtt_client.on_publish = publish
mqtt_client.on_message = message

print("Attempting to connect to %s" % mqtt_client.broker)
mqtt_client.connect()

print("Subscribing to %s" % mqtt_topic)
mqtt_client.subscribe(mqtt_topic)

print("Publishing to %s" % mqtt_topic)
mqtt_client.publish(mqtt_topic, "Hello Broker!")

print("Unsubscribing from %s" % mqtt_topic)
mqtt_client.unsubscribe(mqtt_topic)

print("Disconnecting from %s" % mqtt_client.broker)
mqtt_client.disconnect()

### CHOM


# Main loop
while True:

    #mqtt_client.loop()

#    s_stairs.value = ack.value
    if ack.value:
        s_stairs.value = 1
        time.sleep(sleep_len)
        s_stairs.value = 0
        time.sleep(sleep_len)

        level_1.value = 1
        time.sleep(sleep_len)
        level_1.value = 0
        time.sleep(sleep_len)

        level_a.value = 1
        time.sleep(sleep_len)
        level_a.value = 0
        time.sleep(sleep_len)

        n_stairs.value = 1
        time.sleep(sleep_len)
        n_stairs.value = 0
        time.sleep(sleep_len)
