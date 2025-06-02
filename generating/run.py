from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from google import genai

from generating.settings import MONGODB_URI, MONGODB_DB_NAME, GEMINI_API_KEY
from generating.functionalities import process_user_action
from utils.database import MongoDB


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.gemini_client = genai.Client(api_key=GEMINI_API_KEY)

    with MongoDB(MONGODB_URI, MONGODB_DB_NAME) as app.state.db:
        print("Starting up")
        yield
        print("Shutting down")


fastapi_app = FastAPI(lifespan=lifespan)


@fastapi_app.get("/")
def read_root(request: Request):
    return {
        "message": "Bienvenue sur l'API d'AutoRevise ! 🎓",
        "docs": "Accédez à la documentation via /docs",
    }


@fastapi_app.post("/process_action")
async def process_action_route(request: Request, action: str, collection: str, session: str):
    return process_user_action(request.app, action, collection, session)


if __name__ == "__main__":
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8080)
