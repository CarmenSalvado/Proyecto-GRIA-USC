from fastapi import APIRouter, File, UploadFile

router = APIRouter(
    prefix="/rag",
    tags=["rag"],
    responses={404: {"error": "Not found"}},
)


@router.post("/chat/text")
async def get_response_text(message: str):
    print("POST /rag/chat/text")
    
    return f"###### Message: {message}"
    
@router.post("/chat/audio")
async def get_response_audio(audio: UploadFile = File(...)):
    print("POST /rag/chat/audio")
    
    return "OK"
