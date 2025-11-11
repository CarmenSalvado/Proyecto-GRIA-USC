from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import Ollama

class ragService:
    def __init__(self):
        """Inicializa el servicio RAG con embeddings, vectorstore y chain"""
        # Embeddings y Vectorstore
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        self.vectorstore = Chroma(
            persist_directory="./chroma_db",
            embedding_function=self.embeddings
        )
        
        # El buscador trae los 3 chunks mas relevantes
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
        self.llm = Ollama(model="gemma3:4b")
        
        # Chain de RAG con Ollama
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff", # Mete los 3 chunks en el prompt junto a la pregunta del usuario
            retriever=self.retriever, # Busca los chunks
            return_source_documents=True # Importante para obtener evidencia
        )

    def get_rag_response(self, question: str):
        """Procesa una pregunta y devuelve respuesta con fuentes"""
        try:
            cadena = self.qa_chain({"query": question})
            return {
                "exito": True,
                "respuesta": cadena["result"],
                "fuentes": [
                    {
                        #Devuelve 500 caracteres de cada chunk, si tiene mas pone al final "..."
                        "content": doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content,
                        "metadata": doc.metadata
                    }
                    # Que devuelva un diccionario por cada documento
                    for doc in cadena['source_documents']
                    ]
            }
        except Exception as e:
            return {
                "exito": False,
                "error": str(e)
            }
