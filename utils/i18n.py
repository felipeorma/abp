# utils/i18n.py
import json
from pathlib import Path

def load_translations(lang: str = "es"):
    translations_dir = Path(__file__).resolve().parent.parent / "translations"
    file_path = translations_dir / f"{lang}.json"
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                raise Exception(f"Invalid JSON in {file_path}: {str(e)}")
    except FileNotFoundError:
        raise Exception(f"Translation file not found: {file_path}")

def get_text(lang: str, key: str, **kwargs):
    translations = load_translations(lang)
    text = translations.get(key, key)
    return text.format(**kwargs) if kwargs else text
