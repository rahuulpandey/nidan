# NIDAN.ai - Refactored Streamlit App

## Setup
1. Create virtualenv and install:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the project root and add:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   GOOGLE_API_KEY_2=optional_second_key
   ```

   **Do not commit your keys to source control.**

3. Place your images in `images/` (img1.jpg ... img5.jpg) or change `IMAGE_FOLDER` in `config.py`.

## Run
```bash
streamlit run app.py
```

## What was changed
- Split large script into small modules:
  - `app.py` (entry)
  - `config.py` (env)
  - `utils.py` (helpers)
  - `services/ai_service.py`, `services/image_service.py`, `services/speech_service.py`
  - `ui.py` (Streamlit UI)
- Removed hard-coded API keys from source; use `.env` instead.
- Added comments and clearer function boundaries.
