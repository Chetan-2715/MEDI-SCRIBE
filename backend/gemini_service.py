import google.generativeai as genai
import os
import json
from utils.dosage_calculator import calculate_duration

# Configure Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

generation_config = {
    "temperature": 0.1,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
    "response_mime_type": "application/json"
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

SYSTEM_PROMPT = """
You are a medical assistant OCR expert. Your job is to extract structured medicine data from the raw text provided.
Analyze the text and extract a list of medicines with these fields:
- name: (string) Medicine name (e.g., Augmentin 625)
- type: (string) One of: tablet, syrup, ointment, injection, other
- dosage_pattern: (string) e.g., 1-0-1, 1-1-1, OD, BD, TDS. If not found, use null.
- instructions: (string) e.g., After food, Before food.
- quantity: (number) Total count of tablets/bottles if mentioned.
- duration_days: (number) Duration in days if mentioned.
- purpose: (string) Reason for medication (e.g. Pain relief, Antibiotic) - Infer this from the medicine name if not explicitly stated.

Output strictly valid JSON with this structure:
{
  "medicines": [
    { ... }
  ]
}
If duration_days is missing but quantity and dosage_pattern are present, leave it null, we will calculate it.
"""

def extract_medicine_info(ocr_text: str) -> dict:
    """
    Sends OCR text to Gemini and gets structured JSON.
    Auto-calculates duration if missing.
    """
    prompt = f"Extract medicine details from this prescription text:\n\n{ocr_text}"
    
    chat_session = model.start_chat(
        history=[
            {"role": "user", "parts": [SYSTEM_PROMPT]},
        ]
    )
    
    response = chat_session.send_message(prompt)
    
    try:
        data = json.loads(response.text)
        medicines = data.get("medicines", [])
        
        # Post-processing: Calculate duration if missing
        for med in medicines:
            if not med.get("duration_days") and med.get("quantity") and med.get("dosage_pattern"):
                med["duration_days"] = calculate_duration(med["quantity"], med["dosage_pattern"])
                
        return {"medicines": medicines}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from Gemini: {e}")
        return {"medicines": []}

