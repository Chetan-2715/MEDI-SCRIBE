import google.generativeai as genai
import os
import json
import typing_extensions as typing
from utils.dosage_calculator import calculate_duration

# Configure Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# --- 1. Define Schema with "Descriptive" Field Names ---
# We use 'medical_explanation' instead of 'purpose' here to force the AI to write sentences.
class Medicine(typing.TypedDict):
    name: str
    type: str
    dosage_pattern: str
    instructions: str
    quantity: int
    duration_days: int
    medical_explanation: str  # <--- Renamed from 'purpose' to force detail

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

### EXTRACTION RULES:
1. **Name**: Identify the brand or generic name accurately.
2. **Type**: Must be one of: 'tablet', 'syrup', 'ointment', 'injection', 'other'. (Lowercase).
3. **Dosage**: Look for "1-0-1", "OD", "BD" patterns.
4. **Medical Explanation**: For every medicine, provide a **1-2 sentence clinical explanation** of its use.
   - Example: "A proton pump inhibitor used to reduce stomach acid and treat heartburn."
   - Example: "An antibiotic composition used to treat bacterial infections in the respiratory tract."
   - **DO NOT** use short tags like "Antibiotic" or "General Health". Be descriptive.
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
        
        # Post-processing
        for med in medicines:
            # 1. MAP BACK: Move the detailed explanation to the 'purpose' key
            # This ensures it saves to your existing DB column "purpose"
            if "medical_explanation" in med:
                med["purpose"] = med.pop("medical_explanation")
            else:
                med["purpose"] = "General Health"

            # 2. Fix type case
            if med.get("type"):
                med["type"] = med["type"].lower()

            # 3. Fix duration
            q = med.get("quantity")
            d = med.get("dosage_pattern")
            if (not med.get("duration_days") or med["duration_days"] == 0) and q and d:
                med["duration_days"] = calculate_duration(q, d)
                
        return data

    except Exception as e:
        print(f"Gemini Analysis Failed: {e}")
        return {"medicines": [], "doctor_name": "Unknown", "patient_name": "Unknown"}

# --- Verification Feature (Kept Same) ---

class VerificationResult(typing.TypedDict):
    status: str
    identified_medicine_name: str
    purpose: str
    explanation: str
    replacement_for: str

model_verify = genai.GenerativeModel(
    model_name="gemini-flash-latest",
    generation_config={
        "response_mime_type": "application/json",
        "response_schema": VerificationResult
    }
)

VERIFY_PROMPT = """
You are an expert pharmacist helper. 
1. Identify the medicine/tablet in the image. Determine its **Generic Name/Composition** (Salts).
2. Compare it against the USER'S PRESCRIPTION list provided below.

### PRESCRIPTION LIST:
{prescription_list}

### STRICT CLASSIFICATION LOGIC:
1. **prescribed**: ONLY if the medicine name matches EXACTLY.
2. **replacement**: If the brand name is different, but the **SALT COMPOSITION** is the same or chemically equivalent.
3. **not_prescribed**: If neither the name nor the composition matches anything in the list.

Output a JSON with:
- `status`: "prescribed" | "replacement" | "not_prescribed"
- `identified_medicine_name`: Name from image.
- `purpose`: Medical usage.
- `explanation`: "Found match with [Prescribed Name]" OR "Different brand but same composition as [Prescribed Name]" OR "No match found".
- `replacement_for`: The name of the prescribed medicine it replaces (if applicable).
"""

def verify_medicine_match(image_bytes: bytes, prescribed_medicines: list) -> dict:
    try:
        med_list_str = "\\n".join([f"- {m['name']} (Purpose: {m.get('purpose', 'Unknown')})" for m in prescribed_medicines])
        prompt = VERIFY_PROMPT.format(prescription_list=med_list_str)
        
        response = model_verify.generate_content([
            {"mime_type": "image/jpeg", "data": image_bytes},
            prompt
        ])
        return json.loads(response.text)
    except Exception as e:
        print(f"Gemini Verification Failed: {e}")
        return {
            "status": "error",
            "identified_medicine_name": "Unknown",
            "purpose": "Unknown", 
            "explanation": "Could not analyze the image.",
            "replacement_for": ""
        }