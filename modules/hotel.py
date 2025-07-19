# modules/hotel.py

import requests
import os
from dotenv import load_dotenv
from utils.types import AgentClass
from langchain_core.prompts import PromptTemplate
from llm.model import llm
import json
import random
import re

load_dotenv()

RAPIDAPI_HOST = "apidojo-booking-v1.p.rapidapi.com"
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

headers = {
    "x-rapidapi-host": RAPIDAPI_HOST,
    "x-rapidapi-key": RAPIDAPI_KEY
}


def get_simple_hotels(city: str, checkin: str, checkout: str) -> list:
    # Step 1: Get destination ID
    loc_url = "https://apidojo-booking-v1.p.rapidapi.com/locations/auto-complete"
    loc_params = {"text": city, "languagecode": "en-us"}
    loc_res = requests.get(loc_url, headers=headers, params=loc_params)
    loc_data = loc_res.json()

    if not loc_data:
        return []

    dest_id = loc_data[0]["dest_id"]
    dest_type = loc_data[0]["dest_type"]

    # Step 2: Get hotel list
    hotel_url = "https://apidojo-booking-v1.p.rapidapi.com/properties/list"
    hotel_params = {
        "dest_ids": dest_id,
        "dest_type": dest_type,
        "checkin_date": checkin,
        "checkout_date": checkout,
        "adults_number": 1,
        "filter_by_currency": "INR",
        "order_by": "popularity",
        "locale": "en-gb",
        "room_number": 1,
        "page_number": "0"
    }

    hotel_res = requests.get(hotel_url, headers=headers, params=hotel_params)
    hotel_data = hotel_res.json()

    hotels = []
    for h in hotel_data.get("result", [])[:3]:
        name = h.get("hotel_name", "Unknown")
        price = h.get("price_breakdown", {}).get(
            "gross_price", random.randint(2000, 10000))
        hotels.append({
            "name": name,
            "price": int(price)
        })
    return hotels


def hotel_booking(state: AgentClass) -> AgentClass:
    destination = state['destination']
    days = state['days']

    prompt = PromptTemplate(
        template="""
        You are a travel assistant. Return 3 hotel options in JSON format with just name and price_per_night.
        Destination: {destination}
        Days: {days}

        Respond ONLY as:
        {{
            "hotel_1": {{"name": "Hotel Name 1", "price_per_night": 3000}},
            "hotel_2": {{"name": "Hotel Name 2", "price_per_night": 1800}},
            "hotel_3": {{"name": "Hotel Name 3", "price_per_night": 2500}}
        }}
        """,
        input_variables=["destination", "days"]
    )

    chain = prompt | llm
    result = chain.invoke({"destination": destination, "days": days})

    content = re.sub(r"^```(?:json)?|```$", "",
                     result.content.strip(), flags=re.MULTILINE)
    content = content.replace("'", '"').replace("\n", "").replace(",}", "}")
    content = re.sub(r',\s*([}\]])', r'\1', content)

    try:
        hotels = json.loads(content)
    except json.JSONDecodeError as e:
        print("❌ Hotel JSON parsing failed:", e)
        print("⚠️ Raw content was:", content)
        state['hotel'] = {"name": "No Hotel Found",
                          "price_per_night": "N/A", "total_price": "N/A"}
        return state

    # Choose one hotel randomly
    selected = random.choice(list(hotels.values()))
    total_price = selected['price_per_night'] * days

    hotel_final = {
        "name": selected["name"],
        "price_per_night": selected["price_per_night"],
        "total_price": total_price
    }

    print(f"\n✅ Hotel Selected: {hotel_final}")
    state['hotel'] = hotel_final
    return state
