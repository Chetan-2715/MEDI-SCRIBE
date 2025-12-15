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

# --- New Verification Feature ---

class VerificationResult(typing.TypedDict):
    status: str  # "prescribed", "replacement", "not_prescribed"
    identified_medicine_name: str
    purpose: str
    explanation: str
    replacement_for: str  # Name of prescribed medicine being replaced (if applicable)

model_verify = genai.GenerativeModel(
    model_name="gemini-flash-latest",
    generation_config={
        "response_mime_type": "application/json",
        "response_schema": VerificationResult
    }
)

VERIFY_PROMPT = """
You are an expert pharmacist helper. 
1. Identify the medicine/tablet in the image.
2. Compare it against the USER'S PRESCRIPTION list provided below.

### PRESCRIPTION LIST:
{prescription_list}

### STRICT CLASSIFICATION LOGIC:
1. **prescribed**: ONLY if the medicine name in the image matches a name in the list (e.g., "Augmentin" matches "Augmentin", "Augmentin 625" matches "Augmentin").
2. **replacement**: If the medicine name is DIFFERENT from the list, but it contains the SAME active ingredients/salts and serves the SAME purpose (e.g., "Amoxyclav" is a replacement for "Augmentin" because both are Amoxicillin+Clavulanate, but names are different).
3. **not_prescribed**: If it does not match the name OR the content/purpose of any medicine in the list.

Output a JSON with:
- `status`: one of "prescribed", "replacement", "not_prescribed".
- `identified_medicine_name`: Name from image.
- `purpose`: Medical usage.
- `explanation`: Clear explanation. For replacement, explicitly mention: "This is a substitute for [Prescribed Name] as they contain the same salts."
- `replacement_for`: If status is replacement, state which prescribed medicine it replaces. Else empty.
"""

def verify_medicine_match(image_bytes: bytes, prescribed_medicines: list) -> dict:
    """
    Verifies if the uploaded medicine image matches or complements the user's prescription.
    """
    try:
        # Format list for prompt
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
            "explanation": "Could not analyze the image. Please try again.",
            "replacement_for": ""
        }