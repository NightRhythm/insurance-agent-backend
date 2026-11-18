
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.chat_threads.models import ChatThread


class ChatThreadRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, chat_thread: ChatThread):
        self.session.add(chat_thread)