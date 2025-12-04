from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import Ollama
import os
import time
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.service.tts_service import synthesize_with_piper

class ragService:
    def __init__(self):
        """Inicializa el servicio RAG con embeddings, vectorstore y chain"""
        # Embeddings y Vectorstore
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        
        self.vectorstore = Chroma(
            persist_directory = ".\\app\\service\\chroma_db",
            embedding_function=self.embeddings
        )

        if self.vectorstore is None or len(self.vectorstore) == 0:
            print(f"[RAG-ALERT] EMBEDDING_ERROR (vectorstore)")

        print("-------------------------"*10)
        print("El directorio actual es:", os.getcwd())
        print("-------------------------"*10)
        print("Vectorstore cargado para RAG", len(self.vectorstore))

        
        # El buscador trae los 3 chunks mas relevantes
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})

        if self.retriever is None:
            print(f"[RAG-ALERT] EMBEDDING_ERROR (retriever)")


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
            try:
                docs_test = self.vectorstore.similarity_search(question, k=3)
            except Exception as e:
                return {"exito": False, "error": "Error generando embeddings del query"}
        
            if len(docs_test) == 0:
                print("No hay similaridad")
            
            print("CONTENIDO:", [d.page_content[:100] for d in docs_test])

            try:
                # Embedding del query
                query_vec = self.embeddings.embed_query(question)
                
                # Embeddings de docs recuperados
                doc_vecs = [self.embeddings.embed_query(d.page_content) for d in docs_test]
    
                # Similitudes
                sims = cosine_similarity([query_vec], doc_vecs)[0]
                
                if np.mean(sims) < 0.3:
                    print("Recuperación pobre",avg_similarity=float(np.mean(sims)))
            except Exception as e:
                print("Error al comprobar las similitudes de documentos y pregunta")


            try:
                start = time.time()
                cadena = self.qa_chain({"query": question})
                latency = time.time() - start

                if latency > 10: 
                    print("Se ha pasado el tiempo establecido para la LLM")

            except Exception as e:
                return {"exito": False, "error": "Error en el retriever o embeddings"}
            if len(cadena) == 0:
                print(f"[RAG-ALERT] EMBEDDING_ERROR (la cadena esta vacia)")
            
            print("Las keys de la cadena son:", cadena.keys())
            print("Soy la pregunta:", question)
            print("Soy la respuesta:", cadena["result"])

            try:
                answer = cadena["result"]
                # Unir el contexto completo en un solo string
                full_context = " ".join([doc.page_content for doc in cadena["source_documents"]])
    
                answer_vec = self.embeddings.embed_query(answer)
                context_vec = self.embeddings.embed_query(full_context)
                
                sim = cosine_similarity([answer_vec], [context_vec])[0][0]
                
                if sim < 0.20:
                    print(f"Riesgo de estar alucinando hay menos de un 20% de similitud entre la respuesta y el contexto {float(sim)}%")
            except Exception as e:
                print("Error al comprobar las alucinaciones ",str(e))

            
            audio_out = synthesize_with_piper(cadena["result"])


            return {
                "exito": True,
                "respuesta": cadena["result"],
                "audio": audio_out,
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