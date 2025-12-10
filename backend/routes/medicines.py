from fastapi import APIRouter, Depends, HTTPException
from supabase_client import get_supabase_client, get_authenticated_client
from .auth import get_current_user, get_token

router = APIRouter()
supabase = get_supabase_client()

@router.get("/prescriptions")
async def get_prescriptions(user_id: str = Depends(get_current_user), token: str = Depends(get_token)):
    try:
        client = get_authenticated_client(token)
        # Filter by user_id manually as we are using service role client usually
        res = client.table("prescriptions").select("*, medicines(*)").eq("user_id", user_id).order("created_at", desc=True).execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prescriptions/{id}")
async def get_prescription(id: str, user_id: str = Depends(get_current_user), token: str = Depends(get_token)):
    try:
        client = get_authenticated_client(token)
        # Fetch prescription
        pres = client.table("prescriptions").select("*").eq("id", id).eq("user_id", user_id).execute()
        if not pres.data:
            raise HTTPException(status_code=404, detail="Prescription not found")
        
        prescription = pres.data[0]
        
        # Fetch medicines
        meds = client.table("medicines").select("*").eq("prescription_id", id).execute()
        
        # Combine
        prescription["medicines"] = meds.data
        return prescription
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/prescriptions/{id}")
async def delete_prescription(id: str, user_id: str = Depends(get_current_user), token: str = Depends(get_token)):
    try:
        client = get_authenticated_client(token)
        # Verify ownership
        pres = client.table("prescriptions").select("id").eq("id", id).eq("user_id", user_id).execute()
        if not pres.data:
            raise HTTPException(status_code=404, detail="Prescription not found or unauthorized")
        
        # Delete prescription (cascade delete should handle medicines if configured in DB, otherwise delete manually)
        # Assuming cascade delete is ON in Postgres or we delete medicines first
        client.table("medicines").delete().eq("prescription_id", id).execute()
        del_res = client.table("prescriptions").delete().eq("id", id).eq("user_id", user_id).execute()
        
        return {"message": "Prescription deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prescriptions/{id}/medicines")
async def get_prescription_medicines(id: str, user_id: str = Depends(get_current_user), token: str = Depends(get_token)):
    try:
        client = get_authenticated_client(token)
        # Verify ownership
        pres = client.table("prescriptions").select("id").eq("id", id).eq("user_id", user_id).execute()
        if not pres.data:
            raise HTTPException(status_code=404, detail="Prescription not found or unauthorized")
            
        res = client.table("medicines").select("*").eq("prescription_id", id).execute()
        return res.data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
