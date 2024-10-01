# Importar las librerías necesarias
import streamlit as st
import pandas as pd
import os
from mplsoccer import Pitch
import matplotlib.pyplot as plt
from fpdf import FPDF
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                Table, TableStyle)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime

# Configurar el estilo de la página debe ser la primera llamada a Streamlit
st.set_page_config(layout="wide")

def configurar_estilo():
    # Estilos CSS personalizados
    st.markdown(
        """
        <style>
        /* Estilos generales */
        .reportview-container {
            background: #1f1f1f;
            color: white;
        }
        .sidebar .sidebar-content {
            background: #333333;
            color: white;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
        }
        /* Centrar el contenido principal */
        .centered {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def mostrar_campo():
    st.subheader("Player Recruitment Needs / Formulario de pedidos")
    pitch = Pitch(pitch_color='#aabb97', line_color='white', stripe=True)
    fig, ax = pitch.draw()
    return fig

def mostrar_login(CONTRASENA_CORRECTA):
    # Función para mostrar la pantalla de inicio de sesión en la barra lateral
    st.sidebar.title("Login / Inicio de Sesión")
    with st.sidebar.form(key='login_form'):
        contraseña = st.text_input("Password / Introduce la contraseña", type="password")
        iniciar_sesion = st.form_submit_button("Login / Iniciar sesión")
        if iniciar_sesion:
            if contraseña == CONTRASENA_CORRECTA:
                st.session_state['sesion_iniciada'] = True
                st.sidebar.success("¡Inicio de sesión exitoso!")
            else:
                st.sidebar.error("Contraseña incorrecta. Acceso denegado.")

def add_watermark(canvas, doc):
    # Función para agregar la marca de agua (tu nombre o licencia)
    canvas.saveState()
    canvas.setFont('Helvetica-Bold', 20)  # Aumenta el tamaño de la fuente
    canvas.setStrokeColor(colors.lightgrey)
    canvas.setFillColor(colors.lightgrey)
    width, height = letter

    # Texto de la marca de agua (nombre o licencia)
    watermark_text = "José María Martín Núñez - Licencia FIFA Nº 202406-6950"

    # Dibujar la marca de agua repetida en varias posiciones
    step_x = 250  # Distancia entre cada marca de agua en el eje x
    step_y = 150  # Distancia entre cada marca de agua en el eje y

    for x in range(0, int(width), step_x):
        for y in range(0, int(height), step_y):
            canvas.saveState()
            canvas.translate(x, y)
            canvas.rotate(45)  # Rotar la marca de agua en diagonal
            canvas.drawCentredString(0, 0, watermark_text)
            canvas.restoreState()

    canvas.restoreState()

def generar_pdf(datos, idioma):
    # Función para generar el PDF con los datos
    if idioma == 'English':
        pdf_filename = "report.pdf"
    else:
        pdf_filename = "informe.pdf"

    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Estilos personalizados
    custom_style = ParagraphStyle(
        name='CustomStyle',
        fontSize=12,
        textColor=colors.darkblue,
        spaceAfter=10,
        spaceBefore=10,
        alignment=1  # Centrado
    )

    # Título principal
    if idioma == 'English':
        title = Paragraph("Report on club requirements", styles['Title'])
        footer_text = "José María Martín Núñez - FIFA FOOTBALL AGENT - Licence number: 202406-6950"
    else:
        title = Paragraph("Informe sobre requerimientos de futbolistas", styles['Title'])
        footer_text = "José María Martín Núñez - AGENTE DE FÚTBOL FIFA - Licencia Nº: 202406-6950"
    elements.append(title)

    # Añadir un espaciador
    elements.append(Spacer(1, 12))

    # Tabla de datos
    data = []
    for key, value in datos.items():
        if isinstance(value, list):
            value = ', '.join(map(str, value))
        elif isinstance(value, dict):
            # Formatear diccionarios internos
            value = ', '.join(f"{k}: {v}" for k, v in value.items())
        data.append([
            Paragraph(f"<b>{key}</b>", styles['Normal']),
            Paragraph(str(value), styles['Normal'])
        ])

    # Crear la tabla con las columnas ajustadas
    table = Table(data, colWidths=[200, 340])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)

    # Pie de página (opcional)
    footer = Paragraph(footer_text, custom_style)
    elements.append(footer)

    # Generar el PDF con la marca de agua
    doc.build(elements, onFirstPage=add_watermark, onLaterPages=add_watermark)
    with open(pdf_filename, "rb") as pdf_file:
        return pdf_file.read()

def guardar_datos(datos, archivo="informes_jugadores.csv"):
    # Función para guardar los datos en un archivo CSV
    if not os.path.exists(archivo):
        df = pd.DataFrame(columns=datos.keys())  # Crear archivo si no existe
    else:
        df = pd.read_csv(archivo)

    # Usar pd.concat() en lugar de append
    df = pd.concat([df, pd.DataFrame([datos])], ignore_index=True)
    df.to_csv(archivo, index=False)

def reset_form():
    # Función para resetear los campos del formulario
    for key in st.session_state.keys():
        st.session_state[key] = ""

def main():
    configurar_estilo()

    # Contraseña correcta definida
    CONTRASENA_CORRECTA = "240683"

    # Variable para mantener el estado de la sesión
    if 'sesion_iniciada' not in st.session_state:
        st.session_state['sesion_iniciada'] = False

    # Mostrar login si no se ha iniciado sesión
    if not st.session_state['sesion_iniciada']:
        mostrar_login(CONTRASENA_CORRECTA)
        # Mostrar el campo de fútbol centrado y más pequeño
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            fig = mostrar_campo()
            st.pyplot(fig)
        st.stop()  # Detener la ejecución hasta que se inicie sesión

    # Cargar la imagen de tu licencia FIFA
    st.sidebar.image("licencia.png")  # Imagen en la barra lateral

    # Añadir nombre y licencia con iconos
    st.sidebar.markdown("<h3>José María Martín Núñez</h3>", unsafe_allow_html=True)
    st.sidebar.markdown("<h4>Licencia FIFA Nº: 202406-6950</h4>", unsafe_allow_html=True)

    # Añadir email y teléfono con iconos
    st.sidebar.markdown("📧 **Email:** jmnagente@gmail.com")
    st.sidebar.markdown("📱 **Teléfono:** +34 645 764853")

    # Añadir otras redes sociales o información si lo deseas
    st.sidebar.markdown("🔗 [LinkedIn](https://www.linkedin.com/in/jos%C3%A9-m-mart%C3%ADn-6b805728/)")

    # Opciones de idioma, por defecto en inglés
    idioma = st.sidebar.radio("Select the language / Seleccione el idioma", ("English", "Español"), index=0)

    # Lista de las 211 federaciones de FIFA o países
    federaciones_fifa = [
        "Afghanistan", "Albania", "Algeria", "American Samoa", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", 
        "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", 
        "Belgium", "Belize", "Benin", "Bermuda", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", 
        "British Virgin Islands", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cambodia", "Cameroon", "Canada", 
        "Cape Verde", "Cayman Islands", "Central African Republic", "Chad", "Chile", "China PR", "Chinese Taipei", "Colombia", 
        "Comoros", "Congo", "Congo DR", "Cook Islands", "Costa Rica", "Croatia", "Cuba", "Curaçao", "Cyprus", "Czech Republic", 
        "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "England", "Equatorial Guinea", 
        "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Faroe Islands", "Fiji", "Finland", "France", "Gabon", "Gambia", "Georgia", 
        "Germany", "Ghana", "Gibraltar", "Greece", "Grenada", "Guam", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", 
        "Honduras", "Hong Kong", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Israel", "Italy", "Ivory Coast", 
        "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea DPR", "Korea Republic", "Kosovo", "Kuwait", 
        "Kyrgyz Republic", "Lao People's Democratic Republic", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", 
        "Lithuania", "Luxembourg", "Macau", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Mauritania", 
        "Mauritius", "Mexico", "Moldova", "Monaco", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", 
        "Namibia", "Nauru", "Nepal", "Netherlands", "New Caledonia", "New Zealand", "Nicaragua", "Niger", "Nigeria", "Niue", 
        "Northern Ireland", "Norway", "Oman", "Pakistan", "Palau", "Palestine", "Panama", "Papua New Guinea", "Paraguay", "Peru", 
        "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Ireland", "Romania", "Russia", "Rwanda", 
        "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe", 
        "Saudi Arabia", "Scotland", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", 
        "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", 
        "Switzerland", "Syria", "Tajikistan", "Tanzania", "Thailand", "Timor-Leste", "Togo", "Tokelau", "Tonga", "Trinidad and Tobago", 
        "Tunisia", "Turkey", "Turkmenistan", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", "United States of America", 
        "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "Wales", "Yemen", "Zambia", "Zimbabwe"
    ]

    # Definir el formulario en inglés o español
    if idioma == "English":
        # Formulario en inglés
        st.subheader("Player Recruitment Needs")

        # 1. Positions to Strengthen
        club_name = st.text_input("Name of the Club", key='club_name')

        # Market Window
        market_window = st.selectbox(
            "Market Window to reinforce",
            ["Summer Transfer Window", "Winter Transfer Window", "General"],
            key='market_window'
        )

        with st.expander("1. Positions to strengthen"):
            position = st.selectbox(
                "Select the priority position you want to strengthen",
                ["Goalkeeper", "Center Back", "Left Back", "Right Back",
                 "Defensive Midfielder", "Attacking Midfielder", "Left Winger",
                 "Right Winger", "Striker"],
                 key='position'
            )

        # 2. Desired Player Profile
        with st.expander("2. Desired player profile"):
            col1, col2 = st.columns(2)
            with col1:
                ideal_age = st.selectbox(
                    "Ideal Age",
                    ["Under-23", "Between 23-28 years", "Over 28 years"],
                    key='ideal_age'
                )
            with col2:
                competitive_experience = st.multiselect(
                    "Competitive Experience",
                    ["Category 1", "Category 2", "Category 3", "Category 4",
                     "Category 5", "Other Categories"],
                    key='competitive_experience'
                )
            preferred_nationality = st.multiselect(
                "Preferred Nationality (Optional)",
                federaciones_fifa,
                key='preferred_nationality'
            )

            # Style of Play
            style_of_play = st.multiselect(
                "Select the key characteristics of the playing style",
                [
                    "Technical",
                    "Physical",
                    "Versatile",
                    "Specialized in dribbling",
                    "Inverted-foot player",
                    "Associative",
                    "High pressing ability",
                    "Build-up play from the back",
                    "Game vision",
                    "Good long pass",
                    "1-on-1 capability",
                    "Movement and positioning",
                    "Good decision-making",
                    "Experience in European competitions",
                    "Goal-scoring ability",
                    "Leadership",
                    "Ability to play in different tactical systems",
                    "Free-kick specialist",
                    "Stamina",
                    "Tactical intelligence",
                    "Skill in through passes",
                    "Ability to play under pressure",
                    "Winning mentality",
                    "Ability to take on responsibilities",
                    "Good aerial ability",
                    "Associative play",
                    "Able to play multiple positions",
                    "Good anticipation",
                    "Good ball control",
                    "Ability to break lines",
                    "International experience",
                    "On-field leadership",
                    "Adaptability to different leagues",
                    "Penalty specialist",
                    "Teamwork",
                    "Tactical discipline",
                    "Positive aggressiveness",
                    "Recovery ability",
                    "Communication on the field",
                    "Creativity",
                    "Emotional balance"
                ],
                key='style_of_play'
            )

        # 3. Budget Availability
        with st.expander("3. Budget availability"):
            salary_range = st.selectbox(
                "Expected Salary Range",
                ["Less than 50,000€", "Between 50,000€ and 100,000€",
                 "More than 100,000€", "More than 500,000€",
                 "Between 500,000€ and 1,000,000€", "More than 1,000,000€",
                 "No salary limit"],
                 key='salary_range'
            )
            transfer_type = st.selectbox(
                "Type of Transfer",
                ["Loan", "Loan with option to buy", "Permanent signing"],
                key='transfer_type'
            )

        # 4. Immediate Needs
        with st.expander("4. Immediate needs"):
            immediate_needs = st.text_area(
                "Are there any positions that need urgent reinforcement? (Specify position and reason)",
                key='immediate_needs'
            )

        # 5. Current Contract
        with st.expander("5. Current contract"):
            free_agent = st.radio(
                "Do you want the player to be a Free Agent?",
                ("Yes", "No"),
                key='free_agent'
            )

            if free_agent == "No":
                contract_end = st.text_input(
                    "Enter the amount the club can afford to pay for the player",
                    key='contract_end'
                )
            else:
                contract_end = "Unspecified"

        # 6. Injury History
        with st.expander("6. Injury History"):
            injury_history = st.text_area(
                "Describe the player's injury history (if applicable)",
                key='injury_history'
            )

        # 7. Performance Statistics
        with st.expander("7. Performance Statistics"):
            period = st.selectbox("Time Period", ["Last X matches", "Specific season", "Date range", "Total"])

            if period == "Last X matches":
                num_matches = st.number_input("Enter the number of matches", min_value=1, step=1, key='num_matches')
            elif period == "Specific season":
                season = st.selectbox("Select the season", ["2022/2023", "2021/2022", "2020/2021"], key='season')
                num_matches = st.number_input("Number of matches played in the season", min_value=1, step=1, key='num_matches')
            elif period == "Date range":
                start_date = st.date_input("Start date", key='start_date')
                end_date = st.date_input("End date", key='end_date')
                num_matches = st.number_input("Number of matches in the date range", min_value=1, step=1, key='num_matches')
            else:
                num_matches = st.number_input("Total number of matches played", min_value=1, step=1, key='num_matches')

            # Minutes Played
            minutes_played = st.number_input("Minutes played", min_value=0, step=1, key='minutes_played')

            # Matches Played
            matches_played = num_matches

            # Goals
            total_goals = st.number_input("Total goals", min_value=0, step=1, key='total_goals')
            if matches_played > 0:
                goals_per_match = total_goals / matches_played
                st.write(f"Goals per match: {goals_per_match:.2f}")
            else:
                goals_per_match = 0

            # Assists
            total_assists = st.number_input("Total assists", min_value=0, step=1, key='total_assists')
            if matches_played > 0:
                assists_per_match = total_assists / matches_played
                st.write(f"Assists per match: {assists_per_match:.2f}")
            else:
                assists_per_match = 0

            # Shots per match
            shots_per_match = st.number_input("Shots per match", min_value=0.0, step=0.1, key='shots_per_match')

            # Passing Accuracy (%)
            passing_accuracy = st.number_input("Passing accuracy (%)", min_value=0.0, max_value=100.0, step=0.1, key='passing_accuracy')

            # Successful dribbles per match
            successful_dribbles_per_match = st.number_input("Successful dribbles per match", min_value=0.0, step=0.1, key='successful_dribbles_per_match')

            # Duels won per match
            duels_won_per_match = st.number_input("Duels won per match", min_value=0.0, step=0.1, key='duels_won_per_match')

            # Yellow cards
            yellow_cards = st.number_input("Yellow cards", min_value=0, step=1, key='yellow_cards')

            # Red cards
            red_cards = st.number_input("Red cards", min_value=0, step=1, key='red_cards')

            # Defender Statistics
            is_defender = st.radio("Is the player a defender?", ("Yes", "No"), key='is_defender')
            if is_defender == "Yes":
                # Successful tackles per match
                successful_tackles_per_match = st.number_input("Successful tackles per match", min_value=0.0, step=0.1, key='successful_tackles_per_match')

                # Interceptions per match
                interceptions_per_match = st.number_input("Interceptions per match", min_value=0.0, step=0.1, key='interceptions_per_match')

                # Clearances per match
                clearances_per_match = st.number_input("Clearances per match", min_value=0.0, step=0.1, key='clearances_per_match')

                # Aerial duels won per match
                aerial_duels_won_per_match = st.number_input("Aerial duels won per match", min_value=0.0, step=0.1, key='aerial_duels_won_per_match')

                # Calculate total interceptions
                if matches_played > 0:
                    total_interceptions = interceptions_per_match * matches_played
                else:
                    total_interceptions = 0
            else:
                # Inicializar variables para evitar NameError
                successful_tackles_per_match = None
                interceptions_per_match = None
                total_interceptions = None
                clearances_per_match = None
                aerial_duels_won_per_match = None

            # Goalkeeper Statistics
            is_goalkeeper = st.radio("Is the player a goalkeeper?", ("Yes", "No"), key='is_goalkeeper')
            if is_goalkeeper == "Yes":
                # Clean sheets
                clean_sheets = st.number_input("Total clean sheets", min_value=0, step=1, key='clean_sheets')

                # Goals conceded
                goals_conceded = st.number_input("Total goals conceded", min_value=0, step=1, key='goals_conceded')
                if matches_played > 0:
                    goals_conceded_per_match = goals_conceded / matches_played
                    st.write(f"Goals conceded per match: {goals_conceded_per_match:.2f}")
                else:
                    goals_conceded_per_match = 0

                # Total saves
                total_saves = st.number_input("Total saves", min_value=0, step=1, key='total_saves')

                # Save percentage
                total_shots_faced = st.number_input("Total shots faced", min_value=0, step=1, key='total_shots_faced')
                if total_shots_faced > 0:
                    save_percentage = (total_saves / total_shots_faced) * 100
                    st.write(f"Save percentage: {save_percentage:.2f}%")
                else:
                    save_percentage = 0

                # Penalties saved
                penalties_saved = st.number_input("Total penalties saved", min_value=0, step=1, key='penalties_saved')

                # Distribution accuracy (%)
                distribution_accuracy = st.number_input("Distribution accuracy (%)", min_value=0.0, max_value=100.0, step=0.1, key='distribution_accuracy')
            else:
                # Inicializar variables para evitar NameError
                clean_sheets = None
                goals_conceded = None
                goals_conceded_per_match = None
                total_saves = None
                save_percentage = None
                penalties_saved = None
                distribution_accuracy = None

        # Physical Metrics (Optional)
        with st.expander("Physical Metrics (Optional)"):
            # Distance covered per match (km)
            distance_per_match = st.number_input("Distance covered per match (km)", min_value=0.0, step=0.1, key='distance_per_match')

            # Top speed reached (km/h)
            top_speed = st.number_input("Top speed reached (km/h)", min_value=0.0, step=0.1, key='top_speed')

        # Advanced Metrics (Optional)
        with st.expander("Advanced Metrics (Optional)"):
            # Total Expected Goals (xG)
            xg_total = st.number_input("Total Expected Goals (xG)", min_value=0.0, step=0.1, key='xg_total')
            if matches_played > 0:
                xg_per_match = xg_total / matches_played
                st.write(f"xG per match: {xg_per_match:.2f}")
            else:
                xg_per_match = 0

            # Total Expected Assists (xA)
            xa_total = st.number_input("Total Expected Assists (xA)", min_value=0.0, step=0.1, key='xa_total')
            if matches_played > 0:
                xa_per_match = xa_total / matches_played
                st.write(f"xA per match: {xa_per_match:.2f}")
            else:
                xa_per_match = 0



        # 8. International Adaptability
        with st.expander("8. International Adaptability"):
            international_adaptability = st.radio(
                "Has the player played in international leagues?",
                ("Yes", "No"),
                key='international_adaptability'
            )

        # 9. Availability to Travel/Relocate
        with st.expander("9. Availability to Travel/Relocate"):
            availability_to_travel = st.radio(
                "Is the player available to travel/relocate?",
                ("Yes", "No"),
                key='availability_to_travel'
            )

        # 10. Languages Spoken
        with st.expander("10. Languages Spoken"):
            languages = st.text_area("Languages spoken by the player", key='languages')

        # 11. Market Value
        with st.expander("11. Market Value"):
            market_value = st.text_input("Estimated current market value (if applicable)", key='market_value')

        # 12. Positional Flexibility
        with st.expander("12. Positional Flexibility"):
            positional_flexibility = st.text_area(
                "Additional positions the player can play",
                key='positional_flexibility'
            )

        # 13. Scouting Recommendation
        with st.expander("13. Scouting Recommendation"):
            scouting_recommendation = st.text_area(
                "Scouting evaluation of the player's potential",
                key='scouting_recommendation'
            )

        # 14. International Competitions
        with st.expander("14. Participation in International Competitions"):
            international_competitions = st.text_area(
                "International competitions the player has participated in",
                key='international_competitions'
            )

        # 15. Attitude and Character
        with st.expander("15. Attitude and Character"):
            attitude_and_character = st.text_area(
                "Evaluation of the player's attitude and character",
                key='attitude_and_character'
            )

        # 16. Media or Social Media Presence
        with st.expander("16. Media or Social Media Presence"):
            media_presence = st.text_area(
                "Does the player have significant media or social media presence?",
                key='media_presence'
            )

        # Botón para enviar y generar el informe
        if st.button("Download Report"):
            # Preparar las estadísticas de rendimiento
            performance_stats = {
                "Period": period,
                "Number of Matches": matches_played,
                "Minutes Played": minutes_played,
                "Total Goals": total_goals,
                "Goals per Match": goals_per_match,
                "Total Assists": total_assists,
                "Assists per Match": assists_per_match,
                "Shots per Match": shots_per_match,
                "Passing Accuracy (%)": passing_accuracy,
                "Successful Dribbles per Match": successful_dribbles_per_match,
                "Duels Won per Match": duels_won_per_match,
                "Yellow Cards": yellow_cards,
                "Red Cards": red_cards,
            }

            # Añadir estadísticas de defensores si aplica
            if is_defender == "Yes":
                defender_stats = {
                    "Successful Tackles per Match": successful_tackles_per_match,
                    "Interceptions per Match": interceptions_per_match,
                    "Clearances per Match": clearances_per_match,
                    "Aerial Duels Won per Match": aerial_duels_won_per_match,
                }
                performance_stats.update(defender_stats)

            # Añadir estadísticas de porteros si aplica
            if is_goalkeeper == "Yes":
                goalkeeper_stats = {
                    "Clean Sheets": clean_sheets,
                    "Goals Conceded": goals_conceded,
                    "Goals Conceded per Match": goals_conceded_per_match,
                    "Total Saves": total_saves,
                    "Save Percentage": save_percentage,
                    "Penalties Saved": penalties_saved,
                    "Distribution Accuracy (%)": distribution_accuracy,
                }
                performance_stats.update(goalkeeper_stats)

            # Añadir métricas físicas si se proporcionaron
            if distance_per_match > 0 or top_speed > 0:
                physical_metrics = {
                    "Distance Covered per Match (km)": distance_per_match,
                    "Top Speed Reached (km/h)": top_speed,
                }
                performance_stats.update(physical_metrics)

            # Añadir métricas avanzadas si se proporcionaron
            if xg_total > 0 or xa_total > 0:
                advanced_metrics = {
                    "Total Expected Goals (xG)": xg_total,
                    "xG per Match": xg_per_match,
                    "Total Expected Assists (xA)": xa_total,
                    "xA per Match": xa_per_match,
                }
                performance_stats.update(advanced_metrics)

            # Construir el diccionario de datos completo
            datos = {
                "Name of Club": club_name,
                "Market Window to Reinforce": market_window,
                "Position": position,
                "Ideal Age": ideal_age,
                "Competitive Experience": competitive_experience,
                "Preferred Nationality": preferred_nationality,
                "Style of Play": style_of_play,
                "Salary Range": salary_range,
                "Transfer Type": transfer_type,
                "Immediate Needs": immediate_needs or "N/A",
                "Free Agent": free_agent,
                "Transfer Fee or Contract Amount": contract_end,
                "Injury History": injury_history or "N/A",
                "Performance Statistics": performance_stats,
                "International Adaptability": international_adaptability,
                "Availability to Travel/Relocate": availability_to_travel,
                "Languages": languages,
                "Market Value": market_value,
                "Positional Flexibility": positional_flexibility,
                "Scouting Recommendation": scouting_recommendation,
                "International Competitions": international_competitions,
                "Attitude and Character": attitude_and_character,
                "Media or Social Media Presence": media_presence,
            }

            # Guardar los datos y generar el PDF
            guardar_datos(datos)
            st.success("Report successfully submitted and saved.")

            # Generar PDF
            pdf_data = generar_pdf(datos, idioma)

            # Botón para descargar el PDF
            st.download_button(
                label="Download PDF",
                data=pdf_data,
                file_name="report.pdf",
                mime="application/pdf"
            )



    else:
        # Formulario en español
        st.subheader("Necesidades de Incorporación de Jugadores")

        # 1. Posiciones a Refuerzar
        nombre_club = st.text_input("Nombre del club", key='nombre_club')

        # Ventana de Mercado
        ventana_mercado = st.selectbox(
            "Ventana a reforzar",
            ["Ventana de Transferencia Verano", "Ventana de Transferencia Invierno", "General"],
            key='ventana_mercado'
        )

        with st.expander("1. Posiciones a reforzar"):
            position = st.selectbox(
                "Seleccione la posición prioritaria que desea reforzar",
                ["Portero", "Defensa Central", "Lateral Izquierdo", "Lateral Derecho",
                 "Centrocampista Defensivo", "Centrocampista Ofensivo", "Extremo Izquierdo",
                 "Extremo Derecho", "Delantero"],
                 key='position'
            )

        # 2. Perfil del Jugador Deseado
        with st.expander("2. Perfil del Jugador deseado"):
            col1, col2 = st.columns(2)
            with col1:
                ideal_age = st.selectbox(
                    "Edad Ideal",
                    ["Sub-23", "Entre 23-28 años", "Más de 28 años"],
                    key='ideal_age'
                )
            with col2:
                competitive_experience = st.multiselect(
                    "Experiencia Competitiva",
                    ["Categoría 1", "Categoría 2", "Categoría 3", "Categoría 4",
                     "Categoría 5", "Otras Categorías"],
                    key='competitive_experience'
                )
            preferred_nationality = st.multiselect(
                "Nacionalidad Preferente (Opcional)",
                federaciones_fifa,
                key='preferred_nationality'
            )

            # Estilo de Juego
            style_of_play = st.multiselect(
                "Seleccione las características clave del estilo de juego",
                [
                    "Técnico",
                    "Físico",
                    "Versátil",
                    "Especializado en desborde",
                    "Jugador de pierna cambiada",
                    "Asociativo",
                    "Capacidad de presión alta",
                    "Construcción desde el fondo",
                    "Visión de juego",
                    "Buen pase largo",
                    "Capacidad en 1 vs 1",
                    "Desmarque y movilidad",
                    "Buena toma de decisiones",
                    "Experiencia en competiciones europeas",
                    "Capacidad goleadora",
                    "Liderazgo",
                    "Capacidad de jugar en diferentes sistemas tácticos",
                    "Especialista en tiros libres",
                    "Resistencia física",
                    "Inteligencia táctica",
                    "Habilidad en pases filtrados",
                    "Capacidad para jugar bajo presión",
                    "Mentalidad ganadora",
                    "Capacidad para asumir responsabilidades",
                    "Buen juego aéreo",
                    "Juego asociativo",
                    "Polivalente",
                    "Buena anticipación",
                    "Buen control del balón",
                    "Habilidad para romper líneas",
                    "Experiencia internacional",
                    "Capacidad de liderazgo en el campo",
                    "Adaptabilidad a diferentes ligas",
                    "Especialista en penales",
                    "Trabajo en equipo",
                    "Disciplina táctica",
                    "Agresividad positiva",
                    "Capacidad de recuperación",
                    "Comunicación en el campo",
                    "Creatividad",
                    "Equilibrio emocional"
                ],
                key='style_of_play'
            )

        # 3. Disponibilidad Presupuestaria
        with st.expander("3. Disponibilidad presupuestaria"):
            salary_range = st.selectbox(
                "Rango de salario esperado",
                ["Menos de 50,000€", "Entre 50,000€ y 100,000€",
                 "Más de 100,000€", "Más de 500,000€", "Entre 500,000€ y 1,000,000€",
                 "Más de 1,000,000€", "Sin límite salarial"],
                 key='salary_range'
            )
            transfer_type = st.selectbox(
                "Tipología de incorporación",
                ["Cesión", "Cesión con opción de compra", "Fichaje definitivo"],
                key='transfer_type'
            )

        # 4. Necesidades Inmediatas
        with st.expander("4. Necesidades inmediatas"):
            immediate_needs = st.text_area(
                "¿Existen posiciones que necesitan ser reforzadas de manera urgente? (Describa posición y motivo)",
                key='immediate_needs'
            )

        # 5. Contrato Actual
        with st.expander("5. Contrato actual"):
            agente_libre = st.radio(
                "¿Quieren el jugador Agente Libre?",
                ("Sí", "No"),
                key='agente_libre'
            )

            if agente_libre == "No":
                contract_end = st.text_input(
                    "Ingrese lo que puede llegar a pagar el club por el jugador/a",
                    key='contract_end'
                )
            else:
                contract_end = "Sin especificar"

        # 6. Historial de Lesiones
        with st.expander("6. Historial de Lesiones"):
            lesion_historial = st.text_area(
                "Describa el historial de lesiones del jugador (si aplica)",
                key='lesion_historial'
            )

        # 7. Estadísticas de Rendimiento
        with st.expander("7. Estadísticas de Rendimiento"):
            periodo = st.selectbox("Periodo de Tiempo", ["Últimos X partidos", "Temporada específica", "Rango de fechas", "Total"])

            if periodo == "Últimos X partidos":
                num_partidos = st.number_input("Ingrese el número de partidos", min_value=1, step=1, key='num_partidos')
            elif periodo == "Temporada específica":
                temporada = st.selectbox("Seleccione la temporada", ["2022/2023", "2021/2022", "2020/2021"], key='temporada')
                num_partidos = st.number_input("Número de partidos jugados en la temporada", min_value=1, step=1, key='num_partidos')
            elif periodo == "Rango de fechas":
                fecha_inicio = st.date_input("Fecha de inicio", key='fecha_inicio')
                fecha_fin = st.date_input("Fecha de fin", key='fecha_fin')
                num_partidos = st.number_input("Número de partidos en el rango de fechas", min_value=1, step=1, key='num_partidos')
            else:
                num_partidos = st.number_input("Número total de partidos jugados", min_value=1, step=1, key='num_partidos')

            # Minutos Jugados
            minutos_jugados = st.number_input("Minutos jugados", min_value=0, step=1, key='minutos_jugados')

            # Partidos Jugados
            partidos_jugados = num_partidos

            # Goles
            goles_totales = st.number_input("Total de goles", min_value=0, step=1, key='goles_totales')
            if partidos_jugados > 0:
                goles_por_partido = goles_totales / partidos_jugados
                st.write(f"Goles por partido: {goles_por_partido:.2f}")
            else:
                goles_por_partido = 0

            # Asistencias
            asistencias_totales = st.number_input("Total de asistencias", min_value=0, step=1, key='asistencias_totales')
            if partidos_jugados > 0:
                asistencias_por_partido = asistencias_totales / partidos_jugados
                st.write(f"Asistencias por partido: {asistencias_por_partido:.2f}")
            else:
                asistencias_por_partido = 0

            # Tiros por partido
            tiros_por_partido = st.number_input("Tiros por partido", min_value=0.0, step=0.1, key='tiros_por_partido')

            # Precisión de pases (%)
            precision_pases = st.number_input("Precisión de pases (%)", min_value=0.0, max_value=100.0, step=0.1, key='precision_pases')

            # Regates exitosos por partido
            regates_exitosos_por_partido = st.number_input("Regates exitosos por partido", min_value=0.0, step=0.1, key='regates_exitosos_por_partido')

            # Duelos ganados por partido
            duelos_ganados_por_partido = st.number_input("Duelos ganados por partido", min_value=0.0, step=0.1, key='duelos_ganados_por_partido')

            # Tarjetas amarillas
            tarjetas_amarillas = st.number_input("Tarjetas amarillas", min_value=0, step=1, key='tarjetas_amarillas')

            # Tarjetas rojas
            tarjetas_rojas = st.number_input("Tarjetas rojas", min_value=0, step=1, key='tarjetas_rojas')

            # Estadísticas para Defensores
            is_defender = st.radio("¿El jugador es defensa?", ("Sí", "No"), key='is_defender')
            if is_defender == "Sí":
                # Entradas exitosas por partido
                entradas_exitosas_por_partido = st.number_input("Entradas exitosas por partido", min_value=0.0, step=0.1, key='entradas_exitosas_por_partido')

                # Intercepciones por partido
                intercepciones_por_partido = st.number_input("Intercepciones por partido", min_value=0.0, step=0.1, key='intercepciones_por_partido')

                # Despejes por partido
                despejes_por_partido = st.number_input("Despejes por partido", min_value=0.0, step=0.1, key='despejes_por_partido')

                # Duelos aéreos ganados por partido
                duelos_aereos_ganados_por_partido = st.number_input("Duelos aéreos ganados por partido", min_value=0.0, step=0.1, key='duelos_aereos_ganados_por_partido')

                # Calcular total de intercepciones
                if partidos_jugados > 0:
                    intercepciones_totales = intercepciones_por_partido * partidos_jugados
                else:
                    intercepciones_totales = 0
            else:
                # Inicializar variables para evitar NameError
                entradas_exitosas_por_partido = None
                intercepciones_por_partido = None
                intercepciones_totales = None
                despejes_por_partido = None
                duelos_aereos_ganados_por_partido = None

            # Estadísticas para Porteros
            is_goalkeeper = st.radio("¿El jugador es portero?", ("Sí", "No"), key='is_goalkeeper')
            if is_goalkeeper == "Sí":
                # Partidos con portería imbatida
                porterias_imbatidas = st.number_input("Total de porterías imbatidas", min_value=0, step=1, key='porterias_imbatidas')

                # Goles encajados
                goles_encajados = st.number_input("Total de goles encajados", min_value=0, step=1, key='goles_encajados')
                if partidos_jugados > 0:
                    goles_encajados_por_partido = goles_encajados / partidos_jugados
                    st.write(f"Goles encajados por partido: {goles_encajados_por_partido:.2f}")
                else:
                    goles_encajados_por_partido = 0

                # Paradas totales
                paradas_totales = st.number_input("Total de paradas", min_value=0, step=1, key='paradas_totales')

                # Porcentaje de paradas
                total_tiros_enfrentados = st.number_input("Total de tiros enfrentados", min_value=0, step=1, key='total_tiros_enfrentados')
                if total_tiros_enfrentados > 0:
                    porcentaje_paradas = (paradas_totales / total_tiros_enfrentados) * 100
                    st.write(f"Porcentaje de paradas: {porcentaje_paradas:.2f}%")
                else:
                    porcentaje_paradas = 0

                # Penaltis detenidos
                penaltis_detenidos = st.number_input("Total de penaltis detenidos", min_value=0, step=1, key='penaltis_detenidos')

                # Precisión en distribución (%)
                precision_distribucion = st.number_input("Precisión en distribución (%)", min_value=0.0, max_value=100.0, step=0.1, key='precision_distribucion')
            else:
                # Inicializar variables para evitar NameError
                porterias_imbatidas = None
                goles_encajados = None
                goles_encajados_por_partido = None
                paradas_totales = None
                porcentaje_paradas = None
                penaltis_detenidos = None
                precision_distribucion = None

        # Métricas Físicas (Opcional)
        with st.expander("Métricas Físicas (Opcional)"):
            # Distancia recorrida por partido (km)
            distancia_por_partido = st.number_input("Distancia recorrida por partido (km)", min_value=0.0, step=0.1, key='distancia_por_partido')

            # Velocidad máxima alcanzada (km/h)
            velocidad_maxima = st.number_input("Velocidad máxima alcanzada (km/h)", min_value=0.0, step=0.1, key='velocidad_maxima')

        # Métricas Avanzadas (Opcional)
        with st.expander("Métricas Avanzadas (Opcional)"):
            # Goles esperados (xG) totales
            xg_total = st.number_input("Goles esperados (xG) totales", min_value=0.0, step=0.1, key='xg_total')
            if partidos_jugados > 0:
                xg_por_partido = xg_total / partidos_jugados
                st.write(f"xG por partido: {xg_por_partido:.2f}")
            else:
                xg_por_partido = 0

            # Asistencias esperadas (xA) totales
            xa_total = st.number_input("Asistencias esperadas (xA) totales", min_value=0.0, step=0.1, key='xa_total')
            if partidos_jugados > 0:
                xa_por_partido = xa_total / partidos_jugados
                st.write(f"xA por partido: {xa_por_partido:.2f}")
            else:
                xa_por_partido = 0

        # 8. Adaptabilidad Internacional
        with st.expander("8. Adaptabilidad Internacional"):
            adaptabilidad_internacional = st.radio(
                "¿Ha jugado en ligas internacionales?",
                ("Sí", "No"),
                key='adaptabilidad_internacional'
            )

        # 9. Disponibilidad para Viajar/Mudarse
        with st.expander("9. Disponibilidad para Viajar/Mudarse"):
            disponibilidad_viajar = st.radio(
                "¿Está disponible para viajar/mudarse?",
                ("Sí", "No"),
                key='disponibilidad_viajar'
            )

        # 10. Idiomas que habla
        with st.expander("10. Idiomas que habla"):
            idiomas = st.text_area("Idiomas que el jugador habla", key='idiomas')

        # 11. Valor de Mercado
        with st.expander("11. Valor de Mercado"):
            valor_mercado = st.text_input("Valor de mercado actual estimado (si aplica)", key='valor_mercado')

        # 12. Flexibilidad Posicional
        with st.expander("12. Flexibilidad Posicional"):
            flexibilidad_posicional = st.text_area(
                "Posiciones adicionales en las que puede jugar",
                key='flexibilidad_posicional'
            )

        # 13. Recomendación de Scouting
        with st.expander("13. Recomendación de Scouting"):
            scouting_recomendacion = st.text_area(
                "Evaluación del scouting sobre el potencial del jugador",
                key='scouting_recomendacion'
            )

        # 14. Participación en Competiciones Internacionales
        with st.expander("14. Participación en Competiciones Internacionales"):
            competiciones_internacionales = st.text_area(
                "Competiciones internacionales en las que ha participado",
                key='competiciones_internacionales'
            )

        # 15. Actitud y Carácter
        with st.expander("15. Actitud y Carácter"):
            actitud_caracter = st.text_area(
                "Evaluación de actitud y carácter",
                key='actitud_caracter'
            )

        # 16. Seguimiento en Medios o Redes Sociales
        with st.expander("16. Seguimiento en Medios o Redes Sociales"):
            seguimiento_medios = st.text_area(
                "¿Tiene el jugador una presencia relevante en redes sociales o medios?",
                key='seguimiento_medios'
            )

        # Botón para enviar y generar el informe
        if st.button("Descargar Informe"):
            # Preparar las estadísticas de rendimiento
            estadisticas_rendimiento = {
                "Periodo": periodo,
                "Número de Partidos": partidos_jugados,
                "Minutos Jugados": minutos_jugados,
                "Total de Goles": goles_totales,
                "Goles por Partido": goles_por_partido,
                "Total de Asistencias": asistencias_totales,
                "Asistencias por Partido": asistencias_por_partido,
                "Tiros por Partido": tiros_por_partido,
                "Precisión de Pases (%)": precision_pases,
                "Regates Exitosos por Partido": regates_exitosos_por_partido,
                "Duelos Ganados por Partido": duelos_ganados_por_partido,
                "Tarjetas Amarillas": tarjetas_amarillas,
                "Tarjetas Rojas": tarjetas_rojas,
            }

            # Añadir estadísticas de defensores si aplica
            if is_defender == "Sí":
                estadisticas_defensor = {
                    "Entradas Exitosas por Partido": entradas_exitosas_por_partido,
                    "Intercepciones por Partido": intercepciones_por_partido,
                    "Despejes por Partido": despejes_por_partido,
                    "Duelos Aéreos Ganados por Partido": duelos_aereos_ganados_por_partido,
                }
                estadisticas_rendimiento.update(estadisticas_defensor)

            # Añadir estadísticas de porteros si aplica
            if is_goalkeeper == "Sí":
                estadisticas_portero = {
                    "Porterías Imbatidas": porterias_imbatidas,
                    "Goles Encajados": goles_encajados,
                    "Goles Encajados por Partido": goles_encajados_por_partido,
                    "Total de Paradas": paradas_totales,
                    "Porcentaje de Paradas": porcentaje_paradas,
                    "Penaltis Detenidos": penaltis_detenidos,
                    "Precisión en Distribución (%)": precision_distribucion,
                }
                estadisticas_rendimiento.update(estadisticas_portero)

            # Añadir métricas físicas si se proporcionaron
            if distancia_por_partido > 0 or velocidad_maxima > 0:
                metricas_fisicas = {
                    "Distancia Recorrida por Partido (km)": distancia_por_partido,
                    "Velocidad Máxima Alcanzada (km/h)": velocidad_maxima,
                }
                estadisticas_rendimiento.update(metricas_fisicas)

            # Añadir métricas avanzadas si se proporcionaron
            if xg_total > 0 or xa_total > 0:
                metricas_avanzadas = {
                    "Goles Esperados (xG) Totales": xg_total,
                    "xG por Partido": xg_por_partido,
                    "Asistencias Esperadas (xA) Totales": xa_total,
                    "xA por Partido": xa_por_partido,
                }
                estadisticas_rendimiento.update(metricas_avanzadas)

            # Construir el diccionario de datos completo
            datos = {
                "Nombre del Club": nombre_club,
                "Ventana a Reforzar": ventana_mercado,
                "Posición": position,
                "Edad Ideal": ideal_age,
                "Experiencia Competitiva": competitive_experience,
                "Nacionalidad Preferente": preferred_nationality,
                "Estilo de Juego": style_of_play,
                "Rango Salarial": salary_range,
                "Tipología de Incorporación": transfer_type,
                "Necesidad Inmediata": immediate_needs or "N/A",
                "Agente Libre": agente_libre,
                "Monto de Transferencia o Contrato": contract_end,
                "Historial de Lesiones": lesion_historial or "N/A",
                "Estadísticas de Rendimiento": estadisticas_rendimiento,
                "Adaptabilidad Internacional": adaptabilidad_internacional,
                "Disponibilidad para Viajar/Mudarse": disponibilidad_viajar,
                "Idiomas": idiomas,
                "Valor de Mercado": valor_mercado,
                "Flexibilidad Posicional": flexibilidad_posicional,
                "Recomendación de Scouting": scouting_recomendacion,
                "Competiciones Internacionales": competiciones_internacionales,
                "Actitud y Carácter": actitud_caracter,
                "Seguimiento en Redes Sociales": seguimiento_medios,
            }

            # Guardar los datos y generar el PDF
            guardar_datos(datos)
            st.success("Informe enviado y guardado exitosamente.")

            # Generar PDF
            pdf_data = generar_pdf(datos, idioma)

            # Botón para descargar el PDF
            st.download_button(
                label="Descargar PDF",
                data=pdf_data,
                file_name="informe.pdf",
                mime="application/pdf"
            )


if __name__ == "__main__":
    main()
