import streamlit as st
import pandas as pd
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
# FORMULARIO (se mantiene igual)
# ----------------------------------------
with st.expander("➕ Registrar nueva acción"):
    tipo = st.selectbox("Tipo de balón parado", ["Tiro libre", "Córner", "Lateral", "Penal"])
    minuto = st.number_input("⏱️ Minuto", min_value=0, max_value=120, value=0)

    if tipo == "Córner":
        zona_saque = st.selectbox("📍 Zona de saque (solo esquinas)", [1, 2])
    elif tipo == "Penal":
        zona_saque = "Penal"
    else:
        zona_saque = st.selectbox("📍 Zona de saque", list(range(1, 18)))

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
# DATOS Y HEATMAP (parte modificada)
# ----------------------------------------
df = pd.DataFrame(st.session_state.registro)

if not df.empty:
    st.subheader("📋 Acciones registradas")
    filtro_tipo = st.multiselect("🎯 Filtrar por tipo", df["tipo"].unique(), default=df["tipo"].unique())
    df_filtrado = df[df["tipo"].isin(filtro_tipo)]

    st.dataframe(df_filtrado)

    # Coordenadas invertidas para mitad superior vertical
    zona_coords = {
        1: (5, 60),   2: (63, 60),     # Esquinas superiores
        3: (18, 40),  4: (50, 40),     # Laterales superiores
        5: (30, 55),  6: (38, 55),     # Central superior
        7: (34, 55),  8: (22, 55), 
        9: (46, 55),  10: (30, 50),    # Delantera
        11: (38, 50), 12: (22, 50),
        13: (46, 50), 14: (28, 35),    # Mediocampo
        15: (40, 35), 16: (20, 25),    # Defensa
        17: (48, 25), "Penal": (34, 45)  # Punto penal
    }

    # Asignar coordenadas invertidas
    df_filtrado["coords_saque"] = df_filtrado["zona_saque"].map(zona_coords)
    df_filtrado = df_filtrado.dropna(subset=["coords_saque"])
    df_filtrado["x_saque"] = df_filtrado["coords_saque"].apply(lambda c: c[0])
    df_filtrado["y_saque"] = df_filtrado["coords_saque"].apply(lambda c: 100 - c[1])  # Invertir eje Y

    df_filtrado["coords_remate"] = df_filtrado["zona_remate"].map(zona_coords)
    df_filtrado = df_filtrado.dropna(subset=["coords_remate"])
    df_filtrado["x_remate"] = df_filtrado["coords_remate"].apply(lambda c: c[0])
    df_filtrado["y_remate"] = df_filtrado["coords_remate"].apply(lambda c: 100 - c[1])  # Invertir eje Y

    def dibujar_half_pitch(title, x, y, cmap):
        st.subheader(title)
        pitch = VerticalPitch(pitch_type='statsbomb', line_color='white', 
                            pitch_color='grass', half=True)
        fig, ax = pitch.draw(figsize=(8, 6))
        
        # Invertir eje Y automáticamente
        ax.invert_yaxis()
        
        if not x.empty and not y.empty:
            pitch.kdeplot(x=x, y=y, ax=ax, fill=True, 
                         levels=50, cmap=cmap, alpha=0.6)
            pitch.scatter(x, y, ax=ax, color="black", 
                         s=30, edgecolors='white')
        st.pyplot(fig)

    if not df_filtrado.empty:
        dibujar_half_pitch("🟢 Heatmap - Zona de Saque", 
                          df_filtrado["x_saque"], 
                          df_filtrado["y_saque"], "Greens")
        dibujar_half_pitch("🔴 Heatmap - Zona de Remate", 
                          df_filtrado["x_remate"], 
                          df_filtrado["y_remate"], "Reds")
    else:
        st.warning("No hay datos suficientes para generar el heatmap.")

    csv = df_filtrado.drop(columns=["coords_saque", "coords_remate"]).to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar CSV", csv, "acciones_zonas.csv", "text/csv")

else:
    st.info("Aún no has registrado ninguna acción.")