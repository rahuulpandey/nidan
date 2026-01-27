# services/ai_service.py
# Wraps google.generativeai usage so UI code stays simple.

import google.generativeai as genai
from config import GOOGLE_API_KEY, GOOGLE_API_KEY_2
import streamlit as st
from PIL import Image
import io
from services.doctor_service import recommend_real_doctor


#functions for follow up query
def is_follow_up_query(user_query: str) -> bool:
    q = user_query.lower().strip()

    follow_up_keywords = [
        "this", "that", "it", "those", "these",
        "also", "again", "more", "further",
        "what about", "how about",
        "can i", "should i", "is it", "is that"
    ]

    # Very short questions usually depend on context
    if len(q.split()) <= 4:
        return True

    return any(keyword in q for keyword in follow_up_keywords)


def build_recent_context(chat_history, turns: int = 2) -> str:
    if not chat_history:
        return ""

    recent = chat_history[-turns:]
    context_lines = []

    for chat in recent:
        context_lines.append(f"User: {chat['user']}")
        context_lines.append(f"Assistant: {chat['ai']}")

    return "\n".join(context_lines)


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
        use_context = False
        context_block = ""

        if is_follow_up_query(user_input):
            recent_context = build_recent_context(
                st.session_state.get("chat_history", []),
                turns=2
            )

            if recent_context:
                use_context = True
                context_block = (
                    "Previous conversation context:\n"
                    f"{recent_context}\n\n"
                )

        custom_prompt = (
            "You are a professional and empathetic health assistant. "
            "Provide clear, helpful, and engaging explanations. "
            "Keep responses informative but not overly long. "
            "Use short paragraphs if helpful. "
            "Do not answer queries unrelated to healthcare.\n\n"
        )

        if use_context:
            custom_prompt += context_block

        custom_prompt += f"Current question:\n{user_input}"
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
    

def analyze_medical_image_with_ai(image: Image.Image, modality: str) -> str:
    """
    Educational, non-diagnostic visual interpretation of medical images.
    Uses Gemini Vision to provide structured guidance only.
    """

    if not configure_gemini():
        return "AI image analysis is currently unavailable."

    try:
        # Convert PIL image to bytes
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()

        prompt = f"""
            You are NIDAN.ai, an AI-powered medical imaging assistant designed to support early understanding of medical scans.

                Analyze the uploaded medical scan image (X-ray, CT, MRI, Ultrasound, PET, Mammogram, etc.) and provide:
                    -A clear visual interpretation
                    -Possible medical implications
                    -General medical suggestions or next steps
                    -use simple language which can be understood easily be general person

                You may infer likely conditions in probabilistic and supportive language, but you must:
                    -Avoid definitive diagnosis
                    -Avoid prescribing medication
                    -Encourage professional medical consultation where appropriate

            RESPONSE STRUCTURE

            1. Scan Identification-
                Imaging modality and body region (if identifiable)

            2. Visual Assessment-
                Image quality and orientation
                Key anatomical structures visible

            3. Notable Findings-
                Abnormalities, asymmetry, enlargement, opacities, lesions, fluid, signal or density changes

            4. Possible Clinical Significance-
                Explain what the observed findings may be associated with
                Use language such as may suggest, can be seen in, often associated with

            5. AI Medical Guidance-
                General health guidance
                Lifestyle or monitoring suggestions
                When the user should seek medical attention

            6. Recommended Next Steps-
                Further imaging, lab tests, or specialist consultation if relevant
        """

        model = genai.GenerativeModel("gemini-flash-latest")

        response = model.generate_content(
            [
                prompt,
                {
                    "mime_type": "image/png",
                    "data": image_bytes
                }
            ]
        )

        return response.text if hasattr(response, "text") else "No AI analysis generated."

    except Exception as e:
        return f"AI Image Analysis Error: {str(e)}"


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
