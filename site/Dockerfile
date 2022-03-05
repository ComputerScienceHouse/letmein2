FROM golang as builder

WORKDIR /build
COPY * . 
RUN go mod tidy
RUN CGO_ENABLED=0 GOOS=linux go build -a -o letmein2 .

FROM alpine:latest

COPY --from=builder /build/letmein2 .
COPY ./templates ./templates
COPY ./static ./static
ENTRYPOINT ["./letmein2"]
