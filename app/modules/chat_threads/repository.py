
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.chat_threads.models import ChatThread


class ChatThreadRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, chat_thread: ChatThread):
        self.session.add(chat_thread)

    async def list_by_user_id(self, user_id: int):
        threads = await self.session.scalars(
            select(ChatThread).where(ChatThread.user_id == user_id).order_by(ChatThread.updated_at.desc(), ChatThread.created_at.desc())
        )
        return threads.all()

    async def required_owner(self, user_id: int, id: str) -> ChatThread | None:
        """校验指定会话是否属于指定用户"""
        return await self.session.scalar(
            select(ChatThread).where(ChatThread.id == id, ChatThread.user_id == user_id)
        )

    async def delete(self, thread: ChatThread) -> None:
        await self.session.delete(thread)