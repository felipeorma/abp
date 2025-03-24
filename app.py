
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from mplsoccer import VerticalPitch

# Inicialización
if "registro" not in st.session_state:
    st.session_state.registro = []

img = Image.open("MedioCampo_enumerado.JPG")

st.set_page_config(layout="centered")
st.title("⚽ Registro de Acciones de Balón Parado")

st.image(img, caption="Zonas numeradas (portería arriba)", use_column_width=True)

# ----------------------------------------
# FORMULARIO
# ----------------------------------------
with st.expander("➕ Registrar nueva acción"):
    tipo = st.selectbox("Tipo de balón parado", ["Tiro libre", "Córner", "Lateral", "Penal"])
    minuto = st.number_input("⏱️ Minuto", min_value=0, max_value=120, value=0)

    # Lógica condicional para zona de saque
    if tipo == "Córner":
        zona_saque = st.selectbox("📍 Zona de saque (solo esquinas)", [1, 2])
    elif tipo == "Penal":
        zona_saque = "Penal"
    else:
        zona_saque = st.selectbox("📍 Zona de saque", list(range(1, 18)))

    # Zona de remate
    if tipo == "Penal":
        zona_remate = "Penal"
    else:
        zona_remate = st.selectbox("🎯 Zona de remate", list(range(1, 18)))

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

# ----------------------------------------
# DATOS Y HEATMAP
# ----------------------------------------
df = pd.DataFrame(st.session_state.registro)

if not df.empty:
    st.subheader("📋 Acciones registradas")
    filtro_tipo = st.multiselect("🎯 Filtrar por tipo", df["tipo"].unique(), default=df["tipo"].unique())
    df_filtrado = df[df["tipo"].isin(filtro_tipo)]

    st.dataframe(df_filtrado)

    # Coordenadas rotadas 180 grados (volteamos ambos ejes)
    zona_coords = {
        1: (100, 95),   2: (100, 37),     # Esquinas superiores
        3: (78, 82),    4: (78, 50),      # Laterales superiores
        5: (95, 70),    6: (95, 62),      # Central superior
        7: (95, 66),    8: (95, 78),
        9: (95, 54),    10: (88, 70),     # Delantera
        11: (88, 62),   12: (88, 78),
        13: (88, 54),   14: (70, 72),     # Mediocampo
        15: (70, 60),   16: (55, 80),     # Defensa
        17: (55, 52),   "Penal": (88, 66) # Punto penal
    }

    # Asignar coordenadas rotadas
    df_filtrado["coords_saque"] = df_filtrado["zona_saque"].map(zona_coords)
    df_filtrado = df_filtrado.dropna(subset=["coords_saque"])
    df_filtrado["x_saque"] = df_filtrado["coords_saque"].apply(lambda c: c[0])
    df_filtrado["y_saque"] = df_filtrado["coords_saque"].apply(lambda c: c[1])

    df_filtrado["coords_remate"] = df_filtrado["zona_remate"].map(zona_coords)
    df_filtrado = df_filtrado.dropna(subset=["coords_remate"])
    df_filtrado["x_remate"] = df_filtrado["coords_remate"].apply(lambda c: c[0])
    df_filtrado["y_remate"] = df_filtrado["coords_remate"].apply(lambda c: c[1])

    def dibujar_half_pitch(title, x, y, cmap):
        st.subheader(title)
        pitch = VerticalPitch(pitch_type='statsbomb', line_color='white', 
                            pitch_color='grass', half=True)
        fig, ax = pitch.draw(figsize=(8, 6))
        
        # Aplicamos la rotación visual (intercambiamos y complementamos)
        if not x.empty and not y.empty:
            pitch.kdeplot(x=100-np.array(y), y=100-np.array(x), ax=ax, fill=True,
                         levels=50, cmap=cmap, alpha=0.6)
            pitch.scatter(100-np.array(y), 100-np.array(x), ax=ax, color="black",
                         s=30, edgecolors='white')
        st.pyplot(fig)

    # Heatmaps
    if not df_filtrado.empty:
        dibujar_half_pitch("🟢 Heatmap - Zona de Saque", 
                          df_filtrado["x_saque"], 
                          df_filtrado["y_saque"], "Greens")
        dibujar_half_pitch("🔴 Heatmap - Zona de Remate", 
                          df_filtrado["x_remate"], 
                          df_filtrado["y_remate"], "Reds")
    else:
        st.warning("No hay datos suficientes para generar el heatmap.")

    # Descargar CSV
    csv = df_filtrado.drop(columns=["coords_saque", "coords_remate"]).to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar CSV", csv, "acciones_zonas.csv", "text/csv")

else:
    st.info("Aún no has registrado ninguna acción.")