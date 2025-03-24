import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from mplsoccer import VerticalPitch

# ---------------------------
# INICIALIZACIÓN DE SESIÓN
# ---------------------------
if "registro" not in st.session_state:
    st.session_state.registro = []

# ---------------------------
# CARGAR IMAGEN DE ZONAS
# ---------------------------
img = Image.open("MedioCampo_enumerado.JPG")

st.set_page_config(layout="centered")
st.title("⚽ Registro de Acciones de Balón Parado")

# Mostrar imagen de referencia
st.image(img, caption="Zonas numeradas del campo (portería arriba)", use_column_width=True)

# ---------------------------
# FORMULARIO DE REGISTRO
# ---------------------------
with st.expander("➕ Registrar nueva acción"):
    tipo = st.selectbox("Tipo de balón parado", ["Tiro libre", "Córner", "Lateral", "Penal"])
    minuto = st.number_input("⏱️ Minuto", min_value=0, max_value=120, value=0)
    zona_saque = st.selectbox("📍 Zona de saque (inicio)", list(range(1, 18)))
    zona_remate = st.selectbox("🎯 Zona de remate (finalización)", list(range(1, 18)))
    ejecutor = st.text_input("👟 Ejecutante")
    primer_contacto = st.text_input("🎯 Primer contacto")
    segundo_contacto = st.text_input("📌 Segundo contacto (opcional)")

    if st.button("✅ Registrar acción"):
        st.session_state.registro.append({
            "tipo": tipo,
            "minuto": minuto,
            "zona_saque": zona_saque,
            "zona_remate": zona_remate,
            "ejecutor": ejecutor,
            "primer_contacto": primer_contacto,
            "segundo_contacto": segundo_contacto
        })
        st.success("✔️ Acción registrada correctamente")

# ---------------------------
# MOSTRAR TABLA Y FILTROS
# ---------------------------
df = pd.DataFrame(st.session_state.registro)

if not df.empty:
    st.subheader("📋 Acciones registradas")

    filtro_tipo = st.multiselect("🎯 Filtrar por tipo de jugada", df["tipo"].unique(), default=df["tipo"].unique())
    df_filtrado = df[df["tipo"].isin(filtro_tipo)]

    st.dataframe(df_filtrado)

    # ---------------------------
    # MAPA DE ZONAS A COORDENADAS
    # ---------------------------
    zona_coords = {
        1: (10, 95),   2: (58, 95),
        3: (18, 78),   4: (50, 78),
        5: (30, 100),  6: (38, 100),  7: (34, 100),  8: (22, 100), 9: (46, 100),
        10: (30, 88), 11: (38, 88), 12: (22, 88), 13: (46, 88),
        14: (28, 70), 15: (40, 70),
        16: (20, 55), 17: (48, 55)
    }

    # Asignar coordenadas a ZONA DE SAQUE
    df_filtrado["coords_saque"] = df_filtrado["zona_saque"].map(zona_coords)
    df_filtrado = df_filtrado.dropna(subset=["coords_saque"])
    df_filtrado["x_saque"] = df_filtrado["coords_saque"].apply(lambda c: c[0])
    df_filtrado["y_saque"] = df_filtrado["coords_saque"].apply(lambda c: c[1])

    # Asignar coordenadas a ZONA DE REMATE
    df_filtrado["coords_remate"] = df_filtrado["zona_remate"].map(zona_coords)
    df_filtrado = df_filtrado.dropna(subset=["coords_remate"])
    df_filtrado["x_remate"] = df_filtrado["coords_remate"].apply(lambda c: c[0])
    df_filtrado["y_remate"] = df_filtrado["coords_remate"].apply(lambda c: c[1])

    # ---------------------------
    # HEATMAP DE ZONA DE SAQUE
    # ---------------------------
    st.subheader("🟢 Zona de Saque - Heatmap")

    pitch = VerticalPitch(pitch_type='statsbomb', line_color='white', pitch_color='grass')
    fig1, ax1 = pitch.draw(figsize=(8, 6))
    ax1.invert_yaxis()

    pitch.kdeplot(
        x=df_filtrado["x_saque"],
        y=df_filtrado["y_saque"],
        ax=ax1,
        fill=True,
        levels=100,
        cmap="Greens",
        shade_lowest=False,
        alpha=0.8
    )
    pitch.scatter(df_filtrado["x_saque"], df_filtrado["y_saque"], ax=ax1, color="black", s=30, edgecolors='white')
    st.pyplot(fig1)

    # ---------------------------
    # HEATMAP DE ZONA DE REMATE
    # ---------------------------
    st.subheader("🔴 Zona de Remate - Heatmap")

    pitch = VerticalPitch(pitch_type='statsbomb', line_color='white', pitch_color='grass')
    fig2, ax2 = pitch.draw(figsize=(8, 6))
    ax2.invert_yaxis()

    pitch.kdeplot(
        x=df_filtrado["x_remate"],
        y=df_filtrado["y_remate"],
        ax=ax2,
        fill=True,
        levels=100,
        cmap="Reds",
        shade_lowest=False,
        alpha=0.8
    )
    pitch.scatter(df_filtrado["x_remate"], df_filtrado["y_remate"], ax=ax2, color="black", s=30, edgecolors='white')
    st.pyplot(fig2)

    # ---------------------------
    # DESCARGA CSV
    # ---------------------------
    csv = df_filtrado.drop(columns=["coords_saque", "coords_remate"]).to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar CSV", csv, "acciones_zonas.csv", "text/csv")

else:
    st.info("Aún no has registrado ninguna acción.")

