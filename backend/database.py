# database.py
# This file is a placeholder/wrapper as `supabase_client.py` handles the main connection.
# In a traditional SQLAlchemy setup, this would have engine/session logic.
# For this project, it re-exports the supabase client to satisfy the folder structure requirements.

from supabase_client import get_supabase_client

db = get_supabase_client()
