import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
from mplsoccer import VerticalPitch

# Imagen de referencia
img = Image.open("MedioCampo_enumerado.JPG")

# Inicializar estado
if "registro" not in st.session_state:
    st.session_state.registro = []

st.set_page_config(layout="centered")
st.title("⚽ Acciones de balón parado por zona")

# Mostrar imagen de referencia
st.image(img, caption="Zonas numeradas para registrar acciones", use_column_width=True)

# -----------------------------
# REGISTRO DE NUEVA ACCIÓN
# -----------------------------
with st.expander("➕ Registrar nueva acción"):
    tipo = st.selectbox("Tipo de balón parado", ["Tiro libre", "Córner", "Lateral", "Penal"])
    minuto = st.number_input("⏱️ Minuto", min_value=0, max_value=120, value=0)
    zona = st.selectbox("📍 Zona final de la jugada (ver imagen)", list(range(1, 18)))
    ejecutor = st.text_input("👟 Ejecutante")
    primer_contacto = st.text_input("🎯 Primer contacto")
    segundo_contacto = st.text_input("📌 Segundo contacto (opcional)")

    if st.button("✅ Registrar acción"):
        st.session_state.registro.append({
            "tipo": tipo,
            "minuto": minuto,
            "zona": zona,
            "ejecutor": ejecutor,
            "primer_contacto": primer_contacto,
            "segundo_contacto": segundo_contacto
        })
        st.success("✔️ Acción registrada correctamente")

# -----------------------------
# VISUALIZACIÓN Y FILTROS
# -----------------------------
df = pd.DataFrame(st.session_state.registro)

if not df.empty:
    st.subheader("📋 Acciones registradas")

    # Filtro por tipo
    filtro_tipo = st.multiselect("🎯 Filtrar por tipo de jugada", df["tipo"].unique(), default=df["tipo"].unique())
    df_filtrado = df[df["tipo"].isin(filtro_tipo)]

    st.dataframe(df_filtrado)

    # -----------------------------
    # HEATMAP SOBRE CANCHA REAL
    # -----------------------------
    st.subheader("🔥 Heatmap sobre campo de fútbol")

    # Coordenadas promedio por zona (campo 68x105 aprox)
    zona_coords = {
        1: (10, 95),   2: (58, 95),
        3: (18, 78),   4: (50, 78),
        5: (30, 100),  6: (38, 100),  7: (34, 100),  8: (22, 100), 9: (46, 100),
        10: (30, 88), 11: (38, 88), 12: (22, 88), 13: (46, 88),
        14: (28, 70), 15: (40, 70),
        16: (20, 55), 17: (48, 55)
    }

    # Asignar coordenadas al dataframe
    df_filtrado["coords"] = df_filtrado["zona"].map(zona_coords)
    df_filtrado["x"] = df_filtrado["coords"].apply(lambda c: c[0])
    df_filtrado["y"] = df_filtrado["coords"].apply(lambda c: c[1])

    # Crear cancha
    pitch = VerticalPitch(pitch_type='statsbomb', line_color='white', pitch_color='grass')
    fig, ax = pitch.draw(figsize=(8, 6))

    # Heatmap
    pitch.kdeplot(
        x=df_filtrado["x"],
        y=df_filtrado["y"],
        ax=ax,
        fill=True,
        levels=100,
        cmap="Reds",
        shade_lowest=False,
        alpha=0.8
    )

    # Puntos individuales
    pitch.scatter(df_filtrado["x"], df_filtrado["y"], ax=ax, color="black", s=30, edgecolors='white', zorder=2)

    st.pyplot(fig)

    # -----------------------------
    # DESCARGA CSV
    # -----------------------------
    csv = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar CSV", csv, "acciones_zonas.csv", "text/csv")

else:
    st.info("Aún no has registrado ninguna acción.")
