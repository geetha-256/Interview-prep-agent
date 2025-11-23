# utils.py
import os
from typing import Tuple, Any
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

OPENAI_KEY = os.getenv("OPENAI_API_KEY")

def get_openai_client():
    if not OpenAI or not OPENAI_KEY:
        return None
    return OpenAI(api_key=OPENAI_KEY)

def ask_openai(prompt: str, model: str = "gpt-4o-mini") -> str:
    """
    Use OpenAI if configured. Returns the generated text.
    """
    client = get_openai_client()
    if client is None:
        raise RuntimeError("OpenAI client not configured")
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role":"user","content":prompt}],
        max_tokens=400,
        temperature=0.2,
    )
    # new OpenAI client returns choices with message content
    try:
        return resp.choices[0].message["content"].strip()
    except Exception:
        # safe fallback
        return getattr(resp.choices[0].message, "content", "") or str(resp)
