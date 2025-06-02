from fastapi import FastAPI
from generating.api.routes import router as api_router
from generating.db.mongodb import connect_to_mongo, close_mongo_connection
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    await connect_to_mongo()
    yield
    # Shutdown logic
    await close_mongo_connection()

app = FastAPI(title="AI Course Assistant", lifespan=lifespan)

# Include your API routes
app.include_router(api_router, prefix="/api")

# Add a simple root route so the home page doesn't just spin
@app.get("/")
def read_root():
    return {
        "message": "Bienvenue sur l'API d'AutoRevise ! 🎓",
        "docs": "Accédez à la documentation via /docs",
        "api_prefix": "/api"
    }

