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

    async def play(self, file):
        with open(file) as jingle_file:
            self.buzzer.on()
            for action in jingle_file:
                action_split = action.split('#', 1)[0].split(' ', 1)
                note = action_split[0]
                duration = float(action_split[1])
                # FIXME (willnilges): This code is probably slow.
                if "rest" in note:
                    # Turn off the buzzer for a specified period
                    self.buzzer.off()
                    time.sleep(duration)
                    self.buzzer.on()
                elif note.isdigit():
                    # Try playing as hz    
                    hz = int(note)
                    self.buzzer.hz(hz)
                    await asyncio.sleep(duration)
                else:
                    # play a specified note
                    self.buzzer.note(note)
                    await asyncio.sleep(duration)
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

