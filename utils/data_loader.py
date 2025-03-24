import pandas as pd
import requests
from io import StringIO

GITHUB_RAW_URL = "https://raw.githubusercontent.com/felipeorma/abp/refs/heads/main/master_abp.csv"

def load_github_data():
    try:
        response = requests.get(GITHUB_RAW_URL)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        
        # Preprocesamiento
        numeric_cols = ['x_saque', 'y_saque', 'x_remate', 'y_remate']
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
        
        return df.dropna(subset=numeric_cols)
    except Exception as e:
        st.error(f"Error cargando datos: {str(e)}")
        return pd.DataFrame()
