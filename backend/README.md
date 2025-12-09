# Medi-Scribe Backend

This is the FastAPI backend for Medi-Scribe, handling OCR, AI processing, and Database interactions.

## Setup

1.  **Install Dependencies**:
    ```bash
    cd backend
    pip install -r requirements.txt
    ```

2.  **Environment Variables**:
    Copy `.env.example` to `.env` and fill in:
    *   `SUPABASE_URL`, `SUPABASE_KEY` (Service Role)
    *   `GEMINI_API_KEY`
    *   `GOOGLE_APPLICATION_CREDENTIALS` (Path to Google Cloud JSON key)

3.  **Run Server**:
    ```bash
    uvicorn main:app --reload
    ```
    Server runs at `http://localhost:8000`.

## API Endpoints

*   `POST /upload-prescription`: Upload image, extraction medicine info.
*   `GET /prescriptions`: List user prescriptions.
*   `GET /prescriptions/{id}/medicines`: Get details.
*   `POST /reminders`: Generate Google Calendar links.

## Logic
*   **OCR**: Google Vision API extracts raw text.
*   **AI**: Gemini 1.5 Flash parses structured medical data.
*   **DB**: Supabase stores records.
