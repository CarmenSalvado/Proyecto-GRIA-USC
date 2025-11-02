# frontend/api/chat_api.py
import requests
import streamlit as st

# Esta es la URL de tu backend FastAPI que está corriendo
BACKEND_URL = "http://127.0.0.1:8000/rag/chat/text"

def get_rag_response(message: str):
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