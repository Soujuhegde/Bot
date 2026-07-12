from typing import Dict, Any
import re
import random

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
                "price": "INR 28,869.00",
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
                "price": "INR 29,100.00",
                "pricing": [
                    {"class": "Economy", "price": "INR 29,100.00"},
                    {"class": "Premium Economy", "price": "INR 40,000.00"},
                    {"class": "Business", "price": "INR 85,000.00"}
                ]
            }
        ]
    }

def mock_search_hotels(params: Dict[str, Any]) -> Dict[str, Any]:
    city = params.get("city", "Pune")
    budget = params.get("budget", "")
    area = params.get("area", "No Preference")
    category = params.get("category", "No Preference")
    
    # Define budget segments
    all_hotels = [
        # OYO / Treebo / Fab
        {"name": "OYO Townhouse, {city}", "star_rating": 3, "price": 2200, "booking_url": "https://www.oyorooms.com"},
        {"name": "FabHotel Prime, {city}", "star_rating": 3, "price": 2800, "booking_url": "https://www.fabhotels.com"},
        {"name": "Treebo Trend Metropolis, {city}", "star_rating": 3, "price": 3200, "booking_url": "https://www.treebo.com"},
        {"name": "Ginger Hotel, {city}", "star_rating": 3, "price": 4100, "booking_url": "https://www.gingerhotels.com"},
        # Lemon Tree / IBIS / Pride
        {"name": "IBIS Styles Hotel, {city}", "star_rating": 4, "price": 5800, "booking_url": "https://all.accor.com"},
        {"name": "Lemon Tree Premier, {city}", "star_rating": 4, "price": 6500, "booking_url": "https://www.lemontreehotels.com"},
        {"name": "Pride Hotel, {city}", "star_rating": 4, "price": 6900, "booking_url": "https://www.pridehotel.com"},
        {"name": "Fairfield by Marriott, {city}", "star_rating": 4, "price": 7200, "booking_url": "https://fairfield.marriott.com"},
        # Radisson / Courtyard / DoubleTree
        {"name": "DoubleTree by Hilton, {city}", "star_rating": 4, "price": 9200, "booking_url": "https://www.hilton.com"},
        {"name": "Radisson Blu, {city}", "star_rating": 5, "price": 10500, "booking_url": "https://www.radissonhotels.com"},
        {"name": "Courtyard by Marriott, {city}", "star_rating": 4, "price": 11200, "booking_url": "https://courtyard.marriott.com"},
        # Luxury
        {"name": "JW Marriott, {city}", "star_rating": 5, "price": 16800, "booking_url": "https://www.marriott.com"},
        {"name": "The Taj Mahal Palace, {city}", "star_rating": 5, "price": 18500, "booking_url": "https://www.tajhotels.com"},
        {"name": "The Oberoi, {city}", "star_rating": 5, "price": 22000, "booking_url": "https://www.oberoihotels.com"},
    ]
    
    room_type = params.get("room_type", "No Preference").lower()
    
    # Parse budget min/max
    min_p, max_p = 0, 1000000
    if budget and budget != "I'll decide later":
        prices = re.findall(r"[\d,]+", budget)
        if len(prices) == 2:
            min_p = int(prices[0].replace(",", ""))
            max_p = int(prices[1].replace(",", ""))
        elif len(prices) == 1 and "+" in budget:
            min_p = int(prices[0].replace(",", ""))
            
    filtered = []
    for h in all_hotels:
        if min_p <= h["price"] <= max_p:
            # Match Star Category
            if "3-Star" in category and h["star_rating"] != 3: continue
            if "4-Star" in category and h["star_rating"] != 4: continue
            if "5-Star" in category and h["star_rating"] != 5: continue

            # Match Room Type
            if "standard" in room_type and h["star_rating"] != 3: continue
            if "deluxe" in room_type and h["star_rating"] != 4: continue
            if ("luxury" in room_type or "suite" in room_type) and h["star_rating"] != 5: continue
            
            filtered.append(h)

            
    # Fallback if filter too strict
    if len(filtered) < 3:
        filtered = [h for h in all_hotels if min_p <= h["price"] <= max_p]
    if len(filtered) < 3:
        filtered = all_hotels[:3]
        
    results = []
    images_pool = [
        ["https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=600&q=80",
         "https://images.unsplash.com/photo-1582719508461-905c673771fd?auto=format&fit=crop&w=600&q=80"],
        ["https://images.unsplash.com/photo-1540541338287-41700207dee6?auto=format&fit=crop&w=600&q=80",
         "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?auto=format&fit=crop&w=600&q=80"],
        ["https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=600&q=80",
         "https://images.unsplash.com/photo-1445019980597-93fa8acb246c?auto=format&fit=crop&w=600&q=80"]
    ]
    
    for i, h in enumerate(filtered[:3]):
        distance = "Convenient location"
        if "Airport" in area:
            distance = f"{1.5 + i*1.2:.1f} km from Airport"
        elif "City Centre" in area:
            distance = f"{0.8 + i*0.7:.1f} km from City Centre"
        elif "Business District" in area:
            distance = f"{0.5 + i*0.9:.1f} km from Business District"
        elif "Tourist Attractions" in area:
            distance = f"{0.3 + i*0.6:.1f} km from Tourist Attractions"
            
        results.append({
            "name": h["name"].format(city=city),
            "star_rating": h["star_rating"],
            "price_per_night": f"₹{h['price']:,}",
            "distance": distance,
            "amenities": ["Free WiFi", "AC", "Pool", "Room Service"] if h["star_rating"] >= 4 else ["Free WiFi", "AC", "Room Service"],
            "guest_rating": f"{4.0 + (i*0.3) + (random.random()*0.2):.1f}",
            "images": images_pool[i % len(images_pool)],
            "booking_url": h["booking_url"]
        })
        
    return {
        "status": "success",
        "results": results
    }
