# frontend/api/chat_api.py
import requests
import streamlit as st
import mimetypes
from io import BytesIO
from pathlib import Path

# Esta es la URL de tu backend FastAPI que está corriendo
BACKEND_URL = "http://127.0.0.1:8000/rag/chat/text"
BACKEND_AUDIO_URL = "http://127.0.0.1:8000/rag/chat/audio"

def get_rag_response_text(message: str):
    payload = {"message": message}
    
    try:
        # Trae respuesta y fuentes del backend
        response = requests.post(BACKEND_URL, json=payload)
        
        # Lanza un error si el backend devuelve un código de error (ej. 500)
        response.raise_for_status() 
        
        return response.json()

    except requests.exceptions.ConnectionError:
        st.error("Error de conexión: No se pudo conectar al backend.")
        st.error("¿Estás seguro de que el backend (FastAPI) está en marcha en http://127.0.0.1:8000?")
        return None
    
    except requests.exceptions.HTTPError as e:
        # Muestra el error específico que devolvió el backend
        st.error(f"Error en la API (Backend): {e.response.text}")
        return None
    
    except Exception as e:
        st.error(f"Ocurrió un error inesperado al llamar a la API: {e}")
        return None
    
def get_rag_response_audio(audio_file, filename: str | None = None):
    try:
        if isinstance(audio_file, (bytes, bytearray)):
            file_obj = BytesIO(audio_file)
            filename = filename or "audio.wav"
        elif hasattr(audio_file, "read"):
            file_obj = audio_file
            filename = filename or getattr(file_obj, "name", "audio.wav")
        else:
            p = Path(audio_file)
            if not p.exists():
                st.error(f"Archivo de audio no encontrado: {p}")
                return None
            file_obj = open(p, "rb")
            filename = filename or p.name

        try:
            file_obj.seek(0)
        except Exception:
            pass

        mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        
        files = {
            "audio": (filename, file_obj, mime)
        }


        response = requests.post(BACKEND_AUDIO_URL, files=files)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.ConnectionError:
        st.error("Error de conexión: No se pudo conectar al backend.")
        st.error("¿Estás seguro de que el backend (FastAPI) está en marcha en http://127.0.0.1:8000?")
        return None
    
    except requests.exceptions.HTTPError as e:
        # Muestra el error específico que devolvió el backend
        st.error(f"Error en la API (Backend): {e.response.text}")
        return None
    
    except Exception as e:
        st.error(f"Ocurrió un error inesperado al llamar a la API: {e}")
        return None