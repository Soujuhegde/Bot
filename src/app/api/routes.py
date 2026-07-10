from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse
from app.orchestrator.graph import graph
from langchain_core.messages import HumanMessage
import uuid

router = APIRouter()

# In-memory session state storage for the demo (since MemorySaver needs async setup or sqlite)
# For production, use LangGraph's checkpointer
sessions = {}

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    
    # Get or create state
    state = sessions.get(session_id, {
        "messages": [],
        "session_id": session_id,
        "intent": None,
        "flight_params": {},
        "hotel_params": {},
        "pending_clarification": None,
        "flight_result": None,
        "hotel_result": None,
        "final_response": None,
        "options_to_show": []
    })
    
    # Add new message
    state["messages"].append(HumanMessage(content=request.message))
    
    # Run graph
    new_state = graph.invoke(state)
    
    final_resp = new_state.get("final_response", "I encountered an error processing that.")
    # Append bot's response to the context
    from langchain_core.messages import AIMessage
    new_state["messages"].append(AIMessage(content=final_resp))
    
    # Update session
    sessions[session_id] = new_state
    
    return ChatResponse(
        message=final_resp,
        options=new_state.get("options_to_show", []),
        clarification_needed=bool(new_state.get("pending_clarification")),
        quick_replies=new_state.get("quick_replies", [])
    )
