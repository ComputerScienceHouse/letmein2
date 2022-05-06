FROM docker.io/golang:1.17.8-bullseye as builder

WORKDIR /build
COPY go.mod go.sum *.go .
RUN go mod tidy
RUN CGO_ENABLED=0 GOOS=linux go build -a -o letmein2 .

FROM alpine:3.15.0

COPY --from=builder /build/letmein2 .
COPY ./templates ./templates
COPY ./static ./static
ENV GOOGLE_APPLICATION_CREDENTIALS=/static/coral-antonym-327500-492da8519a6c.json
ENTRYPOINT ["./letmein2"]
