from app.core.models import A2ARequest, A2AResponse, envelope


def handle(request: A2ARequest) -> A2AResponse:
    payload = request.payload or {}
    city = payload.get("city") or payload.get("to") or "New York"
    nights = payload.get("nights", 2)

    mock_hotels = [
        {"name": "Grand Plaza", "city": city, "price_per_night": 189, "available": True},
        {"name": "City Loft", "city": city, "price_per_night": 129, "available": True},
    ]
    return envelope("hotels", {"options": mock_hotels, "nights": nights})
