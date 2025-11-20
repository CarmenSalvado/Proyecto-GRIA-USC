from fastapi import FastAPI

def create_app(**kwargs):

    # Create FastAPI app
    app = FastAPI()

    # Include api routers
    from .api import chat
    
    #Placeholder para cuando vayas al puerto 8000
    @app.get("/", tags=["Root"])
    async def root():
        """Devuelve un saludo y redirige a la documentación."""
        return {
            "message": "Bienvenido a la RAG API.",
            "documentation": "Visita /docs para ver los endpoints."
        }
    

    app.include_router(chat.router)

    return app
