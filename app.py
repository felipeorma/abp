import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from mplsoccer import VerticalPitch
from PIL import Image

# Inicializar sesión
if "registro" not in st.session_state:
    st.session_state.registro = []

st.set_page_config(layout="centered")
st.title("⚽ Registro de Acciones de Balón Parado - Zonas Personalizadas")

# Mostrar imagen de referencia
img = Image.open("MedioCampo_enumerado.JPG")
st.image(img, caption="Referencia de zonas (portería arriba)", use_column_width=True)

# -------------------------
# FORMULARIO
# -------------------------
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

# -------------------------
# DATOS
# -------------------------
df = pd.DataFrame(st.session_state.registro)

if not df.empty:
    st.subheader("📋 Acciones registradas")
    filtro_tipo = st.multiselect("🌟 Filtrar por tipo", df["tipo"].unique(), default=df["tipo"].unique())
    df_filtrado = df[df["tipo"].isin(filtro_tipo)]
    st.dataframe(df_filtrado)

    # -------------------------
    # ZONAS CON COORDENADAS PARA VerticalPitch
    # -------------------------
    zonas = {
        1: (0, 80, 20, 20),   2: (78, 80, 18, 20),
        3: (0, 60, 20, 20),   4: (78, 60, 18, 20),
        5: (40, 96, 6, 4),    6: (60, 96, 6, 4),    7: (50, 96, 6, 4),
        8: (34, 96, 6, 4),    9: (66, 96, 6, 4),
        10: (40, 88, 6, 6),   11: (60, 88, 6, 6),
        12: (34, 88, 6, 6),   13: (66, 88, 6, 6),
        14: (40, 60, 6, 28),  15: (60, 60, 6, 28),
        16: (20, 40, 20, 20), 17: (60, 40, 18, 20),
        "Penal": (52, 89, 1, 1)
    }

    def zona_centro(z):
        if z == "Penal":
            return (52.5, 89.5)
        x, y, w, h = zonas[z]
        return (x + w / 2, y + h / 2)

    df_filtrado["coords_saque"] = df_filtrado["zona_saque"].map(zona_centro)
    df_filtrado["coords_remate"] = df_filtrado["zona_remate"].map(zona_centro)

    df_filtrado[["x_saque", "y_saque"]] = pd.DataFrame(df_filtrado["coords_saque"].tolist(), index=df_filtrado.index)
    df_filtrado[["x_remate", "y_remate"]] = pd.DataFrame(df_filtrado["coords_remate"].tolist(), index=df_filtrado.index)

    def graficar(title, x, y, cmap):
        st.subheader(title)
        pitch = VerticalPitch(pitch_type='statsbomb', line_color='white', pitch_color='grass', half=False)
        fig, ax = pitch.draw(figsize=(6, 9))

        for zona, (x0, y0, w, h) in zonas.items():
            if zona != "Penal":
                rect = Rectangle((x0, y0), w, h, linewidth=1, edgecolor='yellow', facecolor='none')
                ax.add_patch(rect)
                cx, cy = x0 + w / 2, y0 + h / 2
                ax.text(cx, cy, str(zona), color='white', ha='center', va='center', fontsize=10, weight='bold', bbox=dict(facecolor='black', boxstyle='circle,pad=0.2'))

        pitch.scatter(x, y, ax=ax, color='black', s=30, edgecolors='white')

        if len(x) >= 2:
            try:
                pitch.kdeplot(x=100 - y, y=x, ax=ax, fill=True, cmap=cmap, alpha=0.7, levels=100)
            except ValueError:
                st.warning("⚠️ No se pudo generar el heatmap (insuficiente variación o puntos muy juntos)")

        st.pyplot(fig)

    graficar("🟢 Heatmap - Zona de Saque", df_filtrado["x_saque"], df_filtrado["y_saque"], "Greens")
    graficar("🔴 Heatmap - Zona de Remate", df_filtrado["x_remate"], df_filtrado["y_remate"], "Reds")

    csv = df_filtrado.drop(columns=["coords_saque", "coords_remate"]).to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar CSV", csv, "acciones_zonas.csv", "text/csv")
else:
    st.info("Aún no has registrado ninguna acción.")
