import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.schemas.schemas import ExtractedIntent, FlightOption, HotelOption
import json

client = TestClient(app)

@pytest.fixture
def mock_llm():
    with patch('app.orchestrator.graph.llm_client') as mock:
        mock.parse_intent = AsyncMock()
        mock.generate_response = AsyncMock()
        yield mock

@pytest.fixture
def mock_serp():
    with patch('app.agents.flight_agent.serp_client') as mock_flight, \
         patch('app.agents.hotel_agent.serp_client') as mock_hotel:
        mock_flight.search_flights = AsyncMock()
        mock_hotel.search_hotels = AsyncMock()
        yield {"flight": mock_flight, "hotel": mock_hotel}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_chat_flight_only_flow(mock_llm, mock_serp):
    # 1. User says "Book a flight to NYC"
    mock_llm.parse_intent.return_value = ExtractedIntent(
        intent="book_flight",
        destination="NYC"
    )
    # The system will see missing origin and date
    
    response = client.post("/api/chat", json={"message": "Book a flight to NYC"})
    assert response.status_code == 200
    data = response.json()
    assert data["needs_clarification"] is True
    assert "Please provide" in data["reply"]
    session_id = data["session_id"]
    
    # 2. User provides the rest: "From LAX on 2026-10-10"
    mock_llm.parse_intent.return_value = ExtractedIntent(
        intent="book_flight",
        origin="LAX",
        destination="NYC",
        departure_date="2026-10-10"
    )
    
    # Mock the search response
    mock_serp["flight"].search_flights.return_value = [
        FlightOption(
            airline="Mock Airlines",
            flight_number="MK123",
            depart_time="10:00 AM",
            arrive_time="02:00 PM",
            duration=240,
            price=250.0,
            stops=0
        )
    ]
    
    mock_llm.generate_response.return_value = "Here are some great flights! Would you like me to look at hotels for those dates too?"
    
    response = client.post("/api/chat", json={"session_id": session_id, "message": "From LAX on 2026-10-10"})
    assert response.status_code == 200
    data = response.json()
    assert data["needs_clarification"] is False
    assert data["flight_options"] is not None
    assert len(data["flight_options"]) == 1
    assert data["flight_options"][0]["airline"] == "Mock Airlines"
    assert "hotels" in data["reply"]
