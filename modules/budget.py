# modules/budget.py

import random
import json
from utils.types import AgentClass


def budget(state: AgentClass):

    try:
        print("📦 Incoming state keys to budget:", state.keys())

        # Parse confirm_ticket
        if isinstance(state["confirm_ticket"], str):
            confirm_ticket = json.loads(state["confirm_ticket"])
        else:
            confirm_ticket = state["confirm_ticket"]

        # Parse return_ticket
        if isinstance(state["return_ticket"], str):
            return_ticket = json.loads(state["return_ticket"])
        else:
            return_ticket = state["return_ticket"]

        # Parse hotel
        if "hotel" not in state:
            raise ValueError("❌ Missing 'hotel' info in state!")

        hotel_price = state["hotel"].get("price_per_night", "0")
        hotel_price_per_night = int(
            str(hotel_price).replace("₹", "").replace(",", ""))

        days = int(state["days"])
        food_expense = [random.randint(250, 700) for _ in range(days)]
        misc_expense = [random.randint(200, 500) for _ in range(days)]

        daily_budget = []
        total = 0

        print("\n📆 Day-by-Day Trip Budget:")
        for i in range(days):
            hotel_cost = hotel_price_per_night
            food = food_expense[i]
            misc = misc_expense[i]
            day_total = hotel_cost + food + misc
            total += day_total

            print(
                f"Day {i+1}: 🏨 Hotel ₹{hotel_cost} | 🍽️ Food ₹{food} | 💼 Other ₹{misc} => 🧾 Total ₹{day_total}"
            )

            daily_budget.append({
                "day": i + 1,
                "hotel": hotel_cost,
                "food": food,
                "misc": misc,
                "total": day_total
            })

        ticket_price = int(confirm_ticket["price"])
        return_ticket_price = int(return_ticket["price"])

        print(f"\n🎟️ Initial Ticket Price: ₹{ticket_price}")
        print(f"🔁 Return Ticket Price: ₹{return_ticket_price}")

        trip_budget = total + ticket_price + return_ticket_price
        print(f"💰 Total Trip Budget: ₹{trip_budget}")

        state["daily_budget"] = daily_budget  # ✅ Add this
        # ✅ Also explicitly add total_budget
        state["total_budget"] = trip_budget

        return state

    except Exception as e:
        print(f"❌ Error in budget calculation: {e}")
        return state
