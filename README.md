# 🧳 AI Trip Travel Planner

An intelligent, AI-powered travel planner built using **LangGraph**, **Streamlit**, and **LLMs (Groq/Gemini)** that helps users:
- Book flight tickets (with Amadeus API)
- Get hotels details
- Generate personalized multi-day itineraries
- Provide local recommendations
- Estimate daily and total trip budget

---

## 🚀 Features

### ✅ Interactive User Input via Streamlit
- Select **source** and **destination**
- Choose **check-in date** and **number of days**
- Streamlit handles user interactions (human-in-the-loop)

### ✈️ Ticket Booking
- Fetches **confirmed** and **return** flight tickets using the **Amadeus Flight API**
- Includes:
  - Airline name
  - From/To airport codes
  - Cabin type
  - Price (with currency)
  - Departure Date

### 🏨 Hotel Suggestions
- get a hotel details based on the destination using **RapidAPI's Hotel Search API**
- Displays:
  - Hotel name
  - Price per night
  - Total cost (based on days)

### 📆 Itinerary Generator
- Creates a **day-wise itinerary** with:
  - Tourist spots
  - Local experiences
  - Food options
  - Balanced travel pace

### 📌 Local Recommendations
- Offers tips and cultural highlights to improve the travel experience

### 📊 Budget Breakdown
- Shows **daily breakdown** of:
  - Hotel
  - Food
  - Miscellaneous
- Calculates **total trip cost**, including tickets and stay

---

## 🧠 Tech Stack

| Tech | Usage |
|------|-------|
| **LangGraph** | Modular agent workflow |
| **LLMs (Groq/Gemini)** | For natural language itinerary and planning |
| **Amadeus API** | Real-time flight data |
| **Rapid's Hotel API** | Real-time hotel data |
| **Streamlit** | Frontend user interface |
| **Python** | Backend logic and LangGraph tools |
| **.env** | API key management |

---

## 🗂️ Project Structure

```
├── app.py # Streamlit entry point
├── config.py # Environment and key config
├── graph_builder.py # LangGraph workflow
├── llm/
│ └── model.py # Groq/Gemini LLM initialization
├── modules/
│ ├── ticket.py # Ticket generation using Amadeus API
│ ├── hotel.py # Hotel selection logic
│ ├── itinerary.py # Itinerary planner
│ ├── recommendation.py # Destination highlights
│ └── budget.py # Daily & total budget calculator
├── utils/
│ └── types.py # Custom types
├── .env # API keys (ignored in Git)
└── requirements.txt # Python dependencies
```


---

## 🔑 .env Setup

Make sure to create a `.env` file in the root directory:
```
GEMINI_KEY=your_google_gemini_api_key
GROQ_API_KEY=your_groq_api_key
AMADEUS_API_KEY=your_amadeus_api_key
AMADEUS_API_SECRET=your_amadeus_api_secret
Gemini_map=your_google_maps_key
RAPIDAPI_HOST = your_api_host_here
RAPIDAPI_KEY = your_rapidapi_key_here
```


> ⚠️ **Keep your API keys secure and do not commit `.env` to version control!**

---

## 🖥️ Run Locally

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

2. **Run the Streamlit app**
```
streamlit run app.py
```

## ScreenShots



## 👨‍💻 Author  
**Nilesh Balkhande**  

Computer Science Graduate | Data Science & AI Enthusiast  <br>  
Reach me via [LinkedIn](https://www.linkedin.com/in/nilesh-balkhande-662283323/) or [GitHub](https://github.com/nkbalkhande)


