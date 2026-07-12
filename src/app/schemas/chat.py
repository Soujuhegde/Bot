from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict, Any

class TaskRequest(BaseModel):
    task_id: str
    task_type: Literal["flight_search", "hotel_search"]
    session_id: str
    parameters: dict
    metadata: dict = Field(default_factory=dict) # {requested_by, timestamp}

class TaskResponse(BaseModel):
    task_id: str
    status: Literal["success", "partial", "failed", "needs_clarification"]
    results: List[dict] = Field(default_factory=list)
    clarification_needed: Optional[str] = None
    error: Optional[str] = None
    metadata: dict = Field(default_factory=dict) # {agent_id, timestamp}

class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    message: str
    options: List[dict] = Field(default_factory=list)
    clarification_needed: bool = False
    quick_replies: List[str] = Field(default_factory=list)
    ticket: Optional[dict] = None
    followup_message: Optional[str] = None
    followup_quick_replies: List[str] = Field(default_factory=list)
    current_flow: Optional[str] = None
