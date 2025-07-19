# main.py

from graph_builder import build_travel_graph

# Compile the graph
travel_planner_app = build_travel_graph()

# Optional: Save the graph visualization
with open("travel_AI.png", "wb") as f:
    f.write(travel_planner_app.get_graph().draw_mermaid_png())

# Invoke the planner
if __name__ == "__main__":
    travel_planner_app.invoke({
        'sourse': 'Hyderabad',
        'destination': 'chennai',
        'days': 5
    })
