import json
import streamlit as st
from pathlib import Path

def get_text(lang, key):
    try:
        # Cargar el archivo desde la ruta correcta
        translations_path = Path(__file__).parent / "i18n.json"
        
        with open(translations_path, "r", encoding="utf-8") as f:
            translations = json.load(f)
            
        return translations.get(lang, {}).get(key, f"[{key} no encontrada]")
    
    except Exception as e:
        st.error(f"Error cargando traducciones: {str(e)}")
        return f"[Error: {key}]"
