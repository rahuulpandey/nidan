# services/doctor_service.py
# Real doctor recommendation using:
# 1) Gemini -> decide specialist from symptom
# 2) Google Maps Places -> fetch real doctors near location
# 3) Gemini -> format a nice, safe response




import os
from typing import List, Dict, Optional
# print("Loaded GEMINI KEY:", os.environ.get("GEMINI_API_KEY"))
import googlemaps
import google.generativeai as genai



# ---------- Setup: Gemini + Google Maps ----------

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set in environment / .env")

if not GOOGLE_MAPS_API_KEY:
    raise RuntimeError("GOOGLE_MAPS_API_KEY is not set in environment / .env")

genai.configure(api_key=GEMINI_API_KEY)
# You can swap the model name if you want
gemini_model = genai.GenerativeModel("gemini-2.0-flash")

gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)


# ---------- 1) Symptom -> Specialist ----------

def _get_specialist_for_symptom(symptom: str) -> str:
    """
    Use Gemini to map free-text symptom to a single specialist type,
    e.g. 'Cardiologist', 'Dermatologist', 'Orthopedic Surgeon'.
    """
    prompt = f"""
You are a medical triage assistant.

The user reports this symptom or concern:
\"\"\"{symptom}\"\"\".

Based on this, reply with the SINGLE most appropriate type of doctor
the user should consult. Examples: "Cardiologist", "Dermatologist",
"Psychiatrist", "Neurologist", "Orthopedic Surgeon", "General Physician".

Return ONLY the specialist name, no extra words, no explanation.
    """.strip()

    resp = gemini_model.generate_content(prompt)
    specialist = resp.text.strip()

    # Clean up common patterns like "Specialist: Cardiologist"
    specialist = specialist.replace("Specialist:", "").strip()
    specialist = specialist.replace("Doctor type:", "").strip()

    # Avoid empty fallback
    if not specialist:
        specialist = "General Physician"

    return specialist


# ---------- 2) Google Places: find real doctors ----------

def _geocode_location(location: str) -> Optional[Dict]:
    results = gmaps.geocode(location)
    if not results:
        return None
    return results[0]["geometry"]["location"]  # { 'lat': ..., 'lng': ... }


def _find_doctors_near_location(
    specialist: str,
    location_text: str,
    max_results: int = 5,
) -> List[Dict]:
    """
    Use Google Places to find real doctors/clinics near the given location.
    Returns a list of dicts with name, address, rating, reviews, phone.
    """
    loc = _geocode_location(location_text)
    if not loc:
        return []

    query = f"{specialist} doctor"

    places_result = gmaps.places_nearby(
        location=(loc["lat"], loc["lng"]),
        radius=5000,  # 5km radius; tweak as you like
        keyword=query,
        type="doctor",
    )

    candidates = places_result.get("results", [])[:max_results]
    doctors: List[Dict] = []

    for place in candidates:
        place_id = place.get("place_id")
        name = place.get("name")
        address = place.get("vicinity") or place.get("formatted_address")
        rating = place.get("rating")
        reviews = place.get("user_ratings_total")

        phone = None
        if place_id:
            # Extra call to get phone number if available
            details = gmaps.place(place_id=place_id, fields=["formatted_phone_number"])
            phone = (
                details.get("result", {})
                .get("formatted_phone_number", None)
            )

        doctors.append(
            {
                "name": name,
                "address": address,
                "rating": rating,
                "reviews": reviews,
                "phone": phone,
            }
        )

    return doctors


def _pick_best_doctor(doctors: List[Dict]) -> Optional[Dict]:
    """
    Choose the best doctor based on rating + review count.
    """
    if not doctors:
        return None

    def score(doc):
        rating = doc.get("rating") or 0
        reviews = doc.get("reviews") or 0
        # Weighted score: rating + small factor of reviews
        return (rating, reviews)

    # Sort descending by score
    doctors_sorted = sorted(doctors, key=score, reverse=True)
    return doctors_sorted[0]


# ---------- 3) Gemini: format final message ----------

def _format_recommendation_with_gemini(
    symptom: str,
    location: str,
    specialist: str,
    doctor: Optional[Dict],
) -> str:
    """
    Take the chosen doctor (real from Google) + context and ask Gemini
    to format a nice but constrained recommendation.
    """
    if not doctor:
        # No doctor found -> graceful fallback
        fallback_prompt = f"""
You are a helpful health assistant.

The user has symptom:
\"\"\"{symptom}\"\"\"

Location:
\"\"\"{location}\"\"\"

You could not find any specific doctors in that location.
Create a short, friendly message that:

1. Suggests the appropriate specialist type: {specialist}
2. Encourages the user to search on local platforms (like Google Maps, Practo, etc.)
3. Includes this disclaimer text at the end:
   "This is not medical advice. Please consult a licensed doctor and verify all details."

Return 3-5 sentences, no bullet points.
        """.strip()

        resp = gemini_model.generate_content(fallback_prompt)
        return resp.text.strip()

    name = doctor.get("name") or "Unknown Clinic"
    address = doctor.get("address") or location
    rating = doctor.get("rating")
    reviews = doctor.get("reviews")
    phone = doctor.get("phone") or "Not available"

    rating_text = f"{rating} / 5" if rating is not None else "Not available"
    reviews_text = f"{reviews} Google reviews" if reviews is not None else "No review data"

    prompt = f"""
You are a helpful health assistant.

User symptom:
\"\"\"{symptom}\"\"\"

User location:
\"\"\"{location}\"\"\"

Inferred specialist type:
\"\"\"{specialist}\"\"\"

Here is a REAL doctor/clinic fetched from Google Places:
- Name: {name}
- Address: {address}
- Phone: {phone}
- Rating: {rating_text}
- Reviews: {reviews_text}

Task:
Write a short recommendation for the user USING ONLY this information.
Do NOT invent any new doctor name, phone number, hospital, or claim anything clinical
about the user's health.

Then output the result in EXACTLY this format:

- Doctor Name: <name>
- Specialty: {specialist}
- Location: <address>
- Contact: <phone>
- Rating: <rating_text> ({reviews_text})
- Note: This is not medical advice. Verify details and consult a licensed doctor.

Do not add any extra lines before or after this block.
    """.strip()

    resp = gemini_model.generate_content(prompt)
    return resp.text.strip()


# ---------- Public function used by the app ----------

def recommend_real_doctor(symptom: str, location: str) -> str:
    """
    Main entrypoint:
    1) Gemini -> specialist
    2) Google Maps -> real doctors near location
    3) Gemini -> formatted recommendation text
    """
    symptom = (symptom or "").strip()
    location = (location or "").strip()

    if not symptom:
        return "Please provide a symptom so I can recommend a suitable specialist."

    if not location:
        return "Please provide a location (city/area) so I can look for doctors near you."

    specialist = _get_specialist_for_symptom(symptom)
    doctors = _find_doctors_near_location(specialist, location, max_results=5)
    best_doctor = _pick_best_doctor(doctors)

    final_text = _format_recommendation_with_gemini(
        symptom=symptom,
        location=location,
        specialist=specialist,
        doctor=best_doctor,
    )
    return final_text
