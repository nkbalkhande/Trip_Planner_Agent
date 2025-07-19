# graph_builder.py

from langgraph.graph import StateGraph
from utils.types import AgentClass
from modules.tickets import book_ticket, return_ticket
from modules.hotel import hotel_booking
from modules.itinerary import itinerary
from modules.recommendation import recommendation
from modules.budget import budget


def build_travel_graph():
    graph = StateGraph(AgentClass)

    # Register nodes
    graph.add_node("book_ticket", book_ticket)
    graph.add_node("hotel_booking", hotel_booking)
    graph.add_node("itinerary", itinerary)
    graph.add_node("recommendation", recommendation)
    graph.add_node("return_ticket", return_ticket)
    graph.add_node("budget", budget)

    # Define transitions
    graph.set_entry_point("book_ticket")
    graph.add_edge("book_ticket", "hotel_booking")
    graph.add_edge("hotel_booking", "itinerary")
    graph.add_edge("itinerary", "recommendation")
    graph.add_edge("recommendation", "return_ticket")
    graph.add_edge("return_ticket", "budget")

    # Compile and return the app
    return graph.compile()
