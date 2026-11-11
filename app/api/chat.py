from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, model_validator

from app.domain.core import require_user
from app.services.chatbot_service import invoke_chatbot

router = APIRouter()


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=1200)

    @model_validator(mode="after")
    def validate_content(self):
        if not self.content.strip():
            raise ValueError("El mensaje no puede estar vacío.")
        return self


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=12)

    @model_validator(mode="after")
    def validate_latest_message(self):
        if self.messages[-1].role != "user":
            raise ValueError("El último mensaje debe ser una pregunta del usuario.")
        return self


@router.post("/api/chat")
def chat(
    request: ChatRequest,
    _: Annotated[dict[str, str], Depends(require_user)],
):
    messages = [
        {"role": message.role, "content": message.content.strip()}
        for message in request.messages
    ]
    try:
        return {"reply": invoke_chatbot(messages)}
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
