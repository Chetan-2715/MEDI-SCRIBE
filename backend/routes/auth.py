from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from typing import Optional
import uuid
import os
import time
import json
import traceback
import jwt as pyjwt
import requests as http_requests

from db import query, execute
from utils.security import hash_password, verify_password, create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])
security = HTTPBearer()
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")

# --- Pre-fetch Google's public keys at startup ---
_google_jwks_cache = {"keys": [], "fetched_at": 0}

def _fetch_google_keys():
    """Fetch Google's public signing keys and cache them."""
    try:
        resp = http_requests.get("https://www.googleapis.com/oauth2/v3/certs", timeout=15)
        resp.raise_for_status()
        _google_jwks_cache["keys"] = resp.json().get("keys", [])
        _google_jwks_cache["fetched_at"] = time.time()
        print(f"[Google Auth] Fetched {len(_google_jwks_cache['keys'])} Google public keys")
    except Exception as e:
        print(f"[Google Auth] WARNING: Could not fetch Google keys: {e}")

_fetch_google_keys()

# --- Models ---
class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class GoogleLoginModel(BaseModel):
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
    existing = query("SELECT id FROM profiles WHERE email = %s", (user.email,))
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists.")

    new_id = str(uuid.uuid4())
    hashed = hash_password(user.password)

    execute(
        """INSERT INTO profiles (id, email, full_name, password_hash)
           VALUES (%s, %s, %s, %s)""",
        (new_id, user.email, user.full_name, hashed)
    )

    access_token = create_access_token(data={"sub": new_id, "email": user.email})
    return {"access_token": access_token, "token_type": "bearer", "user": {"id": new_id, "email": user.email, "name": user.full_name}}

@router.post("/login")
async def login(user: UserLogin):
    rows = query("SELECT * FROM profiles WHERE email = %s", (user.email,))
    if not rows:
        raise HTTPException(status_code=400, detail="Invalid email or password.")

    db_user = rows[0]

    if not db_user.get("password_hash") or not verify_password(user.password, db_user["password_hash"]):
        raise HTTPException(status_code=400, detail="Invalid email or password.")

    access_token = create_access_token(data={"sub": str(db_user["id"]), "email": db_user["email"]})
    return {"access_token": access_token, "token_type": "bearer", "user": {"id": str(db_user["id"]), "email": db_user["email"], "name": db_user["full_name"]}}

@router.post("/google")
async def google_login(login_data: GoogleLoginModel):
    try:
        from jwt.algorithms import RSAAlgorithm

        print(f"[Google Auth] Received token, length: {len(login_data.token)}")

        # Refresh keys if stale (older than 1 hour) or empty
        if not _google_jwks_cache["keys"] or (time.time() - _google_jwks_cache["fetched_at"]) > 3600:
            _fetch_google_keys()

        if not _google_jwks_cache["keys"]:
            raise HTTPException(status_code=503, detail="Google public keys not available.")

        # 1. Get key ID from token header
        unverified_header = pyjwt.get_unverified_header(login_data.token)
        kid = unverified_header.get("kid")

        # 2. Find matching public key
        rsa_key = None
        for key_data in _google_jwks_cache["keys"]:
            if key_data.get("kid") == kid:
                rsa_key = RSAAlgorithm.from_jwk(json.dumps(key_data))
                break

        if not rsa_key:
            _fetch_google_keys()
            for key_data in _google_jwks_cache["keys"]:
                if key_data.get("kid") == kid:
                    rsa_key = RSAAlgorithm.from_jwk(json.dumps(key_data))
                    break

        if not rsa_key:
            raise HTTPException(status_code=400, detail="Google signing key not found.")

        # 3. Verify JWT locally
        id_info = pyjwt.decode(
            login_data.token,
            rsa_key,
            algorithms=["RS256"],
            audience=GOOGLE_CLIENT_ID,
            options={"verify_exp": True, "verify_iss": False}
        )

        token_issuer = id_info.get("iss", "")
        if token_issuer not in ["accounts.google.com", "https://accounts.google.com"]:
            raise HTTPException(status_code=400, detail=f"Invalid token issuer: {token_issuer}")

        email = id_info.get("email")
        google_sub = id_info.get("sub")
        name = id_info.get("name")
        picture = id_info.get("picture")

        print(f"[Google Auth] Token verified for: {email}")

        # 4. Check/Create User in Neon
        rows = query("SELECT * FROM profiles WHERE email = %s", (email,))

        if rows:
            db_user = rows[0]
            # Update google_sub/avatar if missing
            if not db_user.get("google_sub") or not db_user.get("avatar_url"):
                execute(
                    "UPDATE profiles SET google_sub = COALESCE(google_sub, %s), avatar_url = COALESCE(avatar_url, %s) WHERE id = %s",
                    (google_sub, picture, db_user["id"])
                )
            user_id = str(db_user["id"])
            user_name = db_user["full_name"]
        else:
            user_id = str(uuid.uuid4())
            user_name = name
            execute(
                """INSERT INTO profiles (id, email, full_name, google_sub, avatar_url)
                   VALUES (%s, %s, %s, %s, %s)""",
                (user_id, email, name, google_sub, picture)
            )

        # 5. Issue JWT
        access_token = create_access_token(data={"sub": user_id, "email": email})
        print(f"[Google Auth] Login successful for: {email}")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {"id": user_id, "email": email, "name": user_name, "avatar": picture}
        }

    except HTTPException:
        raise
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Google token expired. Please try again.")
    except pyjwt.InvalidTokenError as e:
        print(f"[Google Auth] Token invalid: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid Google token: {str(e)}")
    except Exception as e:
        print(f"[Google Auth] ERROR: {type(e).__name__}: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")

@router.get("/me")
async def get_me(user_id: str = Depends(get_current_user)):
    user = query("SELECT * FROM profiles WHERE id = %s", (user_id,), fetch_one=True)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": str(user["id"]), "email": user["email"], "name": user["full_name"], "avatar": user.get("avatar_url")}

@router.delete("/delete-account")
async def delete_account(user_id: str = Depends(get_current_user)):
    try:
        execute("DELETE FROM profiles WHERE id = %s", (user_id,))
        return {"message": "Account deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
