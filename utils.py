import json
import base64
import streamlit as st

def encode_roster(roster, off_duty, verse):
    """
    Encodes roster, off_duty, and verse into a URL-safe base64 string.
    """
    data = {
        "r": roster,
        "o": off_duty,
        "v": verse
    }
    # JSON dump with ensure_ascii=False to support non-ASCII names/chores natively
    json_str = json.dumps(data, ensure_ascii=False)
    encoded_bytes = base64.urlsafe_b64encode(json_str.encode('utf-8'))
    return encoded_bytes.decode('utf-8')

def decode_roster(encoded_str):
    """
    Decodes a URL-safe base64 string back into roster, off_duty, and verse.
    Returns (roster, off_duty, verse) or (None, None, None) on error.
    """
    if not encoded_str:
        return None, None, None
    try:
        decoded_bytes = base64.urlsafe_b64decode(encoded_str.encode('utf-8'))
        data = json.loads(decoded_bytes.decode('utf-8'))
        return data.get("r"), data.get("o"), data.get("v")
    except Exception as e:
        # Gracefully handle corrupted or outdated query parameters
        return None, None, None

@st.cache_resource
def get_supabase_client():
    """
    Initializes and returns the Supabase client if secrets are configured.
    Returns None otherwise.
    Uses st.cache_resource to cache the connection client resource.
    """
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY")
        if url and key:
            from supabase import create_client
            return create_client(url, key)
    except Exception as e:
        pass
    return None

def db_get(key, default=None):
    """
    Fetches a JSON config value from the Supabase house_state table.
    Returns default if not found or if database is not connected.
    """
    client = get_supabase_client()
    if not client:
        return default
    try:
        res = client.table("house_state").select("value").eq("key", key).execute()
        if res.data:
            return res.data[0]["value"]
    except Exception as e:
        pass
    return default

def db_set(key, value):
    """
    Saves/Upserts a JSON value to the Supabase house_state table.
    Returns True on success, False if database is not connected or error occurs.
    """
    client = get_supabase_client()
    if not client:
        return False
    try:
        client.table("house_state").upsert({"key": key, "value": value}).execute()
        return True
    except Exception as e:
        pass
    return False
