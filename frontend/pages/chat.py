# # frontend/pages/chat.py
# import streamlit as st
# from api.chat_api import get_rag_response

# st.set_page_config(page_title="Chat RAG", layout="wide")
# st.title("🤖 Chat con tus Documentos (RAG)")

# # --- Lógica de Streamlit para mantener el historial ---
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # Muestra los mensajes antiguos del historial
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # --- Input del usuario ---
# if prompt := st.chat_input("Haz una pregunta sobre tus documentos..."):
    
#     # 1. Añade y muestra el mensaje del usuario
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     # 2. Llama al backend para obtener la respuesta
#     with st.spinner("Buscando en los documentos y generando respuesta..."):
#         response_data = get_rag_response(prompt)
    
#     # 3. Muestra la respuesta del asistente (si existe)
#     if response_data:
#         respuesta = response_data.get("respuesta", "No se obtuvo respuesta.")
#         fuentes = response_data.get("fuentes", [])

#         # Formatea la respuesta con las fuentes
#         full_response = f"{respuesta}\n\n"
#         if fuentes:
#             full_response += "**Fuentes encontradas:**\n"
#             for i, fuente in enumerate(fuentes):
#                 # Limita el contenido para que no sea muy largo
#                 content_preview = (fuente['content'][:200] + '...') if len(fuente['content']) > 200 else fuente['content']
#                 full_response += f"\n---\n"
#                 full_response += f"**Fuente {i+1}** (Metadata: {fuente['metadata']})\n"
#                 full_response += f"`{content_preview}`\n"
        
#         # Añade la respuesta completa al historial y la muestra
#         st.session_state.messages.append({"role": "assistant", "content": full_response})
#         with st.chat_message("assistant"):
#             st.markdown(full_response)
#     else:
#         # Si response_data es None, el error ya se mostró con st.error()
#         # en la función get_rag_response
#         pass