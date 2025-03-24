import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch

# Configuración inicial
st.set_page_config(layout="centered")
st.title("⚽ Registro y Heatmap de Balón Parado - Cavalry FC")

# Inicializar sesión para almacenar datos
if "registro" not in st.session_state:
    st.session_state.registro = []

# ========== DATOS ESTÁTICOS ==========
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

zonas_coords = {
    1: (120, 0), 2: (120, 80), 3: (93, 9), 4: (93, 71),
    5: (114, 30), 6: (114, 50), 7: (114, 40), 8: (111, 15),
    9: (111, 65), 10: (105, 35), 11: (105, 45), 12: (105, 25),
    13: (105, 55), 14: (93, 29), 15: (93, 51), 16: (72, 20),
    17: (72, 60), "Penal": (108, 40)
}

# ========== FORMULARIO - ORDEN CRONOLÓGICO ==========
st.subheader("📋 Registrar nueva acción")

# Paso 1: Contexto del partido
with st.container(border=True):
    st.markdown("### 🗓️ Contexto del Partido")
    col1, col2, col3 = st.columns(3)
    with col1:
        match_day = st.selectbox("Jornada", ["Rueda 1", "Rueda 2", "Rueda 3", "Rueda 4"])
    with col2:
        oponente = st.selectbox("Rival", equipos_cpl)
    with col3:
        field = st.selectbox("Condición", ["Local", "Visitante"])

# Paso 2: Tiempo del juego
with st.container(border=True):
    st.markdown("### ⏱️ Tiempo de Juego")
    col1, col2 = st.columns(2)
    with col1:
        periodo = st.selectbox("Periodo", ["1T", "2T"])
    with col2:
        if periodo == "1T":
            minuto_opts = [str(x) for x in range(0, 46)] + ["45+"]
        else:
            minuto_opts = [str(x) for x in range(45, 91)] + ["90+"]
        minuto_str = st.selectbox("Minuto", minuto_opts)

# Paso 3: Tipo de acción y equipo
with st.container(border=True):
    st.markdown("### ⚽ Acción")
    col1, col2 = st.columns(2)
    with col1:
        tipo_accion = st.selectbox("Tipo de acción", ["Tiro libre", "Córner", "Lateral", "Penal"])
    with col2:
        equipo = st.selectbox("Equipo ejecutor", ["Cavalry FC", "Rival"])

# Paso 4: Detalles de ejecución (dependiendo del tipo de acción)
with st.container(border=True):
    st.markdown("### 🎯 Detalles de Ejecución")
    
    # Ejecutor (solo si es Cavalry FC)
    if equipo == "Cavalry FC":
        ejecutor = st.selectbox("Jugador ejecutor", jugadores_cavalry)
    else:
        ejecutor = "Rival"
    
    # Lógica por tipo de acción
    if tipo_accion == "Penal":
        zona_saque = zona_remate = "Penal"
        st.info("Configuración automática para penales")
        primer_contacto = cuerpo1 = segundo_contacto = "N/A"
        
    else:
        col1, col2 = st.columns(2)
        with col1:
            if tipo_accion == "Córner":
                zona_saque = st.selectbox("Zona de saque", [1, 2])
            else:
                zonas_disponibles = [z for z in zonas_coords if z != "Penal"]
                zona_saque = st.selectbox("Zona de saque", zonas_disponibles)
        
        with col2:
            zona_remate = st.selectbox("Zona de remate", [z for z in zonas_coords if z != "Penal"])
        
        primer_contacto = st.selectbox("Primer contacto", jugadores_cavalry + ["Rival"])
        cuerpo1 = st.selectbox("Parte del cuerpo", ["Cabeza", "Pie derecho", "Pie izquierdo", "Tronco", "Otro"])
        segundo_contacto = st.text_input("Segundo contacto (opcional)")

# Paso 5: Resultados y estrategia
with st.container(border=True):
    st.markdown("### 📊 Resultados")
    col1, col2 = st.columns(2)
    with col1:
        gol = st.selectbox("¿Gol?", ["No", "Sí"])
        resultado = st.selectbox("Resultado final", ["Despeje", "Posesión rival", "Disparo desviado", "Disparo al arco", "Gol"])
    with col2:
        perfil = st.selectbox("Perfil ejecutor", ["Hábil", "No hábil"])
        estrategia = st.selectbox("Estrategia", ["Sí", "No"])
        tipo_pase = st.selectbox("Tipo de ejecución", ["Centro", "Pase corto", "Disparo directo"])

