from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from typing import Optional
import uuid
import os
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from supabase_client import get_supabase_client
from utils.security import hash_password, verify_password, create_access_token, decode_access_token
from utils.smtp_verifier import verify_email_smtp

router = APIRouter(prefix="/auth", tags=["Auth"])
security = HTTPBearer()
supabase = get_supabase_client()
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")

# --- Models ---
class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class GoogleLogin(BaseModel):
    token: str

# --- Dependencies ---
def get_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    return credentials.credentials

def get_current_user(token: str = Depends(get_token)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload.get("sub")

# --- Routes ---

@router.post("/register")
async def register(user: UserRegister):
    # 1. SMTP Validation
    if not verify_email_smtp(user.email):
         raise HTTPException(status_code=400, detail="Email address does not exist or is undeliverable.")

    # 2. Check if user exists
    # We use the Service Role (or Anon if RLS allows) client. Backend should ideally have Service Role.
    # Assuming supabase client works for SELECT.
    res = supabase.table("profiles").select("*").eq("email", user.email).execute()
    if res.data:
        raise HTTPException(status_code=400, detail="User with this email already exists.")

    # 3. Create User
    new_id = str(uuid.uuid4())
    hashed = hash_password(user.password)
    
    user_data = {
        "id": new_id,
        "email": user.email,
        "full_name": user.full_name,
        "password_hash": hashed,
        "created_at": "now()"
    }
    
    insert_res = supabase.table("profiles").insert(user_data).execute()
    if not insert_res.data:
        raise HTTPException(status_code=500, detail="Failed to register user.")

    # 4. Issue Token
    access_token = create_access_token(data={"sub": new_id, "email": user.email})
    return {"access_token": access_token, "token_type": "bearer", "user": {"id": new_id, "email": user.email, "name": user.full_name}}

@router.post("/login")
async def login(user: UserLogin):
    # 1. Fetch User
    res = supabase.table("profiles").select("*").eq("email", user.email).execute()
    if not res.data:
        raise HTTPException(status_code=400, detail="Invalid email or password.")
    
    db_user = res.data[0]
    
    # 2. Verify Password
    if not db_user.get("password_hash") or not verify_password(user.password, db_user["password_hash"]):
         raise HTTPException(status_code=400, detail="Invalid email or password.")
         
    # 3. Issue Token
    access_token = create_access_token(data={"sub": db_user["id"], "email": db_user["email"]})
    return {"access_token": access_token, "token_type": "bearer", "user": {"id": db_user["id"], "email": db_user["email"], "name": db_user["full_name"]}}

@router.post("/google")
async def google_login(login_data: GoogleLogin):
    try:
        # 1. Verify Google Token
        id_info = id_token.verify_oauth2_token(login_data.token, google_requests.Request(), GOOGLE_CLIENT_ID)
        
        email = id_info.get("email")
        google_sub = id_info.get("sub")
        name = id_info.get("name")
        picture = id_info.get("picture")
        
        # 2. Check/Create User
        res = supabase.table("profiles").select("*").eq("email", email).execute()
        
        if res.data:
            # Login existing
            db_user = res.data[0]
            # Optional: Update google_sub or avatar if missing
            updates = {}
            if not db_user.get("google_sub"): updates["google_sub"] = google_sub
            if not db_user.get("avatar_url"): updates["avatar_url"] = picture
            if updates:
                supabase.table("profiles").update(updates).eq("id", db_user["id"]).execute()
            
            user_id = db_user["id"]
            user_name = db_user["full_name"]
            
        else:
            # Register new Google User
            user_id = str(uuid.uuid4())
            user_name = name
            user_data = {
                "id": user_id,
                "email": email,
                "full_name": name,
                "google_sub": google_sub,
                "avatar_url": picture,
                "created_at": "now()"
            }
            try:
                supabase.table("profiles").insert(user_data).execute()
            except Exception as insert_err:
                # Fallback if DB insert fails (e.g. duplicate UUID almost impossible, but generic error)
                raise HTTPException(status_code=500, detail=f"Failed to create Google user: {str(insert_err)}")
            
        # 3. Issue Token
        access_token = create_access_token(data={"sub": user_id, "email": email})
        return {"access_token": access_token, "token_type": "bearer", "user": {"id": user_id, "email": email, "name": user_name, "avatar": picture}}

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Google Token")
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))
