from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import Ollama
import os

class ragService:
    def __init__(self):
        """Inicializa el servicio RAG con embeddings, vectorstore y chain"""
        # Embeddings y Vectorstore
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        self.vectorstore = Chroma(
            persist_directory = ".\\app\\service\\chroma_db",
            embedding_function=self.embeddings
        )
        print("-------------------------"*10)
        print("El directorio actual es:", os.getcwd())
        print("-------------------------"*10)
        print("Vectorstore cargado para RAG", len(self.vectorstore))

        
        # El buscador trae los 3 chunks mas relevantes
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
        self.llm = Ollama(model="gemma3:4b")

        self.vectorstore.persist()
        
        
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
            docs_test = self.vectorstore.similarity_search(question, k=3)
            print("CONTENIDO:", [d.page_content[:100] for d in docs_test])
            cadena = self.qa_chain({"query": question})
            print("Soy la pregunta:", question)
            print("Soy la respuesta:", cadena["result"])
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
RAG = ragService()