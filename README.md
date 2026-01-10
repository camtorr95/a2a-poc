# a2a-poc

Multi-agent travel assistant proof of concept using an MCP/A2A-style envelope. A Go router dispatches to Python agents (flights, hotels, itinerary) over HTTP, all runnable via docker-compose.

## Repo layout
- `go/` – Go net/http router (central agent)
  - `cmd/router` – entrypoint
  - `internal/a2a` – shared envelope types
  - `internal/dispatch` – agent resolution + forwarding
  - `internal/server` – HTTP handlers
- `python/` – Python FastAPI agents (Poetry-managed, `a2a-sdk`)
  - `app/core` – shared models/envelope helpers
  - `app/core/config.py` – loads .env + YAML config
  - `app/agents` – flights, hotels, itinerary, echo
  - `app/a2a_handler.py` – A2A RequestHandler + AgentCard
  - `app/api.py` – FastAPI wiring (A2A JSON-RPC)
- `python/pyproject.toml` – Poetry project definition
- `docs/ARCHITECTURE.md` – protocol and flow overview
- `docker-compose.yml` – brings everything up locally
- `config/openai.yaml` – OpenAI model parameters
- `env.example` – sample env vars (copy to `.env`)

## Quick start
```bash
docker compose up --build
```

Router endpoint:
```bash
curl -X POST http://localhost:8080/a2a/route \
  -H 'Content-Type: application/json' \
  -d '{
        "conversation_id": "demo-123",
        "user_id": "user-1",
        "task": "flights",
        "payload": { "from": "SFO", "to": "JFK" }
      }'
```

Direct agent calls (bypass router):
- Agent Card: `http://localhost:8000/.well-known/agent-card.json`
- JSON-RPC: `POST http://localhost:8000/a2a` (A2A protocol via `a2a-sdk`)

## OpenAI configuration
- Copy `env.example` to `.env` and set `OPENAI_API_KEY` (and optional `OPENAI_BASE_URL`, `OPENAI_ORG`, `OPENAI_CONFIG_PATH`).
- Model parameters live in `config/openai.yaml`; per-task overrides are supported.
- The FastAPI app loads `.env` + YAML on startup and stores settings in `app.state.settings`.
- Python dependencies are managed with Poetry; install locally via:
  ```bash
  cd python
  poetry install
  poetry run uvicorn app.main:app --reload --port 8000
  ```
- JSON-RPC paths (A2A):
  - RPC: `http://localhost:8000/a2a`
  - Card: `http://localhost:8000/.well-known/agent-card.json`

## Environment overrides
- `FLIGHTS_AGENT_URL` (default `http://python-agents:8000`)
- `HOTELS_AGENT_URL` (default `http://python-agents:8000`)
- `ITINERARY_AGENT_URL` (default `http://python-agents:8000`)
- `AGENT_PUBLIC_URL` (default `http://localhost:8000`, overridden in compose to `http://python-agents:8000`)

## Notes
- Responses include a `trace` field to show the hop path (router + agent).
- Agents use mock data; swap in real providers later without changing the envelope.
