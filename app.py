import streamlit as st
import pandas as pd

# Inicializar sesión
if "registro" not in st.session_state:
    st.session_state.registro = []

st.title("⚽ Registro de Acciones de Balón Parado")

# Paso 1: Tipo de balón parado
accion = st.selectbox("Tipo de balón parado", ["Tiro libre", "Córner", "Lateral", "Penal"])

# Paso 2: Zona donde se ejecutó la jugada
zona_inicio = st.selectbox("📍 Zona de ejecución", [
    "Frontal", "Lado izquierdo", "Lado derecho", 
    "Cerca del córner", "Cerca del área", "Otra"
])

# Paso 3: Zona donde terminó la jugada
zona_fin = st.selectbox("🎯 Zona de finalización", [
    "Primer palo", "Segundo palo", "Media luna", 
    "Fuera del área", "Remate bloqueado", "Otra"
])

# Paso 4: Datos del jugador
ejecutor = st.text_input("👟 Nombre del ejecutor")
primer_contacto = st.text_input("🧠 Primer contacto (quien recibió)")
segundo_contacto = st.text_input("📌 Segundo contacto (opcional)")

# Botón para registrar
if st.button("✅ Registrar acción"):
    st.session_state.registro.append({
        "tipo": accion,
        "zona_inicio": zona_inicio,
        "zona_fin": zona_fin,
        "ejecutor": ejecutor,
        "primer_contacto": primer_contacto,
        "segundo_contacto": segundo_contacto
    })
    st.success("✔️ Acción registrada con éxito")

# Mostrar tabla
df = pd.DataFrame(st.session_state.registro)
if not df.empty:
    st.subheader("📊 Acciones registradas")
    st.dataframe(df)

    # Exportar CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar CSV", csv, "acciones_balon_parado.csv", "text/csv")


