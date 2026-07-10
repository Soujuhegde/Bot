from app.schemas.chat import TaskRequest, TaskResponse
from app.utils.mock_data import mock_search_hotels
import time

def call_hotel_agent(request: TaskRequest) -> TaskResponse:
    # Validate input
    params = request.parameters
    if not params.get("city") or not params.get("check_in_date") or not params.get("check_out_date"):
        return TaskResponse(
            task_id=request.task_id,
            status="needs_clarification",
            clarification_needed="I need the city, check-in date, and check-out date to search for hotels.",
            metadata={"agent_id": "hotel_agent", "timestamp": time.time()}
        )
    
    # Mock search
    search_result = mock_search_hotels(params)
    
    if search_result["status"] == "success":
        return TaskResponse(
            task_id=request.task_id,
            status="success",
            results=search_result["results"],
            metadata={"agent_id": "hotel_agent", "timestamp": time.time()}
        )
    else:
        return TaskResponse(
            task_id=request.task_id,
            status="failed",
            error="Failed to find hotels for the specified parameters.",
            metadata={"agent_id": "hotel_agent", "timestamp": time.time()}
        )
