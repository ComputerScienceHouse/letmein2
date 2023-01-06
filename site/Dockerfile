FROM docker.io/golang:1.18 as builder

WORKDIR /build
COPY go.mod go.sum *.go ./
RUN go get -d .
RUN CGO_ENABLED=0 GOOS=linux go build -a -o letmein2 .

FROM alpine:latest

WORKDIR /

COPY --from=builder /build/letmein2 ./
COPY ./templates ./templates
COPY ./static ./static
ENTRYPOINT ["./letmein2"]
