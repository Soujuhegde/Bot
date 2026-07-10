from typing import Dict, Any

def mock_search_flights(params: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "success",
        "results": [
            {
                "airline_name": "Air India",
                "airline_logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Air_India_Logo.svg/512px-Air_India_Logo.svg.png",
                "flight_numbers": "AI 2802 | AI 2118",
                "departure_date": "Fri, 21 Aug 26",
                "arrival_date": "Sat, 22 Aug 26",
                "departure_time": "18:20",
                "arrival_time": "09:15",
                "origin_airport": "Bengaluru (BLR)",
                "destination_airport": "Singapore (SIN)",
                "duration": "12h 25m",
                "stops": "1 Stop",
                "booking_link": "https://www.airindia.com/in/en/ibe/booking.html#/availability/departure",
                "pricing": [
                    {"class": "Economy", "price": "INR 28,869.00"},
                    {"class": "Premium Economy", "price": "INR 39,373.00"},
                    {"class": "Business", "price": "INR 82,366.00"}
                ]
            },
            {
                "airline_name": "IndiGo",
                "airline_logo": "https://upload.wikimedia.org/wikipedia/en/thumb/5/5c/IndiGo_logo.svg/512px-IndiGo_logo.svg.png",
                "flight_numbers": "6E 2511 | 6E 2380",
                "departure_date": "Fri, 21 Aug 26",
                "arrival_date": "Sat, 22 Aug 26",
                "departure_time": "15:10",
                "arrival_time": "07:25",
                "origin_airport": "Bengaluru (BLR)",
                "destination_airport": "Singapore (SIN)",
                "duration": "13h 45m",
                "stops": "1 Stop",
                "booking_link": "https://www.goindigo.in/booking/flight-select.html",
                "pricing": [
                    {"class": "Economy", "price": "INR 29,100.00"},
                    {"class": "Premium Economy", "price": "INR 40,000.00"},
                    {"class": "Business", "price": "INR 85,000.00"}
                ]
            }
        ]
    }

def mock_search_hotels(params: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "success",
        "results": [
            {
                "name": "Taj Palace",
                "star_rating": "5-star",
                "price_per_night": "$180",
                "amenities": ["Pool", "Free WiFi", "Breakfast"],
                "distance_from_landmark": "2 km from center",
                "booking_url": "https://example.com/book/taj-palace"
            },
            {
                "name": "Holiday Inn",
                "star_rating": "4-star",
                "price_per_night": "$90",
                "amenities": ["Free WiFi", "Gym"],
                "distance_from_landmark": "5 km from center",
                "booking_url": "https://example.com/book/holiday-inn"
            }
        ]
    }
