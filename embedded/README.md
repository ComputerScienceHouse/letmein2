# LetMeIn2 Firmware for TinyS2
This directory contains all the firwmware and config file templates required to build and enroll a new LetMeIn2 client.

Tested with a TinyS2 running Circuit Python 6.

## Libs
You'll need the following to get the board to run

- [`adafruit_minimqtt`](https://github.com/adafruit/Adafruit_CircuitPython_MiniMQTT)
- [`adafruit_requests`](https://github.com/adafruit/Adafruit_CircuitPython_Requests)
- [`adafruit_ticks`](https://github.com/adafruit/Adafruit_CircuitPython_Ticks)
- [`asynccp`](https://github.com/WarriorOfWire/CircuitPython_async)
<!-- - [`asyncio`]() -->
<!-- - [`simpleio`]() -->

## Installation
- Plug in the client, drag and drop all python files over to it.
- Fetch the libs and place them in a directory called 'lib' on the device
- Copy the `secrets.py.template` file over to the device and fill it out appropriately.

## Developing

To program the device, just copy code over to the device that mounts on your computer when you plug it in:
`cp Code/letmein2/feather/code.py /run/media/wilnil/CIRCUITPY/code.py`