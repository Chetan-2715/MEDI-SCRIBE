import google.generativeai as genai
import os
import json
import typing_extensions as typing
from utils.dosage_calculator import calculate_duration

# Configure Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Define the Exact Schema we want (Strict Mode)
class Medicine(typing.TypedDict):
    name: str
    type: str
    dosage_pattern: str
    instructions: str
    quantity: int
    duration_days: int
    purpose: str

class PrescriptionResponse(typing.TypedDict):
    doctor_name: str
    patient_name: str
    medicines: list[Medicine]

# Configure model with the schema
model = genai.GenerativeModel(
    model_name="gemini-flash-latest",
    generation_config={
        "response_mime_type": "application/json",
        "response_schema": PrescriptionResponse
    }
)

SYSTEM_PROMPT = """
You are an expert pharmacist digitizing prescriptions. 
Analyze the image and extract the medicine list.

### RULES:
1. **Type**: Must be one of: 'tablet', 'syrup', 'ointment', 'injection', 'other'. (Lowercase).
2. **Handwriting**: "Tab" = tablet, "Cap" = tablet/capsule.
3. **Dosage**: Look for "1-0-1" patterns.
"""

def extract_medicine_info(image_bytes: bytes) -> dict:
    """
    Sends prescription image to Gemini with strict schema enforcement.
    """
    try:
        response = model.generate_content([
            {"mime_type": "image/jpeg", "data": image_bytes},
            SYSTEM_PROMPT
        ])
        
        data = json.loads(response.text)
        medicines = data.get("medicines", [])
        
        # Post-processing to Clean Data
        for med in medicines:
            # 1. FIX: Force type to lowercase to satisfy DB constraint
            if med.get("type"):
                med["type"] = med["type"].lower()

            # 2. Fix potential 0 values
            q = med.get("quantity")
            d = med.get("dosage_pattern")
            
            if (not med.get("duration_days") or med["duration_days"] == 0) and q and d:
                med["duration_days"] = calculate_duration(q, d)
                
        return data

    except Exception as e:
        print(f"Gemini Analysis Failed: {e}")
        return {"medicines": [], "doctor_name": "Unknown", "patient_name": "Unknown"}