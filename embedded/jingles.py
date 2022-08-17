import asyncio, time
from buzzer import Buzzer

class Jingle:
    def __init__(self, pin):
        self.buzzer = Buzzer(pin)

    async def boot(self):
        self.buzzer.on()
        self.buzzer.note("C4")
        await asyncio.sleep(0.1)
        self.buzzer.note("F4")
        await asyncio.sleep(0.2)
        self.buzzer.off()

    def boot_sync(self):
        self.buzzer.on()
        self.buzzer.note("C4")
        time.sleep(0.1)
        self.buzzer.note("F4")
        time.sleep(0.2)
        self.buzzer.off()

    async def ready(self):
        self.buzzer.on()
        self.buzzer.note("C4")
        await asyncio.sleep(0.1)
        self.buzzer.note("D4")
        await asyncio.sleep(0.1)
        self.buzzer.note("E4")
        await asyncio.sleep(0.1)
        self.buzzer.note("F4")
        await asyncio.sleep(0.1)
        self.buzzer.note("G4")
        await asyncio.sleep(0.1)
        self.buzzer.note("A4")
        await asyncio.sleep(0.1)
        self.buzzer.note("B4")
        await asyncio.sleep(0.1)
        self.buzzer.note("C5")
        await asyncio.sleep(0.2)
        self.buzzer.off()

    async def s_stairs(self):
        self.buzzer.on()
        self.buzzer.note("C5")
        await asyncio.sleep(0.2)
        self.buzzer.note("F4")
        await asyncio.sleep(0.4)
        self.buzzer.off()
        time.sleep(0.2)
        self.buzzer.on()
        self.buzzer.note("C5")
        await asyncio.sleep(0.2)
        self.buzzer.note("F4")
        await asyncio.sleep(0.2)
        self.buzzer.note("G4")
        await asyncio.sleep(0.2)
        self.buzzer.note("C5")
        await asyncio.sleep(1.0)
        self.buzzer.off()

    async def n_stairs(self):
        self.buzzer.on()
        for x in range(0, 2):
            self.buzzer.note("C4")
            await asyncio.sleep(0.2)
            self.buzzer.note("F4")
            await asyncio.sleep(0.2)
            self.buzzer.note("C4")
            await asyncio.sleep(0.2)
            self.buzzer.note("A4")
            await asyncio.sleep(0.2)
        self.buzzer.note("C5")
        await asyncio.sleep(0.4)
        self.buzzer.note("B4")
        await asyncio.sleep(0.1)
        self.buzzer.note("A4")
        await asyncio.sleep(0.1)
        self.buzzer.note("G4")
        await asyncio.sleep(0.1)
        self.buzzer.note("F4")
        await asyncio.sleep(0.2)
        self.buzzer.off()

    async def level_a(self):
        self.buzzer.on()
        for i in range(0, 3):
            self.buzzer.hz(659)
            await asyncio.sleep(0.1)
            self.buzzer.hz(587)
            await asyncio.sleep(0.1)
            self.buzzer.note("C4")
            await asyncio.sleep(0.3)
        self.buzzer.note("C4")
        await asyncio.sleep(0.3)
        self.buzzer.note("F4")
        await asyncio.sleep(0.5)
        self.buzzer.off()

    async def level_1(self):
        self.buzzer.on()
        for i in range(0,2):
            self.buzzer.note("E4")
            await asyncio.sleep(0.1)
            self.buzzer.hz(800)
            await asyncio.sleep(0.5)
            self.buzzer.note("D4")
            await asyncio.sleep(0.1)
        self.buzzer.hz(1200)
        await asyncio.sleep(0.5)
        self.buzzer.off()

    async def l_well(self):
        self.buzzer.on()
        self.buzzer.note("A4")
        await asyncio.sleep(0.3)
        self.buzzer.note("B4")
        await asyncio.sleep(0.5)
        self.buzzer.note("A4")
        await asyncio.sleep(0.5)
        self.buzzer.note("E4")
        await asyncio.sleep(0.5)
        self.buzzer.note("B4")
        await asyncio.sleep(0.5)
        self.buzzer.hz(1000)
        await asyncio.sleep(0.5)
        self.buzzer.off()

