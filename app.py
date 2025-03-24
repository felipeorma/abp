import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from mplsoccer import Pitch

# Inicializar sesión
if "registro" not in st.session_state:
    st.session_state.registro = []

st.set_page_config(layout="centered")
st.title("⚽ Registro de Acciones de Balón Parado - Zonas Personalizadas")

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
    # ZONAS SOBRE EL CAMPO
    # -------------------------
    zonas = {
        1: (0, 0, 20, 20),     2: (100, 0, 20, 20),
        3: (20, 20, 20, 20),   4: (80, 20, 20, 20),
        5: (40, 0, 10, 12),    6: (70, 0, 10, 12),    7: (55, 0, 10, 12),
        8: (30, 0, 10, 12),    9: (90, 0, 10, 12),
        10: (40, 12, 10, 8),   11: (70, 12, 10, 8),
        12: (30, 12, 10, 8),   13: (90, 12, 10, 8),
        14: (40, 20, 10, 20),  15: (70, 20, 10, 20),
        16: (20, 40, 20, 20),  17: (80, 40, 20, 20),
        "Penal": (60, 11, 1, 1)
    }

    def zona_centro(z):
        if z == "Penal":
            return (60.5, 11.5)
        x, y, w, h = zonas[z]
        return (x + w / 2, y + h / 2)

    df_filtrado["coords_saque"] = df_filtrado["zona_saque"].map(zona_centro)
    df_filtrado["coords_remate"] = df_filtrado["zona_remate"].map(zona_centro)

    df_filtrado[["x_saque", "y_saque"]] = pd.DataFrame(df_filtrado["coords_saque"].tolist(), index=df_filtrado.index)
    df_filtrado[["x_remate", "y_remate"]] = pd.DataFrame(df_filtrado["coords_remate"].tolist(), index=df_filtrado.index)

    def graficar(title, x, y, cmap):
        st.subheader(title)
        pitch = Pitch(pitch_type='statsbomb', line_color='white', pitch_color='grass')
        fig, ax = pitch.draw(figsize=(8, 6))

        # Dibujar zonas
        for zona, (x0, y0, w, h) in zonas.items():
            if zona != "Penal":
                rect = Rectangle((x0, y0), w, h, linewidth=1, edgecolor='yellow', facecolor='none')
                ax.add_patch(rect)
                cx, cy = x0 + w / 2, y0 + h / 2
                ax.text(cx, cy, str(zona), color='white', ha='center', va='center', fontsize=10, weight='bold', bbox=dict(facecolor='black', boxstyle='circle,pad=0.2'))

        pitch.scatter(x, y, ax=ax, color='black', s=30, edgecolors='white')

        if len(x) >= 2:
            try:
                pitch.kdeplot(x=x, y=y, ax=ax, fill=True, cmap=cmap, alpha=0.7, levels=100)
            except ValueError:
                st.warning("⚠️ No se pudo generar el heatmap (insuficiente variación o puntos muy juntos)")

        st.pyplot(fig)

    graficar("🟢 Heatmap - Zona de Saque", df_filtrado["x_saque"], df_filtrado["y_saque"], "Greens")
    graficar("🔴 Heatmap - Zona de Remate", df_filtrado["x_remate"], df_filtrado["y_remate"], "Reds")

    # Descargar CSV
    csv = df_filtrado.drop(columns=["coords_saque", "coords_remate"]).to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar CSV", csv, "acciones_zonas.csv", "text/csv")
else:
    st.info("Aún no has registrado ninguna acción.")
