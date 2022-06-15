# Website Development
To work on the site, you can either build and run Podman containers, or you can build and run a binary.

## Podman container
1. Fill out a `.env` file using the `.env.template`.
2. Use `build_dev_instance.sh` and `run_dev_instance.sh` to create and run a container.

## Baremetal
The benefit of this is, that because I can't use computers, the container takes a long time to build the binary. This skips all that crap and lets you run manually.

1. Fill out a `.env` file.
3. Use `go build -a -o letmein2 .` to build a binary.
4. `source .env`
5. `./letmein2`
