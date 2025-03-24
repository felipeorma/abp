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

    # Coordenadas rotadas 90 grados (intercambiamos X e Y)
    zona_coords = {
        1: (100, 5),   2: (100, 63),     # Esquinas superiores
        3: (78, 18),   4: (78, 50),      # Laterales superiores
        5: (95, 30),   6: (95, 38),      # Central superior
        7: (95, 34),   8: (95, 22),
        9: (95, 46),   10: (88, 30),     # Delantera
        11: (88, 38),  12: (88, 22),
        13: (88, 46),  14: (70, 28),     # Mediocampo
        15: (70, 40),  16: (55, 20),     # Defensa
        17: (55, 48),  "Penal": (88, 34) # Punto penal
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
        
        # Aplicamos la rotación visual (sin modificar los datos)
        if not x.empty and not y.empty:
            pitch.kdeplot(x=y, y=x, ax=ax, fill=True,  # Intercambiamos X e Y aquí
                         levels=50, cmap=cmap, alpha=0.6)
            pitch.scatter(y, x, ax=ax, color="black",  # Intercambiamos X e Y aquí
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