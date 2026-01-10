package dispatch

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"
	"sync"
	"time"

	sdka2a "github.com/a2aproject/a2a-go/a2a"
	"github.com/a2aproject/a2a-go/a2aclient"
	"github.com/a2aproject/a2a-go/a2aclient/agentcard"

	"a2a-poc/internal/a2a"
)

type Endpoints struct {
	FlightsURL   string
	HotelsURL    string
	ItineraryURL string
}

// Dispatcher resolves tasks to agent URLs and forwards envelopes.
type Dispatcher struct {
	endpoints Endpoints
	clients   map[string]*a2aclient.Client
	mu        sync.Mutex
}

func New(endpoints Endpoints) *Dispatcher {
	return &Dispatcher{
		endpoints: endpoints,
		clients:   map[string]*a2aclient.Client{},
	}
}

// Route selects the agent URL and performs the downstream call.
func (d *Dispatcher) Route(ctx context.Context, req a2a.Request) (a2a.Response, error) {
	agentURL, agentName := d.pickAgent(req.Task)
	if agentURL == "" {
		return a2a.Response{}, fmt.Errorf("no agent for task")
	}

	return d.forward(ctx, agentURL, agentName, req)
}

func (d *Dispatcher) pickAgent(task string) (url string, name string) {
	switch strings.ToLower(task) {
	case "flights", "flight":
		return d.endpoints.FlightsURL, "flights"
	case "hotels", "hotel", "lodging":
		return d.endpoints.HotelsURL, "hotels"
	case "itinerary", "plan":
		return d.endpoints.ItineraryURL, "itinerary"
	default:
		// Graceful fallback to itinerary.
		return d.endpoints.ItineraryURL, "itinerary"
	}
}

func (d *Dispatcher) forward(ctx context.Context, agentURL, agentName string, req a2a.Request) (a2a.Response, error) {
	client, err := d.ensureClient(ctx, agentName, agentURL)
	if err != nil {
		return a2a.Response{}, fmt.Errorf("client init: %w", err)
	}

	userPayload, err := json.Marshal(req.Payload)
	if err != nil {
		return a2a.Response{}, fmt.Errorf("encode payload: %w", err)
	}

	msg := sdka2a.NewMessage(sdka2a.MessageRoleUser, sdka2a.TextPart{Text: string(userPayload)})
	msg.Metadata = map[string]any{
		"task":            req.Task,
		"payload":         req.Payload,
		"conversation_id": req.ConversationID,
		"user_id":         req.UserID,
	}

	params := &sdka2a.MessageSendParams{Message: msg}

	ctx, cancel := context.WithTimeout(ctx, 8*time.Second)
	defer cancel()

	res, err := client.SendMessage(ctx, params)
	if err != nil {
		return a2a.Response{}, err
	}

	resultMap, err := toResultMap(res)
	if err != nil {
		return a2a.Response{}, err
	}

	return a2a.Response{
		Agent:  agentName,
		Status: "ok",
		Result: resultMap,
		Trace:  nil,
	}.WithTrace(agentName), nil
}

func (d *Dispatcher) ensureClient(ctx context.Context, agentName, baseURL string) (*a2aclient.Client, error) {
	d.mu.Lock()
	if client, ok := d.clients[agentName]; ok {
		d.mu.Unlock()
		return client, nil
	}
	d.mu.Unlock()

	cardURL := strings.TrimSuffix(baseURL, "/") + "/.well-known/agent-card.json"
	card, err := agentcard.DefaultResolver.Resolve(ctx, cardURL)
	if err != nil {
		return nil, fmt.Errorf("resolve agent card: %w", err)
	}

	client, err := a2aclient.NewFromCard(ctx, card)
	if err != nil {
		return nil, fmt.Errorf("create client: %w", err)
	}

	d.mu.Lock()
	d.clients[agentName] = client
	d.mu.Unlock()
	return client, nil
}

func toResultMap(event sdka2a.SendMessageResult) (map[string]interface{}, error) {
	raw, err := json.Marshal(event)
	if err != nil {
		return nil, err
	}
	var out map[string]interface{}
	if err := json.Unmarshal(raw, &out); err != nil {
		return nil, err
	}
	return out, nil
}
