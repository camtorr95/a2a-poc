from app.core.models import A2ARequest, A2AResponse, envelope


def handle(request: A2ARequest) -> A2AResponse:
    payload = request.payload or {}
    city = payload.get("city") or payload.get("to") or "New York"
    from_city = payload.get("from", "SFO")

    plan = [
        f"Fly from {from_city} to {city}",
        f"Check in to a central hotel in {city}",
        f"Spend day 1 exploring downtown and a museum",
        f"Day 2: food crawl and a park visit",
    ]
    return envelope("itinerary", {"plan": plan})
