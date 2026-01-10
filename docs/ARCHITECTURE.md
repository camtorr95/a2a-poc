## Overview
This proof of concept demonstrates a multi-agent travel assistant built on MCP/A2A-style messaging. A Go “central agent” routes requests to specialized Python agents (flights, hotels, itinerary) using the official A2A SDKs: `a2a-go` for the router client and `a2a-sdk` for the FastAPI JSON-RPC server.

## Components
- Go router (`go/`): net/http service that accepts a simple A2A envelope, uses `a2a-go` to resolve AgentCards and send JSON-RPC messages, and returns responses with a hop trace.
- Python agents (`python/`): FastAPI service exposing three agents via `a2a-sdk` JSON-RPC:
  - `flights-agent`: mock flight status/search.
  - `hotels-agent`: mock hotel search/book placeholder.
  - `itinerary-agent`: composes a simple plan from prior steps or a direct ask.
- Docker Compose (`docker-compose.yml`): runs the Go router and Python agents on one network; service names are used as stable endpoints.

## A2A Envelope (HTTP/JSON)
Request (to router and between agents):
```
{
  "conversation_id": "uuid",
  "user_id": "string",
  "task": "flights|hotels|itinerary",
  "payload": { ... } // agent-specific arguments
}
```

Response (agents and router):
```
{
  "agent": "flights|hotels|itinerary|router",
  "status": "ok|error",
  "result": { ... },      // agent-specific data or error info
  "trace": [ "router", "flights" ] // hop order for observability
}
```

## Routing
- Task → agent mapping lives in the Go router.
- The router resolves the AgentCard at `/.well-known/agent-card.json` and connects over JSON-RPC.
- Endpoints are configurable via env vars (base URLs):
  - `FLIGHTS_AGENT_URL` (default `http://python-agents:8000`)
  - `HOTELS_AGENT_URL` (default `http://python-agents:8000`)
  - `ITINERARY_AGENT_URL` (default `http://python-agents:8000`)
- Unknown tasks fall back to the itinerary agent for graceful handling.

## Local URLs
- Router: `POST http://localhost:8080/a2a/route` (simple envelope)
- Agent Card: `GET http://localhost:8000/.well-known/agent-card.json`
- Agent JSON-RPC: `POST http://localhost:8000/a2a` (A2A JSON-RPC via `a2a-sdk`)

## Observability
- Simple structured logging in the router.
- Hop trace in every response to illustrate A2A routing flow.

## Extending
- Add new agents by implementing the same envelope and registering their URL in the router.
- Replace mocks with real providers once credentials are available; the envelope remains unchanged.

