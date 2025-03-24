import streamlit as st
from streamlit_image_coordinates import image_coordinates
import pandas as pd
from PIL import Image

# Cargar imagen del campo (portería arriba)
img = Image.open("campo_medio_vertical.png")

# Inicializar session state
if "fase" not in st.session_state:
    st.session_state.fase = "inicio"
if "temp" not in st.session_state:
    st.session_state.temp = {}
if "registro" not in st.session_state:
    st.session_state.registro = []

st.title("⚽ Registro de Acciones de Balón Parado")

# Paso 1: Tipo de jugada
accion = st.selectbox("Tipo de balón parado", ["Tiro libre", "Córner", "Lateral", "Penal"])

st.subheader("Haz clic en el campo para registrar la acción")
coords = image_coordinates(img, key="campo", use_container_width=True)

if coords:
    x = coords["x"]
    y = coords["y"]

    if st.session_state.fase == "inicio":
        st.session_state.temp["tipo"] = accion
        st.session_state.temp["x_inicio"] = x
        st.session_state.temp["y_inicio"] = y
        st.session_state.fase = "esperando_final"
        st.success(f"📍 Punto de ejecución: ({x}, {y}). Ahora haz clic donde finalizó la jugada.")
    
    elif st.session_state.fase == "esperando_final":
        st.session_state.temp["x_fin"] = x
        st.session_state.temp["y_fin"] = y
        st.session_state.fase = "datos"
        st.success(f"📍 Punto de finalización: ({x}, {y}). Completa los datos abajo.")

# Paso 3: ingresar ejecutor y contactos
if st.session_state.fase == "datos":
    ejecutor = st.text_input("Nombre del ejecutor")
    primer_contacto = st.text_input("Primer contacto (quien recibió)")
    segundo_contacto = st.text_input("Segundo contacto (opcional)")

    if st.button("Registrar acción"):
        st.session_state.temp.update({
            "ejecutor": ejecutor,
            "primer_contacto": primer_contacto,
            "segundo_contacto": segundo_contacto
        })
        st.session_state.registro.append(st.session_state.temp.copy())
        st.session_state.temp = {}
        st.session_state.fase = "inicio"
        st.success("✅ Acción registrada")

# Mostrar tabla
df = pd.DataFrame(st.session_state.registro)
if not df.empty:
    st.subheader("📊 Acciones registradas")
    st.dataframe(df)

    # CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar CSV", csv, "acciones_balon_parado.csv", "text/csv")

