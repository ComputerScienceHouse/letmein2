# Website Development
To work on the site, you can either build and run Podman containers, or you can build and run a binary.

## Podman container
1. `build_dev_instance.sh`
2.  Fill out `.env.container` (Created after you run `build_dev_instance.sh`)
3. `run_dev_instance.sh`

## Baremetal
The benefit of this is, that because I can't use computers, the container takes a long time to build the binary. This skips all that crap and lets you run manually.

1. Fill out a `.env` file.
2. Use `go build -a -o letmein2 .` to build a binary.
3. `source .env`
4. `./letmein2`

