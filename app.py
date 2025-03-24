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

st.image(img, caption="Zonas numeradas (referencia visual)", use_column_width=True)

# ----------------------------------------
# FORMULARIO
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
        zona_remate = st.selectbox("🌟 Zona de remate", list(range(1, 18)))

    ejecutor = st.text_input("👟 Ejecutante")
    primer_contacto = st.text_input("🌟 Primer contacto")
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
    filtro_tipo = st.multiselect("🌟 Filtrar por tipo", df["tipo"].unique(), default=df["tipo"].unique())
    df_filtrado = df[df["tipo"].isin(filtro_tipo)]

    st.dataframe(df_filtrado)

    # Coordenadas calibradas para medio campo superior (campo completo)
    zona_coords = {
        1: (10, 10),   2: (90, 10),
        3: (25, 25),   4: (75, 25),
        5: (40, 5),    6: (60, 5),    7: (50, 5),
        8: (30, 5),    9: (70, 5),
        10: (40, 20),  11: (60, 20),
        12: (30, 20),  13: (70, 20),
        14: (38, 35),  15: (62, 35),
        16: (25, 48),  17: (75, 48),
        "Penal": (50, 20)
    }

    df_filtrado["coords_saque"] = df_filtrado["zona_saque"].map(zona_coords)
    df_filtrado = df_filtrado.dropna(subset=["coords_saque"])
    df_filtrado["x_saque"] = df_filtrado["coords_saque"].apply(lambda c: c[0])
    df_filtrado["y_saque"] = df_filtrado["coords_saque"].apply(lambda c: c[1])

    df_filtrado["coords_remate"] = df_filtrado["zona_remate"].map(zona_coords)
    df_filtrado = df_filtrado.dropna(subset=["coords_remate"])
    df_filtrado["x_remate"] = df_filtrado["coords_remate"].apply(lambda c: c[0])
    df_filtrado["y_remate"] = df_filtrado["coords_remate"].apply(lambda c: c[1])

    def dibujar_pitch_completo(title, x, y, cmap):
        st.subheader(title)
        pitch = VerticalPitch(pitch_type='statsbomb', line_color='white', pitch_color='grass')
        fig, ax = pitch.draw(figsize=(6, 9))

        # Restringir a la mitad superior del campo (portería arriba)
        ax.set_ylim(55, 0)

        pitch.scatter(x, y, ax=ax, color="black", s=30, edgecolors='white')

        if len(x) >= 2:
            pitch.kdeplot(x=x, y=y, ax=ax, fill=True, levels=100, cmap=cmap, alpha=0.8)

        for zona, (x_z, y_z) in zona_coords.items():
            if isinstance(zona, int):
                ax.text(x_z, y_z, str(zona), fontsize=11, color='white', weight='bold', ha='center', va='center',
                        bbox=dict(facecolor='black', edgecolor='none', boxstyle='circle,pad=0.2'))

        st.pyplot(fig)

    dibujar_pitch_completo("🟢 Heatmap - Zona de Saque", df_filtrado["x_saque"], df_filtrado["y_saque"], "Greens")
    dibujar_pitch_completo("🔴 Heatmap - Zona de Remate", df_filtrado["x_remate"], df_filtrado["y_remate"], "Reds")

    csv = df_filtrado.drop(columns=["coords_saque", "coords_remate"]).to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar CSV", csv, "acciones_zonas.csv", "text/csv")

else:
    st.info("Aún no has registrado ninguna acción.")
