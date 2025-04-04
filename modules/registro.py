import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch
import datetime
from utils.i18n import get_text

def registro_page(lang):
    jugadores, equipos, zonas_coords = cargar_datos(lang)

    with st.form("form_registro", clear_on_submit=True):
        datos = mostrar_formulario(jugadores, equipos, zonas_coords, lang)

    if datos:
        procesar_registro(datos, lang)

    mostrar_datos_y_visualizaciones(zonas_coords, lang)

def cargar_datos(lang):
    jugadores = sorted([
        "Joseph Holliday", "Neven Fewster", "Callum Montgomery", "Bradley Kamdem",
        "Tom Field", "Eryk Kobza", "Michael Harms", "Fraser Aird",
        "Mihail Gherasimencov", "Charlie Trafford", "Jesse Daley", "Sergio Camargo",
        "Jay Herdman", "Caniggia Elva", "Maël Henry", "Shamit Shome",
        "Diego Gutiérrez", "Niko Myroniuk", "Josh Belbin", "James McGlinchey",
        "Ali Musse", "Tobias Warschewski", "Nicolas Wähling", "Chanan Chanda",
        "Myer Bevan"
    ], key=lambda x: x.split()[-1]) + ["Marco Carducci", get_text(lang, "opponent")]

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

def mostrar_formulario(jugadores, equipos, zonas, lang):
    datos = {}
    st.subheader(get_text(lang, "register_new_action"))

    with st.container(border=True):
        st.markdown(get_text(lang, "match_context"))
        col1, col2, col3 = st.columns(3)
        datos["Jornada"] = col1.selectbox(get_text(lang, "matchday"), ["Rueda 1", "Rueda 2", "Rueda 3", "Rueda 4"])
        datos["Rival"] = col2.selectbox(get_text(lang, "opponent"), equipos)
        datos["Condición"] = col3.selectbox(get_text(lang, "home_away"), ["Local", "Visitante"])
        datos["Fecha"] = st.date_input(get_text(lang, "date"), value=datetime.date.today())

    with st.container(border=True):
        st.markdown(get_text(lang, "game_time"))
        col1, col2 = st.columns(2)
        periodo = col1.selectbox(get_text(lang, "period"), ["1T", "2T"])

        if periodo == "1T":
            minutos = [str(x) for x in range(0, 46)] + ["45+"]
        else:
            minutos = [str(x) for x in range(45, 91)] + ["90+"]

        minuto_str = col2.selectbox(get_text(lang, "minute"), minutos)
        datos["Minuto"] = 46 if "45+" in minuto_str else 91 if "90+" in minuto_str else int(minuto_str)
        datos["Periodo"] = periodo

    with st.container(border=True):
        st.markdown(get_text(lang, "action"))
        col1, col2, col3 = st.columns(3)
        datos["Acción"] = col1.selectbox(get_text(lang, "action_type"), ["Tiro libre", "Córner", "Lateral", "Penal"], key="accion_key")
        datos["Equipo"] = col2.selectbox(get_text(lang, "executing_team"), ["Cavalry FC", "Rival"])

        if datos["Equipo"] == "Cavalry FC":
            datos["Ejecutor"] = col3.selectbox(get_text(lang, "executor"), jugadores)
        else:
            datos["Ejecutor"] = "Rival"
            col3.text_input(get_text(lang, "executor"), value="Rival", disabled=True)

    with st.container(border=True):
        st.markdown(get_text(lang, "execution_details"))
        st.image("https://github.com/felipeorma/abp/blob/main/MedioCampo_enumerado.JPG?raw=true", use_column_width=True)

        if datos["Acción"] == "Penal":
            datos["Zona Saque"] = "Penal"
            datos["Zona Remate"] = "Penal"
            datos["Primer Contacto"] = "N/A"
            datos["Parte Cuerpo"] = "N/A"
            datos["Segundo Contacto"] = ""
            st.info(get_text(lang, "penalty_auto_config"))
        else:
            col1, col2 = st.columns(2)
            zona_opciones_saque = [1, 2] if datos["Acción"] == "Córner" else [z for z in zonas if z != "Penal"]
            datos["Zona Saque"] = col1.selectbox(get_text(lang, "kick_zone"), zona_opciones_saque)
            datos["Zona Remate"] = col2.selectbox(get_text(lang, "shot_zone"), [z for z in zonas if z != "Penal"])

            opciones_contacto = jugadores + ["Oponente"]
            datos["Primer Contacto"] = st.selectbox(get_text(lang, "first_contact"), opciones_contacto)
            datos["Parte Cuerpo"] = st.selectbox(get_text(lang, "body_part"), ["Cabeza", "Otro", "Pie"])
            segundo_contacto = st.selectbox(get_text(lang, "second_contact_optional"), ["Ninguno"] + opciones_contacto)
            datos["Segundo Contacto"] = segundo_contacto if segundo_contacto != "Ninguno" else ""

    with st.container(border=True):
        st.markdown(get_text(lang, "results"))
        col1, col2 = st.columns(2)

        datos["Gol"] = col1.selectbox(get_text(lang, "goal"), ["No", "Sí"], key="gol_key")

        if st.session_state.get("gol_key") == "Sí":
            datos["Resultado"] = "Gol"
            col1.text_input(get_text(lang, "final_result"), value="Gol", disabled=True)
        else:
            datos["Resultado"] = col1.selectbox(
                get_text(lang, "final_result"),
                ["Gol", "Despeje", "Posesión rival", "Disparo desviado", "Disparo al arco"]
            )

        datos["Perfil"] = col2.selectbox(get_text(lang, "foot_profile"), ["Hábil", "No hábil"])
        datos["Estrategia"] = col2.selectbox(get_text(lang, "strategy"), ["Sí", "No"])
        datos["Tipo Ejecución"] = col2.selectbox(get_text(lang, "execution_type"), ["Centro", "Pase corto", "Disparo directo"])

    return datos if st.form_submit_button(get_text(lang, "register_button")) else None

