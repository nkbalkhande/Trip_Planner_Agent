# modules/itinerary.py

from langchain_core.prompts import PromptTemplate
from llm.model import llm
from utils.types import AgentClass
from modules.tickets import fetch_top_places


def itinerary(state: AgentClass) -> AgentClass:
    destination = state.get("destination")
    days = int(state.get("days", 1))

    if not destination:
        print("❌ Destination is required.")
        return state

    # Use reusable Google Maps tool
    place_names = fetch_top_places.invoke({'destination': destination})
    if not place_names:
        print("❌ No places found for itinerary generation.")
        return state

    prompt = PromptTemplate(
        template="""
        You are a professional travel planner.

        Create a detailed {days}-day itinerary for a tourist visiting {destination}.
        Use the following top tourist attractions:
        {places}

        For each day, include:
        - Morning: a popular sightseeing spot or activity
        - Afternoon: a cultural or adventure activity
        - Evening: a relaxing or entertainment option

        Format:
        Day 1:
            Morning: ...
            Afternoon: ...
            Evening: ...
        """,
        input_variables=["destination", "places", "days"]
    )

    chain = prompt | llm
    result = chain.invoke({
        "destination": destination,
        "places": ", ".join(place_names),
        "days": str(days)
    })

    itinerary_text = result.content.strip()
    itinerary_lines = [line.strip()
                       for line in itinerary_text.split("\n") if line.strip()]

    state["itinerary"] = itinerary_lines

    print("\n📅 Final Itinerary:")
    for line in itinerary_lines:
        print(line)

    return state
