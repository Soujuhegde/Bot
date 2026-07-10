import os
from datetime import datetime, timedelta
from typing import TypedDict, Annotated, Literal, List, Dict, Any
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_groq import ChatGroq
from app.schemas.chat import TaskRequest, TaskResponse
from app.agents.flight_agent import call_flight_agent
from pydantic import BaseModel
import time
import random
import string

class ConversationState(TypedDict):
    messages: List[BaseMessage]
    session_id: str
    current_step: str | None
    flight_params: Dict[str, Any] | None
    pending_clarification: str | None
    quick_replies: List[str] | None
    flight_result: Dict[str, Any] | None
    final_response: str | None
    options_to_show: List[Dict[str, Any]] | None
    selected_flight: Dict[str, Any] | None
    passenger_details: Dict[str, Any] | None
    
    # Multi-passenger flow
    passenger_count: Dict[str, int] | None
    passengers_details: List[Dict[str, Any]] | None
    current_passenger_index: int | None

class ExtractedInfo(BaseModel):
    intent: Literal["book_flight", "general_qa", "select_flight", "provide_details", "payment_done", "provide_passenger_count", "confirm", "reject"]
    origin: str | None = None
    destination: str | None = None
    departure_date: str | None = None
    journey_type: Literal["One Way", "Round Trip"] | None = None
    selected_class: str | None = None
    selected_airline: str | None = None
    selected_price: str | None = None
    passenger_name: str | None = None
    passenger_email: str | None = None
    passenger_contact: str | None = None
    passenger_passport: str | None = None
    adults_count: int | None = None
    children_count: int | None = None
    infants_count: int | None = None

try:
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
except Exception as e:
    print(f"Warning: Failed to initialize ChatGroq. {e}")
    llm = None

