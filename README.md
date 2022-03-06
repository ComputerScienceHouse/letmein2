To subscribe to a device answering, use this:

`mosquitto_sub -h mqtt.csh.rit.edu -t letmeinv2/ack -t letmeinv2/req`

To run the container with mapped resources (for hacking), use this.
`podman run --rm -it -v static:/static -v templates:/templates -p 8080:8080 letmein-site:latest`
