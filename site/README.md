# Website Development
To work on the site, you can either build and run Podman containers, or you can build and run a binary.

## Podman container
1. `build_dev_instance.sh`
2.  Copy `.env.template` to `.env.container` and fill it out
3. `run_dev_instance.sh`

## Temporary HTTPS certification
For the Slack request URL, it is necessary to have an HTTPS connection. For this you can use `ngrok`:
1. Download the `ngrok` package
2. Run `ngrok http 8080` in a `screen` session, or in a terminal window
3. Use the Forwarding URL (something like `https://<#####>.ngrok.io`) to access the local instance

The Forwarding URL + `/actions` is now the Slack request URL as well.

<!--
## Baremetal
The benefit of this is, that because I can't use computers, the container takes a long time to build the binary. This skips all that crap and lets you run manually.

1. Fill out a `.env` file.
2. Use `go build -a -o letmein2 .` to build a binary.
3. `source .env`
4. `./letmein2`
-->