def parse_intent(state: ConversationState):
    if not llm:
        return {"current_step": "general_qa", "final_response": "LLM not configured."}
    
    recent_messages = state["messages"][-5:]
    flight_params = state.get("flight_params") or {}
    passenger_details = state.get("passenger_details") or {}
    selected_flight = state.get("selected_flight") or {}
    
    passenger_count = state.get("passenger_count") or {}
    passengers_details = state.get("passengers_details") or []
    current_passenger_index = state.get("current_passenger_index") or 0
    
    today_date = datetime.now().strftime("%A, %Y-%m-%d")
    tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%A, %Y-%m-%d")
    prompt = f"""You are a helpful travel assistant. Analyze the user's latest message and extract their intent and any travel details.
    
    Current known flight params: {flight_params}
    Current known passenger count: {passenger_count}
    Current passenger index being filled: {current_passenger_index + 1}
    Current Date: {today_date}
    Tomorrow's Date: {tomorrow_date}
    
    Intents:
    - book_flight: user wants to search for flights.
    - select_flight: user selects a specific flight and class.
    - provide_passenger_count: user tells you how many adults/children/infants. Extract this into adults_count, children_count, infants_count.
    - provide_details: user provides their passenger info (name, email, contact, passport).
    - payment_done: user says payment is done.
    - confirm: user confirms something (e.g., says "Yes").
    - reject: user rejects something (e.g., says "No").
    - general_qa: anything else.
    
    Extract the information as structured data. If they just say hi, intent is general_qa.
    CRITICAL: 
    - Convert all dates strictly to YYYY-MM-DD format.
    - Convert all origin and destination cities/airports strictly to their 3-letter IATA airport codes (e.g., 'Bangalore' -> 'BLR', 'Singapore' -> 'SIN', 'New York' -> 'JFK')."""
    
    messages = [SystemMessage(content=prompt)] + recent_messages
    
    structured_llm = llm.with_structured_output(ExtractedInfo)
    result = structured_llm.invoke(messages)
    
    if result.origin: flight_params["origin"] = result.origin
    if result.destination: flight_params["destination"] = result.destination
    
    invalid_date = False
    if result.departure_date:
        try:
            date_obj = datetime.strptime(result.departure_date, "%Y-%m-%d").date()
            if date_obj < datetime.now().date():
                flight_params["departure_date"] = None
                invalid_date = True
            else:
                flight_params["departure_date"] = result.departure_date
        except ValueError:
            flight_params["departure_date"] = result.departure_date

    if result.journey_type: flight_params["journey_type"] = result.journey_type
    
    step = state.get("current_step", "start")
    
    if result.intent == "select_flight":
        if result.selected_class: selected_flight["class"] = result.selected_class
        if result.selected_airline: selected_flight["airline"] = result.selected_airline
        if result.selected_price: selected_flight["price"] = result.selected_price
        
        fr = state.get("flight_result") or {}
        flight_results = fr.get("results") or []
        if flight_results and "booking_link" in flight_results[0]:
            selected_flight["booking_link"] = flight_results[0]["booking_link"]
            
        step = "awaiting_passenger_count"
        
    elif step == "verify_passenger_count":
        if result.intent == "confirm" or "yes" in state["messages"][-1].content.lower():
            step = "awaiting_passenger_details"
        elif result.intent == "reject" or "no" in state["messages"][-1].content.lower():
            step = "awaiting_passenger_count"
        else:
            step = "verify_passenger_count"
            
    elif result.intent == "provide_passenger_count" or (step == "awaiting_passenger_count" and result.intent != "general_qa"):
        adults = result.adults_count or 1
        children = result.children_count or 0
        infants = result.infants_count or 0
        total = adults + children + infants
        if total == 0:
            total = 1
            adults = 1
        
        passenger_count = {"adults": adults, "children": children, "infants": infants, "total": total}
        passengers_details = []
        current_passenger_index = 0
        step = "verify_passenger_count"
            
    elif result.intent == "provide_details" or (step == "awaiting_passenger_details" and result.intent != "general_qa"):
        total_pax = passenger_count.get("total") or 1
        
        if current_passenger_index >= len(passengers_details):
            passengers_details.append({})
            
        pax = passengers_details[current_passenger_index]
        if result.passenger_name: pax["name"] = result.passenger_name
        if result.passenger_email: pax["email"] = result.passenger_email
        if result.passenger_contact: pax["contact"] = result.passenger_contact
        if result.passenger_passport: pax["passport"] = result.passenger_passport
        
        if not pax.get("name") or not pax.get("email") or not pax.get("contact") or not pax.get("passport"):
            step = "awaiting_passenger_details"
        else:
            current_passenger_index += 1
            if current_passenger_index >= total_pax:
                step = "awaiting_payment"
            else:
                step = "awaiting_passenger_details"
                
    elif result.intent == "payment_done":
        step = "booking_confirmed"
    elif result.intent == "book_flight" or flight_params.get("origin"):
        if not flight_params.get("origin") or not flight_params.get("destination"):
            step = "awaiting_origin_dest"
        elif invalid_date:
            step = "invalid_departure_date"
        elif not flight_params.get("departure_date"):
            step = "awaiting_departure_date"
        elif not flight_params.get("journey_type"):
            step = "awaiting_journey_type"
        else:
            step = "ready_to_search"
    else:
        if step not in ["awaiting_passenger_details", "awaiting_passenger_count", "verify_passenger_count", "awaiting_payment", "booking_confirmed"]:
            step = "general_qa"
        
    return {
        "current_step": step,
        "flight_params": flight_params,
        "passenger_details": passenger_details,
        "selected_flight": selected_flight,
        "passenger_count": passenger_count,
        "passengers_details": passengers_details,
        "current_passenger_index": current_passenger_index
    }

def route_next(state: ConversationState):
    step = state.get("current_step")
    if step == "ready_to_search":
        return "flight_node"
    return "ask_clarification"

