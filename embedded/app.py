import asyncio
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from gpio import *

class App:
    def __init__(self, jingle):
        # Set up MQTT Client
        mqtt_client = MQTT.MQTT(
            broker=secrets["broker"],
            port=secrets["port"],
            socket_pool=pool,
            ssl_context=ssl.create_default_context(),
        )
        mqtt_client.on_message = self.message

        print("Attempting to connect to %s" % mqtt_client.broker)
        mqtt_client.connect()
        mqtt_client.subscribe(mqtt_req_topic)
        mqtt_client.subscribe(mqtt_ack_topic)
        mqtt_client.subscribe(mqtt_nvm_topic)
        mqtt_client.subscribe(mqtt_timeout_topic)

        self.mqtt_client = mqtt_client
        self.jingle = jingle

    async def run(self):
        asyncio.run(self.loop())

    async def loop(self):
        # Jingle + ASCII art to let the user know the board is ready to go
        await self.jingle.ready()
        art_ready()
        check_ack_task = asyncio.create_task(check_ack())
        check_jingle_task = asyncio.create_task(check_jingle())
        check_mqtt_task = asyncio.create_task(check_mqtt())
        await asyncio.gather(check_ack_task, check_jingle_task, check_mqtt_task)

    async def check_mqtt(self):
        while True:
            if self.jingle.buzzer.is_off():
                self.mqtt_client.loop()
            await asyncio.sleep(1)

    async def check_ack(self):
        while True:
            if ack.value:
                self.mqtt_client.publish(mqtt_ack_topic, f"{secrets['location']}")
                self.jingle.buzzer.off()
                all_off()
            await asyncio.sleep(0.5)

    async def check_jingle(self):
        while True:
            if self.jingle.buzzer.is_off():
                if s_stairs.value:
                    await self.jingle.s_stairs()
                    continue
                if n_stairs.value:
                    await self.jingle.n_stairs()
                    continue
                if level_a.value:
                    await self.jingle.level_a()
                    continue
                if level_1.value:
                    await self.jingle.level_1()
                    continue
                if l_well.value:
                    await self.jingle.l_well()
                    continue
            await asyncio.sleep(1)

    def message(self, client, topic, message):
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
            self.jingle.buzzer.off()
            level_a.value = 0
            level_1.value = 0
            s_stairs.value = 0
            n_stairs.value = 0
            l_well.value = 0
        elif topic == mqtt_timeout_topic:
            self.jingle.buzzer.off()
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
            self.jingle.buzzer.off()
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

