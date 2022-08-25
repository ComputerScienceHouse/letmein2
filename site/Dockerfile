FROM golang:1.18 as builder

WORKDIR /build
COPY * . 
#RUN go mod tidy
RUN go get -d .
RUN CGO_ENABLED=0 GOOS=linux go build -a -o letmein2 .

FROM alpine:latest

WORKDIR site

COPY --from=builder /build/letmein2 .
#RUN mkdir /templates /static
# These lines are duplicated because OKD needs you to explicitly specify `site`
# but to build + test locally, you need it like this.
COPY ./templates ./templates
COPY ./static ./static
#COPY ./templates ./templates
#COPY ./static ./static
ENTRYPOINT ["./letmein2"]
