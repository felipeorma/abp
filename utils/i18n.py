import json
from typing import Dict

def get_text(lang: str, key: str) -> str:
    with open("utils/i18n.json", "r", encoding="utf-8") as f:
        translations = json.load(f)
    return translations.get(lang, {}).get(key, f"[{key}]")
