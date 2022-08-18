import board, digitalio, time
import asyncio

s_stairs = digitalio.DigitalInOut(board.IO0)
n_stairs = digitalio.DigitalInOut(board.IO18)
level_a = digitalio.DigitalInOut(board.IO17)
level_1 = digitalio.DigitalInOut(board.IO7)
l_well = digitalio.DigitalInOut(board.IO6)

s_stairs.direction = digitalio.Direction.OUTPUT
level_1.direction = digitalio.Direction.OUTPUT
level_a.direction = digitalio.Direction.OUTPUT
n_stairs.direction = digitalio.Direction.OUTPUT
l_well.direction = digitalio.Direction.OUTPUT

# Button for acknowledging requests
ack = digitalio.DigitalInOut(board.IO33)
ack.direction = digitalio.Direction.INPUT
ack.pull = digitalio.Pull.DOWN

# Button for telling LetMeIn to shut the fuck up
stfu = digitalio.DigitalInOut(board.IO38)
stfu.direction = digitalio.Direction.INPUT
stfu.pull = digitalio.Pull.DOWN
led_stfu = digitalio.DigitalInOut(board.IO36)
led_stfu.direction = digitalio.Direction.OUTPUT

async def light_show():
    # Flash all the lights to show the idiot is on
    # Making this async is probably excessive
    all_off()
    s_stairs.value = 1
    await asyncio.sleep(0.1)

    all_off()
    n_stairs.value = 1
    await asyncio.sleep(0.1)

    all_off()
    level_a.value = 1
    await asyncio.sleep(0.1)

    all_off()
    level_1.value = 1
    await asyncio.sleep(0.1)

    all_off()
    l_well.value = 1
    await asyncio.sleep(0.1)

    all_off()
    l_well.value = 1
    await asyncio.sleep(0.1)

    all_off()
    level_1.value = 1
    await asyncio.sleep(0.1)

    all_off()
    level_a.value = 1
    await asyncio.sleep(0.1)

    all_off()
    n_stairs.value = 1
    await asyncio.sleep(0.1)

    all_off()
    s_stairs.value = 1
    await asyncio.sleep(0.1)

    all_off()

def all_off():
    s_stairs.value = 0
    n_stairs.value = 0
    level_a.value = 0
    level_1.value = 0
    l_well.value = 0
