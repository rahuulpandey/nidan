# services/ai_service.py
# Wraps google.generativeai usage so UI code stays simple.

import google.generativeai as genai
from config import GOOGLE_API_KEY, GOOGLE_API_KEY_2
import streamlit as st

#new import for doctor search
from services.doctor_service import recommend_real_doctor


def configure_gemini(api_key=None):
    """Configure genai SDK with given API key (or use config)."""
    key = api_key or GOOGLE_API_KEY
    if not key:
        # Surface friendly message to Streamlit UI
        st.error("⚠️ Missing GOOGLE_API_KEY environment variable. Set it before running.")
        return False
    genai.configure(api_key=key)
    return True

def chat_with_ai(user_input: str):
    """
    Ask the model to respond as a short health assistant.
    Returns the response text or an error string.
    """
    if not configure_gemini():
        return "⚠️ AI service is unavailable due to missing API Key."

    try:
        custom_prompt = (
            "You are a professional and empathetic health assistant. "
            "Provide clear, helpful, and engaging explanations. "
            "Keep responses informative but not overly long. "
            "Use short paragraphs if helpful. "
            "Do not answer queries unrelated to healthcare.\n\n"
            f"{user_input}"
        )
        model = genai.GenerativeModel(model_name="gemini-flash-latest", 
                                      generation_config={
                                                            "temperature": 0.7,
                                                            "top_p": 0.95,
                                                            "max_output_tokens": 1024
                                                        }
        )
        response = model.generate_content(custom_prompt)
        return response.text if hasattr(response, "text") else "No response from AI."
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"
    




def recommend_doctor(symptom: str, location: str):

        return recommend_real_doctor(symptom, location)



#     """Return a single concise doctor recommendation from the model."""
#     # Use alternate API key if provided, else fall back to normal one.
#     if not configure_gemini(GOOGLE_API_KEY_2 or GOOGLE_API_KEY):
#         return "⚠️ AI service is unavailable due to missing API Key."

#     try:
#         # prompt = (
#         #     f"You are a helpful health assistant. Based on the symptom '{symptom}' and "
#         #     f"location '{location}', suggest a single doctor by name, contact and experience. "
#         #     "If you cannot find specifics, provide dummy data in the format:\n"
#         #     "- Doctor Name:\n- Contact:\n- Experience: ____\n\nReturn only the concise details."
#         # )

#         prompt = (
#             f"You are a helpful health assistant. The user is experiencing the symptom '{symptom}' in the location '{location}'.Recommend ONE appropriate specialist doctor. "
#             # f"in the location '{location}'. Recommend ONE appropriate specialist doctor. "
#             # "If real data cannot be confirmed, provide realistic placeholder dummy details, and clearly label them as such.\n\n"
#             "Use this exact format:\n"
#             "- Doctor Name: _______\n"
#             "- Experience: ____ years\n"
#             "- Specialty: _______\n"
#             "- Contact: _______\n"
#             "- Experience: ____ years\n"
#             "- Note: This is not a medical diagnosis. Please consult a certified doctor for confirmation.\n\n"
#             "Return ONLY the response in this format. Do not add extra sentences or explanations."
#         )



#         model = genai.GenerativeModel(model_name="gemini-flash-latest")
#         response = model.generate_content(prompt)
#         return response.text if hasattr(response, "text") else "No response from AI."
#     except Exception as e:
#         return f"⚠️ AI Error: {str(e)}"
