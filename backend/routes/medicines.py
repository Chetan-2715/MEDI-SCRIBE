from fastapi import APIRouter, Depends, HTTPException
from .auth import get_current_user, get_token
from db import query, execute

router = APIRouter()

@router.get("/prescriptions")
async def get_prescriptions(user_id: str = Depends(get_current_user)):
    try:
        # Fetch prescriptions with their medicines
        prescriptions = query(
            "SELECT * FROM prescriptions WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,)
        )

        for pres in prescriptions:
            pres["id"] = str(pres["id"])
            pres["user_id"] = str(pres["user_id"])
            if pres.get("created_at"):
                pres["created_at"] = pres["created_at"].isoformat()

            meds = query(
                "SELECT * FROM medicines WHERE prescription_id = %s",
                (pres["id"],)
            )
            for m in meds:
                m["id"] = str(m["id"])
                m["prescription_id"] = str(m["prescription_id"])
                if m.get("created_at"):
                    m["created_at"] = m["created_at"].isoformat()
            pres["medicines"] = meds

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
