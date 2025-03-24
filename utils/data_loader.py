import pandas as pd
import requests
import streamlit as st
from io import StringIO

GITHUB_RAW_URL = "https://raw.githubusercontent.com/felipeorma/abp/main/master_abp.csv"

def load_github_data():
    try:
        response = requests.get(GITHUB_RAW_URL)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        
        # Convertir coordenadas
        coord_columns = ['x_saque', 'y_saque', 'x_remate', 'y_remate']
        df[coord_columns] = df[coord_columns].apply(pd.to_numeric, errors='coerce')
        
        return df.dropna(subset=coord_columns)
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame()
