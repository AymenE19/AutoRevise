from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

client = None
db = None

async def connect_to_mongo():
    global client, db
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["ai_course"]

async def close_mongo_connection():
    client.close()

async def get_content_by_title(title: str):
    document = await db["seances"].find_one({"title": title})
    return document.get("content") if document else None

async def save_history(title: str, action: str, result: dict):
    history_doc = {
        "title": title,
        "action": action,
        "result": result,
        "timestamp": datetime.utcnow()
    }
    await db["history"].insert_one(history_doc)