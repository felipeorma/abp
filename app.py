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

# ========== DATOS ORDENADOS ==========
jugadores_cavalry = sorted([
    "Joseph Holliday", "Neven Fewster", "Callum Montgomery", "Bradley Kamdem",
    "Tom Field", "Eryk Kobza", "Michael Harms", "Fraser Aird", 
    "Mihail Gherasimencov", "Charlie Trafford", "Jesse Daley", "Sergio Camargo",
    "Jay Herdman", "Caniggia Elva", "Maël Henry", "Shamit Shome",
    "Diego Gutiérrez", "Niko Myroniuk", "Josh Belbin", "James McGlinchey",
    "Ali Musse", "Tobias Warschewski", "Nicolas Wähling", "Chanan Chanda",
    "Myer Bevan"
], key=lambda x: x.split()[-1]) + ["Marco Carducci"]

equipos_cpl = sorted([
    "Atlético Ottawa", "Forge FC", "HFX Wanderers FC",
    "Pacific FC", "Valour FC", "Vancouver FC", "York United FC"
])

zonas_coords = {
    1: (120, 0), 2: (120, 80), 3: (93, 9), 4: (93, 71),
    5: (114, 30), 6: (114, 50), 7: (114, 40), 8: (111, 15),
    9: (111, 65), 10: (105, 35), 11: (105, 45), 12: (105, 25),
    13: (105, 55), 14: (93, 29), 15: (93, 51), 16: (72, 20),
    17: (72, 60), "Penal": (108, 40)
}

# ========== FORMULARIO ==========
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
        minuto_str = st.selectbox("Minuto", 
            [str(x) for x in (range(0,46) if periodo == "1T" else range(45,91))] + 
            (["45+"] if periodo == "1T" else ["90+"]))

# Paso 3: Tipo de acción
with st.container(border=True):
    st.markdown("### ⚽ Acción")
    col1, col2 = st.columns(2)
    with col1:
        tipo_accion = st.selectbox("Tipo de acción", ["Tiro libre", "Córner", "Lateral", "Penal"])
    with col2:
        equipo = st.selectbox("Equipo ejecutor", ["Cavalry FC", "Rival"])

# Paso 4: Detalles de ejecución
with st.container(border=True):
    st.markdown("### 🎯 Detalles de Ejecución")
    
    st.image("https://github.com/felipeorma/abp/blob/main/MedioCampo_enumerado.JPG?raw=true", 
             caption="Referencia de Zonas de Balón Parado",
             use_column_width=True)
    
    if equipo == "Cavalry FC":
        ejecutor = st.selectbox("Jugador ejecutor", jugadores_cavalry)
    else:
        ejecutor = "Rival"
    
    if tipo_accion == "Penal":
        zona_saque = zona_remate = "Penal"
        st.info("Configuración automática para penales")
        primer_contacto = cuerpo1 = segundo_contacto = "N/A"
    else:
        col1, col2 = st.columns(2)
        with col1:
            zona_saque = st.selectbox("Zona de saque", 
                [1, 2] if tipo_accion == "Córner" else [z for z in zonas_coords if z != "Penal"])
        with col2:
            zona_remate = st.selectbox("Zona de remate", [z for z in zonas_coords if z != "Penal"])
        
        opciones_contacto = jugadores_cavalry + ["Oponente"]
        primer_contacto = st.selectbox("Primer contacto", opciones_contacto)
        cuerpo1 = st.selectbox("Parte del cuerpo", ["Cabeza", "Pie derecho", "Pie izquierdo", "Tronco", "Otro"])
        segundo_contacto = st.selectbox("Segundo contacto (opcional)", ["Ninguno"] + opciones_contacto)

# Paso 5: Resultados
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
        "Segundo Contacto": segundo_contacto if segundo_contacto != "Ninguno" else "",
        "Gol": gol,
        "Resultado": resultado,
        "Perfil": perfil,
        "Estrategia": estrategia,
        "Tipo Ejecución": tipo_pase
    }
    
    st.session_state.registro.append(registro_data)
    st.success("Acción registrada exitosamente!")
    st.balloons()

# ========== VISUALIZACIÓN ==========
if st.session_state.registro:
    st.subheader("📊 Datos Registrados")
    df = pd.DataFrame(st.session_state.registro)
    
    # Eliminar registros
    index_to_delete = st.number_input("Índice a eliminar", min_value=0, max_value=len(df)-1)
    if st.button("🗑️ Eliminar Registro"):
        st.session_state.registro.pop(index_to_delete)
        st.experimental_rerun()
    
    st.dataframe(df, use_container_width=True)

    # Filtro de equipo
    st.markdown("### 🔍 Filtro de Equipo")
    equipo_filtro = st.radio(
        "Seleccionar equipo para visualizar:",
        ["Cavalry FC", "Oponente"],
        index=0
    )

    # Aplicar filtro
    filtered_df = df[df["Equipo"] == ("Cavalry FC" if equipo_filtro == "Cavalry FC" else "Rival")]

    # Procesamiento seguro de coordenadas
    if not filtered_df.empty:
        filtered_df = filtered_df.copy()
        filtered_df["coords_saque"] = filtered_df["Zona Saque"].map(zonas_coords)
        filtered_df["coords_remate"] = filtered_df["Zona Remate"].map(zonas_coords)
        filtered_df = filtered_df.dropna(subset=["coords_saque", "coords_remate"])
        
        if not filtered_df.empty:
            filtered_df[["x_saque", "y_saque"]] = pd.DataFrame(filtered_df["coords_saque"].tolist(), index=filtered_df.index)
            filtered_df[["x_remate", "y_remate"]] = pd.DataFrame(filtered_df["coords_remate"].tolist(), index=filtered_df.index)
        else:
            st.warning("⚠️ No hay datos válidos para visualizar después del filtrado")
            st.stop()
    else:
        st.warning("⚠️ No hay datos para el equipo seleccionado")
        st.stop()

    # Función de graficación corregida
    def graficar_heatmap(title, x, y, color):
        pitch = VerticalPitch(
            pitch_type='statsbomb', 
            pitch_color='grass', 
            line_color='white',
            half=True,
            goal_type='box'
        )
        fig, ax = pitch.draw(figsize=(10, 6.5))
        
        try:
            if not x.empty and not y.empty:
                pitch.kdeplot(
                    x, y, ax=ax,
                    cmap=f'{color.capitalize()}s',
                    levels=100,
                    fill=True,
                    alpha=0.75,
                    bw_adjust=0.5,
                    zorder=2
                )
                
                # Firma profesional
                ax.text(
                    0.02, 0.03,
                    "By: Felipe Ormazabal\nFootball Scout - Data Analyst",
                    fontsize=9,
                    color='#404040',
                    ha='left',
                    va='bottom',
                    transform=ax.transAxes,
                    alpha=0.9,
                    fontstyle='italic'
                )
                
        except Exception as e:
            st.error(f"Error al generar el gráfico: {str(e)}")
        
        st.subheader(title)
        st.pyplot(fig)

    # Generar heatmaps
    graficar_heatmap("🟢 Densidad de Saques", filtered_df["x_saque"], filtered_df["y_saque"], "green")
    graficar_heatmap("🔴 Densidad de Remates", filtered_df["x_remate"], filtered_df["y_remate"], "red")

    # Descarga de datos
    csv = filtered_df.drop(columns=["coords_saque", "coords_remate", "x_saque", "y_saque", "x_remate", "y_remate"]).to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Descargar CSV Filtrado", csv, "acciones_filtradas.csv", "text/csv")

else:
    st.info("📭 No hay acciones registradas. Comienza registrando una acción arriba.")