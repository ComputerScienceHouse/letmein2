# LetMeIn v2 <img src="https://forthebadge.com/images/badges/you-didnt-ask-for-this.svg" alt="ohio badge" height="30px"/>

<!-- <img src="https://csh.rit.edu/~wilnil/storage/of-ohioan-descent.svg" alt="ohio badge" height="30px"/>  -->

<img src="https://forthebadge.com/images/badges/0-percent-optimized.svg" alt="0 badge" height="30px"/> <img src="https://forthebadge.com/images/badges/made-with-go.svg" alt="GO badge" height="30px"/> <img src="https://forthebadge.com/images/badges/made-with-python.svg" alt="Python badge" height="30px"/>

Original Project: https://github.com/nfatkhiyev/letMeIn/

LetMeIn2 is a completely new re-write of LetMeIn that focuses on scalability and maintainability, while keeping cost-per-unit as low as possible. Current development uses the [Tiny S2](https://www.adafruit.com/product/5029) to reduce costs.

<img src="https://user-images.githubusercontent.com/42927786/175322711-ea0d8880-9d07-4e7d-a05b-ac3031fbf712.jpg" width="40%" height="40%"/>


## How it works

A user, let's say Alice, visits the website, she selects a floor. Her phone POSTs to the server specifying where she is. The server will send an MQTT message on the letmein2/req topic with Alice's location. This will cause all letmein devices on floor to light up and make noise, indicating Alice's location. Alice's phone will redirect her to a waiting screen (/anybody_home) that does another POST request (could be a GET) that waits for the server to give her a 200 response. On the backend, two things could happen: One is that someone on floor could hit one of the buttons and go get her. That causes another MQTT message on the letmein2/ack topic, which answer's Alice's phone with a 200 message, and she's notified that someone is coming for her. The other is that nobody is there to answer the box (or maybe they don't like Alice), and after a set amount of time, the server sends Alice's phone a 408 message, and will send out a timeout message on the letmein2/ack topic.

## Developing

### Terminology

**Server**: The LetMeIn2 server, presumably running in a container on OKD.

**Guest**: The person/device/browser trying to connect to the Server.

**Knock**: Noun/Verb. A request to be let in, or the act of making a request to be let in.

**Client**: The embedded device that subscribes to the `letmein2/req` topic and listens for when a Gurst knocks

### MQTT
To subscribe to the **Server** as a **Client**, use this:
`mosquitto_sub -h mqtt.csh.rit.edu -t letmein2/ack -t letmein2/req`

You could also set up an app like `MQTT Explorer` (Works on Mac and Linux. If you're using Windows, please stop.)

### Server
In production, the **Server** is deployed to OKD.

Check the `/site` directory for instructions on how to run the **Server**.

### Client
Check the `/embedded` directory for instructions on how to work on the **Clients**.

You can use a program like `minicom` to connect a serial console.

### Hardware (As of Prototype 3)

You'll need:

- 5x Through-hole LEDs, any color, I used green. (Something like [this](https://www.digikey.com/en/products/detail/parallax-inc/751-00005/7791465))
- 1x [E-Switch LS085R100F160C1A](https://www.digikey.com/en/products/detail/e-switch/LS085R100F160C1A/1628106) along with an arcade button
- 1x Pushbutton (like, one of those [smol bois](https://www.digikey.com/en/products/detail/sparkfun-electronics/PRT-14460/7915747))
- 1x [Piezo Buzzer](https://www.digikey.com/en/products/detail/db-unlimited/TP134005-1/9990672)
- 1x [Tiny S2](https://www.digikey.com/en/products/detail/adafruit-industries-llc/5029/14307381?s=N4IgTCBcDaICoEsB2BPAyhAugXyA)

For the LED connectors:
- 1x 10 2.54mm pitch Position Header
- 1x 10 2.54mm pitch Position Header (male)

_This connector sucks. You should only need six headers to make the thing work. I hooked five of them up to GND when I was young and reckless._

Optional:
- 5x 680 ohm resistors for the LEDs (if you need to dim them)

If you'd like to socket your TinyS2, use these:
- 1x [11 Position Header](https://www.digikey.com/en/products/detail/sullins-connector-solutions/PPTC111LFBN-RC/810150?s=N4IgTCBcDaIApwCoGECM6AyAxAQgOQFoAlZEAXQF8g)
- 1x [12 Position Header](https://www.digikey.com/en/products/detail/sullins-connector-solutions/PPTC121LFBN-RC/807231)


Connect the button switch to COM and NO so that when the switch is closed, the circuit is completed and the button press is registered.

## Web API

### `/`
Returns the homepage

### `/session_info` (obsolete)
Returns any relevant info that a client should be aware of. Currently only returns the current timeout period of the server.

### `/request/:location` (obsolete)
Prompts a server to publish a request for a particular door.

### `/nvm` (obsolete)
Cancels a request that a client sends to the server.
<!--See the MVP issue for more info on this.-->

### `/anybody_home/:location` (obsolete)
Awaits an answer to a request made via the `/request/:location` route.

### `/knock/socket/:location`
Prompts a server to set up a "KnockSession" (not a real thing) that publishes a request on the MQTT network and opens a websocket connection with the client

## MQTT API

### `letmein2/req`
A topic meant for sending requests to the LetMeIn network. The payload should be a location that is registered in the app. The app should have a `location_map` defined. That looks like this:

```Go
var location_map = map[string]string{
	"n_stairs": "North Side Stairwell",
	"s_stairs": "South Side Stairwell",
	"level_a":  "Level A Elevator Lobby",
	"level_1":  "Level 1 Elevator Lobby",
	"l_well":   "L Well",
}
```

So, for example, you could publish on topic `letmein2/req` with payload `level_1` to indicate to the devices that you're waiting to be let in on the NRH Level 1 Elevator Lobby. 

### `letmein2/ack`
A topic meant for letting **Clients** acknowledge a **Knock**. The payload should be the location/ID of the device acknowledging. These aren't in a database anywhere, but they ought to be.

Here's an example that isn't real. We'll probably need this later anyway.

```Go
var clientMap = map[string]string {
    "usercenter": "User Center",
    "lounge": "Lounge",
    "luser": "Luser Center",
    "software": "Software Room",
    "server": "Server Room"
}
```

For example, you could publish on `letmein2/ack` with payload `usercenter` to let a waiting **Guest** know that you've heard their **Knock** and are coming to let them in.

### `letmein2/nvm`
A topic for notifying all **Clients** that a **Knock** is being cancelled. The payload should be a location from the above `location_map`.

If you publish on topic `letmein2/nvm` with payload `s_stairs`, that indicates that any pending **Knock** originating from the South Side Stairwell should be ignored (and that **Clients** should turn their lights/sound off!)