import json
from pathlib import Path

# Cargar traducciones desde archivo JSON válido
TRANSLATIONS_FILE = Path(__file__).parent / "translations.json"

with open(TRANSLATIONS_FILE, "r", encoding="utf-8") as f:
    translations = json.load(f)

def get_text(lang: str, key: str) -> str:
    return translations.get(lang, {}).get(key, f"[[{key}]]")
