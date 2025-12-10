# pages/chat.py

import streamlit as st
import sys, os
import base64
from PIL import Image
import sounddevice as sd
import wave
from io import BytesIO
import numpy as np
from streamlit_option_menu import option_menu

# Asegurarse de que el módulo api se puede importar
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api import chat_api

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Chat RAG - Proyecto GRIA CU5",
    page_icon="assets/icono.png",
    layout="wide"
)

# ---- FUNCIONES AUXILIARES ----

def cargar_imagen_base64(ruta):
    with open(ruta, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def img_to_base64(img_path):
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def spinner_icon(container, icon_path="assets/icono_BALIDEARAG.png", size=150):
    icon_base64 = img_to_base64(icon_path)
    container.markdown(f"""
    <div style="display:flex; justify-content:center; align-items:center; margin:20px;">
        <img src="data:image/png;base64,{icon_base64}" style="
            width:{size}px; 
            height:{size}px; 
            animation: spin 1s linear infinite;
        ">
    </div>
    <style>
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    </style>
    """, unsafe_allow_html=True)

def numpy_to_wav_bytes(audio_np, samplerate):
    arr = audio_np
    if arr.ndim > 1:
        arr = arr[:, 0]
    if arr.dtype != np.int16:
        if np.issubdtype(arr.dtype, np.floating):
            arr = (arr * 32767).astype(np.int16)
        else:
            arr = arr.astype(np.int16)
    bio = BytesIO()
    with wave.open(bio, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(arr.tobytes())
    bio.seek(0)
    return bio.getvalue()

def reset_chat():
    st.session_state.chat_history = []

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

    if msg.get("sources"):
        with st.expander("Ver fuentes"):
            for src in msg["sources"]:
                content = src.get("content", "")
                if len(content) > 400:
                    content = content[:400] + "..."
                filename = src.get("metadata", {}).get("source", "Fuente desconocida").split("\\")[-1]
                st.markdown(f"""
                <div style="
                    border-left: 4px solid #4B9CD3;
                    background-color: #f1f5f9;
                    padding: 10px;
                    margin-bottom: 8px;
                    border-radius: 6px;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    font-size: 14px;
                    line-height: 1.4;
                    overflow-wrap: break-word;
                ">
                    <strong><img src='data:image/png;base64,{icon_base64}' class='msg-icon' style='width:16px; height:16px; vertical-align:middle;'> {filename}</strong>
                    <p style='margin-top:5px;'>{content}</p>
                </div>
                """, unsafe_allow_html=True)

# ---- FONDO Y ESTILOS ----
fondo_base64 = cargar_imagen_base64("assets/fondo_degradado_azul.png")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&display=swap" rel="stylesheet">

<style>
.title {
    font-family: 'Poppins', sans-serif;
    font-size: 42px;
    font-weight: 700;
    color: #ffffff;
    margin: 0;
}

.subtitle {
    font-family: 'Poppins', sans-serif;
    font-size: 18px;
    color: #e0e0e0;
    margin: 0;
}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<style>
.stApp {{
    background: url("data:image/png;base64,{fondo_base64}") !important;
    background-size: cover !important;
    background-position: center !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
}}

/* CONTENEDOR DEL CHAT */
.chat-container {{
    max-height: 600px;
    overflow-y: auto;
    padding: 1rem;
    border-radius: 1rem;
    background: "transparent";
    border: 1px solid rgba(200,200,200,0.5);
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}}

/* BURBUJAS SIN GLASS */
.user-msg, .rag-msg {{
    padding: 1rem;
    border-radius: 18px;
    margin-bottom: 0.7rem;
    width: fit-content;
    max-width: 70%;
    display: flex;
    align-items: flex-start;
    border: 1px solid rgba(200,200,200,0.5);
    background: #f5f5f5;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
    animation: fadeIn 0.4s ease-out;
    font-size: 18px;
    color: #000000;
    line-height: 1.5;
    word-break: break-word;
}}

.user-msg {{ margin-left: auto; justify-content: flex-end; }}
.rag-msg {{ margin-right: auto; }}

.msg-icon {{ width: 32px; height: 32px; margin-right: 0.5rem; border-radius: 8px; }}

.role-label {{
    font-size: 0.8rem;
    color: #333333;
    margin-bottom: 0.2rem;
    font-weight: bold;
}}

@keyframes fadeIn {{
    0% {{opacity:0; transform:translateY(8px);}}
    100% {{opacity:1; transform:translateY(0);}}
}}
</style>
""", unsafe_allow_html=True)

# ---- LOGO + TÍTULO ----
logo_base64 = img_to_base64("assets/icono_BALIDEARAG.png")
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

# ---- INICIALIZAR HISTORIAL ----
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

chat_container = st.container()

st.markdown("""
<style>
/* Contenedor general del menú: ocupa todo el ancho */
div.option_menu {
    width: 100% !important;
    display: flex !important;
    justify-content: center !important;
}

/* Cada opción ocupa el mismo ancho */
div.option_menu > div {
    flex: 1 !important;
    text-align: center !important;
}

/* Forzar eliminación del fondo blanco */
div.option_menu, div.option_menu * {
    background-color: transparent !important;
    box-shadow: none !important;
}
</style>
""", unsafe_allow_html=True)


modo = option_menu(
    menu_title=None,
    options=["Texto", "Audio"],
    icons=["pencil", "mic"],
    menu_icon=None,
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {
            "padding": "0px",
            "background-color": "#ffffff",   # Antes azul, ahora blanco
            "border-radius": "8px",
            "border": "none",
            "width": "100%",
            "margin": "0 auto",
            "box-shadow": "none",
        },
        "icon": {
            "color": "#1e3a8a",              # Antes blanco, ahora azul
            "font-size": "16px",
        },
        "nav-link": {
            "font-size": "14px",
            "text-align": "center",
            "margin": "2px",
            "color": "#1e3a8a",              # Antes blanco, ahora azul
            "border-radius": "6px",
            "padding": "6px 10px",
            "--hover-color": "#bfdbfe",      # Hover azul clarito (en vez de azul brillante)
            "transition": "all 0.3s ease",
            "border": "none",
        },
        "nav-link-selected": {
            "background-color": "#1e3a8a",   # Antes blanco, ahora azul
            "color": "#ffffff",              # Antes azul, ahora blanco
            "font-weight": "600",
            "box-shadow": "none",
            "transform": "scale(1.02)",
            "border": "none",
        },
    },
)




# ---- FLUJO DE TEXTO ----
if modo == "Texto":
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Escribe tu pregunta:", "")
        submit_button = st.form_submit_button("Enviar")

    if submit_button and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        spinner_container = st.empty()
        spinner_icon(spinner_container)

        response = chat_api.get_rag_response_text(user_input)
        spinner_container.empty()

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

# ---- FLUJO DE AUDIO ----
elif modo == "Audio":
    st.markdown("### Graba tu pregunta por voz y obtén respuesta del RAG")
    audio_file = st.audio_input("Pulsa para grabar tu pregunta")
    if audio_file is not None:
        st.audio(audio_file)
        if st.button("Enviar audio"):
            st.session_state.chat_history.append({
                "role": "user",
                "content": "*Grabación enviada.*"
            })

            spinner_container = st.empty()
            spinner_icon(spinner_container)

            response = chat_api.get_rag_response_audio(audio_file)
            spinner_container.empty()

            if response:
                transcripcion = response.get("transcripcion", "")
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": response.get("transcripcion", "No pudo transcribir")
                })
                st.session_state.chat_history.append({
                    "role": "rag",
                    "content": response.get("respuesta", "No se obtuvo respuesta"),
                    "sources": response.get("fuentes", [])
                })
            else:
                st.session_state.chat_history.append({
                    "role": "rag",
                    "content": "Error al procesar el audio.",
                    "sources": []
                })

# ---- RENDERIZAR HISTORIAL ----
with chat_container:
    for msg in st.session_state.chat_history:
        render_message(msg)

# ---- BOTÓN REINICIAR ----
st.write("---")
if st.button("Reiniciar conversación"):
    reset_chat()

