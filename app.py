import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Inicializar estado
if "registro" not in st.session_state:
    st.session_state.registro = []
if "fase" not in st.session_state:
    st.session_state.fase = "inicio"
if "temp" not in st.session_state:
    st.session_state.temp = {}

st.set_page_config(layout="wide")
st.title("⚽ Registro de Acciones de Balón Parado")

# Paso 1: Tipo de balón parado
accion = st.selectbox("Tipo de balón parado", ["Tiro libre", "Córner", "Lateral", "Penal"])

# Cancha vertical invertida (portería abajo)
fig = go.Figure()

# Fondo y líneas básicas
fig.add_shape(type="rect", x0=0, x1=68, y0=0, y1=52.5, line=dict(color="white", width=3), fillcolor="green")

# Área grande (invertida)
fig.add_shape(type="rect", x0=13.84, x1=54.16, y0=52.5-16.5, y1=52.5, line=dict(color="white", width=2))

# Punto penal
fig.add_shape(type="circle", x0=34 - 0.2, x1=34 + 0.2, y0=41 - 0.2, y1=41 + 0.2,
              line=dict(color="white"), fillcolor="white")

# Arco
fig.add_shape(type="rect", x0=30.34, x1=37.66, y0=52.5, y1=52.5+1.5, line=dict(color="white", width=2))

# Visual settings
fig.update_layout(
    xaxis=dict(range=[0, 68], visible=False),
    yaxis=dict(range=[52.5, 0], visible=False),  # ← ¡Aquí invertimos!
    plot_bgcolor="green",
    height=700,
    clickmode='event+select',
    margin=dict(l=10, r=10, t=10, b=10)
)

# Mostrar cancha y capturar clics (con return_click_data=True)
click_data = st.plotly_chart(fig, use_container_width=True, click_event=True)

event = st.session_state.get("plotly_click_event")

if event:
    x = event["points"][0]["x"]
    y = event["points"][0]["y"]

    if st.session_state.fase == "inicio":
        st.session_state.temp["tipo"] = accion
        st.session_state.temp["x_inicio"] = x
        st.session_state.temp["y_inicio"] = y
        st.session_state.fase = "esperando_final"
        st.success(f"📍 Punto de ejecución registrado en ({x:.1f}, {y:.1f}). Haz clic donde terminó la jugada.")
    
    elif st.session_state.fase == "esperando_final":
        st.session_state.temp["x_fin"] = x
        st.session_state.temp["y_fin"] = y
        st.session_state.fase = "datos"

# Paso final: ingreso de datos
if st.session_state.fase == "datos":
    st.subheader("✏️ Completa los datos de la jugada:")
    ejecutor = st.text_input("Nombre del ejecutor")
    primer_contacto = st.text_input("Primer contacto (jugador que recibió)")
    segundo_contacto = st.text_input("Segundo contacto (opcional)")

    if st.button("Registrar acción"):
        st.session_state.temp.update({
            "ejecutor": ejecutor,
            "primer_contacto": primer_contacto,
            "segundo_contacto": segundo_contacto
        })
        st.session_state.registro.append(st.session_state.temp.copy())
        st.session_state.temp = {}
        st.session_state.fase = "inicio"
        st.success("✅ Acción registrada correctamente.")

# Mostrar tabla
df = pd.DataFrame(st.session_state.registro)
if not df.empty:
    st.subheader("📊 Acciones registradas")
    st.dataframe(df)

    # Exportar CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar CSV", csv, "acciones_balon_parado.csv", "text/csv")

