# pages/intro.py
import streamlit as st
from PIL import Image

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Introducción - Proyecto GRIA CU5",
    page_icon="assets/icono.png",
    layout="wide"
)

# TÍTULO
st.markdown("<h1 class='title'>Introducción al Proyecto CU5</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Conoce los objetivos y la arquitectura del sistema RAG</p>", unsafe_allow_html=True)

st.write("---")

# SECCIÓN: OBJETIVOS DEL PROYECTO
st.subheader("Objetivos del Proyecto")
st.write("""
- Implementar un sistema RAG (Retrieval-Augmented Generation) para consultas internas.
- Facilitar la búsqueda y asistencia basada en documentación corporativa.
- Proporcionar una interfaz intuitiva para que los empleados interactúen con el sistema.
- Garantizar trazabilidad y transparencia de las respuestas generadas.
""")

# SECCIÓN: ARQUITECTURA DEL SISTEMA
# SECCIÓN: ARQUITECTURA DEL SISTEMA
st.subheader("Arquitectura del Sistema")
st.write("""
El sistema está compuesto por varias capas interconectadas:

1. **Frontend (Streamlit)**:  
   - Interfaz de usuario donde se realizan consultas y se visualizan respuestas.  
   - Envía las preguntas del usuario a la API y muestra resultados de manera amigable.  
   - Dependencias clave: `streamlit`, configuración de temas en `.streamlit/config.toml`.

2. **API (FastAPI)**:  
   - Actúa como intermediario entre el frontend y el backend RAG.  
   - Expone endpoints como `/rag/chat/text` y `/rag/chat/audio`.  
   - Valida las solicitudes y formatea las respuestas para el frontend.  
   - Maneja errores comunes (404, 500, problemas de CORS) y los comunica al usuario.

3. **Backend RAG (Retriever-Augmented Generation)**:  
   - Se encarga de buscar información relevante en documentos internos y generar respuestas usando LLM (p. ej., Ollama).  
   - Componentes principales:
     - **Vectorstore**: Almacena representaciones vectoriales de documentos para búsqueda rápida.
     - **LLM (Ollama)**: Genera texto basado en la información recuperada.  
     - **RAG Chain**: Combina la recuperación de información con la generación de texto.
   - Persistencia de documentos y configuración de la RAG para asegurar consistencia en las respuestas.

4. **Assets**:  
   - Contiene recursos estáticos como logos, imágenes, estilos CSS o JSON de configuración visual.
   - Permite mantener coherencia visual y branding a través del frontend.

**Notas adicionales importantes**:  
- Asegurarse de que Ollama esté activo y que el puerto configurado en la API coincida con el daemon.  
- Revisar que dependencias y versiones de `langchain`, `langchain-ollama` y `ollama` sean compatibles para evitar errores de importación o llamadas al LLM.  
""")

st.write("---")
st.markdown(
    """
    <div style='text-align: center; color: #6c757d; margin-top: 2rem;'>
        Desarrollado por el equipo CU5 · Balidea © 2025
    </div>
    """,
    unsafe_allow_html=True
)
