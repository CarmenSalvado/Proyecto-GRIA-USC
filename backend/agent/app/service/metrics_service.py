from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class _Latencia: #Para gestionar las distintas metricas
    total: float = 0.0 #Suma de todas las latencias registradas
    count: int = 0 #Numero de muestras registradas
    ultima: Optional[float] = None #Ultimo valor registrado

    def registrar(self, valor: float) -> None: 
        self.total += valor 
        self.count += 1
        self.ultima = valor

    @property
    def media(self) -> Optional[float]: #Devuelve la media si se han tomado muestras
        if self.count == 0:
            return None
        return self.total / self.count


class MetricsTracker:

    def __init__(self) -> None:
        self.total_peticiones = 0
        self.fallos = 0

        self.latencia_asr = _Latencia()
        self.latencia_embeddings = _Latencia()
        self.latencia_llm = _Latencia()

        #Para el coste de tokens entrada/salida
        self.ultimo_token_usage: Dict[str, Optional[int]] = {}
        self.ultima_ragas: Dict[str, float] = {}

    def registrar_peticion(self) -> None:
        self.total_peticiones += 1

    def registrar_fallo(self) -> None:
        self.fallos += 1

    #Latencias
    def registrar_asr(self, segundos: float) -> None:
        self.latencia_asr.registrar(segundos)

    def registrar_embeddings(self, segundos: float) -> None:
        self.latencia_embeddings.registrar(segundos)

    def registrar_llm(self, segundos: float) -> None:
        self.latencia_llm.registrar(segundos)
    
    #Coste de tokens 
    def registrar_tokens(self, prompt_tokens: Optional[int], completion_tokens: Optional[int], total_tokens: Optional[int]) -> None:
        self.ultimo_token_usage = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
        }

    #Calidad de la recuperacion con RAGAS, Answer Relevance, Context Precision/Recall
    def registrar_ragas(self, scores: Dict[str, float]) -> None:
        self.ultima_ragas = scores

    #Para la salida
    def dump(self, *, question: Optional[str] = None, retrieval_time: Optional[float] = None) -> None:
        print("\n================ METRICAS RAG =================")
        if question:
            print(f"Pregunta: {question}")
        print(f"Peticiones totales: {self.total_peticiones} | Fallos acumulados: {self.fallos}")

        if self.latencia_asr.count:
            print(
                f"ASR -> ultimo: {self.latencia_asr.ultima:.3f}s | media: {self.latencia_asr.media:.3f}s "
                f"({self.latencia_asr.count} muestras)"
            )
        if self.latencia_embeddings.count:
            print(
                f"Embeddings -> ultimo: {self.latencia_embeddings.ultima:.3f}s | media: {self.latencia_embeddings.media:.3f}s "
                f"({self.latencia_embeddings.count} muestras)"
            )
        if retrieval_time is not None:
            print(f"Recuperacion/vectorstore -> ultimo: {retrieval_time:.3f}s")
        if self.latencia_llm.count:
            print(
                f"LLM Ollama -> ultimo: {self.latencia_llm.ultima:.3f}s | media: {self.latencia_llm.media:.3f}s "
                f"({self.latencia_llm.count} muestras)"
            )

        if self.ultimo_token_usage:
            print(
                "Tokens (prompt/completion/total): "
                f"{self.ultimo_token_usage.get('prompt_tokens')} / "
                f"{self.ultimo_token_usage.get('completion_tokens')} / "
                f"{self.ultimo_token_usage.get('total_tokens')}"
            )

        if self.ultima_ragas:
            salida = ", ".join(
                f"{k}: {v:.3f}" for k, v in self.ultima_ragas.items() if isinstance(v, (float, int))
            )
            print(f"RAGAS -> {salida}")

        print("================================================\n")


metrics_tracker = MetricsTracker()
