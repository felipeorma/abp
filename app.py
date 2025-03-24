import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

# Cargar imagen de zonas numeradas
img = Image.open("image.png")

# Inicializar session state
if "registro" not in st.session_state:
    st.session_state.registro = []

st.title("⚽ Acciones de balón parado por zona (media cancha)")

# Mostrar imagen del campo
st.image(img, caption="Zonas numeradas de la mitad del campo", use_column_width=True)

with st.expander("➕ Registrar nueva acción"):
    tipo = st.selectbox("Tipo de balón parado", ["Tiro libre", "Córner", "Lateral", "Penal"])
    minuto = st.number_input("⏱️ Minuto de la jugada", min_value=0, max_value=120, value=0)
    zona = st.selectbox("📍 Zona final de la acción (ver imagen)", list(range(1, 18)))
    ejecutor = st.text_input("👟 Nombre del ejecutor")
    primer_contacto = st.text_input("🧠 Primer contacto (quien recibió)")
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
        st.success("✔️ Acción registrada")

# Mostrar tabla
df = pd.DataFrame(st.session_state.registro)

if not df.empty:
    st.subheader("📋 Acciones registradas")
    
    filtro_tipo = st.multiselect("🎯 Filtrar por tipo de jugada", df["tipo"].unique(), default=df["tipo"].unique())
    df_filtrado = df[df["tipo"].isin(filtro_tipo)]

    st.dataframe(df_filtrado)

    # HEATMAP por zona
    st.subheader("🔥 Heatmap por zonas (número de acciones por zona)")
    zona_counts = df_filtrado["zona"].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(10, 1))
    sns.heatmap(
        zona_counts.values.reshape(1, -1),
        annot=True,
        fmt="d",
        cmap="OrRd",
        xticklabels=[f"Zona {i}" for i in zona_counts.index],
        yticklabels=["Acciones"],
        cbar=False,
        linewidths=1
    )
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # Botón para descargar CSV
    csv = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar CSV", csv, "acciones_zonales.csv", "text/csv")
else:
    st.info("Aún no has registrado ninguna acción.")
