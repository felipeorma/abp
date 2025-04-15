import json
import os
from pathlib import Path

def get_text(lang: str, key: str) -> str:
    try:
        # Ruta absoluta confiable
        current_dir = Path(__file__).parent
        file_path = current_dir / "i18n.json"
        
        with open(file_path, "r", encoding="utf-8") as f:
            translations = json.load(f)
            
        return translations.get(lang, {}).get(key, f"[{key}]")
    
    except Exception as e:
        return f"⚠️ Error: {str(e)}"
