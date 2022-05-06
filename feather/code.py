import time, gc, os
import board
import tinys2
import digitalio
import wifi
import socketpool
import ssl
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import ipaddress
import adafruit_requests
import asynccp

from secrets import secrets
from buzzer import Buzzer
from jingles import *
from LMIApp import LMIApp

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
print('    -- =- CSH LetMeIn! v2.0alpha2 -= --\n')

# Show available memory
print('Memory Info - gc.mem_free()')
print('---------------------------')
print(f'{gc.mem_free()} Bytes\n')

# Show flash size
flash = os.statvfs('/')
flash_size = flash[0] * flash[2]
flash_free = flash[0] * flash[3]
print("Flash - os.statvfs('/')")
print('---------------------------')
print(f"Size: {flash_size} Bytes\nFree: {flash_free} Bytes\n")

# Set location of this device
location = secrets["location"]
if location == '':
    print('Location not set! Please set location.')
    exit(1)

# ===== GPIO =====
s_stairs = digitalio.DigitalInOut(board.IO0)
n_stairs = digitalio.DigitalInOut(board.IO18)
level_a = digitalio.DigitalInOut(board.IO17)
level_1 = digitalio.DigitalInOut(board.IO7)
l_well = digitalio.DigitalInOut(board.IO6)

s_stairs.direction = digitalio.Direction.OUTPUT
level_1.direction = digitalio.Direction.OUTPUT
level_a.direction = digitalio.Direction.OUTPUT
n_stairs.direction = digitalio.Direction.OUTPUT
l_well.direction = digitalio.Direction.OUTPUT

# Button for acking requests
ack = digitalio.DigitalInOut(board.IO33)
ack.direction = digitalio.Direction.INPUT
ack.pull = digitalio.Pull.DOWN

# Play a little boot jingle to indicate startup
buzz = Buzzer(board.IO4)
buzz.boot()

# ===== WIFI =====
print(f'Connecting to {secrets["ssid"]}')
print('mac address:', "%02x:%02x:%02x:%02x:%02x:%02x" % tuple(map(int, wifi.radio.mac_address)))
wifi.radio.connect(secrets['ssid'], secrets['password'])
print(f'Connected to {secrets["ssid"]}!')

# MQTT topics
mqtt_req_topic = "letmein2/req"
mqtt_ack_topic = "letmein2/ack"

# MQTT callbacks
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
            l_well.value = 1
    elif topic == mqtt_ack_topic:
        level_a.value = 0
        level_1.value = 0
        s_stairs.value = 0
        n_stairs.value = 0
        l_well.value = 0
    
# Create a socket pool
pool = socketpool.SocketPool(wifi.radio)

# Set up MQTT Client
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

mqtt_client.subscribe(mqtt_req_topic)
mqtt_client.subscribe(mqtt_ack_topic)

# Jingle to let the user know the board is ready to go
ready_jingle(buzz)

# We're good to go
print('''

     /$$$$$$$                            /$$
    | $$__  $$                          | $$
    | $$  \ $$  /$$$$$$   /$$$$$$   /$$$$$$$ /$$   /$$
    | $$$$$$$/ /$$__  $$ |____  $$ /$$__  $$| $$  | $$
    | $$__  $$| $$$$$$$$  /$$$$$$$| $$  | $$| $$  | $$
    | $$  \ $$| $$_____/ /$$__  $$| $$  | $$| $$  | $$
    | $$  | $$|  $$$$$$$|  $$$$$$$|  $$$$$$$|  $$$$$$$ /$$
    |__/  |__/ \_______/ \_______/ \_______/ \____  $$|__/
                                             /$$  | $$
                                            |  $$$$$$/
                                             \______/

''')

def main():
    app = LMIApp()

    asynccp.schedule(frequency=80, coroutine_function=app.check_ack)
    asynccp.schedule(frequency=10, coroutine_function=app.check_req)
    asynccp.schedule(frequency=80, coroutine_function=app.check_mqtt)
    asynccp.run()

if __name__ == '__main__':
    main()
