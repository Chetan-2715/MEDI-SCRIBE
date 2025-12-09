from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import shutil
import os
import uu
import uuid
import base64
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
        
        # 2. Upload image to Supabase Storage
        file_ext = file.filename.split(".")[-1]
        file_path = f"{user_id}/{uuid.uuid4()}.{file_ext}"
        
        try:
            res = client.storage.from_("prescriptions").upload(file_path, content)
            project_url = os.environ.get("SUPABASE_URL")
            image_url = f"{project_url}/storage/v1/object/public/prescriptions/{file_path}"
        except Exception as e:
            print(f"Storage upload failed (bucket might be missing): {e}")
            image_url = "https://placehold.co/600x400?text=Prescription"

        # 3. Gemini Extraction (Direct Vision)
        extracted_data = extract_medicine_info(content)
        medicines = extracted_data.get("medicines", [])
        doctor_name = extracted_data.get("doctor_name", "Unknown")
        patient_name = extracted_data.get("patient_name", "Unknown")

        # 4. Insert Prescription
        prescription_data = {
            "user_id": user_id,
            "image_url": image_url,
            "doctor_name": doctor_name,
            "patient_name": patient_name,
            "notes": "Uploaded via app"
        }
        
        pres_res = client.table("prescriptions").insert(prescription_data).execute()
        if not pres_res.data:
            raise HTTPException(status_code=500, detail="Failed to save prescription")
            
        prescription_id = pres_res.data[0]['id']

        # 5. Insert Medicines
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
            final_medicines.append(med_data)
        
        if final_medicines:
            client.table("medicines").insert(final_medicines).execute()

        return {
            "prescription_id": prescription_id,
            "medicines": final_medicines,
            "doctor_name": doctor_name,
            "patient_name": patient_name
        }

    except Exception as e:
        print(f"Error in upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))
