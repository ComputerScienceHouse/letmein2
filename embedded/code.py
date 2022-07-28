import time, gc, os, board, tinys2, digitalio, wifi, socketpool, ssl, adafruit_minimqtt.adafruit_minimqtt as MQTT, ipaddress, adafruit_requests, asynccp
from secrets import *
from gpio import *
from jingles import Jingle
from art import *
from LMIApp import LMIApp

art_logo()
art_mem_info()

def main():
    # Set location of this device
    location = secrets["location"]
    if location == '':
        print('Location not set! Please set location.')
        exit(1)

    # Play a little boot jingle to indicate startup
    buzz = Jingle(board.IO4)
    buzz.jingle_boot()

    # ===== WIFI =====
    print(f'Connecting to {secrets["ssid"]}')
    print('mac address:', "%02x:%02x:%02x:%02x:%02x:%02x" % tuple(map(int, wifi.radio.mac_address)))
    wifi.radio.connect(secrets['ssid'], secrets['password'])
    print(f'Connected to {secrets["ssid"]}!')
        
    # Create a socket pool
    pool = socketpool.SocketPool(wifi.radio)

    # Set up MQTT Client
    mqtt_client = MQTT.MQTT(
        broker=secrets["broker"],
        port=secrets["port"],
        socket_pool=pool,
        ssl_context=ssl.create_default_context(),
    )

    app = LMIApp(buzz, mqtt_client)

    # Connect callback handlers to mqtt_client. Mostly for debugging.
    # mqtt_client.on_connect = connect
    # mqtt_client.on_disconnect = disconnect
    # mqtt_client.on_subscribe = subscribe
    # mqtt_client.on_unsubscribe = unsubscribe
    # mqtt_client.on_publish = publish
    mqtt_client.on_message = message

    print("Attempting to connect to %s" % mqtt_client.broker)
    mqtt_client.connect()
    mqtt_client.subscribe(mqtt_req_topic)
    mqtt_client.subscribe(mqtt_ack_topic)

    asynccp.schedule(frequency=10, coroutine_function=app.check_ack)
    asynccp.schedule(frequency=10, coroutine_function=app.check_req)
    asynccp.schedule(frequency=10, coroutine_function=app.check_mqtt)
    asynccp.schedule(frequency=10, coroutine_function=app.check_stfu)
    asynccp.schedule(frequency=1, coroutine_function=app.stfu_decay)


    # Jingle + ASCII art to let the user know the board is ready to go
    art_ready()
    buzz.jingle_ready()

    asynccp.run()

# MQTT callbacks (Mostly for debugging)
'''
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
'''

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
    elif topic == mqtt_ack_topic: # Eww, this is cringe. The MQTT client is still subbed so it gets messages and turns on the lights, but then it just turns right back off. Should fix this. IDEA: Sub/Unsub.
        level_a.value = 0
        level_1.value = 0
        s_stairs.value = 0
        n_stairs.value = 0
        l_well.value = 0
    elif topic == mqtt_nvm_topic:
        # TODO: Set up some kind of configurable dingus for this (and other)
        # location-based trees
        if message == "level_a":
            level_a.value = 0
        elif message == "level_1":
            level_1.value = 0
        elif message == "s_stairs":
            s_stairs.value = 0
        elif message == "n_stairs":
            n_stairs.value = 0
        elif message == "l_well":
            l_well.value = 0

if __name__ == '__main__':
    main()
