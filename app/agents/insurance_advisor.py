from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from app.agents.tools import query_candidate_products
from app.core.config import settings
from app.core.logging import get_logger
logger = get_logger(__name__)


SYSTEM_PROMPT = """
你是“安心保”的智能保险顾问。
你需要使用专业、准确、容易理解的语言回答用户的保险问题。
当信息不足时，应先向用户追问，不要编造保险产品或保障内容。
"""

# agent 在整个系统中只初始化一次
async def init_insurance_advisor(checkpointer):
    model = init_chat_model(
        model=settings.llm.chat_model,
        api_key=settings.llm.api_key,
        base_url=settings.llm.base_url,
        extra_body={"thinking": {"type": "disabled"}}
    )

    agent = create_agent(
        model=model,
        tools=[query_candidate_products],
        checkpointer=checkpointer,
        system_prompt=SYSTEM_PROMPT
    )

    logger.info("保险顾问 Agent 初始化完毕")

    return agent