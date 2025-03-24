import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --------------------------
# INICIALIZAR SESSION STATE
# --------------------------
if "fase" not in st.session_state:
    st.session_state.fase = "inicio"
if "temp" not in st.session_state:
    st.session_state.temp = {}
if "registro" not in st.session_state:
    st.session_state.registro = []
if "last_click" not in st.session_state:
    st.session_state.last_click = None

st.title("⚽ Registro de Acciones de Balón Parado")

# --------------------------
# SELECCIÓN DE LA ACCIÓN
# --------------------------
accion = st.selectbox("Tipo de balón parado", ["Tiro libre", "Córner", "Lateral", "Penal"])

# --------------------------
# DIBUJAR CANCHA VERTICAL
# --------------------------
fig = go.Figure()

# Fondo y límites
fig.add_shape(type="rect", x0=0, x1=68, y0=0, y1=52.5, line=dict(color="white"), fillcolor="green")

# Área grande
fig.add_shape(type="rect", x0=13.84, x1=54.16, y0=0, y1=16.5, line=dict(color="white"))

# Punto penal
fig.add_shape(type="circle", x0=34-0.3, x1=34+0.3, y0=11-0.3, y1=11+0.3,
              line=dict(color="white"), fillcolor="white")

# Arco
fig.add_shape(type="rect", x0=30.34, x1=37.66, y0=0, y1=1.5, line=dict(color="white"))

fig.update_layout(
    xaxis=dict(range=[0, 68], visible=False),
    yaxis=dict(range=[0, 52.5], visible=False),
    height=700,
    plot_bgcolor="green",
    margin=dict(l=10, r=10, t=10, b=10),
    clickmode="event+select"
)

# Mostrar cancha con captura de clics activada
click_data = st.plotly_chart(fig, use_container_width=True, click_event=True)

# --------------------------
# ALMACENAR CLICK MANUALMENTE
# --------------------------
# 👇 Este bloque garantiza que el clic se guarde
if click_data and click_data.click_event:
    st.session_state.last_click = click_data.click_event

# --------------------------
# LÓGICA DEL REGISTRO
# --------------------------
if st.session_state.last_click:
    point = st.session_state.last_click["points"][0]
    x = point["x"]
    y = point["y"]

    if st.session_state.fase == "inicio":
        st.session_state.temp["tipo"] = accion
        st.session_state.temp["x_inicio"] = x
        st.session_state.temp["y_inicio"] = y
        st.session_state.fase = "esperando_fin"
        st.success(f"✅ Punto de ejecución guardado en ({x:.1f}, {y:.1f}). Ahora haz clic donde finalizó la jugada.")
        st.session_state.last_click = None  # limpiar
    elif st.session_state.fase == "esperando_fin":
        st.session_state.temp["x_fin"] = x
        st.session_state.temp["y_fin"] = y
        st.session_state.fase = "datos"
        st.success(f"✅ Punto de finalización guardado en ({x:.1f}, {y:.1f}). Completa los datos.")
        st.session_state.last_click = None  # limpiar

# --------------------------
# FORMULARIO FINAL
# --------------------------
if st.session_state.fase == "datos":
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

# --------------------------
# MOSTRAR REGISTROS
# --------------------------
df = pd.DataFrame(st.session_state.registro)
if not df.empty:
    st.subheader("📊 Acciones registradas")
    st.dataframe(df)

    # Exportar CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar CSV", csv, "acciones_balon_parado.csv", "text/csv")
