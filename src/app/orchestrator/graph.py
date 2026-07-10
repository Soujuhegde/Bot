import os
from datetime import datetime, timedelta
from typing import TypedDict, Annotated, Literal, List, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_groq import ChatGroq
from app.schemas.chat import TaskRequest, TaskResponse
from app.agents.flight_agent import call_flight_agent
from pydantic import BaseModel, Field
import time
import random
import string

class ConversationState(TypedDict):
    messages: List[BaseMessage]
    session_id: str
    current_step: str | None
    latest_intent: str | None
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
    ticket: Dict[str, Any] | None

class ExtractedInfo(BaseModel):
    intent: Literal["book_flight", "general_qa", "select_flight", "provide_details", "payment_done", "provide_passenger_count", "confirm", "reject"]
    origin: str | None = None
    destination: str | None = None
    departure_date: str | None = None
    limit: int | None = Field(description="The number of flights the user wants to see, if they explicitly mention a number (e.g. 'show me 5 flights').", default=None)
    journey_type: Literal["One Way", "Round Trip"] | None = None
    selected_class: str | None = None
    selected_airline: str | None = None
    selected_price: Optional[str] = Field(description="The price of the flight", default=None)
    booking_link: Optional[str] = Field(description="The booking URL link if provided in the message", default=None)
    passenger_name: Optional[str] = Field(description="Name of the passenger", default=None)
    passenger_email: str | None = None
    passenger_contact: str | None = None
    passenger_passport: str | None = None
    adults_count: int | None = None
    children_count: int | None = None
    infants_count: int | None = None

