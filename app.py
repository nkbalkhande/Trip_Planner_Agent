import streamlit as st
import json
from datetime import date, timedelta, datetime
from graph_builder import build_travel_graph

# ---------------------- Streamlit Config ----------------------
st.set_page_config(page_title="AI TRIP Travel Planner", page_icon="🧳")
st.title("🧳 AI TRIP Travel Planner")

# ---------------------- Utilities ----------------------


def parse_json(obj):
    if isinstance(obj, str):
        try:
            return json.loads(obj)
        except:
            return {}
    return obj


# ---------------------- Session State ----------------------
if "checkin" not in st.session_state:
    st.session_state.checkin = date.today()

if "days" not in st.session_state:
    st.session_state.days = 5

# Auto-update checkout based on checkin and days
st.session_state.checkout = st.session_state.checkin + \
    timedelta(days=st.session_state.days)

# ---------------------- Dynamic Inputs (outside form) ----------------------
st.session_state.checkin = st.date_input(
    "Check-in Date", value=st.session_state.checkin)
st.session_state.days = st.number_input(
    "Number of Days", min_value=1, max_value=30, value=st.session_state.days)

# ---------------------- Form Inputs ----------------------
with st.form("planner_form"):
    source = st.text_input("Enter Source Location")
    destination = st.text_input("Enter Destination")

    # Show calculated checkout (read-only)
    st.markdown(f"**Checkout Date:** `{st.session_state.checkout}`")

    submit = st.form_submit_button("Plan My Trip")

# Utility to format date string (e.g., 2025-07-18 → 18 July 2025)


def format_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d %B %Y")
    except:
        return date_str


# ---------------------- Backend Logic ----------------------
if submit:
    st.subheader("📦 Planning in Progress...")

    try:
        travel_planner_app = build_travel_graph()
        state = travel_planner_app.invoke({
            "sourse": source,  # backend expects 'sourse'
            "destination": destination,
            "days": st.session_state.days,
            "checkin_date": st.session_state.checkin.strftime("%Y-%m-%d"),
            "checkout_date": st.session_state.checkout.strftime("%Y-%m-%d")
        })

        st.success("🎉 Trip Planned Successfully!")

        # ---------- Confirmed Ticket ----------
        st.subheader("🛫 Confirmed Ticket")
        confirm_ticket = parse_json(state.get("confirm_ticket", {}))
        if confirm_ticket:
            st.write(f"**Type:** {confirm_ticket.get('type', 'N/A')}")
            st.write(f"**Name:** {confirm_ticket.get('name', 'N/A')}")
            st.write(f"**From:** {confirm_ticket.get('from', 'N/A')}")
            st.write(f"**To:** {confirm_ticket.get('to', 'N/A')}")
            st.write(f"**Cabin:** {confirm_ticket.get('cabin', 'N/A')}")
            st.write(
                f"**Price:** ₹{confirm_ticket.get('price', 'N/A')} {confirm_ticket.get('currency', '')}")
        else:
            st.info("No ticket has been confirmed yet.")

        # ---------- Return Ticket ----------
        st.subheader("🔁 Return Ticket")
        return_ticket = parse_json(state.get("return_ticket", {}))
        if return_ticket:
            st.write(f"**Type:** {return_ticket.get('type', 'N/A')}")
            st.write(f"**Name:** {return_ticket.get('name', 'N/A')}")
            st.write(f"**From:** {return_ticket.get('from', 'N/A')}")
            st.write(f"**To:** {return_ticket.get('to', 'N/A')}")
            st.write(f"**Cabin:** {return_ticket.get('cabin', 'N/A')}")
            st.write(
                f"**Price:** ₹{return_ticket.get('price', 'N/A')} {return_ticket.get('currency', '')}")
        else:
            st.info("No return ticket found.")

        # ---------- Hotel ----------
        st.subheader("🏨 Hotel Details")
        hotel = parse_json(state.get("hotel", {}))
        if hotel:
            st.markdown(f"✅ **Name:** `{hotel.get('name', 'N/A')}`")
            st.markdown(
                f"💵 **Price per night:** ₹{hotel.get('price_per_night', 'N/A')}")
            st.markdown(f"🧾 **Total:** ₹{hotel.get('total_price', 'N/A')}")
        else:
            st.info("No hotel selected.")

        # ---------- Itinerary ----------
        st.subheader("📆 Itinerary")
        itinerary = state.get("itinerary", [])
        if isinstance(itinerary, str):
            itinerary = itinerary.split("\n")
        if itinerary:
            for item in itinerary:
                st.markdown(f"- {item.strip()}")
        else:
            st.warning("No itinerary available.")

        # ---------- Recommendations ----------
        st.subheader("📌 Recommendations")
        st.markdown(state.get("recommendation", "No recommendations found."))

        # ---------- Daily Budget ----------
        st.subheader("📊 Day-by-Day Budget Breakdown")
        daily_budget = state.get("daily_budget", [])
        if daily_budget:
            st.table([
                {
                    "Day": day["day"],
                    "🏨 Hotel": f"₹{day['hotel']}",
                    "🍽️ Food": f"₹{day['food']}",
                    "💼 Misc": f"₹{day['misc']}",
                    "🧾 Total": f"₹{day['total']}"
                }
                for day in daily_budget
            ])
        else:
            st.warning("No daily budget breakdown available.")

        # ---------- Total Budget ----------
        st.subheader("💰 Total Trip Budget")
        st.markdown(f"### ₹ {state.get('total_budget', 'N/A')}")

    except Exception as e:
        st.error(f"❌ Something went wrong: {e}")
