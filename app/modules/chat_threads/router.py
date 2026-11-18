

from typing import Annotated

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.database import get_session
from app.modules.chat_threads.schemas import ChatThreadCreate, ChatThreadResponse
from app.modules.chat_threads.service import ChatThreadService


router = APIRouter(prefix="/api/v1/chat-threads", tags=["会话管理接口"])

def get_chat_thread_service(session: AsyncSession = Depends(get_session)):
    return ChatThreadService(session=session)

@router.post("", response_model=ChatThreadResponse)
async def create_chat_thread(
    request: ChatThreadCreate,
    user_id: Annotated[int, Header(alias="x-user-id")],
    service: ChatThreadService = Depends(get_chat_thread_service)
):
    return await service.add(user_id, request.title)

@router.get("", response_model=list[ChatThreadResponse])
async def list_chat_threads(
    user_id: Annotated[int, Header(alias="x-user-id")],
    service: ChatThreadService = Depends(get_chat_thread_service)
):
    return await service.list_by_user_id(user_id)