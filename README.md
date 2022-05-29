# LetMeIn v2

<img src="https://csh.rit.edu/~wilnil/storage/of-ohioan-descent.svg" alt="C badge" height="30px"/>

Original Project: https://github.com/nfatkhiyev/letMeIn/

LetMeIn2 is a completely new re-write of LetMeIn that focuses on scalability and maintainability, while keeping cost-per-unit as low as possible. Current development uses the [Feather S2](https://www.adafruit.com/product/4769), but we are looking at switching to the [Tiny S2](https://www.adafruit.com/product/5029) to reduce costs.

## How it works

A user, let's say Alice, visits the website, she selects a floor. Her phone POSTs to the server specifying where she is. The server will send an MQTT message on the letmein2/req topic with Alice's location. This will cause all letmein devices on floor to light up and make noise, indicating Alice's location. Alice's phone will redirect her to a waiting screen (/anybody_home) that does another POST request (could be a GET) that waits for the server to give her a 200 response. On the backend, two things could happen: One is that someone on floor could hit one of the buttons and go get her. That causes another MQTT message on the letmein2/ack topic, which answer's Alice's phone with a 200 message, and she's notified that someone is coming for her. The other is that nobody is there to answer the box (or maybe they don't like Alice), and after a set amount of time, the server sends Alice's phone a 408 message, and will send out a timeout message on the letmein2/ack topic.

## Developing

To subscribe to a device answering, use this:

`mosquitto_sub -h mqtt.csh.rit.edu -t letmeinv2/ack -t letmeinv2/req`

To run the container with mapped resources (for hacking), use this.
`podman run --rm -it -v ./static:/static -v ./templates:/templates -p 8080:8080 letmein-site:latest`


To program the device:
`cp Code/letmein2/feather/code.py /run/media/wilnil/CIRCUITPY/code.py`

## Libs
You'll need the following to get the board to run


- `adafruit_minimqtt`
- `adafruit_requests`
- `adafruit_ticks`
- `asynccp`
- `asyncio`
- `simpleio`

## Hardware

You'll need:

- 5x Through-hole LEDs, any color, I used green. (Something like [this](https://www.digikey.com/en/products/detail/parallax-inc/751-00005/7791465))
- 1x [E-Switch LS085R100F160C1A](https://www.digikey.com/en/products/detail/e-switch/LS085R100F160C1A/1628106)
    - _Honestly, if I had to do this again, I'd probably buy_ [these](https://www.adafruit.com/product/3489) _next time_
- 1x [Tiny S2](https://www.adafruit.com/product/5029) as the brain
- 1x Pushbutton (like, one of those [smol bois](https://www.digikey.com/en/products/detail/sparkfun-electronics/PRT-14460/7915747))
- 1x [Piezo Buzzer](https://www.digikey.com/en/products/detail/db-unlimited/TP134005-1/9990672)
- 1x [Tiny S2](https://www.digikey.com/en/products/detail/adafruit-industries-llc/5029/14307381?s=N4IgTCBcDaICoEsB2BPAyhAugXyA)

For the LED connectors:
- 1x [10 Position Header](https://www.digikey.com/en/products/detail/sullins-connector-solutions/LPPB101NFFN-RC/1786368)
- 1x [10 Position Header (male)](https://www.digikey.com/en/products/detail/sullins-connector-solutions/GRPB101VWVN-RC/1786446)


Optional:
- 5x 680 ohm resistors for the LEDs (if you need to dim them)

If you'd like to socket your TinyS2, use these:
- 1x [11 Position Header](https://www.digikey.com/en/products/detail/sullins-connector-solutions/PPTC111LFBN-RC/810150?s=N4IgTCBcDaIApwCoGECM6AyAxAQgOQFoAlZEAXQF8g)
- 1x [12 Position Header](https://www.digikey.com/en/products/detail/sullins-connector-solutions/PPTC121LFBN-RC/807231)


Connect the button switch to COM and NO so that when the switch is closed, the circuit is completed and the button press is registered.
