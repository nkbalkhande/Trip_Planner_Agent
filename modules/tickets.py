import requests
import json
import random
import os
import googlemaps
from llm.model import llm
from utils.types import AgentClass
from langchain_core.tools import tool
from amadeus import Client
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()
amadeus = Client(
    client_id=os.getenv("AMADEUS_CLIENT_ID"),
    client_secret=os.getenv("AMADEUS_CLIENT_SECRET")
)

gmaps = googlemaps.Client(key=os.getenv("Gemini_map"))


@tool
def fetch_top_places(destination: str, max_results: int = 10) -> list:
    """Fetch the top tourist places for that destination."""
    try:
        response = gmaps.places(
            query=f"Top tourist attractions in {destination}"
        )
        places = response.get("results", [])[:max_results]
        return [place["name"] for place in places]
    except Exception as e:
        print("❌ Error fetching from Google Maps:", e)
        return []


def fetch_amadeus_flight_price(transport_mode: str, source: str, dest: str, departure_date: str):
    """Fetches flight price, airline name, cabin, and cities using Amadeus API."""
    print(f"🛫 Fetching flights from {source} to {dest} using Amadeus API...")

    # ✅ Step 1: Authenticate
    auth_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    auth_data = {
        "grant_type": "client_credentials",
        "client_id": os.getenv("AMADEUS_CLIENT_ID"),
        "client_secret": os.getenv("AMADEUS_CLIENT_SECRET")
    }

    auth_response = requests.post(auth_url, data=auth_data)
    access_token = auth_response.json().get("access_token")
    if not access_token:
        print("❌ Failed to authenticate with Amadeus API")
        return {"type": "plane", "name": "Unknown", "price": 0}

    # ✅ Step 2: Search Flights
    flight_url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {"Authorization": f"Bearer {access_token}"}

    airport_map = {
        "Delhi": "DEL", "Mumbai": "BOM", "Bangalore": "BLR", "Hyderabad": "HYD",
        "Chennai": "MAA", "Kolkata": "CCU", "Pune": "PNQ", "Ahmedabad": "AMD",
        "Jaipur": "JAI", "Goa": "GOI", "Panaji": "GOI", "Varanasi": "VNS",
        "Amritsar": "ATQ", "Coimbatore": "CJB", "Madurai": "IXM", "Kochi": "COK",
        "Trivandrum": "TRV", "Mysore": "MYQ", "Udaipur": "UDR", "Jodhpur": "JDH",
        "Shimla": "SLV", "Manali": "KUU", "Kullu": "KUU", "Rishikesh": "DED",
        "Haridwar": "DED", "Dehradun": "DED", "Leh": "IXL", "Srinagar": "SXR",
        "Darjeeling": "IXB", "Gangtok": "PYG", "Andaman": "IXZ", "Port Blair": "IXZ",
        "Agra": "AGR", "Bhopal": "BHO", "Nagpur": "NAG", "Raipur": "RPR",
        "Lucknow": "LKO", "Indore": "IDR", "Chandigarh": "IXC", "Patna": "PAT",
        "Guwahati": "GAU", "Shillong": "SHL", "Tirupati": "TIR", "Visakhapatnam": "VTZ",
        "Vijayawada": "VGA"
    }

    # ✅ Clean input and lookup airport codes
    source_clean = source.strip().title()
    dest_clean = dest.strip().title()

    origin = airport_map.get(source_clean)
    destination = airport_map.get(dest_clean)

    print(
        f"📍 Mapping source='{source}' → {origin}, destination='{dest}' → {destination}")

    if not origin or not destination:
        print(
            f"❌ Unknown airport code for source='{source_clean}' or destination='{dest_clean}'")
        return {"type": "plane", "name": "Unknown", "price": 0}

    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": departure_date,
        "adults": 1,
        "nonStop": 'true',
        "currencyCode": "INR",
        "max": 3
    }

    response = requests.get(flight_url, headers=headers, params=params)
    if response.status_code != 200:
        print("❌ Failed to fetch flight data:", response.json())
        return {"type": "plane", "name": "Unknown", "price": 0}

    try:
        data = response.json()
        offers = data["data"]
        dictionaries = data.get("dictionaries", {})
        locations = dictionaries.get("locations", {})
        carriers = dictionaries.get("carriers", {})

        flight = random.choice(offers)
        segment = flight["itineraries"][0]["segments"][0]
        fare_details = flight["travelerPricings"][0]["fareDetailsBySegment"][0]

        departure_code = segment["departure"]["iataCode"]
        arrival_code = segment["arrival"]["iataCode"]
        departure_city = locations.get(
            departure_code, {}).get("cityCode", departure_code)
        arrival_city = locations.get(
            arrival_code, {}).get("cityCode", arrival_code)

        airline_code = segment.get("carrierCode", "AI")
        airline_name = carriers.get(airline_code, airline_code).title()

        cabin = fare_details.get("cabin", "Unknown").capitalize()
        price = float(flight["price"]["grandTotal"])
        currency = flight["price"]["currency"]

        return {
            "type": "plane",
            "name": airline_name,
            "price": price,
            "currency": currency,
            "from": departure_city,
            "to": arrival_city,
            "cabin": cabin
        }

    except Exception as e:
        print(f"❌ Error parsing flight data: {e}")
        return {"type": "plane", "name": "Unknown", "price": 0}


def book_ticket(state: AgentClass) -> AgentClass:
    source = state['sourse']
    dest = state['destination']
    checkin_date = state.get('checkin_date', '2025-08-01')  # fallback
    ticket = fetch_amadeus_flight_price("Plane", source, dest, checkin_date)
    state['confirm_ticket'] = json.dumps(ticket)
    return state


def return_ticket(state: AgentClass) -> AgentClass:
    source = state['destination']
    dest = state['sourse']
    return_date = state.get('checkout_date', '2025-08-05')  # fallback
    ticket = fetch_amadeus_flight_price("Plane", source, dest, return_date)
    state['return_ticket'] = ticket
    return state
