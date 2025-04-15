import json
from pathlib import Path

# Configuración correcta de rutas
TRANSLATIONS_PATH = Path(__file__).parent / "translations.json"

try:
    with open(TRANSLATIONS_PATH, "r", encoding="utf-8") as f:
        translations = json.load(f)
except Exception as e:
    raise RuntimeError(f"Error loading translations: {str(e)}") from e

def get_text(lang: str, key: str) -> str:
    return translations.get(lang, {}).get(key, f"[[{key}]]")
