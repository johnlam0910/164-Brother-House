import json
import base64

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
