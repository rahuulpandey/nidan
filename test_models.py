import google.generativeai as genai
from config import GOOGLE_API_KEY

# print("KEY LOADED:", GOOGLE_API_KEY)

genai.configure(api_key=GOOGLE_API_KEY)

print("Listing models...\n")
for m in genai.list_models():
    print(m.name, " | supported: ", m.supported_generation_methods)
