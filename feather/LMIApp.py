from secrets import *
from gpio import *
from jingles import *

class LMIApp:
    def __init__(self, buzz, ack, mqtt_client):
        self.buzz        = buzz
        self.mqtt_client = mqtt_client
        self.ack         = ack

    async def check_ack(self):
        if self.ack.value:
            self.buzz.off() # First and foremost, turn off the speaker. Shit's annoying.
            self.mqtt_client.publish(mqtt_ack_topic, f"{secrets['location']}")
            s_stairs.value = 0
            n_stairs.value = 0
            level_a.value = 0
            level_1.value = 0
            l_well.value = 0
            await asynccp.delay(0.1)

    async def check_req(self):
        if s_stairs.value and self.buzz.is_off():
            await jingle_s_stairs(self.buzz)
        elif n_stairs.value and self.buzz.is_off():
            await jingle_n_stairs(self.buzz)
        elif level_a.value and self.buzz.is_off():
            await jingle_level_a(self.buzz)

    async def check_mqtt(self):
        self.mqtt_client.loop() # I guess we have to poll. Fuck this.