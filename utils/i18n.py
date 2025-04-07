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
    
def get_text(lang, key):
    translations = {
        "es": {
            "live_registration": "Registro en Vivo",
            "analytics_panel": "Panel Analítico",
            "heatmaps_tab": "Mapas de Calor",
            "select_module": "Seleccionar módulo:",
            "logo_error": "Error cargando logo: {error}"
        },
        "en": {
            "live_registration": "Live Registration",
            "analytics_panel": "Analytics Panel",
            "heatmaps_tab": "Heatmaps",
            "select_module": "Select module:",
            "logo_error": "Error loading logo: {error}"
        }
    }
    return translations.get(lang, {}).get(key, f"[{key} not found]")
