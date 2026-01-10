from pydantic import BaseModel, Field
from typing import Dict, List


class A2ARequest(BaseModel):
    conversation_id: str = Field(..., description="Conversation identifier")
    user_id: str = Field(..., description="Caller id")
    task: str = Field(..., description="Requested task")
    payload: Dict = Field(default_factory=dict, description="Agent-specific args")


class A2AResponse(BaseModel):
    agent: str
    status: str
    result: Dict
    trace: List[str] = Field(default_factory=list)


def envelope(agent: str, result: Dict, status: str = "ok") -> A2AResponse:
    return A2AResponse(agent=agent, status=status, result=result, trace=[agent])
