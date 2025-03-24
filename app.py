import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch

# Configuración inicial
st.set_page_config(layout="centered")
st.title("⚽ Registro y Heatmap de Balón Parado")

# Inicializar sesión para almacenar datos
if "registro" not in st.session_state:
    st.session_state.registro = []

# Listados de jugadores y rivales
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

# Coordenadas de zonas
zonas_coords = {
    1: (120, 0), 2: (120, 80), 3: (93, 9), 4: (93, 71),
    5: (114, 30), 6: (114, 50), 7: (114, 40), 8: (111, 15),
    9: (111, 65), 10: (105, 35), 11: (105, 45), 12: (105, 25),
    13: (105, 55), 14: (93, 29), 15: (93, 51), 16: (72, 20),
    17: (72, 60), "Penal": (108, 40)
}

# Formulario de registro
st.subheader("📋 Registrar nueva acción")

# Campos principales en columnas
col1, col2 = st.columns(2)
with col1:
    ejecutor = st.selectbox("👟 Ejecutante", jugadores_cavalry)
    match_day = st.selectbox("🗓️ Jornada", ["Rueda 1", "Rueda 2", "Rueda 3", "Rueda 4"])
    oponente = st.selectbox("🆚 Rival", equipos_cpl)

with col2:
    tipo_accion = st.selectbox("⚙️ Tipo de acción", ["Tiro libre", "Córner", "Lateral", "Penal"])
    equipo = st.selectbox("🏳️ Equipo que ejecutó", ["Cavalry FC", "Rival"])
    field = st.selectbox("📍 Condición de campo", ["Local", "Visitante"])

# Tiempo de juego
periodo = st.selectbox("⏱️ Periodo", ["1T", "2T"])
if periodo == "1T":
    minuto_opts = [str(x) for x in range(0, 46)] + ["45+"]
else:
    minuto_opts = [str(x) for x in range(45, 91)] + ["90+"]
minuto_str = st.selectbox("⏱️ Minuto", minuto_opts)

# Lógica condicional para diferentes tipos de acciones
if tipo_accion == "Penal":
    zona_saque = "Penal"
    zona_remate = "Penal"
    primer_contacto = "N/A"
    cuerpo1 = "N/A"
    segundo_contacto = "N/A"
    st.info("⚠️ Para penales: Zonas y contactos se establecen automáticamente")
    
elif tipo_accion == "Córner":
    col1, col2 = st.columns(2)
    with col1:
        zona_saque = st.selectbox("📍 Zona de saque (córner)", [1, 2])
    with col2:
        zona_remate = st.selectbox("🎯 Zona de remate", [z for z in zonas_coords if z != "Penal"])
    primer_contacto = st.selectbox("🤝 Primer contacto (jugador)", jugadores_cavalry + ["Rival"])
    cuerpo1 = st.selectbox("🦵 Parte del cuerpo (1er contacto)", ["Cabeza", "Pie derecho", "Pie izquierdo", "Tronco", "Otro"])
    segundo_contacto = st.text_input("📌 Segundo contacto (opcional)")
    
else:
    col1, col2 = st.columns(2)
    with col1:
        zona_saque = st.selectbox("📍 Zona de saque", [z for z in zonas_coords if z != "Penal"])
    with col2:
        zona_remate = st.selectbox("🎯 Zona de remate", [z for z in zonas_coords if z != "Penal"])
    primer_contacto = st.selectbox("🤝 Primer contacto (jugador)", jugadores_cavalry + ["Rival"])
    cuerpo1 = st.selectbox("🦵 Parte del cuerpo (1er contacto)", ["Cabeza", "Pie derecho", "Pie izquierdo", "Tronco", "Otro"])
    segundo_contacto = st.text_input("📌 Segundo contacto (opcional)")

# Campos restantes
gol = st.selectbox("🥅 ¿Terminó en gol?", ["No", "Sí"])
resultado = st.selectbox("🎯 Resultado final de la jugada", ["Despeje", "Posesión rival", "Disparo desviado", "Disparo al arco", "Gol"])
perfil = st.selectbox("🦶 Perfil del ejecutante", ["Hábil", "No hábil"])
estrategia = st.selectbox("📈 ¿Fue jugada estratégica?", ["Sí", "No"])
tipo_pase = st.selectbox("📨 Tipo de ejecución", ["Centro", "Pase corto", "Disparo directo"])

# Conversión de minutos
if "45+" in minuto_str:
    minuto = 46
elif "90+" in minuto_str:
    minuto = 91
else:
    minuto = int(minuto_str)

# Botón de registro
if st.button("✅ Agregar acción"):
    registro_data = {
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
    }
    
    st.session_state.registro.append(registro_data)
    st.success("Acción registrada correctamente ✅")

# Visualización de datos
df = pd.DataFrame(st.session_state.registro)
if not df.empty:
    st.subheader("📊 Acciones registradas")
    
    # Eliminación de registros
    index_to_delete = st.number_input("🗑️ Eliminar registro por índice", min_value=0, max_value=len(df)-1, step=1)
    if st.button("Eliminar registro"):
        st.session_state.registro.pop(index_to_delete)
        st.experimental_rerun()
    
    st.dataframe(df)

    # Procesamiento para heatmaps
    df["coords_saque"] = df["zona_saque"].map(zonas_coords)
    df["coords_remate"] = df["zona_remate"].map(zonas_coords)
    df = df.dropna(subset=["coords_saque", "coords_remate"])
    df[["x_saque", "y_saque"]] = pd.DataFrame(df["coords_saque"].tolist(), index=df.index)
    df[["x_remate", "y_remate"]] = pd.DataFrame(df["coords_remate"].tolist(), index=df.index)

    # Función de graficación corregida
    def graficar_heatmap(title, x, y, color):
        pitch = VerticalPitch(pitch_type='statsbomb', pitch_color='grass', line_color='white')
        fig, ax = pitch.draw(figsize=(6, 9))
        
        try:
            # Convertir a numérico y filtrar NaNs
            x = pd.to_numeric(x, errors='coerce')
            y = pd.to_numeric(y, errors='coerce')
            valid = x.notna() & y.notna()
            x_valid = x[valid]
            y_valid = y[valid]
            
            if not x_valid.empty:
                # Scatter plot siempre visible
                pitch.scatter(x_valid, y_valid, ax=ax, 
                            s=150, color=color, 
                            edgecolors='black', zorder=3)
                
                # KDE solo si hay suficientes puntos
                if len(x_valid) > 1:
                    pitch.kdeplot(x_valid, y_valid, ax=ax, 
                                cmap=f"{color.capitalize()}s",  # Corrección clave aquí
                                levels=50, fill=True, alpha=0.5)
                    
        except Exception as e:
            st.error(f"Error al generar el gráfico: {str(e)}")
        
        st.subheader(title)
        st.pyplot(fig)

    # Generación de heatmaps
    graficar_heatmap("🟢 Zona de Saque", df["x_saque"], df["y_saque"], "green")
    graficar_heatmap("🔴 Zona de Remate", df["x_remate"], df["y_remate"], "red")

    # Descarga de datos
    csv = df.drop(columns=["coords_saque", "coords_remate", "x_saque", "y_saque", "x_remate", "y_remate"]).to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar CSV", csv, "acciones_balon_parado.csv", "text/csv")
else:
    st.info("📭 No hay acciones registradas todavía. Usa el formulario para comenzar.")