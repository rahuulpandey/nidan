# config file containing api keys and we use it for importing keys to other parts of code

import os
from dotenv import load_dotenv

# Load .env immediately when this module is imported
load_dotenv()

def load_env():
    load_dotenv()

# Now these read from the environment that was just loaded
GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY", None)
GOOGLE_API_KEY_2=os.getenv("GOOGLE_API_KEY_2", None)
GOOGLE_MAPS_API_KEY=os.getenv("GOOGLE_MAPS_API_KEY")

IMAGE_FOLDER = os.getenv("IMAGE_FOLDER",  r"C:\Users\pande\Desktop\new project\Final Project AI Assistant\Final Project\images")
CSS_FILE    = os.getenv("CSS_FILE", "styles.css")
