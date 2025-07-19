# llm/model.py

from config import GEMINI_KEY, GROQ_KEY
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

# Default to Gemini, fallback to Groq
try:
    llm = ChatGoogleGenerativeAI(
        model='gemini-2.0-flash',
        google_api_key=GEMINI_KEY,
        temperature=0.8
    )

    # Try a small test to confirm the model works
    _ = llm.invoke("ping")  # Throws if setup fails

except Exception as e:
    print(f"[⚠️ Gemini Fallback] Error with Gemini: {e}")
    print("➡️ Switching to Groq LLaMA3...")

    # Fallback to Groq
    llm = ChatGroq(
        model='llama3-70b-8192',
        api_key=GROQ_KEY
    )
