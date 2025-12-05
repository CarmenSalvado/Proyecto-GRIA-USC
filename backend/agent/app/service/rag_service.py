from __future__ import annotations
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import Ollama
from typing import Dict, List, Optional

from datasets import Dataset
import time
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from time import perf_counter
from ragas import aevaluate
from ragas.metrics import answer_relevancy, context_precision, context_recall
import asyncio
from app.service.metrics_service import metrics_tracker
from langchain.prompts import PromptTemplate

import nest_asyncio


nest_asyncio.apply()
class ragService:
    def __init__(self):
        """Inicializa el servicio RAG con embeddings, vectorstore y chain"""
        # Embeddings y Vectorstore
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        self.vectorstore = Chroma(
            #persist_directory = ".\\app\\service\\chroma_db", #windows
            persist_directory = "./app/service/chroma_db", #linux
            embedding_function=self.embeddings
        )

        if self.vectorstore is None or len(self.vectorstore) == 0:
            print(f"[RAG-ALERT] EMBEDDING_ERROR (vectorstore)")
        
        print("-------------------------"*10)
        print("Vectorstore cargado para RAG", len(self.vectorstore))

        
        # El buscador trae los 3 chunks mas relevantes
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
        if self.retriever is None:
            print(f"[RAG-ALERT] EMBEDDING_ERROR (retriever)")
        self.llm = Ollama(model="gemma3:4b")

        self.vectorstore.persist()
        
        self.template = """Eres un asistente útil que responde SIEMPRE en español NATURAL/FORMAL y de forma concisa.
                    Usa solo la información del contexto; si falta información, admite que no la tienes.
                    Contexto:
                    {context}

                    Pregunta:
                    {question}

                    Respuesta (en español):"""
        prompt = PromptTemplate(template=self.template, input_variables=["context", "question"])

        
        # Chain de RAG con Ollama
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff", # Mete los 3 chunks en el prompt junto a la pregunta del usuario
            retriever=self.retriever, # Busca los chunks
            return_source_documents=True, # Importante para obtener evidencia
            chain_type_kwargs={"prompt": prompt} # Le pasamos el prompt para que hable en español y no alucine
        )
       


    def get_rag_response(self, question: str):
        """Procesa una pregunta y devuelve respuesta con fuentes"""
        metrics_tracker.registrar_peticion()
        try:
            start_embeddings = perf_counter()
            query_embedding = self.embeddings.embed_query(question)
            embedding_time = perf_counter() - start_embeddings
            metrics_tracker.registrar_embeddings(embedding_time)

            start_search = perf_counter()
            source_documents = self.vectorstore.similarity_search_by_vector(query_embedding, k=3)
            retrieval_time = perf_counter() - start_search

            # Construimos el prompt con los mismos templates que la chain por defecto
            combine_chain = self.qa_chain.combine_documents_chain
            prompt_inputs = combine_chain._get_inputs(source_documents, question=question)
            prompt_value = combine_chain.llm_chain.prompt.format_prompt(**prompt_inputs)

            # Llamada al LLM para poder capturar generacion y tokens
            start_llm = perf_counter()
            llm_result = combine_chain.llm_chain.llm.generate_prompt([prompt_value])
            llm_time = perf_counter() - start_llm
            metrics_tracker.registrar_llm(llm_time)

            generation = llm_result.generations[0][0]
            token_usage = self._extraer_tokens(generation.generation_info)
            metrics_tracker.registrar_tokens(**token_usage)

            respuesta = generation.text
            ragas_scores = self._calcular_ragas(question, respuesta, source_documents)
            if ragas_scores:
                metrics_tracker.registrar_ragas(ragas_scores)

            metrics_tracker.dump(question=question, retrieval_time=retrieval_time)
            try:
                docs_test = self.vectorstore.similarity_search(question, k=3)
            except Exception as e:
                metrics_tracker.registrar_fallo()
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
                metrics_tracker.registrar_fallo()
                return {"exito": False, "error": "Error en el retriever o embeddings"}
            if len(cadena) == 0:
                metrics_tracker.registrar_fallo()
                print(f"[RAG-ALERT] EMBEDDING_ERROR (la cadena esta vacia)")
            

            print("Soy la pregunta:", question)
            print("Soy la respuesta:", cadena["result"])
            #########
            print("🔍 QUERY:", question)
            docs_test = self.vectorstore.similarity_search(question, k=5)
            for i, d in enumerate(docs_test):
                print(f"TOP {i+1}: sim={cosine_similarity([self.embeddings.embed_query(question)], [self.embeddings.embed_documents([d.page_content])[0]])[0][0]:.3f}")
                print(d.page_content[:200], "\n")


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
            metrics_tracker.registrar_fallo()
            return {
                "exito": False,
                "error": str(e)
            }
        
    def _extraer_tokens(self, generation_info: Optional[Dict]) -> Dict[str, Optional[int]]:
        """Extrae tokens de la respuesta de Ollama."""
        if not generation_info:
            return {"prompt_tokens": None, "completion_tokens": None, "total_tokens": None}

        prompt_tokens = generation_info.get("prompt_eval_count") or generation_info.get("prompt_tokens")
        completion_tokens = generation_info.get("eval_count") or generation_info.get("completion_tokens")
        total_tokens = generation_info.get("total_tokens")
        if total_tokens is None and prompt_tokens is not None and completion_tokens is not None:
            total_tokens = prompt_tokens + completion_tokens

        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
        }

    async def _calcular_ragas_async(self, question: str, answer: str, docs: List):
        """Versión asíncrona, protegida con timeout."""
        try:
            dataset = Dataset.from_list([
                {
                    "question": question,
                    "answer": answer,
                    "contexts": [doc.page_content for doc in docs],
                    "ground_truth": "\n\n".join(doc.page_content for doc in docs),
                }
            ])

            # Timeout duro para que no se quede colgado
            resultados = await asyncio.wait_for(
                aevaluate(
                    dataset=dataset,
                    metrics=[answer_relevancy, context_precision, context_recall],
                    llm=self.llm, #None
                    embeddings=self.embeddings,
                    raise_exceptions=False,
                ),
                timeout=300
            )

            # En algunas versiones de ragas, resultados tiene _repr_dict
            if hasattr(resultados, "_repr_dict"):
                return dict(getattr(resultados, "_repr_dict"))
            # En otras, se puede castear directamente a dict
            try:
                return dict(resultados)
            except TypeError:
                return {}
        except asyncio.TimeoutError:
            print("[METRICAS] No se pudo calcular RAGAS: timeout")
            return {}
        except Exception as ragas_error:
            print(f"[METRICAS] No se pudo calcular RAGAS: {ragas_error}")
            return {}


    def _calcular_ragas(self, question, answer, docs):
        """Wrapper síncrono: nunca debe romper la petición principal."""
        try:
            loop = asyncio.get_event_loop()

            # Si el loop ya esta ocupado! → usamos create_task + awaitable Future
            if loop.is_running():
                future = asyncio.ensure_future(
                    self._calcular_ragas_async(question, answer, docs)
                )
                # Bloqueo!
                return loop.run_until_complete(asyncio.gather(future))[0]

            # si no esta ocupado
            return loop.run_until_complete(
                self._calcular_ragas_async(question, answer, docs)
            )

        except Exception as e:
            print(f"[METRICAS] Error al ejecutar loop de RAGAS: {e}")
            return {}
        
RAG = ragService()
