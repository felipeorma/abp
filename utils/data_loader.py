import pandas as pd
import requests
import streamlit as st
from io import StringIO

def load_github_data():
    try:
        # Usar URL raw correcta
        url = "https://raw.githubusercontent.com/felipeorma/abp/main/master_abp.csv"
        response = requests.get(url)
        response.raise_for_status()
        
        df = pd.read_csv(StringIO(response.text))
        
        # Convertir coordenadas
        coord_cols = ['x_saque', 'y_saque', 'x_remate', 'y_remate']
        df[coord_cols] = df[coord_cols].apply(pd.to_numeric, errors='coerce')
        
        return df.dropna(subset=coord_cols)
        
    except Exception as e:
        st.error(f"Error cargando datos: {str(e)}")
        return pd.DataFrame()
