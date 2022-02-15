import time, gc, os
import adafruit_dotstar
import board
import feathers2
import digitalio
import wifi
import socketpool
import ssl # TODO: Use this
import adafruit_minimqtt.adafruit_minimqtt as MQTT

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
print("\nCSH LetMeIn! v2.0alpha1")

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

# === EM QUEUE TEE TEE ===

### Code ###

my_feed = "usercenter/feed/s_stairs"

# Define callback methods which are called when events occur
# pylint: disable=unused-argument, redefined-outer-name
def connected(client, userdata, flags, rc):
    # This function will be called when the client is connected
    # successfully to the broker.
    print("Connected to Broker!")
    # Subscribe to all changes on the onoff_feed.
    client.subscribe(my_feed)


def disconnected(client, userdata, rc):
    # This method is called when the client is disconnected
    print("Disconnected from Broker!")

def message(client, topic, message):
    # This method is called when a topic the client is subscribed to
    # has a new message.
    print("New message on topic {0}: {1}".format(topic, message))


# Create a socket pool
pool = socketpool.SocketPool(wifi.radio)

# Set up a MiniMQTT Client
mqtt_client = MQTT.MQTT(
    broker=secrets["broker"],
    port=secrets["port"],
    username=secrets["username"],
    password=secrets["key"],
    socket_pool=pool,
    ssl_context=ssl.create_default_context(),
)

# Setup the callback methods above
mqtt_client.on_connect = connected
mqtt_client.on_disconnect = disconnected
mqtt_client.on_message = message

# Connect the client to the MQTT broker.
print("Connecting to Adafruit IO...")
mqtt_client.connect()

while True:
    # Poll the message queue
    mqtt_client.loop()

    # Send a new message
    print("Sending message...")
    mqtt_client.publish(test_topic, "ligma")
    print("Sent!")
    time.sleep(5)
'''
# Main loop
while True:

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
'''
