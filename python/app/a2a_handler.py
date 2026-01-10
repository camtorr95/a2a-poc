import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from a2a.server.events.event_queue import Event
from a2a.server.request_handlers.request_handler import RequestHandler
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentSkill,
    Message,
    MessageSendParams,
    Role,
    Task,
    TaskIdParams,
    TaskPushNotificationConfig,
    TaskQueryParams,
    TaskState,
    TaskStatus,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils.errors import ServerError

from app.agents import flights, hotels, itinerary
from app.core.config import Settings
from app.core.models import A2ARequest


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_agent_card(base_url: str) -> AgentCard:
    """Create an AgentCard describing this service."""
    rpc_url = f"{base_url}/a2a"
    return AgentCard(
        name="travel-agents",
        description="Travel assistant with flights, hotels, and itinerary skills.",
        url=rpc_url,
        preferred_transport="JSONRPC",
        default_input_modes=["text/plain"],
        default_output_modes=["application/json"],
        capabilities=AgentCapabilities(streaming=False),
        skills=[
            AgentSkill(
                id="flights",
                name="Flights",
                description="Check or mock flight status and times.",
                tags=["travel", "flights"],
            ),
            AgentSkill(
                id="hotels",
                name="Hotels",
                description="Search or mock hotel options.",
                tags=["travel", "hotels"],
            ),
            AgentSkill(
                id="itinerary",
                name="Itinerary",
                description="Draft a simple travel plan.",
                tags=["travel", "plan"],
            ),
        ],
        version="0.1.0",
        additional_interfaces=[
            AgentInterface(transport="JSONRPC", url=rpc_url),
        ],
    )


class TravelRequestHandler(RequestHandler):
    """Bridges A2A JSON-RPC calls to the domain agents."""

    def __init__(self, settings: Settings, base_url: str):
        self.settings = settings
        self.base_url = base_url.rstrip("/")
        self.tasks: Dict[str, Task] = {}

    # Core message entrypoint (non-streaming)
    async def on_message_send(
        self, params: MessageSendParams, context=None
    ) -> Task | Message:
        message = params.message
        task_id = message.task_id or str(uuid.uuid4())
        context_id = message.context_id or str(uuid.uuid4())

        # Normalize incoming message
        message.task_id = task_id
        message.context_id = context_id

        meta = message.metadata or {}
        task = (meta.get("task") or "itinerary").lower()
        payload = meta.get("payload") or {}

        agent_result = self.run_agent(task, payload)

        agent_message = Message(
            message_id=str(uuid.uuid4()),
            role=Role.AGENT,
            parts=[
                TextPart(
                    text=json.dumps(agent_result["result"]),
                    metadata={"agent": agent_result["agent"]},
                )
            ],
            metadata={"agent": agent_result["agent"], "trace": agent_result["trace"]},
            task_id=task_id,
            context_id=context_id,
        )

        status = TaskStatus(
            state=TaskState.completed,
            message=None,
            timestamp=iso_now(),
        )

        task_obj = Task(
            id=task_id,
            context_id=context_id,
            status=status,
            history=[message, agent_message],
        )

        self.tasks[task_id] = task_obj
        return task_obj

    async def on_message_send_stream(
        self, params: MessageSendParams, context=None
    ) -> Event:
        raise ServerError(error=UnsupportedOperationError())

    async def on_get_task(
        self, params: TaskQueryParams, context=None
    ) -> Optional[Task]:
        return self.tasks.get(params.id)

    async def on_cancel_task(
        self, params: TaskIdParams, context=None
    ) -> Optional[Task]:
        task = self.tasks.get(params.id)
        if not task:
            return None
        task.status.state = TaskState.canceled
        return task

    async def on_set_task_push_notification_config(
        self, params: TaskPushNotificationConfig, context=None
    ) -> TaskPushNotificationConfig:
        raise ServerError(error=UnsupportedOperationError())

    async def on_get_task_push_notification_config(
        self, params, context=None
    ) -> TaskPushNotificationConfig:
        raise ServerError(error=UnsupportedOperationError())

    async def on_resubscribe_to_task(self, params, context=None) -> Event:
        raise ServerError(error=UnsupportedOperationError())

    async def on_list_task_push_notification_config(
        self, params, context=None
    ) -> list[TaskPushNotificationConfig]:
        raise ServerError(error=UnsupportedOperationError())

    async def on_delete_task_push_notification_config(
        self, params, context=None
    ) -> None:
        raise ServerError(error=UnsupportedOperationError())

    # Internal agent routing
    def run_agent(self, task: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        a2a_request = A2ARequest(
            conversation_id=str(uuid.uuid4()),
            user_id=payload.get("user_id", "a2a-user"),
            task=task,
            payload=payload,
        )

        if task in {"flights", "flight"}:
            resp = flights.handle(a2a_request)
        elif task in {"hotels", "hotel", "lodging"}:
            resp = hotels.handle(a2a_request)
        else:
            resp = itinerary.handle(a2a_request)

        return {
            "agent": resp.agent,
            "result": resp.result,
            "trace": resp.trace,
        }
