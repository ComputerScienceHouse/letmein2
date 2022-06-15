import time
from secrets import *
from gpio import *
from jingles import *

class LMIApp:
    def __init__(self, buzz, mqtt_client):
        self.buzz        = buzz
        self.mqtt_client = mqtt_client
        self.stfu_counter = 0
        light_show()

    async def check_ack(self):
        if ack.value:
            self.buzz.off() # First and foremost, turn off the speaker. Shit's annoying.
            self.mqtt_client.publish(mqtt_ack_topic, f"{secrets['location']}")
            all_off()
            await asynccp.delay(0.1)

    async def check_req(self):
        if not led_stfu.value and self.buzz.is_off():
            if s_stairs.value:
                await self.buzz.jingle_s_stairs()
            elif n_stairs.value:
                await self.buzz.jingle_n_stairs()
            elif level_a.value:
                await self.buzz.jingle_level_a()
            elif level_1.value:
                await self.buzz.jingle_level_1()
            elif l_well.value:
                await self.buzz.jingle_l_well()
        else:
            all_off()

    async def check_mqtt(self):
        self.mqtt_client.loop() # I guess we have to poll. Fuck this.

    async def check_stfu(self):
        if stfu.value:
            if led_stfu.value:
                self.stfu_counter = 0
                self.mqtt_client.subscribe(mqtt_req_topic)
            else:
                self.stfu_counter = stfu_duration_minutes * 60 # Scale the counter to seconds (since the counter counts down once per second)
                self.mqtt_client.unsubscribe(mqtt_req_topic)
            led_stfu.value = not led_stfu.value # We're gonna use the LED to keep track of the status b/c we're goblins.
            print(f"SHUT THE FUCK UP MODE = {led_stfu.value}")
            print(f"stfu_counter = {self.stfu_counter}")
            time.sleep(0.1)
    
    async def stfu_decay(self):
        if self.stfu_counter > 0:
            self.stfu_counter -= 1
            print(f"stfu_counter = {self.stfu_counter}")
        else:
            led_stfu.value = 0
            self.mqtt_client.subscribe(mqtt_req_topic)
