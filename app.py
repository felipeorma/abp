import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch

# Configuración de la página
st.set_page_config(layout="centered")
st.title("⚽ Registro y Heatmap de Balón Parado")

# Inicializar sesión para almacenar datos
if "registro" not in st.session_state:
    st.session_state.registro = []

# Listado de jugadores y rivales
jugadores_cavalry = [
    "Marco Carducci", "Joseph Holliday", "Neven Fewster", "Callum Montgomery", "Bradley Kamdem",
    "Tom Field", "Eryk Kobza", "Michael Harms", "Fraser Aird", "Mihail Gherasimencov", "Charlie Trafford",
    "Jesse Daley", "Sergio Camargo", "Jay Herdman", "Caniggia Elva", "Maël Henry", "Shamit Shome",
    "Diego Gutiérrez", "Niko Myroniuk", "Josh Belbin", "James McGlinchey", "Ali Musse", "Tobias Warschewski",
    "Nicolas Wähling", "Chanan Chanda", "Myer Bevan"
]

equipos_cpl = [
    "Atlético Ottawa", "Forge FC", "HFX Wanderers FC", "Pacific FC", "Valour FC",
    "Vancouver FC", "York United FC"
]

# Coordenadas centrales representativas para cada zona (finales)
zonas_coords = {
    1:  (120, 0),    2:  (120, 80),   3:  (93, 9),    4:  (93, 71),
    5:  (114, 30),  6:  (114, 50),  7:  (114, 40),  8:  (111, 15),
    9:  (111, 65), 10: (105, 35), 11: (105, 45), 12: (105, 25),
   13: (105, 55), 14: (93, 29),  15: (93, 51), 16: (72, 20),
   17: (72, 60), "Penal": (108, 40)
}

# Formulario de registro
st.subheader("📋 Registrar nueva acción")
match_day = st.selectbox("🗓️ Jornada", ["Rueda 1", "Rueda 2", "Rueda 3", "Rueda 4"])
oponente = st.selectbox("🆚 Rival", equipos_cpl)
field = st.selectbox("📍 Condición de campo", ["Local", "Visitante"])
tipo_accion = st.selectbox("⚙️ Tipo de acción", ["Tiro libre", "Córner", "Lateral", "Penal"])
equipo = st.selectbox("🏳️ Equipo que ejecutó", ["Cavalry FC", "Rival"])
minuto = st.number_input("⏱️ Minuto", min_value=0, max_value=120, value=0)
periodo = "1T" if minuto <= 45 else "2T"

zona_saque = st.selectbox("📍 Zona de saque", list(zonas_coords.keys()))
zona_remate = st.selectbox("🎯 Zona de remate", list(zonas_coords.keys()))
ejecutor = st.selectbox("👟 Ejecutante", jugadores_cavalry)
gol = st.selectbox("🥅 ¿Terminó en gol?", ["No", "Sí"])
primer_contacto = st.selectbox("🤝 Primer contacto (jugador)", jugadores_cavalry + ["Rival"])
cuerpo1 = st.selectbox("🦵 Parte del cuerpo (1er contacto)", ["Cabeza", "Pie derecho", "Pie izquierdo", "Tronco", "Otro"])
segundo_contacto = st.text_input("📌 Segundo contacto (opcional)")
resultado = st.selectbox("🎯 Resultado final de la jugada", ["Despeje", "Posesión rival", "Disparo desviado", "Disparo al arco", "Gol"])
perfil = st.selectbox("🦶 Perfil del ejecutante", ["Hábil", "No hábil"])
estrategia = st.selectbox("📈 ¿Fue jugada estratégica?", ["Sí", "No"])
tipo_pase = st.selectbox("📨 Tipo de ejecución", ["Centro", "Pase corto", "Disparo directo"])

if st.button("✅ Agregar acción"):
    st.session_state.registro.append({
        "MatchDay": match_day,
        "Opponent": oponente,
        "Field": field,
        "Action Type": tipo_accion,
        "Team": equipo,
        "minuto": minuto,
        "Period": periodo,
        "zona_saque": zona_saque,
        "zona_remate": zona_remate,
        "Player Taker": ejecutor,
        "Goal": gol,
        "Player 1st Contact": primer_contacto,
        "Body Part 1st Contact": cuerpo1,
        "2nd Contact": segundo_contacto,
        "Play Outcome": resultado,
        "Taker Profile": perfil,
        "Strategic": estrategia,
        "Direct / Short Pass": tipo_pase
    })
    st.success("Acción registrada correctamente ✅")

# Mostrar tabla de acciones registradas
df = pd.DataFrame(st.session_state.registro)
if not df.empty:
    st.subheader("📊 Acciones registradas")

    # Eliminar registros específicos
    index_to_delete = st.number_input("🗑️ Eliminar registro por índice", min_value=0, max_value=len(df)-1, step=1)
    if st.button("Eliminar registro"):
        st.session_state.registro.pop(index_to_delete)
        st.experimental_rerun()

    st.dataframe(df)

    # Agregar coordenadas
    df["coords_saque"] = df["zona_saque"].map(zonas_coords)
    df["coords_remate"] = df["zona_remate"].map(zonas_coords)
    df = df.dropna(subset=["coords_saque", "coords_remate"])
    df[["x_saque", "y_saque"]] = pd.DataFrame(df["coords_saque"].tolist(), index=df.index)
    df[["x_remate", "y_remate"]] = pd.DataFrame(df["coords_remate"].tolist(), index=df.index)

    # Función de graficación
    def graficar_heatmap(title, x, y, cmap):
        st.subheader(title)
        pitch = VerticalPitch(pitch_type='statsbomb', pitch_color='grass', line_color='white')
        fig, ax = pitch.draw(figsize=(6, 9))

        if len(x) == 1:
            pitch.scatter(x, y, ax=ax, s=150, color=cmap, edgecolors='white', zorder=3)
        elif len(x) >= 2:
            try:
                pitch.kdeplot(x, y, ax=ax, fill=True, cmap=cmap, levels=100, alpha=0.6, bw_adjust=0.4)
            except ValueError:
                st.warning("⚠️ No se pudo generar el heatmap. Verifica que haya suficientes datos.")

        st.pyplot(fig)

    graficar_heatmap("🟢 Heatmap - Zona de Saque", df["x_saque"], df["y_saque"], "Greens")
    graficar_heatmap("🔴 Heatmap - Zona de Remate", df["x_remate"], df["y_remate"], "Reds")

    # Botón de descarga CSV
    csv = df.drop(columns=["coords_saque", "coords_remate", "x_saque", "y_saque", "x_remate", "y_remate"]).to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar CSV", csv, "acciones_abp.csv", "text/csv")
else:
    st.info("No hay acciones registradas todavía. Usa el formulario para comenzar.")
