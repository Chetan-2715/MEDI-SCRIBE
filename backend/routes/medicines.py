from fastapi import APIRouter, Depends, HTTPException
from .auth import get_current_user, get_token
from db import query, execute

router = APIRouter()

@router.get("/prescriptions")
async def get_prescriptions(user_id: str = Depends(get_current_user)):
    try:
        # Fetch prescriptions without the heavy image_url for the list view
        prescriptions = query(
            "SELECT id, user_id, doctor_name, patient_name, notes, created_at FROM prescriptions WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,)
        )

        if not prescriptions:
            return []

        # Convert to strings and format dates for frontend
        for pres in prescriptions:
            pres["id"] = str(pres["id"])
            pres["user_id"] = str(pres["user_id"])
            if pres.get("created_at"):
                pres["created_at"] = pres["created_at"].isoformat()
            pres["medicines"] = []
            
        pres_ids = tuple(p["id"] for p in prescriptions)
        
        # Batch fetch all medicines for all returned prescriptions in a single query
        meds = query(
            "SELECT * FROM medicines WHERE prescription_id IN %s",
            (pres_ids,)
        )
        
        # Group medicines by prescription_id
        meds_by_pres = {}
        for m in meds:
            m["id"] = str(m["id"])
            pid = str(m["prescription_id"])
            m["prescription_id"] = pid
            if m.get("created_at"):
                m["created_at"] = m["created_at"].isoformat()
            
            if pid not in meds_by_pres:
                meds_by_pres[pid] = []
            meds_by_pres[pid].append(m)
            
        # Attach medicines to their respective prescriptions
        for pres in prescriptions:
            pres["medicines"] = meds_by_pres.get(pres["id"], [])

        return prescriptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prescriptions/{id}")
async def get_prescription(id: str, user_id: str = Depends(get_current_user)):
    try:
        pres = query(
            "SELECT * FROM prescriptions WHERE id = %s AND user_id = %s",
            (id, user_id),
            fetch_one=True
        )
        if not pres:
            raise HTTPException(status_code=404, detail="Prescription not found")

        pres["id"] = str(pres["id"])
        pres["user_id"] = str(pres["user_id"])
        if pres.get("created_at"):
            pres["created_at"] = pres["created_at"].isoformat()

        meds = query("SELECT * FROM medicines WHERE prescription_id = %s", (id,))
        for m in meds:
            m["id"] = str(m["id"])
            m["prescription_id"] = str(m["prescription_id"])
            if m.get("created_at"):
                m["created_at"] = m["created_at"].isoformat()

        pres["medicines"] = meds
        return pres
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/prescriptions/{id}")
async def delete_prescription(id: str, user_id: str = Depends(get_current_user)):
    try:
        pres = query(
            "SELECT id FROM prescriptions WHERE id = %s AND user_id = %s",
            (id, user_id)
        )
        if not pres:
            raise HTTPException(status_code=404, detail="Prescription not found or unauthorized")

        # Medicines are deleted automatically via CASCADE
        execute("DELETE FROM prescriptions WHERE id = %s AND user_id = %s", (id, user_id))
        return {"message": "Prescription deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prescriptions/{id}/medicines")
async def get_prescription_medicines(id: str, user_id: str = Depends(get_current_user)):
    try:
        pres = query(
            "SELECT id FROM prescriptions WHERE id = %s AND user_id = %s",
            (id, user_id)
        )
        if not pres:
            raise HTTPException(status_code=404, detail="Prescription not found or unauthorized")

        meds = query("SELECT * FROM medicines WHERE prescription_id = %s", (id,))
        for m in meds:
            m["id"] = str(m["id"])
            m["prescription_id"] = str(m["prescription_id"])
            if m.get("created_at"):
                m["created_at"] = m["created_at"].isoformat()

        return meds
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
