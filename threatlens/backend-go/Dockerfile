FROM golang:1.24-alpine AS build
WORKDIR /app
COPY go.mod go.sum* ./
RUN go mod download || true
COPY . .
RUN go build -o threatlens-backend ./cmd/server

FROM alpine:3.20
WORKDIR /app
COPY --from=build /app/threatlens-backend /usr/local/bin/threatlens-backend
EXPOSE 8080
CMD ["threatlens-backend"]