def procesar_registro(datos, lang):
    st.session_state.registro.append(datos)
    st.success(get_text(lang, "registered_successfully"))

def mostrar_datos_y_visualizaciones(zonas, lang):
    if st.session_state.registro:
        df = pd.DataFrame(st.session_state.registro)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(get_text(lang, "registered_data"))
            st.dataframe(df, use_container_width=True)
        with col2:
            index_to_delete = st.number_input(get_text(lang, "index_to_delete"), min_value=0, max_value=len(df) - 1)
            if st.button(get_text(lang, "delete_record")):
                st.session_state.registro.pop(index_to_delete)
                st.experimental_rerun()

        st.markdown(get_text(lang, "team_filter"))
        equipo_filtro = st.radio(
            get_text(lang, "select_team_to_visualize"),
            ["Cavalry FC", "Oponente"],
            index=0
        )

        filtered_df = df[df["Equipo"] == ("Cavalry FC" if equipo_filtro == "Cavalry FC" else "Rival")]
        generar_heatmaps(filtered_df, zonas, lang)

def generar_heatmaps(df, zonas, lang):
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

        fig1, ax1 = plt.subplots(figsize=(12, 8))
        pitch.draw(ax=ax1)
        pitch.kdeplot(df['x_saque'], df['y_saque'], ax=ax1, **heatmap_params)
        ax1.set_title(get_text(lang, "kick_distribution"), fontsize=16, pad=20, fontweight='bold')
        st.pyplot(fig1)

        fig2, ax2 = plt.subplots(figsize=(12, 8))
        pitch.draw(ax=ax2)
        heatmap_params['cmap'] = 'Reds'
        pitch.kdeplot(df['x_remate'], df['y_remate'], ax=ax2, **heatmap_params)
        ax2.set_title(get_text(lang, "shot_zones"), fontsize=16, pad=20, fontweight='bold')
        st.pyplot(fig2)

        csv = df.drop(columns=["coords_saque", "coords_remate", "x_saque", "y_saque", "x_remate", "y_remate"]).to_csv(index=False).encode('utf-8')

        st.download_button(
            get_text(lang, "download_filtered_csv"),
            csv,
            "acciones_filtradas.csv",
            "text/csv",
            key='download-csv'
        )

    except Exception as e:
        st.error(get_text(lang, "critical_error") + f": {str(e)}")
