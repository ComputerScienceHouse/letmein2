import gc, os, board, tinys2, digitalio, wifi, socketpool, ssl
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import asyncio
from secrets import *
from gpio import *
from art import *
from jingles import Jingle

async def run():
    # Jingle + ASCII art to let the user know the board is ready to go
    await jingle.ready()
    art_ready()
    check_ack_task = asyncio.create_task(check_ack())
    check_jingle_task = asyncio.create_task(check_jingle())
    check_mqtt_task = asyncio.create_task(check_mqtt())
    await asyncio.gather(check_ack_task, check_jingle_task, check_mqtt_task)

# Run MQTT transactions
async def check_mqtt():
    while True:
        if jingle.buzzer.is_off():
            mqtt_client.loop()
        await asyncio.sleep(1)

# See if the button is being pressed
async def check_ack():
    while True:
        if ack.value:
            mqtt_client.publish(mqtt_ack_topic, f"{secrets['location']}")
            jingle.buzzer.off()
            all_off()
        await asyncio.sleep(0.5)

# Check if we should be playing music, and play music if so
async def check_jingle():
    while True:
        if jingle.buzzer.is_off():
            # Probably has a bug: If one light is playing its jingle, then
            # another higher up on this list lights up, it'll switch songs
            # to the new light. 
            if s_stairs.value:
                await jingle.s_stairs()
                continue
            elif n_stairs.value:
                await jingle.n_stairs()
            elif level_a.value:
                await jingle.level_a()
            elif level_1.value:
                await jingle.level_1()
            elif l_well.value:
                await jingle.l_well()
        await asyncio.sleep(1)

# MQTT message handler
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
        # FIXME (willnilges): The MQTT client is still subbed so it gets
        # messages and turns on the lights, but then it just turns right
        # back off. Should fix this. IDEA: Sub/Unsub.
        # TODO (willnilges): Perhaps a timeout topic would be nice.
        jingle.buzzer.off()
        level_a.value = 0
        level_1.value = 0
        s_stairs.value = 0
        n_stairs.value = 0
        l_well.value = 0
    elif topic == mqtt_timeout_topic:
        jingle.buzzer.off()
        if "level_a" in message:
            level_a.value = 0
        elif "level_1" in message:
            level_1.value = 0
        elif "s_stairs" in message:
            s_stairs.value = 0
        elif "n_stairs" in message:
            n_stairs.value = 0
        elif "l_well" in message:
            l_well.value = 0
    elif topic == mqtt_nvm_topic:
        # TODO: Set up some kind of configurable dingus for this (and other)
        # location-based trees
        jingle.buzzer.off()
        if "level_a" in message:
            level_a.value = 0
        elif "level_1" in message:
            level_1.value = 0
        elif "s_stairs" in message:
            s_stairs.value = 0
        elif "n_stairs" in message:
            n_stairs.value = 0
        elif "l_well" in message:
            l_well.value = 0

# Class for controlling the speaker and playing music
jingle = Jingle(board.IO4)

# Runs setup, then passes it off to loop()
# Show signs of life
art_logo()
art_mem_info()
jingle.boot_sync()

# Set location of this device
location = secrets["location"]
if location == '':
    print('Location not set! Please set location.')
    exit(1)

# WiFi
print(f'Connecting to {secrets["ssid"]}')
print('mac address:', "%02x:%02x:%02x:%02x:%02x:%02x" % tuple(map(int, wifi.radio.mac_address)))
wifi.radio.connect(secrets['ssid'], secrets['password'])
print(f'Connected to {secrets["ssid"]}!')
pool = socketpool.SocketPool(wifi.radio) # Create a socket pool

# Set up MQTT Client
mqtt_client = MQTT.MQTT(
    broker=secrets["broker"],
    port=secrets["port"],
    socket_pool=pool,
    ssl_context=ssl.create_default_context(),
)

mqtt_client.on_message = message

print("Attempting to connect to %s" % mqtt_client.broker)
mqtt_client.connect()
mqtt_client.subscribe(mqtt_req_topic)
mqtt_client.subscribe(mqtt_ack_topic)
mqtt_client.subscribe(mqtt_nvm_topic)
mqtt_client.subscribe(mqtt_timeout_topic)

asyncio.run(run())


