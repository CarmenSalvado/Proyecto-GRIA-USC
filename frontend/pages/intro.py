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
st.markdown("<p class='subtitle'>Conoce la arquitectura, objetivos y alcance del sistema RAG</p>", unsafe_allow_html=True)

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
st.subheader("Arquitectura del Sistema")
st.write("""
El sistema está compuesto por varias capas:
1. **Frontend (Streamlit)**: Interfaz de usuario para consultas y visualización.
2. **API (FastAPI)**: Gestiona las solicitudes entre el frontend y el backend RAG.
3. **Backend RAG**: Motor de búsqueda y generación de respuestas basado en documentos internos.
4. **Assets**: Recursos estáticos como logos, imágenes y estilos.
""")

# Diagrama de ejemplo (si tienes uno en assets)
try:
    diagram = Image.open("assets/arquitectura.png")
    st.image(diagram, caption="Diagrama de Arquitectura", use_column_width=True)
except:
    st.write("Imagen de arquitectura no disponible.")

st.write("---")

# SECCIÓN: DOCUMENTACIÓN Y REFERENCIAS
st.subheader("Documentación y Referencias")
st.write("""
- Este proyecto utiliza técnicas de RAG para mejorar la precisión de respuestas.
- Basado en FastAPI para la lógica de backend.
- Frontend desarrollado en Streamlit para facilidad de despliegue y pruebas internas.
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
