package a2a

// Request represents the shared A2A/MCP-style envelope.
type Request struct {
	ConversationID string                 `json:"conversation_id"`
	UserID         string                 `json:"user_id"`
	Task           string                 `json:"task"`
	Payload        map[string]interface{} `json:"payload"`
}

// Response is the standardized agent reply with hop trace.
type Response struct {
	Agent  string                 `json:"agent"`
	Status string                 `json:"status"`
	Result map[string]interface{} `json:"result"`
	Trace  []string               `json:"trace,omitempty"`
}

// WithTrace prepends a hop to the trace for observability.
func (r Response) WithTrace(hop string) Response {
	r.Trace = append([]string{hop}, r.Trace...)
	return r
}
