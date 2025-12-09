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
    Returns a new Supabase client instance authenticated with the given user token.
    This ensures RLS policies are applied correctly for the user.
    """
    client = create_client(url, key)
    client.postgrest.auth(token)
    return client
