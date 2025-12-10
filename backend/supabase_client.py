from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Supabase URL and Key must be set in environment variables")

supabase: Client = create_client(url, key)

def get_supabase_client() -> Client:
    return supabase

def get_authenticated_client(token: str) -> Client:
    """
    Returns the Supabase client.
    Since we are using custom auth, we do not pass the token to Supabase.
    Access control is handled by the backend logic using user_id.
    """
    return supabase
