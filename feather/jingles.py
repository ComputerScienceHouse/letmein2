import pulseio
import asynccp
import time
from buzzer import Buzzer

class Jingle(Buzzer):
    def jingle_boot(self):
        self.on()
        self.note("C4")
        time.sleep(0.1)
        self.note("F4")
        time.sleep(0.2)
        self.off()

    def jingle_ready(self):
        self.on()
        self.note("C4")
        time.sleep(0.1)
        self.note("D4")
        time.sleep(0.1)
        self.note("E4")
        time.sleep(0.1)
        self.note("F4")
        time.sleep(0.1)
        self.note("G4")
        time.sleep(0.1)
        self.note("A4")
        time.sleep(0.1)
        self.note("B4")
        time.sleep(0.1)
        self.note("C5")
        time.sleep(0.2)
        self.off()

    async def jingle_s_stairs(self):
        self.on()
        self.note("C5")
        await asynccp.delay(0.2)
        self.note("F4")
        await asynccp.delay(1.0)
        self.note("C5")
        await asynccp.delay(0.2)
        self.note("F4")
        await asynccp.delay(0.2)
        self.note("G4")
        await asynccp.delay(1.0)
        self.note("C5")
        await asynccp.delay(2.0)
        self.off()

    async def jingle_n_stairs(self):
        self.on()
        for x in range(0, 2):
            self.note("C4")
            await asynccp.delay(0.2)
            self.note("F4")
            await asynccp.delay(0.2)
            self.note("C4")
            await asynccp.delay(0.2)
            self.note("A4")
            await asynccp.delay(0.2)
        self.note("C5")
        await asynccp.delay(0.4)
        self.note("B4")
        await asynccp.delay(0.1)
        self.note("A4")
        await asynccp.delay(0.1)
        self.note("G4")
        await asynccp.delay(0.1)
        self.note("F4")
        await asynccp.delay(0.2)
        self.off()

    async def jingle_level_a(self):
        self.on()
        for i in range(0, 3):
            self.hz(659)
            await asynccp.delay(0.1)
            self.hz(587)
            await asynccp.delay(0.1)
        self.note("C4")
        await asynccp.delay(0.3)
        self.note("D4")
        await asynccp.delay(0.5)
        self.off()