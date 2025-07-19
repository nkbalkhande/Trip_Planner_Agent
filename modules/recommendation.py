# modules/recommendation.py

from langchain_core.prompts import PromptTemplate
from llm.model import llm
from utils.types import AgentClass
from modules.tickets import fetch_top_places


def recommendation(state: AgentClass) -> AgentClass:
    destination = state.get('destination')

    if not destination:
        print("❌ Destination is required.")
        return state

    try:
        place_names = fetch_top_places.invoke({'destination': destination})
    except Exception as e:
        print("❌ Error using place-fetch tool:", e)
        return state

    if not place_names:
        print("❌ No places found for recommendations.")
        return state

    recommendation_prompt = PromptTemplate(
        template="""
        You are a professional travel guide.

        Based on the following top tourist attractions in {destination}, suggest the must-visit places for a first-time traveler.

        Tourist Attractions:
        {places}

        Return a short, engaging paragraph recommending 5–7 top places and why they're worth visiting.
        """,
        input_variables=["destination", "places"]
    )

    chain = recommendation_prompt | llm

    try:
        response = chain.invoke({
            "destination": destination,
            "places": ", ".join(place_names)
        })
        recommendation_text = response.content.strip()
    except Exception as e:
        print("❌ Error generating recommendation:", e)
        return state

    state["recommendation"] = recommendation_text

    print("\n🌟 Travel Recommendations:")
    print(recommendation_text)

    return state
