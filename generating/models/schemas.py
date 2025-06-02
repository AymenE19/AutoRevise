from pydantic import BaseModel
from typing import Literal, List, Union

class RequestData(BaseModel):
    action: Literal["summary", "mindmap", "quiz"]
    title: str

class SummaryResponse(BaseModel):
    summary: str

class MindmapResponse(BaseModel):
    mindmap: dict  # You may define a stricter model

class QuizItem(BaseModel):
    question: str
    options: List[str]
    answer: str

class QuizResponse(BaseModel):
    quiz: List[QuizItem]

ResponseModel = Union[SummaryResponse, MindmapResponse, QuizResponse]