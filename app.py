import streamlit as st
import pandas as pd
import os
from io import StringIO
from fpdf import FPDF
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt


# Configurar tema oscuro
st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
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
    </style>
    """, unsafe_allow_html=True
)

# Función para mostrar y dibujar un campo de fútbol usando mplsoccer
def mostrar_campo():
    pitch = Pitch(pitch_color='#aabb97', line_color='white', stripe=True)
    fig, ax = pitch.draw(figsize=(10, 10))  # Tamaño ajustado a 2.5x1.5 (más pequeño)
    return fig


# Función personalizada de FPDF para trabajar con UTF-8
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Player Recruitment Report", 0, 1, "C")

    def chapter_title(self, title):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, 0, 1, "L")
        self.ln(4)

    def chapter_body(self, body):
        self.set_font("Arial", "", 12)
        self.multi_cell(0, 10, body)
        self.ln()

    def add_chapter(self, title, body):
        self.add_page()
        self.chapter_title(title)
        self.chapter_body(body)


# Función para agregar la marca de agua (tu nombre o licencia)
def add_watermark(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica-Bold', 20)
    canvas.setStrokeColor(colors.lightgrey)
    canvas.setFillColor(colors.lightgrey)
    width, height = letter

    # Texto de la marca de agua (nombre o licencia)
    watermark_text = "Jose Maria Martin Nuñez - Licence FIFA Nº 202406-6950"

    # Dibujar la marca de agua repetida en varias posiciones
    for x in range(0, int(width), 150):  # Cada 200 unidades en el eje x
        for y in range(0, int(height),200):  # Cada 150 unidades en el eje y
            canvas.saveState()
            canvas.translate(x, y)
            canvas.rotate(45)  # Rotar la marca de agua en diagonal
            canvas.drawCentredString(0, 0, watermark_text)  # Texto de la marca de agua
            canvas.restoreState()

    canvas.restoreState()

# Función para generar el PDF con mejor diseño visual y sin colores en la tabla
def generar_pdf(datos):
    # Crear el documento PDF
    doc = SimpleDocTemplate("report.pdf", pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Espaciado general
    general_spacer = Spacer(1, 12)

    # Título principal: Nombre de Agente FIFA
    titulo_fifa = Paragraph("Report for FIFA Agent:<br/><b>José Mª Martín Núñez - LIcence: 202406-6950</b>", styles["Title"])
    elements.append(titulo_fifa)
    elements.append(Spacer(1, 12))

    # Línea divisoria
    elements.append(Spacer(1, 6))
    elements.append(Paragraph('<hr width="100%" color="gray" size="1">', styles["Normal"]))

    # Título secundario: Nombre del club recogido del formulario
    #nombre_club = datos.get("Name of Club", "Club name not available")
    #titulo_club = Paragraph(f"<b>Club:</b> {nombre_club}", styles["Title"])
    #elements.append(titulo_club)
    elements.append(Spacer(1, 24))

    # Línea divisoria
    elements.append(Paragraph('<hr width="100%" color="gray" size="1">', styles["Normal"]))
    elements.append(general_spacer)

    # Estructura en dos columnas: Claves (a la izquierda) y Valores (a la derecha)
    data = []
    for key, value in datos.items():
        # Solo texto plano, sin HTML
        data.append([f"{key}", f"{value}"])

    # Crear tabla para organizar los datos en dos columnas, sin colores
    table = Table(data, colWidths=[150, 300])  # Ajustar los anchos de las columnas
    table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),  # Tamaño de fuente ajustado para la tabla
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Solo líneas negras, sin fondo
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alinear en el medio verticalmente
    ]))
    elements.append(table)

    # Generar el PDF con la marca de agua (nombre o licencia)
    doc.build(elements, onFirstPage=add_watermark, onLaterPages=add_watermark)

    # Leer y devolver el archivo PDF generado
    with open("report.pdf", "rb") as pdf_file:
        return pdf_file.read()





# Función para generar el archivo CSV en memoria
def generar_csv(datos):
    df = pd.DataFrame([datos])
    output = StringIO()
    df.to_csv(output, index=False)
    processed_data = output.getvalue()
    return processed_data




# Inicializar session_state para evitar errores
if 'jugador' not in st.session_state:
    st.session_state['jugador'] = ""
if 'agente' not in st.session_state:
    st.session_state['agente'] = ""
if 'url_transfermarkt' not in st.session_state:
    st.session_state['url_transfermarkt'] = ""
if 'position' not in st.session_state:
    st.session_state['position'] = "Goalkeeper"
if 'ideal_age' not in st.session_state:
    st.session_state['ideal_age'] = "Under-23"
if 'competitive_experience' not in st.session_state:
    st.session_state['competitive_experience'] = "Experience in 1st Division"
if 'preferred_nationality' not in st.session_state:
    st.session_state['preferred_nationality'] = "Afghanistan"
if 'style_of_play' not in st.session_state:
    st.session_state['style_of_play'] = []
if 'salary_range' not in st.session_state:
    st.session_state['salary_range'] = "Less than 50,000€"
if 'transfer_type' not in st.session_state:
    st.session_state['transfer_type'] = "Loan"
if 'immediate_needs' not in st.session_state:
    st.session_state['immediate_needs'] = ""
if 'jugadores_observados' not in st.session_state:
    st.session_state['jugadores_observados'] = []

# Función para guardar los datos en un archivo CSV
def guardar_datos(datos, archivo="informes_jugadores.csv"):
    if not os.path.exists(archivo):
        df = pd.DataFrame(columns=datos.keys())  # Crear archivo si no existe
    else:
        df = pd.read_csv(archivo)
    
    # Usar pd.concat() en lugar de append
    df = pd.concat([df, pd.DataFrame([datos])], ignore_index=True)
    df.to_csv(archivo, index=False)



# Mostrar el campo de fútbol justo antes de comenzar el formulario
#campo_fig = mostrar_campo()
#st.sidebar.pyplot(campo_fig)


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

# Función para resetear los campos del formulario
def reset_form():
    for key in ['jugador', 'agente', 'url_transfermarkt']:
        st.session_state[key] = ""

# Definir el formulario en inglés o español
if idioma == "English":
    st.subheader("Player Recruitment Needs")

    # 1. Positions to Strengthen
    # Campo para el nombre del club
    club_name = st.text_input("Name of the Club", key='club_name')
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
            competitive_experience = st.selectbox(
                "Competitive Experience",
                ["Experience in 1st Division", "Experience in 2nd Division", "Young talent to develop"],
                key='competitive_experience'
            )
        preferred_nationality = st.multiselect("Preferred Nationality (Optional)", federaciones_fifa, key='preferred_nationality')

        # Style of Play
        style_of_play = st.multiselect(
            "Select the key characteristics of the playing style",
            ["Technical", "Physical", "Versatile", "Specialized in dribbling", 
             "High pressing ability", "Build-up play from the back", 
             "Vision", "Good long pass", "1-on-1 capability", 
             "Movement and positioning"],
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
        immediate_needs = st.text_area("Are there any positions that need urgent reinforcement? (Specify position and reason)", key='immediate_needs')



    # 5. Field to select if the player is a free agent or not
    with st.expander("5. Current contract"):
        free_agent = st.radio(
            "Do you want the player to be a Free Agent?", 
            ("Yes", "No"), 
            key='free_agent'
        )

    # If the player is not a free agent, show field for contract end date
    if free_agent == "No":
        contract_end =  st.text_input("Enter the amount the club can afford to pay for the player", key='contract_end')
    else:
        contract_end = "Unspecified"  # If the player is a free agent, no contract end date is required

    # Submit Button
    if st.button("Download Report"):
        datos = {
            "Name of Club": club_name,
            "Position": position,
            "Ideal Age": ideal_age,
            "Competitive Experience": competitive_experience,
            "Preferred Nationality": st.session_state['preferred_nationality'],
            "Style of Play": ", ".join(st.session_state['style_of_play']),
            "Salary Range": st.session_state['salary_range'],
            "Transfer Type": st.session_state['transfer_type'],
            "Immediate Needs": st.session_state['immediate_needs'] or "N/A",
            "Observed Players": st.session_state['jugadores_observados'],
            "Free Agent": free_agent,  # Guardar si es agente libre
            "Contract End Date": contract_end  # Save the contract end date if the player is not a free agent

        }
        guardar_datos(datos)
        st.success("Report successfully submitted and saved.")
        st.session_state['jugadores_observados'] = []
        
        

        # Generar PDF
        pdf_data = generar_pdf(datos)

        # Botón para descargar el PDF
        st.download_button(
            label="Download PDF",
            data=pdf_data,  # 'pdf_data' ahora es un objeto de tipo 'bytes'
            file_name="report.pdf",
            mime="application/pdf"
        )


        

# Formulario en español
else:
    st.subheader("Necesidades de Incorporación de Jugadores")

    # 1. Posiciones a Refuerzar
    nombre_club = st.text_input("Nombre del club", key='nombre_club')
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
            competitive_experience = st.selectbox(
                "Experiencia Competitiva",
                ["Experiencia en 1ª División", "Experiencia en 2ª División", "Potencial joven a desarrollar"],
                key='competitive_experience'
            )
        preferred_nationality = st.multiselect("Nacionalidad Preferente (Opcional)", federaciones_fifa, key='preferred_nationality')

        # Estilo de Juego
        style_of_play = st.multiselect(
            "Seleccione las características clave del estilo de juego",
            ["Técnico", "Físico", "Versátil", "Especializado en desborde", 
             "Capacidad de presión alta", "Construcción desde el fondo", 
             "Visión", "Buen pase largo", "Capacidad en 1 vs 1", 
             "Desmarque y movilidad"],
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
            "Tipología de cncorporación",
            ["Cesión", "Cesión con opción de compra", "Fichaje definitivo"],
            key='transfer_type'
        )

    # 4. Necesidades Inmediatas
    with st.expander("4. Necesidades inmediatas"):
        immediate_needs = st.text_area("¿Existen posiciones que necesitan ser reforzadas de manera urgente? (Describa posición y motivo)", key='immediate_needs')


    #   5. Campo para seleccionar si el jugador es Agente Libre o no
    with st.expander("5. Contrato actual"):
        agente_libre = st.radio(
            "¿Quieren el jugador Agente Libre?", 
            ("Sí", "No"), 
            key='agente_libre'
        )

    # Si no es agente libre, mostrar campo para la fecha de finalización de contrato
    if agente_libre == "No":
        contract_end =  st.text_input("Ingrese lo que puede llegar a pagar el club por el jugador/a", key='contract_end')
    else:
        contract_end = "Sin especificar"  # Si es agente libre, no se requiere fecha de finalización del contrato

    # Botón de Enviar
    if st.button("Descargar Informe"):
        datos = {
            "Nombre del Club": nombre_club,
            "Posiciones": position,
            "Edad Ideal": ideal_age,
            "Experiencia Competitiva": competitive_experience,
            "Nacionalidad Preferente": st.session_state['preferred_nationality'],
            "Estilo de Juego": ", ".join(st.session_state['style_of_play']),
            "Rango Salarial": st.session_state['salary_range'],
            "Tipología de Incorporación": st.session_state['transfer_type'],
            "Necesidad Inmediata": st.session_state['immediate_needs'] or "N/A",
            "Agente Libre": agente_libre,  # Guardar si es agente libre
            "Fecha de Fin de Contrato": contract_end  # Guardar la fecha de fin de contrato si no es agente libre
        }
        guardar_datos(datos)
        st.success("Informe enviado correctamente y guardado.")
 


        # Generar PDF
        pdf_data = generar_pdf(datos)

        # Botón para descargar el PDF
        st.download_button(
            label="Download PDF",
            data=pdf_data,  # 'pdf_data' ahora es un objeto de tipo 'bytes'
            file_name="report.pdf",
            mime="application/pdf"
        )
