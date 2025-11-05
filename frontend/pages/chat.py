# pages/chat.py
import streamlit as st
import sys, os
from PIL import Image
import base64

# Asegurarse de que el módulo api se puede importar
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api import chat_api

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Chat RAG - Proyecto GRIA CU5",
    page_icon="assets/icono.png",
    layout="wide"
)

# CSS para estilo avanzado tipo Slack/Teams
st.markdown(
    """
    <style>
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 1rem;
        border-radius: 1rem;
        background-color: #f7f9fb;
    }
    .user-msg, .rag-msg {
        padding: 1rem;
        border-radius: 1rem;
        margin-bottom: 0.7rem;
        width: fit-content;
        max-width: 70%;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
        display: flex;
        align-items: flex-start;
    }
    .user-msg {
        background-color: #D0E7FF;
        margin-left: auto;
        justify-content: flex-end;
    }
    .rag-msg {
        background-color: #F0F0F0;
        margin-right: auto;
        justify-content: flex-start;
    }
    .msg-icon {
        width: 32px;
        height: 32px;
        margin-right: 0.5rem;
    }
    .source-box {
        background-color: #ffffff;
        border-left: 4px solid #002B49;
        padding: 0.5rem;
        margin-top: 0.3rem;
        margin-bottom: 0.3rem;
        font-size: 0.9rem;
        border-radius: 0.5rem;
    }
    .role-label {
        font-size: 0.8rem;
        color: #555;
        margin-bottom: 0.2rem;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

#FUNCIÓN PARA PODER PONER EL LOGO EN LOS MENSAJES
def img_to_base64(img_path):
    with open(img_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Icono + Título
logo_path = "assets/icono_BALIDEARAG.png"
logo_base64 = img_to_base64(logo_path)

# Mostrar logo + título + subtítulo
st.markdown(f"""
<div style="display: flex; align-items: center; margin-bottom: 10px;">
    <img src="data:image/png;base64,{logo_base64}" style="width:50px; height:50px; margin-right:15px;">
    <div>
        <h1 class='title'>Chat RAG - Asistencia Inteligente</h1>
        <p class='subtitle'>Haz preguntas y obtén respuestas basadas en documentos internos.</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.write("---")


# Inicializar historial
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Función reiniciar chat
def reset_chat():
    st.session_state.chat_history = []

# Contenedor principal del chat
chat_container = st.container()
import base64

# Función mensajes 
def render_message(msg):
    if msg["role"] == "user":
        icon_base64 = img_to_base64("assets/icono_USUARIO.png")
        content_html = f"""
        <div class='user-msg'>
            <img src='data:image/png;base64,{icon_base64}' class='msg-icon'>
            <div>
                <div class='role-label'>Tú</div>
                {msg['content']}
            </div>
        </div>
        """
        st.markdown(content_html, unsafe_allow_html=True)
    else:
        icon_base64 = img_to_base64("assets/icono_BALIDEARAG.png")
        content_html = f"""
        <div class='rag-msg'>
            <img src='data:image/png;base64,{icon_base64}' class='msg-icon'>
            <div>
                <div class='role-label'>BALIDEA RAG</div>
                {msg['content']}
            </div>
        </div>
        """
        st.markdown(content_html, unsafe_allow_html=True)
        # Fuentes en desplegable
        if msg.get("sources"):
            with st.expander("Ver fuentes"):
                for src in msg["sources"]:
                    st.markdown(f"<div class='source-box'>📄 {src}</div>", unsafe_allow_html=True)



# Formulario de entradastreamlit run app.py
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Escribe tu pregunta:", "")
    submit_button = st.form_submit_button("Enviar")

# Procesar envío
if submit_button and user_input:
    # Guardar mensaje de usuario
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Llamar API
    response = chat_api.get_rag_response(user_input)
    
    if response:
        st.session_state.chat_history.append({
            "role": "rag",
            "content": response.get("respuesta", "No se obtuvo respuesta"),
            "sources": response.get("fuentes", [])
        })
    else:
        st.session_state.chat_history.append({
            "role": "rag",
            "content": "Ocurrió un error al obtener la respuesta.",
            "sources": []
        })

# Renderizar todo el historial **después** de procesar la entrada
with chat_container:
    for msg in st.session_state.chat_history:
        render_message(msg)

# Botón reiniciar chat
st.write("---")
if st.button("Reiniciar conversación"):
    reset_chat()
