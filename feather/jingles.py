import pulseio
import asynccp
import time
from buzzer import Buzzer

def ready_jingle(buzz):
    buzz.on()
    buzz.note("C4")
    time.sleep(0.1)
    buzz.note("D4")
    time.sleep(0.1)
    buzz.note("E4")
    time.sleep(0.1)
    buzz.note("F4")
    time.sleep(0.1)
    buzz.note("G4")
    time.sleep(0.1)
    buzz.note("A4")
    time.sleep(0.1)
    buzz.note("B4")
    time.sleep(0.1)
    buzz.note("C5")
    time.sleep(0.2)
    buzz.off()

async def south_stairs_jingle(buzz):
    buzz.on()
    buzz.note("C5")
    await asynccp.delay(0.2)
    buzz.note("F4")
    await asynccp.delay(1.0)
    buzz.note("C5")
    await asynccp.delay(0.2)
    buzz.note("F4")
    await asynccp.delay(0.2)
    buzz.note("G4")
    await asynccp.delay(1.0)
    buzz.note("C5")
    await asynccp.delay(2.0)
    buzz.off()

async def north_stairs_jingle(buzz):
    buzz.on()
    for x in range(0, 2):
        buzz.note("C4")
        await asynccp.delay(0.2)
        buzz.note("F4")
        await asynccp.delay(0.2)
        buzz.note("C4")
        await asynccp.delay(0.2)
        buzz.note("A4")
        await asynccp.delay(0.2)
    buzz.note("C5")
    await asynccp.delay(0.4)
    buzz.note("B4")
    await asynccp.delay(0.1)
    buzz.note("A4")
    await asynccp.delay(0.1)
    buzz.note("G4")
    await asynccp.delay(0.1)
    buzz.note("F4")
    await asynccp.delay(0.2)
    buzz.off()