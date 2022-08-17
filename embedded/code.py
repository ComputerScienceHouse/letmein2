import gc, os, board, tinys2, digitalio, wifi, socketpool, ssl
from secrets import *
#from gpio import *
from art import *
from jingles import Jingle

def main():
    art_logo()
    art_mem_info()
    jingle = Jingle(board.IO4)
    jingle.boot_sync() # Play a lil' tune to indicate that the device is alive.
    # Set location of this device
    location = secrets["location"]
    if location == '':
        print('Location not set! Please set location.')
        exit(1)

    # ===== WIFI =====
    print(f'Connecting to {secrets["ssid"]}')
    print('mac address:', "%02x:%02x:%02x:%02x:%02x:%02x" % tuple(map(int, wifi.radio.mac_address)))
    wifi.radio.connect(secrets['ssid'], secrets['password'])
    print(f'Connected to {secrets["ssid"]}!')
    pool = socketpool.SocketPool(wifi.radio) # Create a socket pool

    # ===== THE APP ====
    app = App(jingle)
    app.run()

if __name__ == '__main__':
    main()
