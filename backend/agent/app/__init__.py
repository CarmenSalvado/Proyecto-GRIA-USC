from fastapi import FastAPI

def create_app(**kwargs):

    # Create FastAPI app
    app = FastAPI()

    # Include api routers
    from .api import chat
    
    app.include_router(chat.router)

    return app
