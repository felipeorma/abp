import json
import os
from typing import Dict

def get_text(lang: str, key: str) -> str:
    # Obtener la ruta absoluta del archivo
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "i18n.json")
    
    with open(file_path, "r", encoding="utf-8") as f:
        translations = json.load(f)
    return translations.get(lang, {}).get(key, f"[{key}]")
