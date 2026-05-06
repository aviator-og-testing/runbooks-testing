// Package handler contains HTTP handlers for the runbooks_testing API.
//
// Each handler follows the standard http.HandlerFunc signature.
// For more complex applications, consider using a router like chi
// or implementing middleware for logging, auth, etc.
package handler

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
)

// Response represents a standard JSON response structure.
// Using a consistent response format makes client integration easier.
type Response struct {
	Message string `json:"message"`
	Status  string `json:"status,omitempty"`
}

// ItemRequest represents the body of a POST /items request.
type ItemRequest struct {
	Name        string `json:"name"`
	Description string `json:"description"`
}

// Root handles the base path and serves as a simple health indicator.
func Root(w http.ResponseWriter, r *http.Request) {
	log.Printf("handling root request from %s", r.RemoteAddr)
	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(Response{
		Message: "Hello World",
		Status:  "ok",
	}); err != nil {
		log.Printf("failed to encode root response: %v", err)
	}
}

// Hello returns a personalized greeting.
// The name parameter is extracted from the URL path using Go 1.22+ routing.
func Hello(w http.ResponseWriter, r *http.Request) {
	name := r.PathValue("name")
	log.Printf("handling hello request for name=%s", name)
	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(Response{
		Message: fmt.Sprintf("Hello %s", name),
	}); err != nil {
		log.Printf("failed to encode hello response: %v", err)
	}
}

// Health provides a dedicated health check endpoint for load balancers
// and orchestration systems (k8s, etc.).
func Health(w http.ResponseWriter, r *http.Request) {
	log.Printf("health check from %s", r.RemoteAddr)
	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(Response{
		Status: "healthy",
	}); err != nil {
		log.Printf("failed to encode health response: %v", err)
	}
}

// ListItems returns all items.
func ListItems(w http.ResponseWriter, r *http.Request) {
	log.Printf("listing items, request from %s", r.RemoteAddr)
	w.Header().Set("Content-Type", "application/json")
	items := []Response{
		{Message: "item1", Status: "active"},
		{Message: "item2", Status: "active"},
	}
	if err := json.NewEncoder(w).Encode(items); err != nil {
		log.Printf("failed to encode items response: %v", err)
		http.Error(w, "internal server error", http.StatusInternalServerError)
	}
}

// CreateItem handles POST /items to add a new item.
func CreateItem(w http.ResponseWriter, r *http.Request) {
	log.Printf("creating item, request from %s", r.RemoteAddr)

	var req ItemRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		log.Printf("failed to decode item request: %v", err)
		http.Error(w, "invalid request body", http.StatusBadRequest)
		return
	}

	if req.Name == "" {
		log.Printf("item creation rejected: empty name")
		http.Error(w, "name is required", http.StatusBadRequest)
		return
	}

	log.Printf("item created: name=%s", req.Name)
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	if err := json.NewEncoder(w).Encode(Response{
		Message: fmt.Sprintf("Created item: %s", req.Name),
		Status:  "created",
	}); err != nil {
		log.Printf("failed to encode create item response: %v", err)
	}
}
