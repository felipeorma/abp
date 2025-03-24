import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch

# Configuración de la página
st.set_page_config(layout="centered")
st.title("⚽ Heatmaps de Balón Parado - Saque y Remate")

# Inicializar sesión para almacenar datos
if "registro" not in st.session_state:
    st.session_state.registro = []

# Coordenadas centrales representativas para cada zona (finales)
zonas_coords = {
    1:  (120, 0),    2:  (120, 80),   3:  (93, 9),    4:  (93, 71),
    5:  (114, 30),  6:  (114, 50),  7:  (114, 40),  8:  (111, 15),
    9:  (111, 65), 10: (105, 35), 11: (105, 45), 12: (105, 25),
   13: (105, 55), 14: (93, 29),  15: (93, 51), 16: (72, 20),
   17: (72, 60), "Penal": (108, 40)
}

# Formulario de registro
st.subheader("📋 Registrar nueva acción")
tipo = st.selectbox("Tipo de balón parado", ["Tiro libre", "Córner", "Lateral", "Penal"])
minuto = st.number_input("⏱️ Minuto", min_value=0, max_value=120, value=0)

zona_saque = st.selectbox("📍 Zona de saque", list(zonas_coords.keys()))
zona_remate = st.selectbox("🎯 Zona de remate", list(zonas_coords.keys()))
ejecutor = st.text_input("👟 Ejecutante")
primer_contacto = st.text_input("🤝 Primer contacto")
segundo_contacto = st.text_input("📌 Segundo contacto (opcional)")

if st.button("✅ Agregar acción"):
    st.session_state.registro.append({
        "tipo": tipo,
        "minuto": minuto,
        "zona_saque": zona_saque,
        "zona_remate": zona_remate,
        "ejecutor": ejecutor,
        "primer_contacto": primer_contacto,
        "segundo_contacto": segundo_contacto
    })
    st.success("Acción registrada correctamente ✅")

# Mostrar tabla de acciones registradas
df = pd.DataFrame(st.session_state.registro)
if not df.empty:
    st.subheader("📊 Acciones registradas")

    # Eliminar registros específicos
    index_to_delete = st.number_input("🗑️ Eliminar registro por índice", min_value=0, max_value=len(df)-1, step=1)
    if st.button("Eliminar registro"):
        st.session_state.registro.pop(index_to_delete)
        st.experimental_rerun()

    st.dataframe(df)

    # Agregar coordenadas
    df["coords_saque"] = df["zona_saque"].map(zonas_coords)
    df["coords_remate"] = df["zona_remate"].map(zonas_coords)
    df = df.dropna(subset=["coords_saque", "coords_remate"])
    df[["x_saque", "y_saque"]] = pd.DataFrame(df["coords_saque"].tolist(), index=df.index)
    df[["x_remate", "y_remate"]] = pd.DataFrame(df["coords_remate"].tolist(), index=df.index)

    # Función de
