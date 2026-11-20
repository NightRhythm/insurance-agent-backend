from uuid import UUID

from langchain.messages import AIMessage, HumanMessage
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.chat_thread.exceptions import ChatThreadNotFound
from app.modules.chat_thread.models import ChatThread
from app.modules.chat_thread.repository import ChatThreadRepository
from langgraph.graph.state import CompiledStateGraph

from app.modules.chat_thread.schemas import ChatHistoryResponse, ChatMessageResponse


class ChatThreadService:
    def __init__(self, session: AsyncSession, agent: CompiledStateGraph) -> None:
        self.session = session
        self.repository = ChatThreadRepository(session=session)
        self.agent = agent

    async def add(self, user_id: int, title: str):
        async with self.session.begin():
            chat_thread = ChatThread(user_id = user_id, title = title)
            await self.repository.add(chat_thread=chat_thread)
            return chat_thread

    async def list_by_user_id(self, user_id: int):
        return await self.repository.list_by_user_id(user_id=user_id)

    async def rename(self, user_id: int, thread_id: UUID, title: str):
        async with self.session.begin():
            chat_thread = await self.repository.required_owner(
                user_id=user_id,
                id=thread_id,
            )
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

            await self.agent.checkpointer.adelete_thread(thread_id=str(thread_id)) # type: ignore
            await self.repository.delete(thread)

    async def get_chat_history(self, user_id: int, thread_id: UUID):
        chat_thread = await self.repository.required_owner(
            user_id=user_id,
            id=thread_id,
        )
        if chat_thread is None:
            raise ChatThreadNotFound()

        config = {"configurable": {"thread_id": str(thread_id)}}
        state_snapshot = await self.agent.aget_state(config=config) # type: ignore

        messages = []
        for message in state_snapshot.values.get('messages', []):
            if isinstance(message, HumanMessage):
                role = "user"
            elif isinstance(message, AIMessage):
                role = "assistant"
            else:
                continue

            if message.text:
                messages.append(ChatMessageResponse(role=role, content=message.text))

        return ChatHistoryResponse(thread_id=thread_id, messages=messages)
