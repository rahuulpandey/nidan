# # config.py
# # Central place to store config like API keys and paths.
# import os
# from dotenv import load_dotenv

# def load_env():
#     # Load environment variables from .env (if present)
#     load_dotenv()

# # IMPORTANT: Do NOT hardcode API keys in source.
# # Set GOOGLE_API_KEY and GOOGLE_API_KEY_2 in your environment or .env
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", None)
# GOOGLE_API_KEY_2 = os.getenv("GOOGLE_API_KEY_2", None)

# IMAGE_FOLDER = os.getenv("IMAGE_FOLDER", r"C:\Users\pande\Desktop\new project\Final Project AI Assistant\Final Project\images")
# CSS_FILE = os.getenv("CSS_FILE", "styles.css")


# print("KEY LOADED:", GOOGLE_API_KEY)




# config.py
# Central place to store config like API keys and paths.



import os
from dotenv import load_dotenv

# Load .env immediately when this module is imported
load_dotenv()

def load_env():
    """
    Kept for compatibility. If you ever want to reload .env at runtime,
    you can call this, but normally it's not needed anymore.
    """
    load_dotenv()

# Now these read from the environment that was just loaded
GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY", None)
GOOGLE_API_KEY_2=os.getenv("GOOGLE_API_KEY_2", None)
GOOGLE_MAPS_API_KEY=os.getenv("GOOGLE_MAPS_API_KEY")

IMAGE_FOLDER = os.getenv("IMAGE_FOLDER",  r"C:\Users\pande\Desktop\new project\Final Project AI Assistant\Final Project\images")
CSS_FILE    = os.getenv("CSS_FILE", "styles.css")
