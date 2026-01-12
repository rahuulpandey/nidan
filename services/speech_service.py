# services/speech_service.py
# Encapsulates pyttsx3 and speech_recognition usage so the UI only calls simple functions.

import threading
import pyttsx3
import speech_recognition as sr
import streamlit as st

def speak_text(text: str):
    """Speak the provided text in a background thread (non-blocking)."""
    def run_speech():
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            # Use streamlit to show a warning if something fails
            st.warning(f"Speech error: {e}")

    threading.Thread(target=run_speech, daemon=True).start()

# def listen_speech(timeout: int = 5) -> str:
#     """Listen on microphone and return recognized text or an error message."""
#     recognizer = sr.Recognizer()
#     try:
#         with sr.Microphone() as source:
#             st.info("Listening... Please speak")
#             audio = recognizer.listen(source, timeout=timeout)
#             try:
#                 speech_text = recognizer.recognize_google(audio)
#                 return speech_text
#             except sr.UnknownValueError:
#                 return "Sorry, I didn't understand that."
#             except sr.RequestError:
#                 return "Sorry, there was an issue with the speech service."
#     except Exception as e:
#         return f"Microphone error: {e}"


def listen_speech(phrase_time_limit: int = 8) -> str:
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(
                source,
                phrase_time_limit=phrase_time_limit
            )

        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return ""

    except Exception:
        return ""