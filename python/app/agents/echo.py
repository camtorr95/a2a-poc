from app.core.models import A2ARequest, A2AResponse, envelope


def handle(request: A2ARequest) -> A2AResponse:
    return envelope("echo", {"request": request.model_dump()})
