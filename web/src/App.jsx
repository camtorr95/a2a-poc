import { useEffect, useMemo, useState } from 'react';
import './App.css';

const defaultPayload = JSON.stringify(
  {
    from: 'SFO',
    to: 'JFK',
  },
  null,
  2
);

const tasks = ['flights', 'hotels', 'itinerary'];

function App() {
  const [conversationId] = useState(() => crypto.randomUUID());
  const [userId] = useState(() => 'demo-user');
  const [task, setTask] = useState('flights');
  const [payloadText, setPayloadText] = useState(defaultPayload);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [response, setResponse] = useState(null);
  const [meta, setMeta] = useState(null);

  const payload = useMemo(() => {
    try {
      return JSON.parse(payloadText || '{}');
    } catch {
      return null;
    }
  }, [payloadText]);

  const payloadError = payload ? '' : 'Invalid JSON payload';

  const send = async () => {
    if (!payload) return;
    setLoading(true);
    setError('');
    setResponse(null);
    try {
      const res = await fetch('http://localhost:8080/a2a/route', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation_id: conversationId,
          user_id: userId,
          task,
          payload,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(JSON.stringify(data, null, 2));
      } else {
        setResponse(data);
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetch('http://localhost:8000/.well-known/agent-card.json')
      .then((r) => r.json())
      .then(setMeta)
      .catch(() => {});
  }, []);

  return (
    <div className="app-shell">
      <header className="header">
        <div>
          <h1>Travel A2A Chat</h1>
          <p className="subhead">
            User → Go router → A2A agents (flights / hotels / itinerary)
          </p>
        </div>
        <div className="ids">
          <span>conversation_id: {conversationId}</span>
          <span>user_id: {userId}</span>
        </div>
      </header>

      <main className="grid">
        <section className="panel">
          <h2>Compose</h2>
          <label className="label">Task</label>
          <select value={task} onChange={(e) => setTask(e.target.value)}>
            {tasks.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>

          <label className="label">Payload (JSON)</label>
          <textarea
            className="payload"
            rows={8}
            value={payloadText}
            onChange={(e) => setPayloadText(e.target.value)}
          />
          {payloadError && <div className="error">⚠ {payloadError}</div>}

          <button disabled={loading || !!payloadError} onClick={send}>
            {loading ? 'Sending…' : 'Send to router'}
          </button>
          {error && <pre className="error-block">{error}</pre>}
        </section>

        <section className="panel">
          <h2>Response</h2>
          {response ? (
            <pre className="console">{JSON.stringify(response, null, 2)}</pre>
          ) : (
            <div className="placeholder">No response yet.</div>
          )}
        </section>

        <section className="panel">
          <h2>Agent Metadata (A2A)</h2>
          {meta ? (
            <pre className="console">{JSON.stringify(meta, null, 2)}</pre>
          ) : (
            <div className="placeholder">Loading agent card…</div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