def ask_clarification(state: ConversationState):
    step = state.get("current_step")
    msg = "How can I help you?"
    replies = []
    options = []
    
    if step == "general_qa":
        if llm:
            qa_prompt = "You are a helpful travel assistant. Please respond to the user's query naturally."
            msgs = [SystemMessage(content=qa_prompt)] + state["messages"][-5:]
            response = llm.invoke(msgs)
            msg = response.content
        else:
            msg = "Hello! How may I assist you today?"
    elif step == "awaiting_origin_dest":
        msg = "I can help with that! Where are you flying from and to?"
    elif step == "invalid_departure_date":
        msg = "Wrong data. Please enter a present or future date."
        replies = ["Today", "Tomorrow"]
    elif step == "awaiting_departure_date":
        msg = "Sure! I'll assist you in finding the best flights.\n\nWhen are you departing? For instance, you could say \"tomorrow,\" \"next Monday,\" or \"7th December.\""
        replies = ["Today", "Tomorrow"]
    elif step == "awaiting_journey_type":
        msg = "Are you planning a one-way or return journey?"
        replies = ["One Way", "Round Trip"]
        
    elif step == "awaiting_passenger_count":
        msg = "How many adults, children, and infants will be traveling? For instance, you could say '2 adults, 2 children, 1 infant'."
        replies = ["1 adult", "2 adults", "2 adults, 1 child"]
        
    elif step == "verify_passenger_count":
        count = state.get("passenger_count", {})
        msg = f"Wonderful! Please verify the number of passengers.\n- Adults: {count.get('adults', 0)}\n- Children: {count.get('children', 0)}\n- Infants: {count.get('infants', 0)}"
        replies = ["Yes", "No"]
        
    elif step == "awaiting_passenger_details":
        pax_idx = state.get("current_passenger_index") or 0
        pax_list = state.get("passengers_details") or []
        pax = {}
        if pax_idx < len(pax_list):
            pax = pax_list[pax_idx]
            
        missing = []
        if not pax.get("name"): missing.append("Name")
        if not pax.get("email"): missing.append("Email")
        if not pax.get("contact"): missing.append("Contact No")
        if not pax.get("passport"): missing.append("Passport No")
        
        total_pax = (state.get("passenger_count") or {}).get("total") or 1
        msg = f"Please provide the {', '.join(missing)} for Passenger {pax_idx + 1} of {total_pax} to proceed."
        
    elif step == "awaiting_payment":
        flight = state.get("selected_flight", {})
        # Use the dynamic booking_link provided by the flight agent, which contains the specific search URL for that flight
        link = flight.get("booking_link", "https://flights.google.com")
        msg = "Perfect! Let's proceed with your booking."
        replies = ["Payment done"]
        options = [{"type": "action_button", "label": "Proceed With Booking", "url": link}]
        
    elif step == "booking_confirmed":
        flight = state.get("selected_flight", {})
        pax_list = state.get("passengers_details") or []
        if not pax_list:
            pax_list = [state.get("passenger_details", {})]
            
        pnr = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
            
        pax_text = ""
        for i, pax in enumerate(pax_list):
            pax_text += f"**Passenger {i+1}:** {pax.get('name', 'N/A')} (Passport: {pax.get('passport', 'N/A')})\n"
            
        msg = f"🎉 **Payment Successful! Booking Confirmed.** 🎉\n\n**PNR:** {pnr}\n\n{pax_text}\n**Flight:** {flight.get('airline', 'N/A')} ({flight.get('class', 'N/A')})\n**Total Paid:** {flight.get('price', 'N/A')}\n\nHave a great trip! Let me know if you need to book anything else."
        
    return {"final_response": msg, "quick_replies": replies, "options_to_show": options}

def flight_node(state: ConversationState):
    request = TaskRequest(
        task_id=f"flight_{int(time.time())}",
        task_type="flight_search",
        session_id=state.get("session_id", "default"),
        parameters=state.get("flight_params", {})
    )
    response = call_flight_agent(request)
    
    options = []
    if response.status == "success":
        for r in response.results:
            r["type"] = "flight"
            options.append(r)
            
    final_text = "Here are the flight options. Click to choose your preferred one." if options else "Sorry, we do not have any flights available on the searched date."
    return {"final_response": final_text, "options_to_show": options, "quick_replies": [], "flight_result": response.model_dump()}

# Build Graph
builder = StateGraph(ConversationState)

builder.add_node("parse_intent", parse_intent)
builder.add_node("ask_clarification", ask_clarification)
builder.add_node("flight_node", flight_node)

builder.add_edge(START, "parse_intent")
builder.add_conditional_edges("parse_intent", route_next)
builder.add_edge("ask_clarification", END)
builder.add_edge("flight_node", END)

graph = builder.compile()
