# syntax=docker/dockerfile:1
FROM golang:1.22-alpine AS builder

WORKDIR /app

# Copy go mod files first for better layer caching
COPY go.mod ./
# COPY go.sum ./ # Uncomment when you have dependencies

# Download dependencies (none currently, but ready for future)
RUN go mod download

# Copy source code
COPY . .

# Build the binary
RUN CGO_ENABLED=0 GOOS=linux go build -o /server ./cmd/server

# Production stage - minimal image
FROM alpine:3.19 AS prod

WORKDIR /app

# Add ca-certificates for HTTPS calls
RUN apk --no-cache add ca-certificates

# Copy binary from builder
COPY --from=builder /server .

EXPOSE 8080

CMD ["./server"]
