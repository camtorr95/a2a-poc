from datetime import datetime, timedelta

from app.core.models import A2ARequest, A2AResponse, envelope


def handle(request: A2ARequest) -> A2AResponse:
    payload = request.payload or {}
    origin = payload.get("from", "SFO")
    dest = payload.get("to", "JFK")
    depart_at = datetime.utcnow() + timedelta(hours=2)

    mock = {
        "from": origin,
        "to": dest,
        "flight_number": "POC123",
        "status": "on-time",
        "departure": depart_at.isoformat() + "Z",
        "arrival": (depart_at + timedelta(hours=5)).isoformat() + "Z",
    }
    return envelope("flights", {"flight": mock})
