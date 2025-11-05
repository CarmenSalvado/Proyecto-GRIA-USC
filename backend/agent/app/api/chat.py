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



@router.post("/chat/audio")
async def get_response_audio(audio: UploadFile = File(...)):
    print("POST /rag/chat/audio")
    
    return "OK"
