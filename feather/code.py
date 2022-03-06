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
print("--  -- =- CSH LetMeIn! v2.0alpha2 -= -- --\n")

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
level_a = digitalio.DigitalInOut(board.IO1)
level_1 = digitalio.DigitalInOut(board.IO3)
n_stairs = digitalio.DigitalInOut(board.IO7)
s_stairs = digitalio.DigitalInOut(board.IO10)
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

### Topic Setup ###

# MQTT Topics. One for requesting, one for acknowledging.
# The deal is that whenever someone needs to be let in, she'll hit the
# button on the website, which will publish to `req` with the name of their
# door. The µController will get this message and turn on the corresponding LED.
# When a µController hits their button, they'll publish to `ack`, which everyone
# is subscribed to. For now, any message on `ack` will be sent to all devices, and
# everyone will trun their lights off, and the client will be directed to
# the `someone is coming` screen.
mqtt_req_topic = "letmein2/req"
mqtt_ack_topic = "letmein2/ack"

# Define callback methods which are called when events occur
# pylint: disable=unused-argument, redefined-outer-name
def connect(mqtt_client, userdata, flags, rc):
    # This function will be called when the mqtt_client is connected
    # successfully to the broker.
    print("Connected to MQTT Broker!")
    print("Flags: {0}\n RC: {1}".format(flags, rc))

# This method is called when the mqtt_client disconnects
# from the broker.
def disconnect(mqtt_client, userdata, rc):
    print("Disconnected from MQTT Broker!")

# This method is called when the mqtt_client subscribes to a new feed.
def subscribe(mqtt_client, userdata, topic, granted_qos):
    print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))

# This method is called when the mqtt_client unsubscribes from a feed.
def unsubscribe(mqtt_client, userdata, topic, pid):
    print("Unsubscribed from {0} with PID {1}".format(topic, pid))

# This method is called when the mqtt_client publishes data to a feed.
def publish(mqtt_client, userdata, topic, pid):
    print("Published to {0} with PID {1}".format(topic, pid))

def message(client, topic, message):
    # Method called when a client's subscribed feed has a new value.
    print("New message on topic {0}: {1}".format(topic, message))
    if topic == mqtt_req_topic:
        if message == "level_a":
            level_a.value = 1
        elif message == "level_1":
            level_1.value = 1
        elif message == "s_stairs":
            s_stairs.value = 1
        elif message == "n_stairs":
            n_stairs.value = 1
        elif message == "l_well":
            pass # TODO: install l-well LED
    elif topic == mqtt_ack_topic:
        level_a.value = 0
        level_1.value = 0
        s_stairs.value = 0
        n_stairs.value = 0
        pass # TODO: install l-well LED

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

'''
for topic in topics.values():
    mqtt_client.subscribe(topic)
'''
mqtt_client.subscribe(mqtt_req_topic)
mqtt_client.subscribe(mqtt_ack_topic)

# We're good to go
print("Ready.")

# Main loop
while True:

    # Checks for updates
    mqtt_client.loop()

#    s_stairs.value = ack.value
    if ack.value:
        location="usercenter"
        mqtt_client.publish(mqtt_ack_topic, f"{location}")
        s_stairs.value = 0
        n_stairs.value = 0
        level_a.value = 0
        level_1.value = 0
        # well_l.value = 0 # TODO: install l well led

