import json
import os
from pathlib import Path

# This saves settings persistently in your mounted 'data' volume
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SETTINGS_FILE = BASE_DIR / "data" / "settings.json"

# We use your exact current key and model as the default so nothing breaks!
DEFAULT_SETTINGS = {
    "provider": "openrouter",
    "model": "google/gemini-2.0-flash-lite-preview-02-05:free",
    "api_key": "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",
    "ollama_base_url": "http://localhost:11434"
}

def load_settings():
    """Loads settings from JSON, or creates it with defaults if missing."""
    if not SETTINGS_FILE.exists():
        os.makedirs(SETTINGS_FILE.parent, exist_ok=True)
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS
    
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_SETTINGS

def save_settings(settings_dict):
    """Saves the user's API keys and model choices to JSON."""
    os.makedirs(SETTINGS_FILE.parent, exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings_dict, f, indent=4)