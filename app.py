import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Inicializar estado
if "registro" not in st.session_state:
    st.session_state.registro = []
if "fase" not in st.session_state:
    st.session_state.fase = "esperando_inicio"
if "temp_data" not in st.session_state:
    st.session_state.temp_data = {}

st.title("⚽ Registro de Acciones de Balón Parado")

# Paso 1: Tipo de acción
accion = st.selectbox("Tipo de balón parado", ["Tiro libre", "Córner", "Lateral", "Penal"])

# Paso 2: Mostrar mitad de cancha con Plotly
st.subheader("Haz clic en la mitad del campo para registrar la acción")

# Dimensiones para media cancha
fig = go.Figure()

# Fondo cancha
fig.add_shape(type="rect", x0=0, y0=0, x1=60, y1=40,
              line=dict(color="white", width=2), fillcolor="green")

# Área
fig.add_shape(type="rect", x0=0, y0=13, x1=16.5, y1=27,
              line=dict(color="white", width=2))

# Punto penal
fig.add_shape(type="circle", x0=10.5 - 0.2, x1=10.5 + 0.2, y0=20 - 0.2, y1=20 + 0.2,
              line=dict(color="white"), fillcolor="white")

fig.update_layout(
    width=700,
    height=500,
    margin=dict(l=10, r=10, t=10, b=10),
    plot_bgcolor="green",
    paper_bgcolor="green",
    xaxis=dict(range=[0, 60], showgrid=False, zeroline=False),
    yaxis=dict(range=[0, 40], showgrid=False, zeroline=False),
    clickmode='event+select'
)

click = st.plotly_chart(fig, use_container_width=True)

# Captura de clic
event = st.get_click_data()

if event:
    x = event["points"][0]["x"]
    y = event["points"][0]["y"]

    if st.session_state.fase == "esperando_inicio":
        st.session_state.temp_data["x_inicio"] = x
        st.session_state.temp_data["y_inicio"] = y
        st.session_state.fase = "esperando_final"
        st.success("📍 Punto de ejecución registrado. Ahora haz clic donde finalizó la acción.")
    elif st.session_state.fase == "esperando_final":
        st.session_state.temp_data["x_fin"] = x
        st.session_state.temp_data["y_fin"] = y
        st.session_state.fase = "datos"

# Cuando ambos clics estén listos
if st.session_state.fase == "datos":
    st.subheader("Completa los detalles de la jugada:")
    ejecutor = st.text_input("Nombre del ejecutor")
    primer_contacto = st.text_input("Primer contacto (jugador que recibió)")
    segundo_contacto = st.text_input("Segundo contacto (opcional)")

    if st.button("Registrar acción"):
        st.session_state.temp_data.update({
            "tipo": accion,
            "ejecutor": ejecutor,
            "primer_contacto": primer_contacto,
            "segundo_contacto": segundo_contacto
        })
        st.session_state.registro.append(st.session_state.temp_data.copy())
        st.success("✅ Acción registrada con éxito")
        st.session_state.fase = "esperando_inicio"
        st.session_state.temp_data = {}

# Mostrar registros
df = pd.DataFrame(st.session_state.registro)
if not df.empty:
    st.subheader("📊 Acciones registradas")
    st.dataframe(df)

    # Botón para descargar CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Descargar CSV", csv, "acciones_balon_parado.csv", "text/csv")

