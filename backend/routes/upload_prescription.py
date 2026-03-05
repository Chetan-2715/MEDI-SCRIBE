from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import os
import uuid
import base64
from gemini_service import extract_medicine_info
from db import query, execute, execute_many
from .auth import get_current_user, get_token

router = APIRouter()

@router.post("/upload-prescription")
async def upload_prescription(file: UploadFile = File(...), user_id: str = Depends(get_current_user)):
    try:
        # 1. Read file
        content = await file.read()

        # 2. Store image as base64 data URL (no external storage needed)
        file_ext = file.filename.split(".")[-1].lower()
        mime_type = f"image/{file_ext}" if file_ext in ["png", "jpg", "jpeg", "gif", "webp"] else "image/jpeg"
        image_b64 = base64.b64encode(content).decode("utf-8")
        image_url = f"data:{mime_type};base64,{image_b64}"

        # 3. Gemini Extraction
        extracted_data = extract_medicine_info(content)
        medicines = extracted_data.get("medicines", [])
        doctor_name = extracted_data.get("doctor_name", "Unknown")
        patient_name = extracted_data.get("patient_name", "Unknown")

        # 4. Insert Prescription
        pres = execute(
            """INSERT INTO prescriptions (user_id, image_url, doctor_name, patient_name, notes)
               VALUES (%s, %s, %s, %s, %s) RETURNING id""",
            (user_id, image_url, doctor_name, patient_name, "Uploaded via app"),
            returning=True
        )

        if not pres:
            raise HTTPException(status_code=500, detail="Failed to save prescription")

        prescription_id = str(pres["id"])

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
            for med_data in final_medicines:
                execute(
                    """INSERT INTO medicines (prescription_id, name, type, dosage_pattern, instructions, total_quantity, duration_days, purpose)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        med_data["prescription_id"],
                        med_data["name"],
                        med_data["type"],
                        med_data["dosage_pattern"],
                        med_data["instructions"],
                        med_data["total_quantity"],
                        med_data["duration_days"],
                        med_data["purpose"]
                    )
                )

        return {
            "prescription_id": prescription_id,
            "medicines": final_medicines,
            "doctor_name": doctor_name,
            "patient_name": patient_name
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))
