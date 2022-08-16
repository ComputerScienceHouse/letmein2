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

    async def n_stairs(self):
        self.buzzer.on()
        for x in range(0, 2):
            self.buzzer.note("C4")
            await asyncio.delay(0.2)
            self.buzzer.note("F4")
            await asyncio.delay(0.2)
            self.buzzer.note("C4")
            await asyncio.delay(0.2)
            self.buzzer.note("A4")
            await asyncio.delay(0.2)
        self.buzzer.note("C5")
        await asyncio.delay(0.4)
        self.buzzer.note("B4")
        await asyncio.delay(0.1)
        self.buzzer.note("A4")
        await asyncio.delay(0.1)
        self.buzzer.note("G4")
        await asyncio.delay(0.1)
        self.buzzer.note("F4")
        await asyncio.delay(0.2)
        self.buzzer.off()
