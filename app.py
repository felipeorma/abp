import streamlit as st
from streamlit_image_coordinates import image_coordinates
import pandas as pd
from PIL import Image

# Inicializar estado
if "registro" not in st.session_state:
    st.session_state.registro = []
if "fase" not in st.session_state:
    st.session_state.fase = "inicio"
if "accion" not in st.session_state:
    st.session_state.accion = ""
if "coordenadas_inicio" not in st.session_state:
    st.session_state.coordenadas_inicio = None
if "ejecutor" not in st.session_state:
    st.session_state.ejecutor = ""
if "receptor" not in st.session_state:
    st.session_state.receptor = ""

st.title("Registro de Acciones de Balón Parado")

# 1. Selección del tipo de acción
st.subheader("1. Selecciona el tipo de acción:")
accion = st.radio("Tipo de balón parado", ["Tiro libre", "Córner", "Lateral", "Penal"])
st.session_state.accion = accion

# 2. Mostrar campo y capturar clics
st.subheader("2. Haz clic en el campo para registrar la acción:")

image_path = "CAMPO DE FUTBOL CURSO.svg"  # tu imagen cargada
img = Image.open(image_path)
coords = image_coordinates(img)

if coords:
    if st.session_state.fase == "inicio":
        st.session_state.coordenadas_inicio = coords
        st.session_state.ejecutor = st.text_input("¿Quién ejecutó la jugada?")
        if st.session_state.ejecutor:
            st.session_state.fase = "esperando_fin"
            st.success("Ahora haz clic donde terminó la jugada.")
    elif st.session_state.fase == "esperando_fin":
        coordenadas_fin = coords
        st.session_state.receptor = st.text_input("¿Quién recibió o finalizó la jugada?")
        if st.session_state.receptor:
            # Guardar todo
            st.session_state.registro.append({
                "acción": st.session_state.accion,
                "ejecutor": st.session_state.ejecutor,
                "x_inicio": st.session_state.coordenadas_inicio["x"],
                "y_inicio": st.session_state.coordenadas_inicio["y"],
                "x_fin": coordenadas_fin["x"],
                "y_fin": coordenadas_fin["y"],
                "receptor": st.session_state.receptor
            })
            st.success("✔️ Acción registrada")
            # Reset
            st.session_state.fase = "inicio"
            st.session_state.ejecutor = ""
            st.session_state.receptor = ""
            st.session_state.coordenadas_inicio = None

# 3. Mostrar DataFrame
df = pd.DataFrame(st.session_state.registro)
if not df.empty:
    st.subheader("📊 Registro de Acciones")
    st.dataframe(df)

    # Botón para exportar CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Descargar CSV", data=csv, file_name="acciones_balon_parado.csv", mime='text/csv')

