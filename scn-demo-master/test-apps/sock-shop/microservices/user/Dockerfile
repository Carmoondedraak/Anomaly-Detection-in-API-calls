FROM golang:latest as builder

ENV GOPATH /go
ENV PATH $GOPATH/bin:/usr/local/go/bin:$PATH

RUN mkdir -p "$GOPATH/src" "$GOPATH/bin" "$GOPATH/dist" && chmod -R 777 "$GOPATH"

WORKDIR $GOPATH/src/github.com/user

COPY . .

# Download all dependencies. Dependencies will be cached if the go.mod and go.sum files are not changed
#RUN go mod download
RUN go get -d -v \
  && go install -v \
  && go build


# Build the Go user
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o user .


######## Start a new stage from scratch #######
FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /go/src/github.com/user .
EXPOSE 8000
CMD ["./user"]
