import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Zonas agrupadas para el campo
zonas_definidas = [
    "Frontal", "Lado izquierdo", "Lado derecho",
    "Cerca del córner", "Cerca del área",
    "Primer palo", "Segundo palo", "Media luna",
    "Fuera del área", "Remate bloqueado", "Otra"
]

# Inicializar sesión
if "registro" not in st.session_state:
    st.session_state.registro = []

st.title("📊 Visualizador de Acciones de Balón Parado")

# Formulario de registro
with st.expander("➕ Registrar nueva acción"):
    tipo = st.selectbox("Tipo de balón parado", ["Tiro libre", "Córner", "Lateral", "Penal"])
    zona_inicio = st.selectbox("📍 Zona de ejecución", zonas_definidas)
    zona_fin = st.selectbox("🎯 Zona de finalización", zonas_definidas)
    minuto = st.number_input("⏱️ Minuto de la jugada", min_value=0, max_value=120, value=0)
    ejecutor = st.text_input("👟 Nombre del ejecutor")
    primer_contacto = st.text_input("🧠 Primer contacto (quien recibió)")
    segundo_contacto = st.text_input("📌 Segundo contacto (opcional)")

    if st.button("✅ Registrar acción"):
        st.session_state.registro.append({
            "tipo": tipo,
            "zona_inicio": zona_inicio,
            "zona_fin": zona_fin,
            "minuto": minuto,
            "ejecutor": ejecutor,
            "primer_contacto": primer_contacto,
            "segundo_contacto": segundo_contacto
        })
        st.success("✔️ Acción registrada")

# Mostrar tabla
df = pd.DataFrame(st.session_state.registro)

if not df.empty:
    st.subheader("📋 Acciones registradas")
    
    # Filtro por tipo de acción
    tipos_disponibles = df["tipo"].unique().tolist()
    filtro_tipo = st.multiselect("🎯 Filtrar por tipo de balón parado", tipos_disponibles, default=tipos_disponibles)
    
    df_filtrado = df[df["tipo"].isin(filtro_tipo)]

    st.dataframe(df_filtrado)

    # ---------------------------
    # HEATMAP POR ZONAS AGRUPADAS
    # ---------------------------
    st.subheader("🔥 Heatmap por zonas de finalización")
    
    zona_counts = df_filtrado["zona_fin"].value_counts().reindex(zonas_definidas, fill_value=0)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(
        zona_counts.values.reshape(1, -1),
        annot=True,
        fmt="d",
        cmap="Reds",
        xticklabels=zonas_definidas,
        yticklabels=["Zonas"],
        cbar=False,
        linewidths=1,
        linecolor='black'
    )
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig)

    # ---------------------------
    # DESCARGA DE CSV
    # ---------------------------
    csv = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar CSV", csv, "acciones_balon_parado.csv", "text/csv")

else:
    st.info("Aún no has registrado ninguna acción.")
