import streamlit as st
from PIL import Image  # para abrir imágenes



# CONFIGURACIÓN DEL TEMA EN .streamlit/config.toml  <---------------- IMPORTANTE!!!!

#[theme]
#primaryColor="#e86969"
#backgroundColor="#b0ccf3"
#secondaryBackgroundColor="#f7f5f5"
#textColor="#273179"


# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Proyecto CU5 GrIA - Balidea",
    page_icon="assets/icono_BALIDEARAG.png",
    layout="wide"
)

# PERSONALIZACIÓN DE ESTILOS
st.markdown(
    """
    <style>
    /* Fondo general y texto */
    .main {
        background‑color: #003366; /* azul marino aproximado */
        color: #003366;            /* texto azul marino */
        font-family: Arial, sans-serif;
    }

    /* Título principal */
    .title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        color: #003366; /* azul marino */
    }

    /* Subtítulo */
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #000000; /* negro */
        margin-bottom: 2rem;
    }

    /* Tarjetas de opciones */
    .card {
        background-color: #001F3F; /* azul marino bonito */
        color: #ffffff;            /* texto blanco */
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }

    .card:hover {
        transform: scale(1.02);
        box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
    }

    /* Botones dentro de las tarjetas */
    button[kind="primary"] {
        background-color: #003366; /* azul oscuro */
        color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# LOGO BALIDEA Y TÍTULO
col_logo, col_space, col_text = st.columns([1, 0.2, 3])
with col_logo:
    try:
        logo = Image.open("assets/balidea_logo.png")
        st.image(logo, width=500)
    except:
        st.write("")  # si no existe el logo, no pasa nada

with col_text:
    st.markdown("<h1 class='title'>HOME - Balidea</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>¡Bienvenido al sistema RAG para asistencia inteligente en gestión documental!</p>", unsafe_allow_html=True)

st.write("---")

# OPCIONES TARJETAS DE CHAT RAG Y INTRODUCCIÓN
col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Nuestros Usuarios")
    st.write("Conoce los fundamentos del proyecto, su arquitectura y objetivos.")
    if st.button("Ir a Intro", key="intro_btn"):
        st.switch_page("pages/intro.py")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Chat RAG")
    st.write("Interactúa con el modelo RAG. Haz preguntas y obtén respuestas basadas en documentación interna.")
    if st.button("Abrir Chat", key="chat_btn"):
        st.switch_page("pages/chat.py")
    st.markdown("</div>", unsafe_allow_html=True)

st.write("---")

# PIE DE PÁGINA
st.markdown(
    """
    <div style='text-align: center; color: #b0ccf3"; margin-top: 2rem;'>
        Desarrollado por el equipo CU5 · Balidea © 2025
    </div>
    """,
    unsafe_allow_html=True
)
