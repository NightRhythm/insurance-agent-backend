from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.chat_thread.exceptions import ChatThreadNotFound
from app.modules.chat_thread.models import ChatThread
from app.modules.chat_thread.repository import ChatThreadRepository


class ChatThreadService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ChatThreadRepository(session=session)

    async def add(self, user_id: int, title: str):
        async with self.session.begin():
            chat_thread = ChatThread(user_id = user_id, title = title)
            await self.repository.add(chat_thread=chat_thread)
            return chat_thread

    async def list_by_user_id(self, user_id: int):
        return await self.repository.list_by_user_id(user_id=user_id)

    async def rename(self, user_id: int, id: str, title: str):
        async with self.session.begin():
            chat_thread = await self.repository.required_owner(user_id=user_id, id=id)
            if chat_thread is None:
                raise ChatThreadNotFound()

            chat_thread.title = title

            await self.session.flush()
            await self.session.refresh(chat_thread)

            return chat_thread

    async def delete(
        self,
        thread_id: UUID,
        user_id: int,
    ) -> None:
        async with self.session.begin():
            thread = await self.repository.required_owner(user_id=user_id, id=thread_id)
            if thread is None:
                raise ChatThreadNotFound

            await self.repository.delete(thread)