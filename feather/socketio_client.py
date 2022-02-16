import digitalio
import usocketio.client
import logging
from secrets import secrets
import wifi

logging.basicConfig(level=logging.DEBUG)

# Make sure the 2nd LDO is turned on
feathers2.enable_LDO2(True)

# Create a DotStar instance
dotstar = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.5, auto_write=True)

# Say hello
print('''
'{tttttttttttttttttttttttt^ *tttt
:@@@@@@@@@@@@@@@@@@@@@@@@@m d@@@@N`
:@@@@@@@@@@@@@@@@@@@@@@@@@m d@@@@N`
:@@@@@m:::::::::::::rQ@@@@m d@@@@N`
:@@@@@] vBBBBBBBBBN,`]oooo* d@@@@N`
:@@@@@] o@@@NNNQ@@@"`ueeee| d@@@@N`
:@@@@@] o@@&   ,||?`'Q@@@@m d@@@@N`
:@@@@@] o@@Q]tt{{{z-'Q@@@@QOQ@@@@N`
:@@@@@] o@@@@@@@@@@"'Q@@@@@@@@@@@N`
:@@@@@] ';;;;;;y@@@"'Q@@@@N7Q@@@@N`
:@@@@@] \KKe^^^a@@@"'Q@@@@m d@@@@N`
:@@@@@] o@@@@@@@@@@" _::::' d@@@@N`
:@@@@@] raaaaaaaaay..H####} d@@@@N`
:@@@@@#eeeeeeeeeeeeek@@@@@m d@@@@N`
:@@@@@@@@@@@@@@@@@@@@@@@@@m d@@@@N`
:@@@@@@@@@@@@@@@@@@@@@@@@@e K@@@@W`
 .........................` `....-
''')
print("\nCSH LetMeIn! v2.0alpha1")

# Show available memory
print("Memory Info - gc.mem_free()")
print("---------------------------")
print("{} Bytes\n".format(gc.mem_free()))

flash = os.statvfs('/')
flash_size = flash[0] * flash[2]
flash_free = flash[0] * flash[3]
# Show flash size
print("Flash - os.statvfs('/')")
print("---------------------------")
print("Size: {} Bytes\nFree: {} Bytes\n".format(flash_size, flash_free))

s_stairs = digitalio.DigitalInOut(board.IO10)
level_1 = digitalio.DigitalInOut(board.IO7)
level_a = digitalio.DigitalInOut(board.IO3)
n_stairs = digitalio.DigitalInOut(board.IO1)
s_stairs.direction = digitalio.Direction.OUTPUT
level_1.direction = digitalio.Direction.OUTPUT
level_a.direction = digitalio.Direction.OUTPUT
n_stairs.direction = digitalio.Direction.OUTPUT

active = {
    'nLevel' : False,
    'sLevel' : False,
    'aLevel' : False,
    '1Level' : False,
}

output = {
    'nLevel' : n_stairs,
    'sLevel' : s_stairs,
    'aLevel' : level_1,
    '1Level' : level_a,
}

ack = digitalio.DigitalInOut(board.IO5)
ack.direction = digitalio.Direction.INPUT

# Turn on the internal blue LED
feathers2.led_set(True)

# Connect to wifi
print("Connecting to %s" % secrets['ssid'])
print("mac address:", "%02x:%02x:%02x:%02x:%02x:%02x" % tuple(map(int, wifi.radio.mac_address)))
wifi.radio.connect(secrets['ssid'], secrets['password'])
print("Connected to %s!" % secrets['ssid'])

def activate(loc):
    global active
    while not ack.value and active[loc]:
        output[loc].value = 1
    output[loc].value = 0

def hello():
    with usocketio.client.connect('https://letmein-dev.cs.house') as socketio:
        @socketio.on('letmein')
        def on_message(self, data):
            global active
            loc = data['location']
            active[loc] = True
            print(loc)
            activate(loc)
            if active[loc]:
                socketio.emit('ack',{'data':'Shut up nerd I got u','room':'nrh3'}) 
                active[loc] = False

        @socketio.on('ack')
        def on_alert(self, data):
            global active
            active = False

        socketio.run_forever()

hello()

