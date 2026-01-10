package server

import (
	"encoding/json"
	"io"
	"log"
	"net/http"

	"a2a-poc/internal/a2a"
	"a2a-poc/internal/dispatch"
)

// Server exposes HTTP handlers for routing and health.
type Server struct {
	dispatcher *dispatch.Dispatcher
}

func New(dispatcher *dispatch.Dispatcher) *Server {
	return &Server{dispatcher: dispatcher}
}

// Mux wires handlers into a standard ServeMux.
func (s *Server) Mux() *http.ServeMux {
	mux := http.NewServeMux()
	mux.HandleFunc("/healthz", s.Health)
	mux.HandleFunc("/a2a/route", s.Route)
	return mux
}

func (s *Server) Health(w http.ResponseWriter, r *http.Request) {
	writeJSON(w, http.StatusOK, map[string]string{"status": "ok"})
}

func (s *Server) Route(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req a2a.Request
	if err := decodeJSON(r, &req); err != nil {
		http.Error(w, "invalid payload: "+err.Error(), http.StatusBadRequest)
		return
	}

	resp, err := s.dispatcher.Route(r.Context(), req)
	if err != nil {
		log.Printf("dispatch error: %v", err)
		writeJSON(w, http.StatusBadGateway, a2a.Response{
			Agent:  "router",
			Status: "error",
			Result: map[string]interface{}{"error": err.Error()},
			Trace:  []string{"router"},
		})
		return
	}

	writeJSON(w, http.StatusOK, resp.WithTrace("router"))
}

func decodeJSON(r *http.Request, dst interface{}) error {
	limited := io.LimitReader(r.Body, 1<<20) // 1MB
	decoder := json.NewDecoder(limited)
	decoder.DisallowUnknownFields()
	return decoder.Decode(dst)
}

func writeJSON(w http.ResponseWriter, status int, payload interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if err := json.NewEncoder(w).Encode(payload); err != nil {
		log.Printf("encode error: %v", err)
	}
}
