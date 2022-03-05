import usocketio.client
import logging
from secrets import secrets
import network
import machine
import ubinascii

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
print("mac address:", ubinascii.hexlify(sta_if.config('mac'),':').decode())
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
    with usocketio.client.connect('http://websocket-letmein2websocket.apps.okd4.csh.rit.edu:80/') as socketio:
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

