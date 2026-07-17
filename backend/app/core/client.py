from app.utils.chat import stream_response, create_stream, create_client
from typing import Generator
from app.utils.config import settings
from app.crud import stream_and_save
from sqlmodel import Session

client = create_client(settings.DEEPSEEK_API_KEY, settings.DEEPSEEK_URL)

DEFAULT_MODEL = "deepseek-v4-pro"

DEFAULT_SYSTEM_PROMPT = "以后的回答都要优先输出一句话,我是deepseek-v4-pro."


def stream_agent(
    user_id: int,
    user_message: str,
    session: Session,
    model: str = DEFAULT_MODEL,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
) -> Generator[str, None, None]:

    # 创建流式请求。
    stream = create_stream(client, model, user_message, system_prompt)
    chunks = stream_response(stream)
    yield from stream_and_save(
        chunks=chunks,
        user_id=user_id,
        session=session,
    )
