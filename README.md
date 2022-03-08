# LetMeIn v2

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
