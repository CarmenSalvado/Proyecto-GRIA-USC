from fastapi import APIRouter, File, UploadFile, HTTPException
from app.service.rag_service import RAG # Importamos la instancia de ragService
from pydantic import BaseModel
import uvicorn

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

    # Llamamos al servicio RAG para obtener la respuesta
    response = RAG.get_rag_response(request.message)
    
    # Si falla
    if not response["exito"]:
        raise HTTPException(status_code=500, detail=response["error"])

    respuesta_y_docs = ChatResponse(

        respuesta = response["respuesta"],
        fuentes = response["fuentes"]

    )

    return respuesta_y_docs


'''
@router.post("/chat/audio")
async def get_response_audio(audio: UploadFile = File(...)):
    print("POST /rag/chat/audio")
    import subprocess, tempfile, os

    # Guardar archivo original (webm/ogg/mp3/etc)
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio.filename)[1]) as tmp_in:
        tmp_in.write(await audio.read())
        input_path = tmp_in.name

    print(f"Audio recibido: {audio.filename} ({audio.content_type})")
    print(f"Guardado como: {input_path}")

    # Convertir a WAV con ffmpeg
    wav_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wav_path = wav_temp.name
    wav_temp.close()

    cmd_convert = ["ffmpeg", "-y", "-i", input_path, "-ar", "16000", "-ac", "1", wav_path]
    conv = subprocess.run(cmd_convert, capture_output=True, text=True)

    if conv.returncode != 0:
        print("FFMPEG ERROR:", conv.stderr)
        raise HTTPException(status_code=500, detail="Error convirtiendo audio a WAV")

    print(f"Audio convertido a WAV en: {wav_path}")

    # Transcribir con WhisperTiny
    cmd = ["ollama", "run", "whisper-tiny", wav_path]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=f"Error en WhisperTiny: {result.stderr}")

    transcripcion = result.stdout.strip()
    print("Transcripción:", transcripcion)

    # Llamar al RAG
    response = RAG.get_rag_response(transcripcion)

    if not response["exito"]:
        raise HTTPException(status_code=500, detail=response["error"])

    return ChatResponse(
        respuesta=response["respuesta"],
        fuentes=response["fuentes"]
    )
'''

@router.post("/chat/audio")
async def get_response_audio(audio: UploadFile = File(...)):
    import traceback
    print("\n--- NUEVA LLAMADA AUDIO ---")

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
        cmd2 = ["ollama", "run", "whisper-tiny", tmp_wav.name]
        print("➡ Whisper cmd:", " ".join(cmd2))
        whisper = subprocess.run(cmd2, capture_output=True, text=True)

        print("➡ Whisper stdout:", whisper.stdout)
        print("➡ Whisper stderr:", whisper.stderr)

        if whisper.returncode != 0:
            raise Exception("Whisper explotó")

        transcripcion = whisper.stdout.strip()
        print("➡ Transcripción:", transcripcion)

        # RAG
        response = RAG.get_rag_response(transcripcion)
        print("➡ RAG response:", response)

        if not response["exito"]:
            raise Exception("RAG explotó")

        return {
            "respuesta": response["respuesta"],
            "fuentes": response["fuentes"]
        }

    except Exception as e:
        print("ERROR EN BACKEND:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

