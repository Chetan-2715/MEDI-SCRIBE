from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from supabase_client import get_supabase_client, get_authenticated_client
from .auth import get_current_user, get_token
from gemini_service import verify_medicine_match
import typing

router = APIRouter()

@router.post("/medicine/verify")
async def verify_medicine(
    file: UploadFile = File(...),
    prescription_id: str = Form(...),
    user_id: str = Depends(get_current_user), 
    token: str = Depends(get_token)
):
    try:
        if not file.content_type.startswith("image/"):
             raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

        # 1. Read Image
        content = await file.read()

        # 2. Fetch Prescribed Medicines for this specific prescription
        client = get_authenticated_client(token)
        
        # Verify ownership of prescription first
        pres_check = client.table("prescriptions").select("id").eq("id", prescription_id).eq("user_id", user_id).execute()
        if not pres_check.data:
             raise HTTPException(status_code=404, detail="Prescription not found or unauthorized")

        # Get medicines list
        meds_res = client.table("medicines").select("name, purpose").eq("prescription_id", prescription_id).execute()
        prescribed_medicines = meds_res.data # List of dicts: [{'name': '...', 'purpose': '...'}, ...]

        # 3. Call Gemini verification service
        verification_result = verify_medicine_match(content, prescribed_medicines)

        return verification_result

    except HTTPException:
        raise
    except Exception as e:
        print(f"Verification Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
