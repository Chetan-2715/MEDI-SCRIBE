from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from .auth import get_current_user, get_token
from db import query
from gemini_service import verify_medicine_match

router = APIRouter()

@router.post("/medicine/verify")
async def verify_medicine(
    file: UploadFile = File(...),
    prescription_id: str = Form(...),
    user_id: str = Depends(get_current_user),
):
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

        # 1. Read Image
        content = await file.read()

        # 2. Verify ownership of prescription
        pres = query(
            "SELECT id FROM prescriptions WHERE id = %s AND user_id = %s",
            (prescription_id, user_id)
        )
        if not pres:
            raise HTTPException(status_code=404, detail="Prescription not found or unauthorized")

        # 3. Get prescribed medicines
        meds = query(
            "SELECT name, purpose FROM medicines WHERE prescription_id = %s",
            (prescription_id,)
        )

        # 4. Call Gemini verification
        verification_result = verify_medicine_match(content, meds)
        return verification_result

    except HTTPException:
        raise
    except Exception as e:
        print(f"Verification Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
