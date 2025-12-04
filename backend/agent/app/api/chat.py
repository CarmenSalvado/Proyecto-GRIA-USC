from fastapi import APIRouter, File, UploadFile, HTTPException
from app.service.rag_service import RAG # Importamos la instancia de ragService
from pydantic import BaseModel
import uvicorn
from faster_whisper import WhisperModel
from app.service.rag_service import RAG # Importamos la instancia de ragService
from app.service.metrics_service import metrics_tracker
from time import perf_counter

#Modelos Pydantic para declarar los tipos de request y response
class ChatRequest(BaseModel):
    """El JSON con la pregunta del usuario"""
    message: str
class FuenteResponse(BaseModel):
    """El JSON en el que se espera recibir cada chunk fuente"""
    content: str
    metadata: dict
class ChatResponse(BaseModel):
    """El JSON con la respuesta y fuentes"""
    respuesta: str
    fuentes: list[FuenteResponse]

#Router para texto y audio

router = APIRouter(
    prefix="/rag",
    tags=["rag"],
    responses={404: {"error": "Not found"}},
)


@router.post("/chat/text", response_model=ChatResponse) #/rag   +   /chat/text   →   /rag/chat/text
async def get_response_text(request: ChatRequest):
    
    print("POST /rag/chat/text - Pregunta:", request.message)

    #Llamamos al servicio RAG para obtener la respuesta
    response = RAG.get_rag_response(request.message)
    
    #Si falla
    if not response["exito"]:
        raise HTTPException(status_code=500, detail=response["error"])

    respuesta_y_docs = ChatResponse(

        respuesta = response["respuesta"],
        fuentes = response["fuentes"]

    )

    return respuesta_y_docs



@router.post("/chat/audio")
async def get_response_audio(audio: UploadFile = File(...)):
    import traceback

    try:
        print("➡ Nombre:", audio.filename)
        print("➡ Tipo:", audio.content_type)

        raw = await audio.read()
        print("➡ Tamaño recibido:", len(raw))

        # Guardar original
        import tempfile, os, subprocess
        ext = os.path.splitext(audio.filename)[1] or ".bin"
        tmp_input = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        tmp_input.write(raw)
        tmp_input.close()
        print("➡ Guardado original en:", tmp_input.name)

        # Convertir a WAV (si falla, vemos el error exacto)
        tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp_wav.close()

        cmd = ["ffmpeg", "-y", "-i", tmp_input.name, "-ar", "16000", "-ac", "1", tmp_wav.name]
        print("➡ Ejecutando:", " ".join(cmd))

        conv = subprocess.run(cmd, capture_output=True, text=True)
        print("➡ FFMPEG stdout:", conv.stdout)
        print("➡ FFMPEG stderr:", conv.stderr)

        if conv.returncode != 0:
            raise Exception("FFMPEG explotó")

        print("➡ WAV creado en:", tmp_wav.name)

        # WHISPER
        asr = WhisperModel("small", device="cpu")
       
        print("Transcribiendo...")
        start_asr = perf_counter()
        segments, info = asr.transcribe(tmp_wav.name)
        asr_time = perf_counter() - start_asr
        metrics_tracker.registrar_asr(asr_time)
        segments, info = asr.transcribe(tmp_wav.name)
        transcripcion = " ".join([seg.text for seg in segments]).strip()
        print("He escuchado:", transcripcion)
        print("➡ Transcripción:", transcripcion)

        # RAG
        response = RAG.get_rag_response(transcripcion)
        print("➡ RAG response:", response)

        if not response["exito"]:
            raise Exception("RAG explotó")

        return {
            "transcripcion": transcripcion,
            "respuesta": response["respuesta"],
            "fuentes": response["fuentes"]
        }

    except Exception as e:
        print("ERROR EN BACKEND:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

