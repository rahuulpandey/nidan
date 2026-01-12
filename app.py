# app.py
# Entrypoint for the Streamlit app. Keeps the app bootstrap minimal.
from config import load_env
load_env()
from ui import run_app

# from processor import (
#     pil_to_gray_np, enhance_xray, enhance_ct, enhance_mri,
#     enhance_generic, analyze_quality, to_pil
# )

def main():
    # load_env()  # loads .env if present
    run_app()

if __name__ == "__main__":
    main()
