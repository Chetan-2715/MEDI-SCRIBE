from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import shutil
import os
import uu
import uuid
import base64
from ocr_service import detect_text_from_path, detect_text
from gemini_service import extract_medicine_info
from supabase_client import get_supabase_client, get_authenticated_client
from .auth import get_current_user, get_token

router = APIRouter()
supabase = get_supabase_client()

@router.post("/upload-prescription")
async def upload_prescription(file: UploadFile = File(...), user_id: str = Depends(get_current_user), token: str = Depends(get_token)):
    try:
        # Use authenticated client for RLS
        client = get_authenticated_client(token)

        # 1. Read file
        content = await file.read()
        
        # 2. Upload image to Supabase Storage (Optional but recommended)
        # For now, we will store the base64 in the DB or assume we just process it.
        # The schema has `image_url`. We should upload to bucket 'prescriptions' if possible.
        # Handling storage buckets in code generation is tricky without knowing if buckets exist.
        # We will use a placeholder URL or Base64 data URL if it fits (text field might be small).
        # Better: Upload to 'prescriptions' bucket.
        
        file_ext = file.filename.split(".")[-1]
        file_path = f"{user_id}/{uuid.uuid4()}.{file_ext}"
        
        # Try uploading to Storage
        try:
            res = client.storage.from_("prescriptions").upload(file_path, content)
            # Construct public URL
            # Note: Bucket must be public or use signed url
            project_url = os.environ.get("SUPABASE_URL")
            image_url = f"{project_url}/storage/v1/object/public/prescriptions/{file_path}"
        except Exception as e:
            print(f"Storage upload failed (bucket might be missing): {e}")
            # Fallback: Use a placeholder or data URI (not recommended for DB size)
            image_url = "https://placehold.co/600x400?text=Prescription"

        # 3. Run OCR
        ocr_text = detect_text(content)
        if not ocr_text:
            raise HTTPException(status_code=400, detail="Could not detect text in image")

        # 4. Gemini Extraction
        extracted_data = extract_medicine_info(ocr_text)
        medicines = extracted_data.get("medicines", [])

        # 5. Insert Prescription
        prescription_data = {
            "user_id": user_id,
            "image_url": image_url,
            "doctor_name": "Unknown", # Gemini could extract this too if added to prompt
            "patient_name": "Unknown",
            "notes": "Uploaded via app"
        }
        
        pres_res = client.table("prescriptions").insert(prescription_data).execute()
        if not pres_res.data:
            raise HTTPException(status_code=500, detail="Failed to save prescription")
            
        prescription_id = pres_res.data[0]['id']

        # 6. Insert Medicines
        final_medicines = []
        for med in medicines:
            med_data = {
                "prescription_id": prescription_id,
                "name": med.get("name"),
                "type": med.get("type", "tablet"),
                "dosage_pattern": med.get("dosage_pattern"),
                "instructions": med.get("instructions"),
                "total_quantity": med.get("quantity"),
                "duration_days": med.get("duration_days"),
                "purpose": med.get("purpose")
            }
            # Clean None values if DB has strict checks or defaults
            # (Supabase handles nulls fine usually)
            
            final_medicines.append(med_data)
        
        if final_medicines:
            client.table("medicines").insert(final_medicines).execute()

        return {
            "prescription_id": prescription_id,
            "medicines": final_medicines,
            "ocr_text_preview": ocr_text[:100] + "..."
        }

    except Exception as e:
        print(f"Error in upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))
