FROM golang as builder

WORKDIR /build
COPY go.mod go.sum *.go . 
#RUN go mod tidy
RUN go get -d .
RUN CGO_ENABLED=0 GOOS=linux go build -a -o letmein2 .

FROM alpine:latest

COPY --from=builder /build/letmein2 .
COPY ./templates ./templates
COPY ./static ./static
ENTRYPOINT ["./letmein2"]
