To subscribe to a device answering, use this:

`mosquitto_sub -h mqtt.csh.rit.edu -t letmeinv2/ack -t letmeinv2/req`

To run the container with mapped resources (for hacking), use this.
`podman run --rm -it -v static:/static -v templates:/templates -p 8080:8080 letmein-site:latest`


## How it works

MQTT Topics. One for requesting, one for acknowledging.
The deal is that whenever someone needs to be let in, she'll hit the
button on the website, which will publish to `req` with the name of their
door. The µController will get this message and turn on the corresponding LED.
When a µController hits their button, they'll publish to `ack`, which everyone
is subscribed to. For now, any message on `ack` will be sent to all devices, and
everyone will trun their lights off, and the client will be directed to
the `someone is coming` screen.
