import asyncio
from gpio import *
from secrets import *
from art import art_ready

class App:
    def __init__(self, mqtt_client, jingle):
        self.mqtt_client = mqtt_client
        self.jingle = jingle
        self.stfu_counter = 0

        self.mqtt_client.on_message = self.message

    def launch(self):
        asyncio.run(self.run())

    async def run(self):
        # Jingle + ASCII art to let the user know the board is ready to go
        # Fancy :)
        sound_ready_task = asyncio.create_task(self.jingle.play("ready.jingle"))
        light_show_task = asyncio.create_task(light_show())
        await asyncio.gather(sound_ready_task, light_show_task)
        art_ready()
        check_ack_task = asyncio.create_task(self.check_ack())
        check_jingle_task = asyncio.create_task(self.check_jingle())
        check_mqtt_task = asyncio.create_task(self.check_mqtt())
        check_stfu_task = asyncio.create_task(self.check_stfu())
        stfu_decay_task = asyncio.create_task(self.stfu_decay())
        await asyncio.gather(
            check_ack_task,
            check_jingle_task,
            check_mqtt_task,
            check_stfu_task,
            stfu_decay_task
        )

    # Run MQTT transactions
    async def check_mqtt(self):
        while True:
            if self.jingle.buzzer.is_off():
                self.mqtt_client.loop()
            await asyncio.sleep(1)

    # See if the button is being pressed
    async def check_ack(self):
        while True:
            if ack.value:
                self.mqtt_client.publish(mqtt_ack_topic, f"{secrets['location']}")
                self.jingle.buzzer.off()
                all_off()
            await asyncio.sleep(0.5)

    async def check_stfu(self):
        while True:
            if stfu.value:
                if led_stfu.value:
                    self.stfu_counter = 0
                    self.mqtt_client.subscribe(mqtt_req_topic)
                else:
                    # Scale the counter to seconds (since the counter counts down once per second-ish)
                    # FIXME (willnilges): I think each tick is a bit longer than a second so keep that
                    # in mind when you're setting duration 
                    self.stfu_counter = stfu_duration_minutes * 60
                    self.mqtt_client.unsubscribe(mqtt_req_topic)
                # We're gonna use the LED to keep track of the status b/c we're goblins.
                led_stfu.value = not led_stfu.value
            await asyncio.sleep(0.5)

    async def stfu_decay(self):
        while True:
            if led_stfu.value:
                if self.stfu_counter > 0:
                    self.stfu_counter -= 1
                    print(f"stfu_counter = {self.stfu_counter}")
                else:
                    led_stfu.value = 0
                    self.mqtt_client.subscribe(mqtt_req_topic)
            await asyncio.sleep(1)

    # Check if we should be playing music, and play music if so
    async def check_jingle(self):
        while True:
            if self.jingle.buzzer.is_off():
                # Probably has a bug: If one light is playing its jingle, then
                # another higher up on this list lights up, it'll switch songs
                # to the new light. 
                if s_stairs.value:
                    await self.jingle.play("s_stairs.jingle")
                elif n_stairs.value:
                    await self.jingle.play("n_stairs.jingle")
                elif level_a.value:
                    await self.jingle.play("level_a.jingle")
                elif level_1.value:
                    await self.jingle.play("song_of_storms.jingle") # level_1
                elif l_well.value:
                    await self.jingle.play("song_of_healing.jingle") # l_well
            await asyncio.sleep(1)

    # MQTT message handler
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
            all_off()
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