# Conversión de minutos
minuto = 46 if "45+" in minuto_str else 91 if "90+" in minuto_str else int(minuto_str)

# Botón de registro
if st.button("✅ Registrar Acción", type="primary"):
    registro_data = {
        "Jornada": match_day,
        "Rival": oponente,
        "Condición": field,
        "Periodo": periodo,
        "Minuto": minuto,
        "Acción": tipo_accion,
        "Equipo": equipo,
        "Ejecutor": ejecutor,
        "Zona Saque": zona_saque,
        "Zona Remate": zona_remate,
        "Primer Contacto": primer_contacto,
        "Parte Cuerpo": cuerpo1,
        "Segundo Contacto": segundo_contacto,
        "Gol": gol,
        "Resultado": resultado,
        "Perfil": perfil,
        "Estrategia": estrategia,
        "Tipo Ejecución": tipo_pase
    }
    
    st.session_state.registro.append(registro_data)
    st.success("Acción registrada exitosamente!")
    st.balloons()

# ========== VISUALIZACIÓN DE DATOS ==========
if st.session_state.registro:
    st.subheader("📊 Datos Registrados")
    df = pd.DataFrame(st.session_state.registro)
    
    # Eliminar registros
    col1, col2 = st.columns(2)
    with col1:
        index_to_delete = st.number_input("Índice a eliminar", min_value=0, max_value=len(df)-1)
    with col2:
        st.write("")
        st.write("")
        if st.button("🗑️ Eliminar Registro"):
            st.session_state.registro.pop(index_to_delete)
            st.experimental_rerun()
    
    st.dataframe(df, use_container_width=True)

    # Procesamiento para heatmaps
    df["coords_saque"] = df["Zona Saque"].map(zonas_coords)
    df["coords_remate"] = df["Zona Remate"].map(zonas_coords)
    df[["x_saque", "y_saque"]] = pd.DataFrame(df["coords_saque"].tolist(), index=df.index)
    df[["x_remate", "y_remate"]] = pd.DataFrame(df["coords_remate"].tolist(), index=df.index)

    # Función de graficación mejorada
    def graficar_heatmap(title, x, y, color):
        pitch = VerticalPitch(pitch_type='statsbomb', pitch_color='grass', line_color='white')
        fig, ax = pitch.draw(figsize=(6, 9))
        
        try:
            x = pd.to_numeric(x, errors='coerce')
            y = pd.to_numeric(y, errors='coerce')
            valid = x.notna() & y.notna()
            x_valid = x[valid]
            y_valid = y[valid]
            
            if not x_valid.empty:
                # Scatter plot
                scatter = pitch.scatter(x_valid, y_valid, ax=ax,
                                      s=200, color=color,
                                      edgecolors='white', linewidth=1.5,
                                      zorder=3, label='Acciones')
                
                # KDE plot para 2+ puntos
                if len(x_valid) > 1:
                    kde = pitch.kdeplot(x_valid, y_valid, ax=ax,
                                      cmap=f"{color.capitalize()}s",
                                      levels=50, fill=True, alpha=0.6,
                                      bw_adjust=0.4, zorder=2)
                
                ax.legend(handles=[scatter], loc='upper left')
                
        except Exception as e:
            st.error(f"Error en gráfico: {str(e)}")
        
        st.subheader(title)
        st.pyplot(fig)

    # Generación de heatmaps
    graficar_heatmap("🟢 Zonas de Saque", df["x_saque"], df["y_saque"], "green")
    graficar_heatmap("🔴 Zonas de Remate", df["x_remate"], df["y_remate"], "red")

    # Descarga de datos
    csv = df.drop(columns=["coords_saque", "coords_remate", "x_saque", "y_saque", "x_remate", "y_remate"]).to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Descargar CSV", csv, "acciones_balon_parado.csv", "text/csv")

else:
    st.info("📭 No hay acciones registradas. Comienza registrando una acción arriba.")