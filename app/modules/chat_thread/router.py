

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.database import get_session
from app.modules.chat_thread.schemas import ChatHistoryResponse, ChatThreadCreate, ChatThreadResponse
from app.modules.chat_thread.service import ChatThreadService


router = APIRouter(prefix="/api/v1/chat-threads", tags=["会话管理接口"])

def get_chat_thread_service(request: Request, session: AsyncSession = Depends(get_session)):
    agent = request.app.state.agent
    return ChatThreadService(session=session, agent=agent)

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

@router.patch("/{thread_id}", response_model=ChatThreadResponse)
async def rename(
    thread_id: UUID,
    request: ChatThreadCreate,
    user_id: Annotated[int, Header(alias="x-user-id")],
    service: ChatThreadService = Depends(get_chat_thread_service)
):
    return await service.rename(
        user_id=user_id,
        thread_id=thread_id,
        title=request.title,
    )

from fastapi import Response, status


@router.delete("/{thread_id}", status_code=status.HTTP_204_NO_CONTENT,)
async def delete_chat_thread(
    thread_id: UUID,
    user_id: Annotated[int, Header(alias="x-user-id")],
    service: ChatThreadService = Depends(get_chat_thread_service),
) -> Response:
    """删除指定会话"""

    await service.delete(thread_id, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{thread_id}/messages", response_model=ChatHistoryResponse)
async def get_chat_history(
    thread_id: UUID,
    user_id: Annotated[int, Header(alias="x-user-id")],
    service: ChatThreadService = Depends(get_chat_thread_service),
):
    """查询指定会话的历史消息"""

    return await service.get_chat_history(user_id, thread_id)