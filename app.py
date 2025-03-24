import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Inicializar sesión
if "registro" not in st.session_state:
    st.session_state.registro = []
if "fase" not in st.session_state:
    st.session_state.fase = "inicio"
if "accion" not in st.session_state:
    st.session_state.accion = ""
if "coordenadas_inicio" not in st.session_state:
    st.session_state.coordenadas_inicio = None
if "ejecutor" not in st.session_state:
    st.session_state.ejecutor = ""
if "receptor" not in st.session_state:
    st.session_state.receptor = ""

st.title("Registro de Acciones de Balón Parado")

st.subheader("1. Selecciona el tipo de acción:")
accion = st.radio("Tipo de balón parado", ["Tiro libre", "Córner", "Lateral", "Penal"])
st.session_state.accion = accion

st.subheader("2. Haz clic en el campo para registrar la acción")

# Dibujar el campo (mitad)
fig = go.Figure()

# Fondo del campo
fig.add_shape(type="rect", x0=0, y0=0, x1=68, y1=52.5, line=dict(color="white", width=3), fillcolor="green")

fig.update_layout(
    xaxis=dict(range=[0, 68], showgrid=False),
    yaxis=dict(range=[0, 52.5], showgrid=False),
    width=700,
    height=500,
    margin=dict(l=10, r=10, t=10, b=10),
    plot_bgcolor="green",
    clickmode='event+select'
)

click = st.plotly_chart(fig, use_container_width=True)

# Obtener clic desde Streamlit event
click_data = st.session_state.get("plotly_click_event")

if click_data:
    x = click_data["points"][0]["x"]
    y = click_data["points"][0]["y"]
    
    if st.session_state.fase == "inicio":
        st.session_state.coordenadas_inicio = (x, y)
        st.session_state.ejecutor = st.text_input("¿Quién ejecutó la jugada?", key="ejecutor")
        if st.session_state.ejecutor:
            st.session_state.fase = "esperando_fin"
            st.success("Ahora haz clic donde terminó la jugada.")
    
    elif st.session_state.fase == "esperando_fin":
        x_fin, y_fin = x, y
        st.session_state.receptor = st.text_input("¿Quién recibió la jugada?", key="receptor")
        if st.session_state.receptor:
            st.session_state.registro.append({
                "acción": st.session_state.accion,
                "ejecutor": st.session_state.ejecutor,
                "x_inicio": st.session_state.coordenadas_inicio[0],
                "y_inicio": st.session_state.coordenadas_inicio[1],
                "x_fin": x_fin,
                "y_fin": y_fin,
                "receptor": st.session_state.receptor
            })
            st.success("Acción registrada ✅")
            # Reset
            st.session_state.fase = "inicio"
            st.session_state.ejecutor = ""
            st.session_state.receptor = ""
            st.session_state.coordenadas_inicio = None

# Mostrar acciones registradas
df = pd.DataFrame(st.session_state.registro)
if not df.empty:
    st.subheader("Acciones registradas")
    st.dataframe(df)
