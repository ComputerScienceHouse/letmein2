import usocketio.client
import logging
from secrets import secrets
import network
import machine

logging.basicConfig(level=logging.DEBUG)

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

OUT = machine.Pin.OUT
IN = machine.Pin.IN

s_stairs = machine.Pin(10, OUT)
level_1 = machine.Pin(7, OUT)
level_a = machine.Pin(3, OUT)
n_stairs = machine.Pin(1, OUT)


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

ack = machine.Pin(5, machine.Pin.IN)

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
# Connect to wifi
print("Connecting to %s" % secrets['ssid'])
print("mac address:", "%02x:%02x:%02x:%02x:%02x:%02x" % tuple(map(int, wifi.radio.mac_address)))
sta_if.connect(secrets['ssid'], secrets['password']) # Connect to an AP
while not sta_if.isconnected():
    pass
print("Connected to %s!" % secrets['ssid'])

def activate(loc):
    global active
    while not ack.value() and active[loc]:
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
                socketio.emit('ack',{'data':'Shut up nerd I got u','location':loc,'room':'nrh3'})
                active[loc] = False

        @socketio.on('ack')
        def on_alert(self, data):
            global active
            active[data['location']] = False

        socketio.run_forever()

hello()

