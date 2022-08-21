FROM golang:1.18 as builder

WORKDIR /build
COPY * . 
#RUN go mod tidy
RUN go get -d .
RUN CGO_ENABLED=0 GOOS=linux go build -a -o letmein2 .

FROM alpine:latest

WORKDIR /

COPY --from=builder /build/letmein2 .
#RUN mkdir /templates /static
COPY ./site/templates ./templates
COPY ./site/static ./static
ENTRYPOINT ["./letmein2"]
