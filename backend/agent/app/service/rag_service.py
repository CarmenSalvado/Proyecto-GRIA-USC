from __future__ import annotations

import os
from time import perf_counter
from typing import Dict, List, Optional

from datasets import Dataset
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import Ollama
from langchain.vectorstores import Chroma
from ragas import evaluate, aevaluate
from ragas.metrics import answer_relevancy, context_precision, context_recall
import asyncio
import concurrent.futures

from app.service.metrics_service import metrics_tracker

class ragService:
    def __init__(self):
        """Inicializa el servicio RAG con embeddings, vectorstore y chain"""
        # Embeddings y Vectorstore
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        self.vectorstore = Chroma(
            persist_directory = "./app/service/chroma_db",
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
        metrics_tracker.registrar_peticion()
        try:
            # Embeddings + busqueda
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

            return {
                "exito": True,
                "respuesta": respuesta,
                "fuentes": [
                    {
                        #Devuelve 500 caracteres de cada chunk, si tiene mas pone al final "..."
                        "content": doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content,
                        "metadata": doc.metadata
                    }
                    # Que devuelva un diccionario por cada documento
                    for doc in source_documents
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

    # async def _calcular_ragas(self, question: str, answer: str, docs: List) -> Dict[str, float]:
    #     """Calcula métricas RAGAS básicas."""
    #     try:
    #         dataset = Dataset.from_list(
    #             [
    #                 {
    #                     "question": question,
    #                     "answer": answer,
    #                     "contexts": [doc.page_content for doc in docs],
    #                     # Sin ground truth explicito: usamos el texto concatenado como referencia
    #                     "ground_truth": "\n\n".join(doc.page_content for doc in docs),
    #                 }
    #             ]
    #         )
    #         resultados = await aevaluate(
    #             dataset=dataset,
    #             metrics=[answer_relevancy, context_precision, context_recall],
    #             llm=self.llm,
    #             embeddings=self.embeddings,
    #             show_progress=False,
    #             raise_exceptions=False            )
    #         # _repr_dict contiene la media para cada métrica
    #         return getattr(resultados, "_repr_dict", {})
    #     except Exception as ragas_error:
    #         print(f"[METRICAS] No se pudo calcular RAGAS: {ragas_error}")
    #         return {}


    async def _calcular_ragas_async(self, question: str, answer: str, docs: List):
        dataset = Dataset.from_list([
            {
                "question": question,
                "answer": answer,
                "contexts": [doc.page_content for doc in docs],
                "ground_truth": "\n\n".join(doc.page_content for doc in docs),
            }
        ])

        resultados = await aevaluate(
            dataset=dataset,
            metrics=[answer_relevancy, context_precision, context_recall],
            llm=self.llm,
            embeddings=self.embeddings,
            raise_exceptions=False,
        )

        return dict(resultados)

    def _calcular_ragas(self, question, answer, docs):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(
            self._calcular_ragas_async(question, answer, docs)
        )


RAG = ragService()
