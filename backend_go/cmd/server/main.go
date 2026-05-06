// Package main is the entry point for the runbooks_testing Go backend.
//
// This server provides a lightweight HTTP API that complements
// the Python backend. In production, you might use this for
// performance-critical endpoints or specific microservices.
package main

import (
	"log"
	"net/http"
	"time"

	"github.com/example/runbooks_testing/backend_go/internal/handler"
)

type statusRecorder struct {
	http.ResponseWriter
	statusCode int
}

func (r *statusRecorder) WriteHeader(code int) {
	r.statusCode = code
	r.ResponseWriter.WriteHeader(code)
}

func loggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		recorder := &statusRecorder{ResponseWriter: w, statusCode: http.StatusOK}

		log.Printf("request started method=%s path=%s", r.Method, r.URL.Path)
		next.ServeHTTP(recorder, r)
		duration := time.Since(start)
		log.Printf("request completed method=%s path=%s status=%d duration=%s", r.Method, r.URL.Path, recorder.statusCode, duration)
	})
}

func main() {
	mux := http.NewServeMux()

	// Register routes using Go 1.22+ enhanced routing patterns
	mux.HandleFunc("GET /", handler.Root)
	mux.HandleFunc("GET /hello/{name}", handler.Hello)
	mux.HandleFunc("GET /health", handler.Health)
	mux.HandleFunc("GET /items", handler.ListItems)
	mux.HandleFunc("POST /items", handler.CreateItem)

	wrapped := loggingMiddleware(mux)

	log.Println("Starting server on :8080")
	if err := http.ListenAndServe(":8080", wrapped); err != nil {
		log.Fatal(err)
	}
}
