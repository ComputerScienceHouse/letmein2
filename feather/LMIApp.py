class LMIApp:
    def __init__(self):
        pass

    async def check_ack(self):
        if ack.value:
            buzz.off() # First and foremost, turn off the speaker. Shit's annoying.
            mqtt_client.publish(mqtt_ack_topic, f"{location}")
            s_stairs.value = 0
            n_stairs.value = 0
            level_a.value = 0
            level_1.value = 0
            l_well.value = 0
            await asynccp.delay(0.1)

    async def check_req(self):
        if s_stairs.value and buzz.is_off():
            await south_stairs_jingle(buzz)
        elif n_stairs.value and buzz.is_off():
            await north_stairs_jingle(buzz)
        elif level_a.value and buzz.is_off():
            buzz.on()
            for i in range(0, 3):
                buzz.hz(659)
                await asynccp.delay(0.1)
                buzz.hz(587)
                await asynccp.delay(0.1)
            buzz.note("C4")
            await asynccp.delay(0.3)
            buzz.note("D4")
            await asynccp.delay(0.5)
            buzz.off()

    async def check_mqtt(self):
        mqtt_client.loop() # I guess we have to poll. Fuck this.