import streamlit as st
import pandas as pd
from mplsoccer import VerticalPitch
import matplotlib.pyplot as plt
from io import BytesIO

# Inicializar session state
if "registro" not in st.session_state:
    st.session_state.registro = []
if "fase" not in st.session_state:
    st.session_state.fase = "inicio"
if "datos" not in st.session_state:
    st.session_state.datos = {}

st.title("🎯 Registro de Acciones de Balón Parado")

# Paso 1: tipo de balón parado
st.subheader("1. Tipo de balón parado")
tipo = st.selectbox("Selecciona una opción", ["Tiro libre", "Córner", "Lateral", "Penal"])

# Paso 2: Nombre ejecutor
ejecutor = st.text_input("2. ¿Quién ejecutó la jugada?")

# Paso 3: Nombre del primer contacto
primer_contacto = st.text_input("3. ¿Quién recibió el balón?")

# Paso 4: Nombre del segundo contacto (opcional)
segundo_contacto = st.text_input("4. ¿Segundo contacto (opcional)?")

st.subheader("5. Haz clic en el campo para registrar:")

# Dibujar la cancha con mplsoccer
pitch = VerticalPitch(pitch_type='statsbomb', pitch_color='grass', line_color='white')
fig, ax = pitch.draw(figsize=(8, 6))
buf = BytesIO()
plt.savefig(buf, format="png")
plt.close(fig)

# Mostrar imagen y capturar clics
coords = st.image(buf.getvalue(), use_column_width=True)
st.info("Haz clic en el lugar de ejecución y luego en el de finalización en la imagen (esto se implementará con Plotly si deseas interactividad real)")

# ⛔ Aquí deberíamos integrar clics interactivos (por ahora simularemos coordenadas manuales)

x_inicio = st.slider("Coordenada X - ejecución", 0, 120)
y_inicio = st.slider("Coordenada Y - ejecución", 0, 80)

x_fin = st.slider("Coordenada X - finalización", 0, 120)
y_fin = st.slider("Coordenada Y - finalización", 0, 80)

if st.button("Registrar acción"):
    st.session_state.registro.append({
        "tipo": tipo,
        "ejecutor": ejecutor,
        "primer_contacto": primer_contacto,
        "segundo_contacto": segundo_contacto,
        "x_inicio": x_inicio,
        "y_inicio": y_inicio,
        "x_fin": x_fin,
        "y_fin": y_fin
    })
    st.success("✅ Acción registrada")

# Mostrar dataframe
df = pd.DataFrame(st.session_state.registro)
if not df.empty:
    st.subheader("📋 Registro de acciones")
    st.dataframe(df)

    # Exportar CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Descargar CSV", csv, "acciones_balon_parado.csv", "text/csv")

