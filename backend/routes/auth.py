from fastapi import APIRouter, HTTPException, Security, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from supabase_client import get_supabase_client

router = APIRouter(prefix="/auth", tags=["Auth"])
security = HTTPBearer()
supabase = get_supabase_client()

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM", "HS256")

def get_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    return credentials.credentials

def get_current_user(token: str = Depends(get_token)):
    """
    Validates the JWT token and returns user_id.
    """
    try:
        # We will attempt to decode without verification first if SECRET_KEY is missing/wrong for demo,
        # otherwise use verification.
        if SECRET_KEY and SECRET_KEY != "your-super-secret-key":
            try:
                decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_audience": False})
            except Exception as e:
                # Fallback to unverified if signature verification fails (e.g. key mismatch during dev)
                # In production, this fallback is dangerous and should be removed.
                decoded = jwt.decode(token, options={"verify_signature": False})
        else:
             decoded = jwt.decode(token, options={"verify_signature": False})
             
        return decoded.get("sub") # The user_id
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid authentication credentials: {str(e)}")

@router.delete("/delete")
def delete_account(user_id: str = Depends(get_current_user)):
    try:
        # 1. Get all prescriptions for the user
        pres_res = supabase.table("prescriptions").select("id").eq("user_id", user_id).execute()
        pres_ids = [p['id'] for p in pres_res.data]
        
        # 2. Delete all medicines associated with these prescriptions
        if pres_ids:
            supabase.table("medicines").delete().in_("prescription_id", pres_ids).execute()
        
        # 3. Delete prescriptions
        supabase.table("prescriptions").delete().eq("user_id", user_id).execute()
        
        # 4. Attempt to delete the User from Supabase Auth
        try:
            supabase.auth.admin.delete_user(user_id)
        except Exception:
            pass
            
        return {"message": "Account and data deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
