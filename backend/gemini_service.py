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
You are a medical assistant expert. Your job is to analyze the prescription image provided and extract structured data.
Extract the following fields:
- doctor_name: (string) Name of the doctor/hospital (e.g. Dr. Smith). Use "Unknown" if not found.
- patient_name: (string) Name of the patient. Use "Unknown" if not found.
- medicines: (list) A list of medicines with these fields:
    - name: (string) Medicine name (e.g., Augmentin 625)
    - type: (string) One of: tablet, syrup, ointment, injection, other
    - dosage_pattern: (string) e.g., 1-0-1, 1-1-1, OD, BD, TDS. If not found, use null.
    - instructions: (string) e.g., After food, Before food.
    - quantity: (number) Total count of tablets/bottles if mentioned.
    - duration_days: (number) Duration in days if mentioned.
    - purpose: (string) Reason for medication (e.g. Pain relief, Antibiotic) - Infer this from the medicine name if not explicitly stated.

Output strictly valid JSON with this structure:
{
  "doctor_name": "...",
  "patient_name": "...",
  "medicines": [
    { ... }
  ]
}
If duration_days is missing but quantity and dosage_pattern are present, leave it null, we will calculate it.
"""

def extract_medicine_info(image_bytes: bytes) -> dict:
    """
    Sends prescription image to Gemini and gets structured JSON.
    Auto-calculates duration if missing.
    """
    try:
        response = model.generate_content([
            {"mime_type": "image/jpeg", "data": image_bytes},
            SYSTEM_PROMPT
        ])
        
        data = json.loads(response.text)
        medicines = data.get("medicines", [])
        
        # Post-processing: Calculate duration if missing
        for med in medicines:
            if not med.get("duration_days") and med.get("quantity") and med.get("dosage_pattern"):
                med["duration_days"] = calculate_duration(med["quantity"], med["dosage_pattern"])
                
        return data # Returns full data including doctor/patient names
    except Exception as e:
        print(f"Error decoding JSON from Gemini: {e}")
        return {"medicines": [], "doctor_name": "Unknown", "patient_name": "Unknown"}

