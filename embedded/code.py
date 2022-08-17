import gc, os, board, tinys2, digitalio, wifi, socketpool, ssl
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from secrets import *
from art import art_logo, art_mem_info
from jingles import Jingle
from app import App

def main():
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

    print("Attempting to connect to %s" % mqtt_client.broker)
    mqtt_client.connect()
    mqtt_client.subscribe(mqtt_req_topic)
    mqtt_client.subscribe(mqtt_ack_topic)
    mqtt_client.subscribe(mqtt_nvm_topic)
    mqtt_client.subscribe(mqtt_timeout_topic)

    app = App(mqtt_client, jingle)
    app.launch()

if __name__ == '__main__':
    main()

