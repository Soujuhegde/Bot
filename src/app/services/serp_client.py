import httpx
from typing import Dict, List, Any
from app.config import settings
from app.schemas.schemas import FlightOption, HotelOption

class SerpClient:
    def __init__(self):
        self.api_key = settings.SERPAPI_API_KEY
        self.base_url = "https://serpapi.com/search.json"
        # Simple in-memory cache per session/request
        self.cache: Dict[str, Any] = {}

    def _generate_cache_key(self, engine: str, params: dict) -> str:
        # Sort params to ensure stable cache key
        sorted_params = tuple(sorted(params.items()))
        return f"{engine}_{sorted_params}"

    async def search_flights(self, origin: str, destination: str, departure_date: str, return_date: str = None, passengers: int = 1, cabin_class: str = "1") -> List[FlightOption]:
        params = {
            "engine": "google_flights",
            "departure_id": origin,
            "arrival_id": destination,
            "outbound_date": departure_date,
            "travel_class": cabin_class,
            "adults": passengers,
            "hl": "en",
            "gl": "us",
            "api_key": self.api_key
        }
        if return_date:
            params["return_date"] = return_date

        cache_key = self._generate_cache_key("google_flights", {k: v for k, v in params.items() if k != "api_key"})
        if cache_key in self.cache:
            return self.cache[cache_key]

        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=params, timeout=15.0)
            if response.status_code != 200:
                print(f"SerpApi Error: {response.text}")
                return []
            
            data = response.json()
            flights = []
            
            # Parse 'best_flights' from response
            best_flights = data.get("best_flights", [])
            for f in best_flights[:5]: # Take top 5
                try:
                    flight_info = f["flights"][0]
                    airline = flight_info["airline"]
                    flight_number = flight_info["flight_number"]
                    depart_time = flight_info["departure_airport"]["time"]
                    arrive_time = f["flights"][-1]["arrival_airport"]["time"]
                    duration = f["total_duration"]
                    price = f.get("price", 0)
                    stops = len(f["flights"]) - 1
                    booking_token = f.get("booking_token")
                    
                    flights.append(FlightOption(
                        airline=airline,
                        flight_number=flight_number,
                        depart_time=depart_time,
                        arrive_time=arrive_time,
                        duration=duration,
                        price=price,
                        stops=stops,
                        booking_token=booking_token,
                        departure_token=f.get("departure_token")
                    ))
                except (KeyError, IndexError) as e:
                    print(f"Error parsing flight option: {e}")
                    continue
            
            self.cache[cache_key] = flights
            return flights

    async def search_hotels(self, q: str, check_in_date: str, check_out_date: str, adults: int = 1) -> List[HotelOption]:
        params = {
            "engine": "google_hotels",
            "q": q,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "adults": adults,
            "hl": "en",
            "gl": "us",
            "api_key": self.api_key
        }

        cache_key = self._generate_cache_key("google_hotels", {k: v for k, v in params.items() if k != "api_key"})
        if cache_key in self.cache:
            return self.cache[cache_key]

        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=params, timeout=15.0)
            if response.status_code != 200:
                print(f"SerpApi Error: {response.text}")
                return []
            
            data = response.json()
            hotels = []
            
            properties = data.get("properties", [])
            for p in properties[:5]: # Take top 5
                try:
                    name = p["name"]
                    star_rating = p.get("extracted_hotel_class", 0)
                    price = p.get("rate_per_night", {}).get("extracted_lowest", 0)
                    amenities = p.get("amenities", [])[:3]
                    link = p.get("link")
                    
                    hotels.append(HotelOption(
                        name=name,
                        star_rating=star_rating,
                        price_per_night=price,
                        amenities=amenities,
                        distance_from_landmark=None, # Serpapi doesn't always provide this consistently
                        link=link
                    ))
                except KeyError as e:
                    print(f"Error parsing hotel option: {e}")
                    continue
            
            self.cache[cache_key] = hotels
            return hotels

serp_client = SerpClient()
