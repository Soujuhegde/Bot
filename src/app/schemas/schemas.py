from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict, Any

class TaskRequest(BaseModel):
    task_id: str
    task_type: Literal["flight_search", "hotel_search"]
    session_id: str
    parameters: dict
    metadata: dict  # {requested_by, timestamp}

class TaskResponse(BaseModel):
    task_id: str
    status: Literal["success", "partial", "failed", "needs_clarification"]
    results: list[dict]
    clarification_needed: Optional[str] = None
    error: Optional[str] = None
    metadata: dict  # {agent_id, timestamp}

class ExtractedIntent(BaseModel):
    intent: Optional[Literal["book_flight", "book_hotel", "book_both", "general_qa"]] = Field(default=None, description="The primary intent of the user.")
    origin: Optional[str] = Field(default=None, description="Origin city or airport code.")
    destination: Optional[str] = Field(default=None, description="Destination city or airport code.")
    departure_date: Optional[str] = Field(default=None, description="Departure date in YYYY-MM-DD format.")
    return_date: Optional[str] = Field(default=None, description="Return date in YYYY-MM-DD format.")
    passengers: Optional[int] = Field(default=None, description="Number of passengers/guests.")
    cabin_class: Optional[str] = Field(default=None, description="Cabin class for flights (e.g., economy, premium_economy, business, first).")
    check_in_date: Optional[str] = Field(default=None, description="Check-in date for hotels in YYYY-MM-DD format.")
    check_out_date: Optional[str] = Field(default=None, description="Check-out date for hotels in YYYY-MM-DD format.")

class FlightOption(BaseModel):
    airline: str
    flight_number: str
    depart_time: str
    arrive_time: str
    duration: int
    price: float
    stops: int
    booking_token: Optional[str] = None
    departure_token: Optional[str] = None

class HotelOption(BaseModel):
    name: str
    star_rating: float
    price_per_night: float
    amenities: List[str]
    distance_from_landmark: Optional[str] = None
    link: Optional[str] = None
