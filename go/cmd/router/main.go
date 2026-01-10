package main

import (
	"log"
	"net/http"
	"os"

	"a2a-poc/internal/dispatch"
	"a2a-poc/internal/server"
)

func main() {
	endpoints := dispatch.Endpoints{
		FlightsURL:   envOrDefault("FLIGHTS_AGENT_URL", "http://python-agents:8000"),
		HotelsURL:    envOrDefault("HOTELS_AGENT_URL", "http://python-agents:8000"),
		ItineraryURL: envOrDefault("ITINERARY_AGENT_URL", "http://python-agents:8000"),
	}

	dispatcher := dispatch.New(endpoints)
	srv := server.New(dispatcher)
	mux := srv.Mux()

	addr := ":" + envOrDefault("PORT", "8080")
	log.Printf("router listening on %s", addr)
	if err := http.ListenAndServe(addr, mux); err != nil {
		log.Fatalf("server error: %v", err)
	}
}

func envOrDefault(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}
