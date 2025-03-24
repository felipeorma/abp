import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

# Cargar imagen del campo numerado
img = Image.open("MedioCampo_enumerado.JPG")

# Inicializar estado
if "registro" not in st.session_state:
    st.session_state.registro = []

st.title("⚽ Acciones de balón parado por zonas numeradas")

# Mostrar imagen de referencia
st.image(img, caption="Zonas numeradas para registrar acciones", use_column_width=True)

# -------------------------
# Registro de una nueva acción
# -------------------------
with st.expander("➕ Registrar nueva acción"):
    tipo = st.selectbox("Tipo de balón parado", ["Tiro libre", "Córner", "Lateral", "Penal"])
    minuto = st.number_input("⏱️ Minuto", min_value=0, max_value=120, value=0)
    zona = st.selectbox("📍 Zona final de la jugada", list(range(1, 18)))
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

# -------------------------
# Mostrar tabla y filtros
# -------------------------
df = pd.DataFrame(st.session_state.registro)
if not df.empty:
    st.subheader("📋 Acciones registradas")
    
    filtro_tipo = st.multiselect("🎯 Filtrar por tipo de jugada", df["tipo"].unique(), default=df["tipo"].unique())
    df_filtrado = df[df["tipo"].isin(filtro_tipo)]

    st.dataframe(df_filtrado)

    # -------------------------
    # Heatmap por zona
    # -------------------------
    st.subheader("🔥 Heatmap de zonas (cantidad de acciones por zona)")

    zona_counts = df_filtrado["zona"].value_counts().sort_index()
    zonas = list(range(1, 18))
    valores = [zona_counts.get(z, 0) for z in zonas]

    fig, ax = plt.subplots(figsize=(10, 1))
    sns.heatmap(
        [valores],
        cmap="Reds",
        annot=True,
        fmt="d",
        xticklabels=[f"Zona {z}" for z in zonas],
        yticklabels=["Acciones"],
        cbar=False,
        linewidths=1
    )
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # -------------------------
    # Descargar CSV
    # -------------------------
    csv = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar CSV", csv, "acciones_zonas.csv", "text/csv")

else:
    st.info("Aún no has registrado ninguna acción.")
