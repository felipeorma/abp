# modules/registro.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch
import datetime
from utils.i18n import get_text

# Helper para opciones traducidas
def get_localized_options(lang: str, options: list, translation_prefix: str):
    return {opt: get_text(lang, f"{translation_prefix}_{opt}") for opt in options}

def registro_page(lang: str):
    jugadores, equipos, zonas_coords = cargar_datos()
    
    with st.form("form_registro", clear_on_submit=True):
        datos = mostrar_formulario(lang, jugadores, equipos, zonas_coords)
    
    if datos:
        procesar_registro(lang, datos)
    
    mostrar_datos_y_visualizaciones(lang, zonas_coords)

def cargar_datos():
    jugadores = sorted([
        "Joseph Holliday", "Neven Fewster", "Callum Montgomery", "Bradley Kamdem",
        "Tom Field", "Eryk Kobza", "Michael Harms", "Fraser Aird", 
        "Mihail Gherasimencov", "Charlie Trafford", "Jesse Daley", "Sergio Camargo",
        "Jay Herdman", "Caniggia Elva", "Maël Henry", "Shamit Shome", "Michael Baldisimo",
        "Diego Gutiérrez", "Niko Myroniuk", "Josh Belbin", "James McGlinchey",
        "Ali Musse", "Tobias Warschewski", "Nicolas Wähling", "Chanan Chanda",
        "Myer Bevan"
    ], key=lambda x: x.split()[-1]) + ["Marco Carducci"]

    equipos = sorted([
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
    
    return jugadores, equipos, zonas_coords

def mostrar_formulario(lang: str, jugadores, equipos, zonas):
    datos = {}
    st.subheader(get_text(lang, "registro_subheader"))

    # Contexto del partido
    with st.container(border=True):
        st.markdown(f"### {get_text(lang, 'match_context')}")
        col1, col2, col3 = st.columns(3)
        
        # Jornada
        jornadas = ["Rueda 1", "Rueda 2", "Rueda 3", "Rueda 4"]
        jornadas_tr = get_localized_options(lang, jornadas, "round")
        datos["Jornada"] = col1.selectbox(
            get_text(lang, "round"),
            options=jornadas,
            format_func=lambda x: jornadas_tr[x]
        )
        
        # Rival
        datos["Rival"] = col2.selectbox(
            get_text(lang, "opponent"), 
            equipos
        )
        
        # Condición
        condiciones = ["Local", "Visitante"]
        condiciones_tr = get_localized_options(lang, condiciones, "condition")
        datos["Condición"] = col3.selectbox(
            get_text(lang, "condition"),
            options=condiciones,
            format_func=lambda x: condiciones_tr[x]
        )
        
        datos["Fecha"] = st.date_input(
            get_text(lang, "date"), 
            value=datetime.date.today()
        )

    # Tiempo de juego
    with st.container(border=True):
        st.markdown(f"### {get_text(lang, 'game_time')}")
        col1, col2 = st.columns(2)
        
        # Periodo
        periodos = ["1T", "2T"]
        periodos_tr = get_localized_options(lang, periodos, "period")
        periodo = col1.selectbox(
            get_text(lang, "period"),
            options=periodos,
            format_func=lambda x: periodos_tr[x]
        )

        # Minutos
        minutos = (
            [str(x) for x in range(0, 46)] + ["45+"] if periodo == "1T"
            else [str(x) for x in range(45, 91)] + ["90+"]
        )
        minuto_str = col2.selectbox(
            get_text(lang, "minute"),
            minutos
        )
        datos["Minuto"] = 46 if "45+" in minuto_str else 91 if "90+" in minuto_str else int(minuto_str)
        datos["Periodo"] = periodo

    # Tipo de acción
    with st.container(border=True):
        st.markdown(f"### {get_text(lang, 'action_header')}")
        col1, col2, col3 = st.columns(3)
        
        # Acción
        acciones = ["Tiro libre", "Córner", "Lateral", "Penal"]
        acciones_tr = get_localized_options(lang, acciones, "action")
        datos["Acción"] = col1.selectbox(
            get_text(lang, "action_type"),
            options=acciones,
            format_func=lambda x: acciones_tr[x],
            key="accion_key"
        )
        
        # Equipo
        datos["Equipo"] = col2.selectbox(
            get_text(lang, "executing_team"),
            ["Cavalry FC", "Rival"]
        )

        # Ejecutor
        if datos["Equipo"] == "Cavalry FC":
            datos["Ejecutor"] = col3.selectbox(
                get_text(lang, "executor"), 
                jugadores
            )
        else:
            datos["Ejecutor"] = "Rival"
            col3.text_input(
                get_text(lang, "executor"), 
                value="Rival", 
                disabled=True
            )

    # Detalles de ejecución
    with st.container(border=True):
        st.markdown(f"### {get_text(lang, 'execution_details')}")
        st.image("https://github.com/felipeorma/abp/blob/main/MedioCampo_enumerado.JPG?raw=true", 
                use_column_width=True)

        if datos["Acción"] == "Penal":
            datos["Zona Saque"] = "Penal"
            datos["Zona Remate"] = "Penal"
            datos["Primer Contacto"] = "N/A"
            datos["Parte Cuerpo"] = "N/A"
            datos["Segundo Contacto"] = ""
            st.info(get_text(lang, "auto_penal_config"))
        else:
            col1, col2 = st.columns(2)
            
            # Zonas de saque
            zona_opciones = [z for z in zonas if z != "Penal"]
            zonas_tr = {z: get_text(lang, f"zone_{z}") for z in zona_opciones}
            
            datos["Zona Saque"] = col1.selectbox(
                get_text(lang, "kickoff_zone"),
                options=zona_opciones,
                format_func=lambda x: zonas_tr[x]
            )
            
            datos["Zona Remate"] = col2.selectbox(
                get_text(lang, "shot_zone"),
                options=zona_opciones,
                format_func=lambda x: zonas_tr[x]
            )

            # Contactos
            opciones_contacto = jugadores + [get_text(lang, "opponent")]
            datos["Primer Contacto"] = st.selectbox(
                get_text(lang, "first_contact"), 
                opciones_contacto
            )
            
            # Parte del cuerpo
            partes_cuerpo = ["Cabeza", "Otro", "Pie"]
            partes_tr = get_localized_options(lang, partes_cuerpo, "body_part")
            datos["Parte Cuerpo"] = st.selectbox(
                get_text(lang, "body_part"),
                options=partes_cuerpo,
                format_func=lambda x: partes_tr[x]
            )
            
            # Segundo contacto
            segundo_opciones = ["Ninguno"] + jugadores + [get_text(lang, "opponent")]
            segundo_tr = {
                "Ninguno": get_text(lang, "second_contact_ninguno"),
                **{jugador: jugador for jugador in jugadores},
                get_text(lang, "opponent"): get_text(lang, "opponent")
            }
            segundo_contacto = st.selectbox(  # ← Alineado con el bloque else
                get_text(lang, "second_contact"),
                options=segundo_opciones,
                format_func=lambda x: segundo_tr.get(x, x)
            )
            datos["Segundo Contacto"] = segundo_contacto if segundo_contacto != "Ninguno" else ""

    # Resultados
    with st.container(border=True):
        st.markdown(f"### {get_text(lang, 'results_header')}")
        col1, col2 = st.columns(2)
        
        # Gol
        gol_opciones = ["No", "Sí"]
        gol_tr = get_localized_options(lang, gol_opciones, "is_goal")
        datos["Gol"] = col1.selectbox(
            get_text(lang, "is_goal"),
            options=gol_opciones,
            format_func=lambda x: gol_tr[x],
            key="gol_key"
        )

        # Resultado final
        resultados = ["Gol", "Despeje", "Posesión rival", "Disparo desviado", "Disparo al arco"]
        resultados_tr = get_localized_options(lang, resultados, "result")
        if st.session_state.get("gol_key") == "Sí":
            datos["Resultado"] = "Gol"
            col1.text_input(
                get_text(lang, "final_result"), 
                value=resultados_tr["Gol"], 
                disabled=True
            )
        else:
            datos["Resultado"] = col1.selectbox(
                get_text(lang, "final_result"),
                options=resultados,
                format_func=lambda x: resultados_tr[x]
            )

        # Perfil
        perfiles = ["Hábil", "No hábil"]
        perfiles_tr = get_localized_options(lang, perfiles, "profile")
        datos["Perfil"] = col2.selectbox(
            get_text(lang, "executor_profile"),
            options=perfiles,
            format_func=lambda x: perfiles_tr[x]
        )
        
        # Estrategia
        estrategias = ["Sí", "No"]
        estrategias_tr = get_localized_options(lang, estrategias, "strategy")
        datos["Estrategia"] = col2.selectbox(
            get_text(lang, "strategy"),
            options=estrategias,
            format_func=lambda x: estrategias_tr[x]
        )
        
        # Tipo ejecución
        ejecuciones = ["Centro", "Pase corto", "Disparo directo"]
        ejecuciones_tr = get_localized_options(lang, ejecuciones, "exec_type")
        datos["Tipo Ejecución"] = col2.selectbox(
            get_text(lang, "execution_type"),
            options=ejecuciones,
            format_func=lambda x: ejecuciones_tr[x]
        )

    return datos if st.form_submit_button(get_text(lang, "register_action")) else None

def procesar_registro(lang: str, datos):
    st.session_state.registro.append(datos)
    st.success(get_text(lang, "registration_success"))  

def mostrar_datos_y_visualizaciones(lang: str, zonas):
    if st.session_state.registro:
        df = pd.DataFrame(st.session_state.registro)
        
        col1, col2 = st.columns([3,1])
        with col1:
            st.subheader(get_text(lang, "registered_data"))
            st.dataframe(df, use_container_width=True)
        with col2:
            index_to_delete = st.number_input(
                get_text(lang, "delete_index"), 
                min_value=0, 
                max_value=len(df)-1
            )
            if st.button(f"🗑️ {get_text(lang, 'delete_record')}"):
                st.session_state.registro.pop(index_to_delete)
                st.experimental_rerun()

        st.markdown(f"### {get_text(lang, 'filter_header')}")
        equipo_filtro = st.radio(
            get_text(lang, "team_filter"),
            ["Cavalry FC", "Oponente"],
            index=0
        )
        
        filtered_df = df[df["Equipo"] == ("Cavalry FC" if equipo_filtro == "Cavalry FC" else "Rival")]
        generar_heatmaps(lang, filtered_df, zonas)

def generar_heatmaps(lang: str, df, zonas):
    try:
        if df.empty:
            st.warning(get_text(lang, "no_data_warning"))
            return

        df = df.copy()
        df["coords_saque"] = df["Zona Saque"].map(zonas)
        df["coords_remate"] = df["Zona Remate"].map(zonas)
        df = df.dropna(subset=["coords_saque", "coords_remate"])
        
        df[["x_saque", "y_saque"]] = pd.DataFrame(df["coords_saque"].tolist(), index=df.index)
        df[["x_remate", "y_remate"]] = pd.DataFrame(df["coords_remate"].tolist(), index=df.index)
        
        pitch = VerticalPitch(
            pitch_type='statsbomb',
            pitch_color='grass',
            line_color='white',
            half=True,
            goal_type='box',
            linewidth=1.5
        )

        heatmap_params = {
            'cmap': 'Greens',
            'levels': 100,
            'fill': True,
            'alpha': 0.7,
            'bw_adjust': 0.48,
            'thresh': 0.01,
            'zorder': 2
        }

        # Heatmap de Saques
        fig1, ax1 = plt.subplots(figsize=(12, 8))
        pitch.draw(ax=ax1)
        pitch.kdeplot(df['x_saque'], df['y_saque'], ax=ax1, **heatmap_params)
        ax1.set_title(get_text(lang, "kickoff_distribution"), fontsize=16, pad=20, fontweight='bold')
        st.pyplot(fig1)

        # Heatmap de Remates
        fig2, ax2 = plt.subplots(figsize=(12, 8))
        pitch.draw(ax=ax2)
        heatmap_params['cmap'] = 'Reds'
        pitch.kdeplot(df['x_remate'], df['y_remate'], ax=ax2, **heatmap_params)
        ax2.set_title(get_text(lang, "shot_zones"), fontsize=16, pad=20, fontweight='bold')
        st.pyplot(fig2)

        # Descargar CSV
        csv = df.drop(columns=["coords_saque", "coords_remate", 
                             "x_saque", "y_saque", 
                             "x_remate", "y_remate"]).to_csv(index=False).encode('utf-8')
        
        st.download_button(
            f"⬇️ {get_text(lang, 'download_csv')}",
            csv,
            "acciones_filtradas.csv",
            "text/csv",
            key='download-csv'
        )

    except Exception as e:
        st.error(f"{get_text(lang, 'critical_error')}: {str(e)}")

    # --- Footer signature ---
    st.markdown(
        """
        <hr style='margin-top: 40px; margin-bottom: 10px'>
        <div style='text-align: center; font-size: 14px; color: gray;'>
            <strong>Felipe Ormazabal</strong> &nbsp;|&nbsp; Soccer Scout & Data Analyst
        </div>
        """,
        unsafe_allow_html=True
    )

