# modules/ticket.py

import requests
import json
import random
import os
import googlemaps
from llm.model import llm
from utils.types import AgentClass
from langchain_core.tools import tool
from amadeus import Client, ResponseError
from datetime import datetime
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


def fetch_amadeus_flight_price(transport_mode: str, source: str, dest: str):
    """
    Fetches flight price, airline name, cabin, and cities using Amadeus API.
    Assumes transport_mode is always 'Plane'.
    """
    print(f"🛫 Fetching flights from {source} to {dest} using Amadeus API...")

    # ✅ Step 1: Authenticate
    amadeus_api_key = os.getenv("AMADEUS_CLIENT_ID")
    amadeus_api_secret = os.getenv("AMADEUS_CLIENT_SECRET")
    auth_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    auth_data = {
        "grant_type": "client_credentials",
        "client_id": amadeus_api_key,
        "client_secret": amadeus_api_secret
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
        "Delhi": "DEL",                   # Indira Gandhi International Airport
        "Mumbai": "BOM",                  # Chhatrapati Shivaji Maharaj Int'l
        "Bangalore": "BLR",               # Kempegowda Int'l Airport
        "Hyderabad": "HYD",              # Rajiv Gandhi Int'l Airport
        "Chennai": "MAA",                # Chennai Int'l Airport
        "Kolkata": "CCU",                # Netaji Subhas Chandra Bose Int'l
        "Pune": "PNQ",                   # Pune Airport
        "Ahmedabad": "AMD",              # Sardar Vallabhbhai Patel Int'l
        "Jaipur": "JAI",                 # Jaipur Int'l Airport
        "Goa": "GOI",                    # Dabolim Airport
        "Panaji": "GOI",                 # (same as Goa)
        "Varanasi": "VNS",               # Lal Bahadur Shastri Int'l Airport
        "Amritsar": "ATQ",               # Sri Guru Ram Dass Jee Int'l
        "Coimbatore": "CJB",             # Coimbatore Int'l Airport
        "Madurai": "IXM",                # Madurai Airport
        "Kochi": "COK",                  # Cochin Int'l Airport
        "Trivandrum": "TRV",             # Trivandrum Int'l Airport
        "Mysore": "MYQ",                 # Mysore Airport
        "Udaipur": "UDR",                # Maharana Pratap Airport
        "Jodhpur": "JDH",                # Jodhpur Airport
        "Shimla": "SLV",                 # Shimla Airport (limited service)
        "Manali": "KUU",                 # Kullu–Manali (Bhuntar) Airport
        "Rishikesh": "DED",              # Dehradun Airport (Jolly Grant)
        "Haridwar": "DED",               # Dehradun Airport
        "Dehradun": "DED",               # Jolly Grant Airport
        "Leh": "IXL",                    # Kushok Bakula Rimpochee Airport
        "Srinagar": "SXR",               # Srinagar Airport
        "Darjeeling": "IXB",             # Bagdogra Airport
        "Gangtok": "PYG",                # Pakyong Airport
        "Andaman": "IXZ",                # Veer Savarkar (Port Blair)
        "Port Blair": "IXZ",
        "Agra": "AGR",                   # Kheria Airport
        "Bhopal": "BHO",                 # Raja Bhoj Airport
        "Nagpur": "NAG",                 # Dr. Babasaheb Ambedkar Int'l
        "Raipur": "RPR",                 # Swami Vivekananda Airport
        "Lucknow": "LKO",                # Chaudhary Charan Singh Int'l
        "Indore": "IDR",                 # Devi Ahilya Bai Holkar Airport
        "Chandigarh": "IXC",             # Chandigarh Airport
        "Patna": "PAT",                  # Jay Prakash Narayan Airport
        "Guwahati": "GAU",               # Lokpriya Gopinath Bordoloi Int'l
        "Shillong": "SHL",               # Shillong Airport (limited)
        "Tirupati": "TIR",               # Tirupati Airport
        "Visakhapatnam": "VTZ",          # Visakhapatnam Airport
        "Vijayawada": "VGA",             # Vijayawada Airport
    }

    origin = airport_map.get(source.title(), "HYD")
    destination = airport_map.get(dest.title(), "MAA")

    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": "2025-08-01",  # static or pass as param
        "adults": 1,
        "nonStop": 'true',
        "currencyCode": "INR",
        "max": 3
    }

    response = requests.get(flight_url, headers=headers, params=params)
    print(response)
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
    ticket = fetch_amadeus_flight_price("Plane", source, dest)

    print(f"✅ Confirmed Ticket: {ticket}")
    state['confirm_ticket'] = json.dumps(ticket)
    return state


def return_ticket(state: AgentClass) -> AgentClass:
    source = state['destination']
    dest = state['sourse']
    ticket = fetch_amadeus_flight_price("Plane", source, dest)

    print(f"🔁 Return Ticket: {ticket}")
    state['return_ticket'] = ticket
    return state
