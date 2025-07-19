# config.py
import os
from dotenv import load_dotenv
import googlemaps

load_dotenv()

# API Keys
GEMINI_KEY = os.getenv('Gemini_key')
GROQ_KEY = os.getenv('Groq_key')
GOOGLE_MAP_KEY = os.getenv("Gemini_map")

# Initialize Google Maps client
gmaps = googlemaps.Client(key=GOOGLE_MAP_KEY)
