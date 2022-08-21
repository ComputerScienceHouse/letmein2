FROM golang as builder

WORKDIR /build
COPY go.mod go.sum *.go . 
#RUN go mod tidy
RUN go get -d .
RUN CGO_ENABLED=0 GOOS=linux go build -a -o letmein2 .

WORKDIR /

RUN mv /build/letmein2 .
RUN mkdir /templates /static
COPY ./templates /templates
COPY ./static /static
ENTRYPOINT ["./letmein2"]
