FROM golang:1.24 AS builder

WORKDIR /app
COPY go.mod ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o router ./cmd/router

FROM gcr.io/distroless/base-debian12
WORKDIR /app
COPY --from=builder /app/router /router
ENV PORT=8080
EXPOSE 8080
ENTRYPOINT ["/router"]
