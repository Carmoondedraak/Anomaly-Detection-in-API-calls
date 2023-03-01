FROM golang:latest as builder

ENV GOPATH /go
ENV PATH $GOPATH/bin:/usr/local/go/bin:$PATH

RUN mkdir -p "$GOPATH/src" "$GOPATH/bin" "$GOPATH/dist" && chmod -R 777 "$GOPATH"

WORKDIR $GOPATH/src/github.com/catalogue

COPY . .

# Download all dependencies. Dependencies will be cached if the go.mod and go.sum files are not changed
#RUN go mod download
RUN go get -d -v \
  && go install -v \
  && go build


# Build the Go i360-businessunit
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o catalogue .


######## Start a new stage from scratch #######
FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /go/src/github.com/catalogue .
EXPOSE 80
CMD ["./catalogue"]