try:
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
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
    today = datetime.now()
    today_date = today.strftime("%A, %Y-%m-%d")
    tomorrow_date = (today + timedelta(days=1)).strftime("%A, %Y-%m-%d")
    
    upcoming_days = []
    for i in range(7):
        day = today + timedelta(days=i)
        upcoming_days.append(f"{day.strftime('%A')} ({day.strftime('%Y-%m-%d')})")
    upcoming_str = ", ".join(upcoming_days)
    
    prompt = f"""You are a helpful travel assistant. Analyze the user's latest message and extract their intent and any travel details.
    
    Current known flight params: {flight_params}
    Current known passenger count: {passenger_count}
    Current passenger index being filled: {current_passenger_index + 1}
    Current Date: {today_date}
    Tomorrow's Date: {tomorrow_date}
    Upcoming 7 days reference: {upcoming_str}
    
    Intents:
    - book_flight: user wants to search for flights.
    - select_flight: user selects a specific flight and class. YOU MUST extract selected_airline, selected_class, selected_price, and booking_link if present.
    - provide_passenger_count: user tells you how many adults/children/infants. Extract this into adults_count, children_count, infants_count.
    - provide_details: user provides their passenger info (name, email, contact, passport).
    - payment_done: user says payment is done.
    - confirm: user explicitly says yes/correct.
    - reject: user explicitly says no/wrong.
    - general_qa: anything else.
    
    Rules for Date Extraction:
    - ALWAYS convert departure_date strictly to YYYY-MM-DD format.
    - If the user says "next [day]" (e.g., "next monday"), use the exact date for that day from the "Upcoming 7 days reference". Do NOT add an extra week.
    - Convert all origin and destination cities/countries/airports strictly to their most prominent 3-letter IATA airport code.
      - If a country is provided (e.g., 'India', 'France'), output its major international airport code (e.g., 'DEL' for India, 'CDG' for France).
      - If a city has multiple airports, output the primary airport code (e.g., 'LHR' for London, 'JFK' for New York) or the city code.
      - Be extremely careful with spelling and similar-sounding names (e.g., 'Mangalore' is 'IXE' and must not be confused with 'Bangalore' 'BLR'; 'Goa' is 'GOI' and not 'Genoa').
      - Use your comprehensive knowledge to map ANY global city or country correctly."""
    
    messages = [SystemMessage(content=prompt)] + recent_messages
    
    structured_llm = llm.with_structured_output(ExtractedInfo)
    result = structured_llm.invoke(messages)
    
    if result.origin: flight_params["origin"] = result.origin
    if result.destination: flight_params["destination"] = result.destination
    if result.limit: flight_params["limit"] = result.limit
    
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
    
    # Manual override for flight selection from UI clicks to guarantee accuracy
    user_msg_text = state["messages"][-1].content.strip()
    msg_text_lower = user_msg_text.lower()
    
    if user_msg_text.startswith("I would like to select "):
        result.intent = "select_flight"
        try:
            parts = user_msg_text.replace("I would like to select ", "").split(" class on ")
            cls = parts[0]
            rest = parts[1].split(" for ")
            airline_flight = rest[0]
            price = rest[1]
            selected_flight["class"] = cls
            selected_flight["airline"] = airline_flight
            selected_flight["price"] = price
            
            fr = state.get("flight_result") or {}
            for f in fr.get("results", []):
                if airline_flight in f.get("airline_name", "") or airline_flight in f.get("flight_numbers", "") or f.get("flight_numbers") in airline_flight:
                    selected_flight["booking_link"] = f.get("booking_link") or "https://flights.google.com"
                    selected_flight["flight_numbers"] = f.get("flight_numbers", "N/A")
                    selected_flight["departure_time"] = f.get("departure_time", "00:00")
                    selected_flight["arrival_time"] = f.get("arrival_time", "00:00")
                    selected_flight["origin_airport"] = f.get("origin_airport", "Origin")
                    selected_flight["destination_airport"] = f.get("destination_airport", "Destination")
                    selected_flight["airline_logo"] = f.get("airline_logo", "")
                    selected_flight["airline_name"] = f.get("airline_name", airline_flight)
                    break
        except Exception as e:
            print(f"Error parsing manual flight selection: {e}")
            
    if step == "awaiting_passenger_count" and not user_msg_text.startswith("I would like to select "):
        result.intent = "provide_passenger_count"
            
    is_confirmation = result.intent == "confirm" or msg_text_lower in ["yes", "y", "yeah", "correct", "right", "ok", "okay", "sure", "proceed"] or "yes" in msg_text_lower
    is_rejection = result.intent == "reject" or msg_text_lower in ["no", "n", "nope", "wrong", "wait"] or "no" in msg_text_lower

    # If we are verifying passenger count, strict intercept of confirmation/rejection to prevent LLM hallucinations
    if step == "verify_passenger_count":
        if is_confirmation:
            step = "awaiting_passenger_details"
            result.intent = "confirm"
        elif is_rejection:
            step = "awaiting_passenger_count"
            result.intent = "reject"
        elif result.intent == "provide_details":
            step = "awaiting_passenger_details"
        elif result.intent == "select_flight" and not user_msg_text.startswith("I would like to select "):
            # Prevent hallucinated flight selection
            step = "verify_passenger_count"
            
    if step != "verify_passenger_count" and result.intent == "select_flight":
        if result.selected_airline and not user_msg_text.startswith("I would like to select "): selected_flight["airline"] = result.selected_airline
        if result.selected_class and not user_msg_text.startswith("I would like to select "): selected_flight["class"] = result.selected_class
        if result.selected_price and not user_msg_text.startswith("I would like to select "): selected_flight["price"] = result.selected_price
        if hasattr(result, "booking_link") and result.booking_link and not user_msg_text.startswith("I would like to select "): selected_flight["booking_link"] = result.booking_link
        
        step = "awaiting_passenger_count"
            
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
        "latest_intent": result.intent,
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
    latest_intent = state.get("latest_intent")
    msg = "How can I help you?"
    replies = []
    options = []
    
    # If the user goes off-topic or says something conversational/harsh, handle it dynamically
    if latest_intent == "general_qa" or step == "general_qa":
        if llm:
            qa_prompt = f"You are a polite and professional travel assistant. The user just said something conversational, out of context, or possibly harsh. Respond to them gracefully like a real human. Acknowledge their message, de-escalate if necessary, and then gently steer the conversation back to our current booking step. Our current step is: '{step}'. (For context: awaiting_origin_dest = asking where they are flying; awaiting_passenger_count = asking how many people; awaiting_passenger_details = asking for names/passports). Keep it concise and natural."
            msgs = [SystemMessage(content=qa_prompt)] + state["messages"][-2:]
            try:
                response = llm.invoke(msgs)
                msg = response.content
            except Exception as e:
                print(f"LLM Error in general_qa fallback: {e}")
                msg = "I'm here to help you with your travel bookings! Could we get back to that?"
        else:
            msg = "I'm here to help you with your travel bookings! Could we get back to that?"
            
        return {"final_response": msg, "quick_replies": [], "options_to_show": []}
        
    if step == "awaiting_origin_dest":
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
        origin = state.get("flight_params", {}).get("origin", "")
        destination = state.get("flight_params", {}).get("destination", "")
        
        base_link = flight.get("booking_link") or "https://flights.google.com"
        # Append origin and destination to the specific airline link
        if "?" in base_link:
            link = f"{base_link}&origin={origin}&destination={destination}"
        else:
            link = f"{base_link}?origin={origin}&destination={destination}"
            
        msg = "Perfect! Let's proceed with your booking."
        replies = ["Payment done"]
        options = [{"type": "action_button", "label": "Proceed With Booking", "url": link}]
        
    elif step == "booking_confirmed":
        flight = state.get("selected_flight", {})
        pax_list = state.get("passengers_details") or []
        if not pax_list:
            pax_list = [state.get("passenger_details", {})]
            
        pnr = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
            
        # Determine the origin and destination based on the flight result if possible
        origin = state.get("flight_params", {}).get("origin", "Origin")
        destination = state.get("flight_params", {}).get("destination", "Destination")
        today_date = datetime.now().strftime("%A, %Y-%m-%d")
        date = state.get("flight_params", {}).get("departure_date", today_date)
        
        # Build the ticket dictionary
        ticket = {
            "pnr": pnr,
            "airline": flight.get('airline_name', flight.get('airline', 'N/A')),
            "flight_numbers": flight.get('flight_numbers', 'N/A'),
            "flight_class": flight.get('class', 'Economy'),
            "price": flight.get('price', 'N/A'),
            "date": date,
            "origin": origin.upper(),
            "destination": destination.upper(),
            "origin_full": flight.get("origin_airport", origin.upper()),
            "destination_full": flight.get("destination_airport", destination.upper()),
            "departure_time": flight.get('departure_time', '00:00'),
            "arrival_time": flight.get('arrival_time', '00:00'),
            "airline_logo": flight.get('airline_logo', ''),
            "gate": f"C{random.randint(10, 99)}",
            "seat": f"{random.randint(1, 30)}{random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}",
            "group": random.choice(['A', 'B', 'C', 'D', 'E']),
            "passengers": pax_list
        }
            
        msg = f"🎉 Payment Successful! Booking Confirmed. 🎉\n\nI have generated your flight ticket below. Have a great trip! Let me know if you need to book anything else."
        return {"final_response": msg, "quick_replies": [], "options_to_show": [], "ticket": ticket}

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
