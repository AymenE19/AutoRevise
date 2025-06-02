from fastapi import APIRouter, HTTPException
from generating.models.schemas import RequestData, SummaryResponse, MindmapResponse, QuizResponse
from generating.db.mongodb import get_content_by_title, save_history
from generating.core.ai_client import process_session_action

router = APIRouter()

@router.post("/process_action")
async def process_action_route(data: RequestData):
    content = await get_content_by_title(data.title)
    if not content:
        raise HTTPException(status_code=404, detail="Titre introuvable dans la base de données.")

    result = await process_session_action(data.action, content)
    await save_history(data.title, data.action, result)